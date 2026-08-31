import unittest

from wordle import Mark, format_hints, score_guess, validate_guess


class ScoreGuessTests(unittest.TestCase):
    def marks(self, secret: str, guess: str) -> list[Mark]:
        return [hint.mark for hint in score_guess(secret, guess)]

    def test_win_marks_every_letter_green(self):
        self.assertEqual(self.marks("crane", "crane"), [Mark.CORRECT] * 5)

    def test_green_yellow_and_gray(self):
        self.assertEqual(
            self.marks("crane", "cared"),
            [Mark.CORRECT, Mark.PRESENT, Mark.PRESENT, Mark.PRESENT, Mark.ABSENT],
        )

    def test_repeated_guess_letter_is_not_overcounted(self):
        self.assertEqual(
            self.marks("apple", "alley"),
            [Mark.CORRECT, Mark.PRESENT, Mark.ABSENT, Mark.PRESENT, Mark.ABSENT],
        )

    def test_different_lengths_raise_error(self):
        with self.assertRaises(ValueError):
            score_guess("crane", "four")


class DisplayAndValidationTests(unittest.TestCase):
    def test_plain_display_names_colors(self):
        result = format_hints(score_guess("crane", "cared"), plain=True)
        self.assertEqual(
            result,
            "[GREEN C] [YELLOW A] [YELLOW R] [YELLOW E] [GRAY D]",
        )

    def test_validation_normalizes_case_and_spaces(self):
        self.assertEqual(validate_guess("  CrAnE  "), ("crane", None))

    def test_validation_rejects_wrong_length_and_non_ascii_letters(self):
        self.assertIsNotNone(validate_guess("cat")[1])
        self.assertIsNotNone(validate_guess("cafés")[1])


if __name__ == "__main__":
    unittest.main()
