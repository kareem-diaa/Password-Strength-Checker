"""Tests for the scoring module and the privacy behaviour of the web layer.

Run with:  python -m unittest -v      (or: pytest)
"""

import logging
import unittest

from app import app
from checker import MAX_LENGTH, PasswordTooLongError, StrengthResult, evaluate


class ScoringTests(unittest.TestCase):
    def test_weak_password(self):
        for pw in ("password", "123456", "P@ssw0rd!", "qwerty123", "abc"):
            with self.subTest(pw=pw):
                result = evaluate(pw)
                self.assertEqual(result.label, "Very Weak")
                self.assertLess(result.score, 20)
                self.assertTrue(result.suggestions)

    def test_strong_password(self):
        result = evaluate("violet tractor gravel moonlit harbor")
        self.assertEqual(result.label, "Very Strong")
        self.assertGreaterEqual(result.score, 80)
        self.assertEqual(result.suggestions, ())

    def test_long_lowercase_passphrase_is_strong_without_composition(self):
        # NIST: no forced composition, so a long all-lowercase passphrase is fine.
        result = evaluate("correcthorsebatterystaple")
        self.assertIn(result.label, ("Strong", "Very Strong"))
        self.assertFalse(any("uppercase" in s.lower() for s in result.suggestions))

    def test_long_but_repetitive_password(self):
        for pw in ("a" * 40, "abcabcabcabcabcabcabcabcabcabc", "Summer2024Summer2024Summer2024!"):
            with self.subTest(pw=pw):
                result = evaluate(pw)
                self.assertIn(result.label, ("Very Weak", "Weak"))
                self.assertTrue(any("repeat" in s.lower() for s in result.suggestions))
        # Far weaker than an equally long, non-repetitive passphrase.
        self.assertLess(evaluate("a" * 36).score, evaluate("violet tractor gravel moonlit harbor").score)

    def test_sequences_are_penalised(self):
        result = evaluate("abcdefgh12345678")
        self.assertIn(result.label, ("Very Weak", "Weak"))
        self.assertTrue(any("sequence" in s.lower() for s in result.suggestions))

    def test_embedded_common_password_is_penalised(self):
        self.assertLess(evaluate("dragon-k7Lq").score, evaluate("zebrin-k7Lq").score)

    def test_variety_is_a_modest_bonus(self):
        plain, varied = evaluate("mvkqzrtxwp"), evaluate("mVk7z#txWp")
        self.assertGreater(varied.score, plain.score)
        self.assertLessEqual(varied.score - plain.score, 15)

    def test_empty_input(self):
        result = evaluate("")
        self.assertEqual(result, StrengthResult(0, "Very Weak", ("Enter a password to check its strength.",)))

    def test_input_over_max_length_is_rejected_without_echo(self):
        secret = "Zq9!" * 40  # 160 characters
        with self.assertRaises(PasswordTooLongError) as ctx:
            evaluate(secret)
        self.assertNotIn("Zq9", str(ctx.exception))

    def test_exactly_max_length_is_accepted(self):
        self.assertIsInstance(evaluate("x" * MAX_LENGTH), StrengthResult)

    def test_result_never_contains_password(self):
        pw = "violet tractor gravel moonlit harbor"
        self.assertNotIn(pw, repr(evaluate(pw)))


class WebPrivacyTests(unittest.TestCase):
    SECRET = "Unique-Marker-Xy7!"

    def setUp(self):
        self.client = app.test_client()

    def test_result_page_does_not_echo_password(self):
        with self.assertLogs(level=logging.DEBUG) as logs:
            logging.getLogger().debug("start")  # assertLogs needs at least one record
            resp = self.client.post("/", data={"password": self.SECRET})
        body = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(self.SECRET, body)
        self.assertIn("/ 100", body)
        self.assertNotIn(self.SECRET, "\n".join(logs.output))
        self.assertNotIn("Set-Cookie", resp.headers)
        self.assertEqual(resp.headers["Cache-Control"], "no-store")

    def test_too_long_input_gets_generic_message(self):
        resp = self.client.post("/", data={"password": self.SECRET * 10})
        body = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("128 characters or fewer", body)
        self.assertNotIn(self.SECRET, body)

    def test_oversized_body_is_refused(self):
        resp = self.client.post("/", data={"password": "y" * 10_000})
        self.assertEqual(resp.status_code, 413)
        self.assertNotIn("yyyy", resp.get_data(as_text=True))

    def test_empty_submission(self):
        resp = self.client.post("/", data={"password": ""})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Very Weak", resp.get_data(as_text=True))

    def test_get_with_query_password_is_ignored(self):
        resp = self.client.get("/?password=" + self.SECRET)
        self.assertNotIn(self.SECRET, resp.get_data(as_text=True))

    def test_health(self):
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
