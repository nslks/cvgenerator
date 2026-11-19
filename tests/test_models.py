import pytest
from pydantic import ValidationError

from cvgenerator.models import SkillMatrix, Theme


def test_skill_level_above_the_scale_is_rejected():
    with pytest.raises(ValidationError, match="exceeds max_level"):
        SkillMatrix(max_level=5, rows=[{"skill": "Python", "years": "6", "level": 6}])


def test_skill_level_at_the_scale_maximum_is_allowed():
    matrix = SkillMatrix(max_level=5, rows=[{"skill": "Python", "years": "6", "level": 5}])
    assert matrix.rows[0].level == 5


@pytest.mark.parametrize("value", ["2A5CAA", "#2A5CA", "#GGGGGG", "blue"])
def test_malformed_theme_colour_is_rejected(value):
    with pytest.raises(ValidationError):
        Theme(accent=value)


def test_theme_colour_accepts_lowercase_hex():
    assert Theme(accent="#2a5caa").accent == "#2a5caa"
