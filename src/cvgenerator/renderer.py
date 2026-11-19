from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from cvgenerator.models import CV, YearMonth

TEMPLATE_FILE = "cv.tex.j2"

LABELS = {
    "de": {
        "document_language": "german", "profile": "Profil", "experience": "Erfahrung",
        "project_experience": "Projekterfahrung", "certificates": "Zertifikate",
        "present": "heute", "cv": "Lebenslauf", "page": "Seite", "phone": "Tel.",
        "email": "Email", "birth_date": "Geburtsdatum", "address": "Anschrift",
        "technical_profile": "Technisches Profil", "languages": "Sprache",
        "education": "Ausbildung", "native": "Muttersprache", "fluent": "Fließend",
    },
    "en": {
        "document_language": "english", "profile": "Profile", "experience": "Experience",
        "project_experience": "Project Experience", "certificates": "Certifications",
        "present": "Present", "cv": "CV", "page": "Page", "phone": "Phone",
        "email": "Email", "birth_date": "Date of birth", "address": "Address",
        "technical_profile": "Technical Profile", "languages": "Languages",
        "education": "Education", "native": "Native", "fluent": "Fluent",
    },
}

GERMAN_MONTHS = (
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
)  # fmt: skip

_LATEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
_LATEX_PATTERN = re.compile("|".join(re.escape(c) for c in _LATEX_SPECIALS))


def latex_escape(value: object) -> str:
    """Escape LaTeX special characters. Single pass, so replacements are never re-escaped."""
    return _LATEX_PATTERN.sub(lambda m: _LATEX_SPECIALS[m.group()], str(value))


def year_month(value: YearMonth) -> str:
    return f"{value.month:02d}/{value.year}"


def german_date(value: date) -> str:
    return f"{value.day}. {GERMAN_MONTHS[value.month - 1]} {value.year}"


def build_env(template_dir: Path) -> Environment:
    """Jinja environment with LaTeX-safe delimiters: {{ }} and {% %} collide with TeX braces."""
    env = Environment(
        loader=FileSystemLoader(template_dir),
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        extensions=["jinja2.ext.do"],
        trim_blocks=False,  # keeps the newline after an inline \BLOCK{endif}
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
        autoescape=False,
    )
    env.filters["tex"] = latex_escape
    env.filters["ym"] = year_month
    env.filters["de"] = german_date
    return env


def _asset(path: Path | None, base_dir: Path) -> str | None:
    """Absolute path to an asset. latexmk runs in the output directory, so a
    path relative to the data file would not resolve from there."""
    if path is None:
        return None
    resolved = path if path.is_absolute() else base_dir / path
    return resolved.resolve().as_posix()


def render(
    cv: CV,
    template_dir: Path,
    *,
    base_dir: Path | None = None,
    today: date | None = None,
) -> str:
    base = base_dir if base_dir is not None else Path.cwd()
    template = build_env(template_dir).get_template(TEMPLATE_FILE)
    return template.render(
        cv=cv,
        labels=LABELS[cv.language],
        photo=_asset(cv.header.photo, base),
        signature=_asset(cv.footer.signature if cv.footer else None, base),
        template_dir=template_dir.resolve().as_posix(),
        today=today if today is not None else date.today(),
    )
