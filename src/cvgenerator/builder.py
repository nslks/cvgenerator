from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

LOG_TAIL_LINES = 30


class CompileError(RuntimeError):
    """XeLaTeX could not turn the rendered source into a PDF."""


def latexmk_command(tex_name: str) -> list[str]:
    return [
        "latexmk",
        "-xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        tex_name,
    ]


def compile_pdf(tex: Path) -> Path:
    """Compile `tex` in place and return the resulting PDF path.

    Callers should use a temporary directory when auxiliary files are not wanted.
    """
    if shutil.which("latexmk") is None:
        raise CompileError(
            "latexmk not found. Install a TeX distribution, or run the Docker image "
            "(see README) which ships XeLaTeX and latexmk."
        )

    result = subprocess.run(
        latexmk_command(tex.name),
        cwd=tex.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    pdf = tex.with_suffix(".pdf")
    if result.returncode != 0 or not pdf.is_file():
        raise CompileError(f"latexmk failed for {tex}:\n{_tail(result.stdout, result.stderr)}")
    return pdf


def _tail(stdout: str, stderr: str) -> str:
    lines = (stdout + stderr).splitlines()
    return "\n".join(lines[-LOG_TAIL_LINES:])
