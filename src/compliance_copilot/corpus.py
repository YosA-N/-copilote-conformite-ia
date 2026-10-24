"""Read consolidated EUR-Lex texts (XHTML) and cut them into chunks ready for indexing.

Structure of the documents (same HTML on EUR-Lex and on Cellar):
- each article is a <div id="art_37"> (inserted articles: art_4a = "Article 4 bis"),
  with its number in p.title-article-norm and its title in p.stitle-article-norm;
- each annex is a <div id="anx_III">, with its number in p.title-annex-1 and its title
  usually in p.title-annex-2;
- chapters and sections are <div id="cpt_IV"> and <div id="cpt_IV.sct_4"> around the articles;
- numbered paragraphs are div.norm with a span.no-parag label ("1.", "1 bis."); list items are
  div.grid-list with their label ("a)", "1)") in div.grid-list-column-1;
- annexes may be divided by headings (p.title-gr-seq-level-1 and -2) and contain tables;
- p.modref holds editorial markers (▼B, ▼M1, ►C1) that are not part of the law.
"""

import re
from dataclasses import asdict, dataclass, field

from bs4 import BeautifulSoup, Tag

from compliance_copilot.sources import Source

MAX_CHUNK_CHARS = 4000  # about 1,000 tokens of French text

ARTICLE_ID = re.compile(r"^art_\d+[a-z]?$")
ANNEX_ID = re.compile(r"^anx_[IVXLC]+$")
CHAPTER_ID = re.compile(r"^cpt_[IVXLC]+$")
SECTION_ID = re.compile(r"^cpt_[IVXLC]+\.sct_\d+$")
LABEL = re.compile(r"^(?:Section\s+)?(\w+(?: (?:bis|ter|quater|quinquies|sexies|septies|octies))?)\s*[.)]")
TITLE_CLASSES = {"title-article-norm", "eli-title", "title-annex-1", "title-annex-2"}
HEADING_CLASSES = {"title-gr-seq-level-1", "title-gr-seq-level-2", "title-gr-seq-level-3"}
EDITORIAL_CLASSES = {"modref", "footnote", "arrow"}
PART_ID_PREFIXES = {"paragraphe": "par", "définition": "def", "point": "pt", "section": "sec", "partie": "part"}


@dataclass
class Unit:
    """One article or annex, before chunking."""

    unit_type: str  # "article" or "annex"
    anchor: str  # HTML id, also the anchor in the EUR-Lex URL: art_37, anx_III
    number: str  # "37", "4 bis", "III"
    title: str
    chapter: str | None
    section: str | None
    element: Tag = field(repr=False)
    title_element: Tag | None = field(default=None, repr=False)


@dataclass
class Chunk:
    id: str
    regulation: str
    regulation_ref: str
    celex: str
    unit_type: str
    number: str
    title: str
    chapter: str | None
    section: str | None
    part: str | None  # "paragraphe 2", "définition 12", "point 1", or None for a whole unit
    part_index: int
    part_count: int
    source_url: str
    version_date: str
    text: str
    char_count: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class _Part:
    """A piece of a unit: a numbered paragraph, a definition, an annex point or section..."""

    kind: str | None  # a key of PART_ID_PREFIXES, or None for a whole unit
    label: str | None  # "2", "1 bis", "12", "1 a", "1, points a) à e)"
    lines: list[str]
    context: list[str] = field(default_factory=list)  # headings and lead-in repeated in the chunk
    element: Tag | None = None  # the paragraph or list item, kept to cut it further if needed
    trailing: list[str] = field(default_factory=list)  # text that follows the element

    @property
    def all_lines(self) -> list[str]:
        return [*self.context, *self.lines, *self.trailing]


# ---------------------------------------------------------------- HTML helpers


def _classes(element: Tag) -> set[str]:
    return set(element.get("class") or [])


def _inline_text(element: Tag) -> str:
    """Text of an element on one line, with whitespace normalised."""
    return re.sub(r"\s+", " ", element.get_text()).strip()


def _is_list_item(element: Tag) -> bool:
    return {"grid-container", "grid-list"} <= _classes(element)


def _is_numbered_paragraph(element: Tag) -> bool:
    return "norm" in _classes(element) and element.find("span", class_="no-parag", recursive=False) is not None


def _item_label(element: Tag) -> str:
    """Label of a list item ("a)", "1)", "—") or of a numbered paragraph ("1.")."""
    if _is_list_item(element):
        label = element.find("div", class_="grid-list-column-1", recursive=False)
    else:
        label = element.find("span", class_="no-parag", recursive=False)
    return _inline_text(label) if label else ""


