from pathlib import Path

from typer.testing import CliRunner

import cvgenerator.cli as cli
from cvgenerator.cli import app

DATA = Path(__file__).parent / "fixtures" / "cv.yaml"

runner = CliRunner()


def _templates(tmp_path: Path, *names: str) -> Path:
    templates = tmp_path / "templates"
    for name in names:
        (templates / name).mkdir(parents=True)
        (templates / name / "cv.tex.j2").write_text(
            r"\VAR{ cv.header.name | tex }/" + name, encoding="utf-8"
        )
    return templates


def _build(tmp_path: Path, templates: Path) -> tuple[int, Path]:
    out = tmp_path / "out"
    result = runner.invoke(
        app,
        # fmt: off
        [
            "build",
            "--data", str(DATA),
            "--templates-dir", str(templates),
            "-o", str(out),
            "--no-pdf",
        ],
        # fmt: on
    )
    return result.exit_code, out


def test_every_template_is_rendered_into_one_flat_directory(tmp_path):
    templates = _templates(tmp_path, "modern", "classic")

    code, out = _build(tmp_path, templates)

    assert code == 0
    assert sorted(p.name for p in out.iterdir()) == ["cv-classic.tex", "cv-modern.tex"]
    assert (out / "cv-classic.tex").read_text(encoding="utf-8").endswith("/classic")


def test_directory_without_a_template_file_is_skipped(tmp_path):
    templates = _templates(tmp_path, "modern")
    (templates / "scratch").mkdir()

    code, out = _build(tmp_path, templates)

    assert code == 0
    assert [p.name for p in out.iterdir()] == ["cv-modern.tex"]


def test_template_selection_and_suffix(tmp_path):
    templates = _templates(tmp_path, "modern", "single")
    out = tmp_path / "out"

    result = runner.invoke(
        app,
        [
            "build", "--data", str(DATA), "--templates-dir", str(templates),
            "--template", "single", "--suffix", "en", "-o", str(out), "--no-pdf",
        ],
    )

    assert result.exit_code == 0
    assert [p.name for p in out.iterdir()] == ["cv-single-en.tex"]


def test_empty_templates_directory_is_an_error(tmp_path):
    templates = tmp_path / "templates"
    templates.mkdir()

    code, _ = _build(tmp_path, templates)

    assert code != 0


def test_pdf_build_leaves_only_the_pdf_in_output(tmp_path, monkeypatch):
    templates = _templates(tmp_path, "modern")
    out = tmp_path / "out"

    def fake_compile(tex: Path) -> Path:
        assert out not in tex.parents
        tex.with_suffix(".aux").write_text("aux", encoding="utf-8")
        pdf = tex.with_suffix(".pdf")
        pdf.write_bytes(b"pdf")
        return pdf

    monkeypatch.setattr(cli, "compile_pdf", fake_compile)
    result = runner.invoke(
        app,
        [
            "build",
            "--data", str(DATA),
            "--templates-dir", str(templates),
            "-o", str(out),
        ],
    )

    assert result.exit_code == 0
    assert [p.name for p in out.iterdir()] == ["cv-modern.pdf"]
