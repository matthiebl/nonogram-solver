import pytest

from nonogram.rules.enumeration_rules import EnumerationRule
from tst.nonogram.utils import RuleTester


class TestEnumerationRule:
    tester = RuleTester(EnumerationRule)

    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((4, 1, 3), "            ", "  ##     #  "),
        ],
    )
    def test_apply(self, clues, state, expected):
        self.tester.assert_apply(clues, state, expected)

    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((5, 1, 8, 1), "                     #   #   .", "                   ###   #   ."),
        ],
    )
    def test_real_examples(self, clues, state, expected):
        self.tester.assert_apply(clues, state, expected)