def _item_body(element: Tag) -> Tag:
    """The part of a list item or numbered paragraph that comes after its label."""
    if _is_list_item(element):
        return element.find("div", class_="grid-list-column-2", recursive=False) or element
    return element.find("div", class_="inline-element", recursive=False) or element


def _render_lines(element: Tag) -> list[str]:
    """Render a block of the law as text: one line per sentence block, list item or table row."""
    if _is_list_item(element) or _is_numbered_paragraph(element):
        body = _item_body(element)
        if body is element:  # label and text side by side: <span>1.</span> text
            text = _inline_text(element).removeprefix(_item_label(element)).strip()
            body_lines = [text] if text else []
        else:
            body_lines = _render_lines(body)
        label = _item_label(element)
        if not body_lines:
            return [label] if label else []
        return [f"{label} {body_lines[0]}".strip(), *body_lines[1:]]
    if element.name == "table":
        rows = []
        for row in element.find_all("tr"):
            cells = [_inline_text(cell) for cell in row.find_all(["td", "th"])]
            if any(cells):
                rows.append(" | ".join(cell for cell in cells if cell))
        return rows
    if element.name == "p" or not element.find(["p", "div", "table"]):
        text = _inline_text(element)
        return [text] if text else []
    lines = []
    for child in element.children:
        if isinstance(child, Tag):
            lines.extend(_render_lines(child))
        elif child.strip():
            lines.append(re.sub(r"\s+", " ", child).strip())
    return lines


def _strip_editorial_marks(soup: BeautifulSoup) -> None:
    """Remove consolidation markers and footnotes: they are not part of the law."""
    for element in soup.find_all(class_=lambda value: value in EDITORIAL_CLASSES):
        element.decompose()
    for link in soup.find_all("a", href=re.compile(r"^#E\d+")):  # footnote call signs
        link.decompose()
    for element in soup.find_all("hr"):
        element.decompose()
    for text_node in soup.find_all(string=re.compile("[►◄▼]")):
        text_node.replace_with(re.sub(r"[►◄▼]\s?(?:[A-Z]\d+)?", "", text_node))


# ---------------------------------------------------------------- reading


def read_amendments(html: str) -> list[str]:
    """List the amending acts and corrigenda named in the header of a consolidated text."""
    soup = BeautifulSoup(html, "html.parser")
    amendments = []
    for marker in soup.select("p.arrow"):
        row = marker.find_parent("tr")
        member = row.select_one('p[class^="title-fam-member"]') if row else None
        if member:
            amendments.append(f"{_inline_text(marker).lstrip('►')} : {_inline_text(member)}")
    return amendments


def _division_label(division: Tag | None) -> str | None:
    """'Chapitre IV — Responsable du traitement et sous-traitant' from a cpt_/sct_ div."""
    if division is None:
        return None
    parts = [
        _inline_text(p)
        for p in division.find_all("p", class_=["title-division-1", "title-division-2"], recursive=False)
    ]
    label = " — ".join(part for part in parts if part)
    return re.sub(r"^CHAPITRE", "Chapitre", label) or None


def _article_number(heading: str) -> str:
    number = re.sub(r"^Article\s+", "", heading).strip()
    return "1" if number.lower() == "premier" else number


def _annex_title(element: Tag) -> Tag | None:
    """Annex titles are in p.title-annex-2, in a second p.title-annex-1, or in the first paragraph."""
    title = element.find("p", class_="title-annex-2", recursive=False)
    headings = element.find_all("p", class_="title-annex-1", recursive=False)
    if title is None and len(headings) > 1:
        title = headings[1]
    if title is None and headings:
        candidate = headings[0].find_next_sibling(lambda tag: tag.name == "p" and _inline_text(tag))
        if candidate is not None and len(_inline_text(candidate)) <= 300:
            title = candidate
    return title


def read_units(html: str) -> list[Unit]:
    """Extract every article and annex, in document order."""
    soup = BeautifulSoup(html, "html.parser")
    _strip_editorial_marks(soup)
    units = []
    for element in soup.find_all("div", id=True):
        anchor = element["id"]
        if ARTICLE_ID.match(anchor):
            heading = element.find("p", class_="title-article-norm", recursive=False)
            title = element.find("p", class_="stitle-article-norm")
            units.append(
                Unit(
                    unit_type="article",
                    anchor=anchor,
                    number=_article_number(_inline_text(heading)) if heading else anchor[4:],
                    title=_inline_text(title) if title else "",
                    chapter=_division_label(element.find_parent("div", id=CHAPTER_ID)),
                    section=_division_label(element.find_parent("div", id=SECTION_ID)),
                    element=element,
                )
            )
        elif ANNEX_ID.match(anchor):
            title = _annex_title(element)
            units.append(
                Unit(
                    unit_type="annex",
                    anchor=anchor,
                    number=anchor[4:],
                    title=_inline_text(title) if title else "",
                    chapter=None,
                    section=None,
                    element=element,
                    title_element=title,
                )
            )
    return units


