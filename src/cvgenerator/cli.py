from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Annotated

import typer

from cvgenerator.builder import CompileError, compile_pdf
from cvgenerator.loader import load_cv
from cvgenerator.renderer import TEMPLATE_FILE, render

app = typer.Typer(
    help="Data-driven CV generator: YAML -> Jinja2 -> XeLaTeX -> PDF.",
    no_args_is_help=True,
)


@app.callback()
def _main() -> None:
    """Keeps `build` a subcommand instead of collapsing it into the top-level app."""


def _discover(templates_dir: Path) -> list[str]:
    if not templates_dir.is_dir():
        raise typer.BadParameter(f"not a directory: {templates_dir}", param_hint="--templates-dir")
    return sorted(p.name for p in templates_dir.iterdir() if (p / TEMPLATE_FILE).is_file())


@app.command()
def build(
    data: Annotated[Path, typer.Option(help="CV data file.")] = Path("data/cv.yaml"),
    templates_dir: Annotated[
        Path,
        typer.Option(
            envvar="CVGENERATOR_TEMPLATES", help="Directory holding the templates."
        ),
    ] = Path("templates"),
    output: Annotated[Path, typer.Option("--output", "-o", help="Output directory.")] = Path(
        "output"
    ),
    pdf: Annotated[
        bool, typer.Option("--pdf/--no-pdf", help="Compile the rendered LaTeX to PDF.")
    ] = True,
    suffix: Annotated[
        str, typer.Option(help="Optional output suffix, for example 'en'.")
    ] = "",
    template: Annotated[
        str | None, typer.Option(help="Render only this template, for example 'single'.")
    ] = None,
) -> None:
    """Render the CV data with every template and compile each one to PDF."""
    if not data.is_file():
        raise typer.BadParameter(f"data file not found: {data}", param_hint="--data")

    names = _discover(templates_dir)
    if not names:
        raise typer.BadParameter(
            f"no template with a {TEMPLATE_FILE} found in {templates_dir}",
            param_hint="--templates-dir",
        )
    if template:
        if template not in names:
            raise typer.BadParameter(
                f"template not found: {template}", param_hint="--template"
            )
        names = [template]

    cv = load_cv(data)
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cvgenerator-") as temp_dir:
        build_dir = Path(temp_dir)
        for name in names:
            filename = f"cv-{name}{'-' + suffix if suffix else ''}"
            # PDF builds happen outside output so latexmk's source and auxiliary
            # files disappear with the temporary directory after compilation.
            tex = (build_dir if pdf else output) / f"{filename}.tex"
            tex.write_text(
                render(cv, templates_dir / name, base_dir=data.parent), encoding="utf-8"
            )
            if not pdf:
                typer.echo(f"wrote {tex}")
                continue

            try:
                compiled = compile_pdf(tex)
            except CompileError as exc:
                typer.secho(str(exc), fg=typer.colors.RED, err=True)
                raise typer.Exit(1) from exc
            dest = output / f"{filename}.pdf"
            shutil.copy2(compiled, dest)
            typer.echo(f"wrote {dest}")
