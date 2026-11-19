from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    StringConstraints,
    model_validator,
)


class Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


# A typo in any of the theme colours would only surface as a cryptic LaTeX error.
HexColor = Annotated[str, StringConstraints(pattern=r"^#[0-9A-Fa-f]{6}$")]


class YearMonth(Base):
    year: int = Field(ge=1900, le=2100)
    month: int = Field(ge=1, le=12)

    @classmethod
    def from_string(cls, value: str) -> YearMonth:
        y, m = value.split("-", 1)
        return cls(year=int(y), month=int(m))

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, value: object) -> object:
        if isinstance(value, str):
            return cls.from_string(value).model_dump()
        if isinstance(value, date):
            return {"year": value.year, "month": value.month}
        return value

    def as_date(self) -> date:
        return date(self.year, self.month, 1)


class Contact(Base):
    location: str
    address: list[str] = Field(default_factory=list)
    email: EmailStr
    phone: str | None = None
    birth_date: date | None = None
    linkedin: HttpUrl | None = None
    github: HttpUrl | None = None
    website: HttpUrl | None = None


class Header(Base):
    name: str
    title: str
    contact: Contact
    photo: Path | None = None


class Achievement(Base):
    title: str
    impact: str | None = None


class ExperiencePhase(Base):
    """A distinct focus or internal role within one employment relationship."""

    title: str
    company: str | None = None
    start: YearMonth
    end: YearMonth | None = None
    achievements: list[Achievement] = Field(default_factory=list)
    tech: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _period_ordered(self) -> Self:
        if self.end and self.end.as_date() < self.start.as_date():
            raise ValueError(f"end {self.end} before start {self.start}")
        return self


class Experience(Base):
    role: str
    company: str
    location: str | None = None
    start: YearMonth
    end: YearMonth | None = None
    achievements: list[Achievement] = Field(default_factory=list)
    tech: list[str] = Field(default_factory=list)
    phases: list[ExperiencePhase] = Field(default_factory=list)

    @model_validator(mode="after")
    def _period_ordered(self) -> Self:
        if self.end and self.end.as_date() < self.start.as_date():
            raise ValueError(f"end {self.end} before start {self.start}")
        return self


class Project(Base):
    name: str
    tagline: str | None = None
    url: HttpUrl | None = None
    achievements: list[Achievement] = Field(default_factory=list)
    tech: list[str] = Field(default_factory=list)


class Education(Base):
    degree: str
    institution: str
    location: str | None = None
    start: YearMonth
    end: YearMonth | None = None
    notes: list[str] = Field(default_factory=list)


class CEFR(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"
    FLUENT = "fluent"
    NATIVE = "native"


class Language(Base):
    name: str
    level: CEFR


class Certification(Base):
    name: str
    issuer: str
    year: int | None = Field(default=None, ge=1900, le=2100)
    url: HttpUrl | None = None


class Talk(Base):
    title: str
    venue: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    url: HttpUrl | None = None


class Tool(Base):
    name: str
    level: str


class SkillRow(Base):
    skill: str
    years: str
    level: int = Field(ge=0)


class SkillMatrix(Base):
    max_level: int = Field(default=5, ge=1)
    rows: list[SkillRow] = Field(default_factory=list)

    @model_validator(mode="after")
    def _levels_fit_the_scale(self) -> Self:
        for row in self.rows:
            if row.level > self.max_level:
                raise ValueError(f"{row.skill}: level {row.level} exceeds max_level {self.max_level}")
        return self


class Footer(Base):
    city: str
    signature: Path | None = None


class Theme(Base):
    accent: HexColor = "#2A5CAA"
    accent_light: HexColor = "#7E9BC8"
    text: HexColor = "#1A1A1A"
    muted: HexColor = "#6E6E6E"
    rule: HexColor = "#C9CFD8"
    sidebar_bg: HexColor = "#EEF2F7"
    pip_off: HexColor = "#D6DCE6"
    font_main: str = "TeX Gyre Pagella"
    font_sans: str = "TeX Gyre Heros"
    section_rule_gap_ex: float = 0.6
    side_rule_gap_ex: float = 0.5
    footer_band_mm: float = 16


class CV(Base):
    language: Literal["de", "en"] = "de"
    date_precision: Literal["month", "year"] = "month"
    header: Header
    summary: str | None = None
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    skills: dict[str, list[str]] = Field(default_factory=dict)
    skill_matrix: SkillMatrix | None = None
    tools: list[Tool] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    talks: list[Talk] = Field(default_factory=list)
    footer: Footer | None = None
    theme: Theme = Field(default_factory=Theme)