# ---------------------------------------------------------------- chunking


def _body_blocks(unit: Unit) -> list[Tag]:
    """Top-level blocks of a unit, without its number and title."""
    blocks = []
    for child in unit.element.children:
        if not isinstance(child, Tag) or child is unit.title_element or _classes(child) & TITLE_CLASSES:
            continue
        if child.name == "div" and not _classes(child):
            blocks.extend(c for c in child.children if isinstance(c, Tag))  # plain wrapper div
        else:
            blocks.append(child)
    return [block for block in blocks if _render_lines(block)]


def _body_lines(unit: Unit) -> list[str]:
    return [line for block in _body_blocks(unit) for line in _render_lines(block)]


def _label_of(text: str) -> str | None:
    """'1' from '1.', 'a' from 'a)', '1 bis' from '1 bis.', 'A' from 'Section A. ...'."""
    match = LABEL.match(text)
    return match.group(1) if match else None


def _split_into_parts(unit: Unit) -> list[_Part]:
    """One part per numbered paragraph, definition or point, or per annex section.

    Text before the first item is a lead-in repeated in every item of the list (for example
    "Les systèmes d'IA à haut risque ... sont les systèmes répertoriés dans l'un des domaines
    suivants:"). Text after an item stays with that item. A heading followed by text without
    any list becomes a "section" part.
    """
    item_kind = "définition" if unit.title.lower() == "définitions" else "point"
    parts: list[_Part] = []
    headings: list[str] = []  # current level-1 and level-2 headings of an annex
    heading_labels: list[str] = []
    lead_in: list[str] = []
    lead_in_used = False
    current: _Part | None = None

    def flush_lead_in() -> None:
        if lead_in and not lead_in_used:
            if headings:
                label = " ".join(heading_labels) or str(len(parts) + 1)
                parts.append(_Part("section", label, list(lead_in), list(headings)))
            else:
                parts.append(_Part(None, None, list(lead_in)))

    for block in _body_blocks(unit):
        lines = _render_lines(block)
        if _classes(block) & HEADING_CLASSES:
            flush_lead_in()
            depth = 0 if "title-gr-seq-level-1" in _classes(block) else 1
            headings = [*headings[:depth], *lines]
            heading_labels = [*heading_labels[:depth], _label_of(lines[0]) or ""]
            lead_in, lead_in_used, current = [], False, None
        elif _is_numbered_paragraph(block) or _is_list_item(block):
            kind = "paragraphe" if _is_numbered_paragraph(block) else item_kind
            label = _label_of(_item_label(block)) or str(len(parts) + 1)
            label = " ".join(filter(None, [*heading_labels, label]))
            current = _Part(kind, label, lines, [*headings, *lead_in], block)
            parts.append(current)
            lead_in_used = lead_in_used or bool(lead_in)
        elif current is not None:
            current.trailing.extend(lines)
        else:
            lead_in.extend(lines)
    flush_lead_in()
    return parts


def _split_by_points(part: _Part, max_chars: int) -> list[_Part]:
    """Cut a paragraph or point between its own points a), b)..., keeping its lead-in."""
    lead_in: list[str] = []
    items: list[tuple[str, list[str]]] = []  # (label, lines) of each point
    for child in _item_body(part.element).children:
        if not isinstance(child, Tag):
            continue
        lines = _render_lines(child)
        if _is_list_item(child):
            items.append((_item_label(child), lines))
        elif items:
            items[-1][1].extend(lines)
        else:
            lead_in.extend(lines)
    if len(items) < 2 or not lead_in:
        return [part]
    lead_in[0] = f"{_item_label(part.element)} {lead_in[0]}"
    items[-1][1].extend(part.trailing)

    groups: list[list[tuple[str, list[str]]]] = []
    for item in items:
        candidate = [line for _, lines in (groups[-1] if groups else []) for line in lines] + item[1]
        if groups and len("\n".join([*part.context, *lead_in, *candidate])) <= max_chars:
            groups[-1].append(item)
        else:
            groups.append([item])
    pieces = []
    for group in groups:
        first, last = group[0][0], group[-1][0]
        points = f"point {first}" if first == last else f"points {first} à {last}"
        lines = [line for _, item_lines in group for line in item_lines]
        pieces.append(_Part(part.kind, f"{part.label}, {points}", lines, [*part.context, *lead_in]))
    return pieces


