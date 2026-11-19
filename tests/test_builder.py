from pathlib import Path

import pytest

from cvgenerator import builder
from cvgenerator.builder import CompileError, compile_pdf, latexmk_command


def test_latexmk_command_runs_xelatex_and_stops_on_the_first_error():
    cmd = latexmk_command("cv.tex")
    assert cmd[0] == "latexmk"
    assert "-xelatex" in cmd
    assert "-halt-on-error" in cmd
    assert cmd[-1] == "cv.tex"


def test_missing_latexmk_points_at_the_docker_image(monkeypatch):
    monkeypatch.setattr(builder.shutil, "which", lambda _: None)
    with pytest.raises(CompileError, match="latexmk not found"):
        compile_pdf(Path("output/modern/cv.tex"))
