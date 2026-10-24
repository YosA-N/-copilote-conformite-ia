"""Official legal texts used by the copilot, each pinned to one consolidated version."""

from dataclasses import dataclass

USER_AGENT = "compliance-copilot/0.1 (+https://github.com/YosA-N/copilote-conformite-ia)"


@dataclass(frozen=True)
class Source:
    key: str  # short id used in file names and chunk ids
    name: str  # short name shown to users
    reference: str  # official reference of the regulation
    celex: str  # CELEX number of the consolidated version
    expected_articles: int
    expected_annexes: int
    count_note: str = ""  # why the expected counts differ from the original text, if they do

    @property
    def version_date(self) -> str:
        """ISO date of the consolidated version, read from the CELEX suffix (e.g. -20260727)."""
        stamp = self.celex.rsplit("-", 1)[1]
        return f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"

    @property
    def cellar_url(self) -> str:
        """Publications Office repository behind EUR-Lex, meant for programmatic access."""
        return f"https://publications.europa.eu/resource/celex/{self.celex}"

    @property
    def eurlex_url(self) -> str:
        """Page that people open in a browser; anchors such as #art_37 point to one article."""
        return f"https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:{self.celex}"

    @property
    def eurlex_html_url(self) -> str:
        """Plain HTML version of the text, used for manual downloads."""
        return f"https://eur-lex.europa.eu/legal-content/FR/TXT/HTML/?uri=CELEX:{self.celex}"

    @property
    def raw_filename(self) -> str:
        return f"{self.key}_{self.celex}.xhtml"


SOURCES = (
    Source(
        key="gdpr",
        name="RGPD",
        reference="règlement (UE) 2016/679",
        celex="02016R0679-20160504",
        expected_articles=99,
        expected_annexes=0,
    ),
    Source(
        key="ai_act",
        name="AI Act",
        reference="règlement (UE) 2024/1689",
        celex="02024R1689-20260727",
        expected_articles=119,
        expected_annexes=14,
        count_note=(
            "113 articles et 13 annexes à l'origine ; le règlement (UE) 2026/1744 a inséré "
            "les articles 4 bis, 60 bis, 75 bis à 75 quinquies et l'annexe XIV."
        ),
    ),
)