def _split_by_lines(part: _Part, max_chars: int) -> list[_Part]:
    """Last resort: cut between lines, so that no sentence is cut in the middle."""
    if len("\n".join(part.all_lines)) <= max_chars:
        return [part]
    groups: list[list[str]] = [[]]
    for line in [*part.lines, *part.trailing]:
        if groups[-1] and len("\n".join([*part.context, *groups[-1], line])) > max_chars:
            groups.append([])
        groups[-1].append(line)
    if len(groups) == 1:  # a single line longer than the limit: keep it whole
        return [part]
    kind = part.kind or "partie"
    return [
        _Part(kind, f"{part.label} ({index}/{len(groups)})" if part.label else str(index), lines, part.context)
        for index, lines in enumerate(groups, start=1)
    ]


def _split_large_part(part: _Part, max_chars: int) -> list[_Part]:
    if len("\n".join(part.all_lines)) <= max_chars:
        return [part]
    pieces = _split_by_points(part, max_chars) if part.element is not None else [part]
    return [piece for p in pieces for piece in _split_by_lines(p, max_chars)]


def _header(source: Source, unit: Unit) -> str:
    kind = "Article" if unit.unit_type == "article" else "Annexe"
    title = f" : {unit.title}" if unit.title else ""
    return f"{source.name} — {source.reference} — {kind} {unit.number}{title}"


def _part_id(part: _Part) -> str:
    """'par_2', 'par_1-bis', 'def_12', 'pt_1-a', 'par_1_a-e', 'sec_2-a_1'."""
    label = (part.label or "").replace(", points ", "_").replace(", point ", "_").replace(" à ", "-")
    label = re.sub(r"\s*\((\d+)/\d+\)", r"_\1", label).replace(")", "")
    label = re.sub(r"[^\w-]+", "-", label).strip("-")
    return f"{PART_ID_PREFIXES[part.kind]}_{label}"


def chunk_unit(source: Source, unit: Unit, max_chars: int = MAX_CHUNK_CHARS) -> list[Chunk]:
    """Cut one article or annex into chunks; every chunk starts with the same header."""
    header = _header(source, unit)
    body = _body_lines(unit)
    if len("\n".join([header, "", *body])) <= max_chars:
        parts = [_Part(None, None, body)]
    else:
        budget = max_chars - len(header) - 2  # the header and a blank line start every chunk
        parts = [piece for part in _split_into_parts(unit) for piece in _split_large_part(part, budget)]

    chunks: list[Chunk] = []
    seen_ids: set[str] = set()
    for index, part in enumerate(parts, start=1):
        chunk_id = f"{source.key}:{unit.anchor}"
        if part.kind:
            chunk_id += f":{_part_id(part)}"
        elif len(parts) > 1:
            chunk_id += f":part_{index}"
        if chunk_id in seen_ids:
            chunk_id += f"-{index}"
        seen_ids.add(chunk_id)
        text = "\n".join([header, "", *part.all_lines]).strip()
        chunks.append(
            Chunk(
                id=chunk_id,
                regulation=source.name,
                regulation_ref=source.reference,
                celex=source.celex,
                unit_type=unit.unit_type,
                number=unit.number,
                title=unit.title,
                chapter=unit.chapter,
                section=unit.section,
                part=f"{part.kind} {part.label}" if part.kind else None,
                part_index=index,
                part_count=len(parts),
                source_url=f"{source.eurlex_url}#{unit.anchor}",
                version_date=source.version_date,
                text=text,
                char_count=len(text),
            )
        )
    return chunks


def missing_lines(unit: Unit, chunks: list[Chunk]) -> list[str]:
    """Lines of the unit that appear in none of its chunks (should always be empty)."""
    texts = "\n".join(chunk.text for chunk in chunks)
    return [line for line in _body_lines(unit) if line not in texts]


def build_chunks(source: Source, html: str, max_chars: int = MAX_CHUNK_CHARS) -> tuple[list[Unit], list[Chunk]]:
    """Read one consolidated text and return its articles and annexes, and their chunks."""
    units = read_units(html)
    chunks = [chunk for unit in units for chunk in chunk_unit(source, unit, max_chars)]
    return units, chunks
