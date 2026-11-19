from cvgenerator.models import YearMonth
from cvgenerator.renderer import latex_escape, year_month


def test_escapes_every_special_character():
    assert latex_escape("&%$#_{}~^") == (
        r"\&\%\$\#\_\{\}\textasciitilde{}\textasciicircum{}"
    )


def test_backslash_replacement_is_not_re_escaped():
    assert latex_escape("a\\b") == r"a\textbackslash{}b"


def test_plain_text_is_untouched():
    assert latex_escape("Softwareentwicklerin – Backend") == "Softwareentwicklerin – Backend"


def test_non_string_values_are_stringified():
    assert latex_escape(2020) == "2020"


def test_year_month_pads_single_digit_month():
    assert year_month(YearMonth(year=2022, month=4)) == "04/2022"
