from datetime import date
from pathlib import Path

import pytest

from cvgenerator.loader import load_cv
from cvgenerator.renderer import render

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).parent / "fixtures" / "cv.yaml"

# Pinned so the footer date does not make the snapshot depend on the calendar.
TODAY = date(2026, 1, 15)


@pytest.mark.parametrize("template", ["modern", "single"])
def test_template_matches_snapshot(template, snapshot):
    cv = load_cv(FIXTURE)
    tex = render(cv, ROOT / "templates" / template, base_dir=FIXTURE.parent, today=TODAY)
    assert tex == snapshot
