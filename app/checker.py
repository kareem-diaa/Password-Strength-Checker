"""Password strength scoring — plain Python, no I/O, no third-party libraries.

`evaluate(password)` is a pure function: it takes the password string and
returns a `StrengthResult` (score, label, suggestions). It never stores,
logs, or returns the password or any part of it.

Scoring rules (aligned with NIST SP 800-63B):

1. Length dominates. Points come from the *effective length*: the number of
   characters that actually add guessing work (see rule 3).
     - 4 points per effective character up to 16 characters  (max 64)
     - 1.5 points per effective character from 17 to 30       (max 21)
2. Character variety is a small bonus, never a requirement. Each extra
   character class (lowercase, uppercase, digit, other/symbol/space/unicode)
   beyond the first adds 5 points, capped at 15, scaled down for short
   passwords. Nothing is deducted for lacking a class.
3. Patterns reduce the effective length — characters that are predictable
   count as zero:
     - runs of the same character ("aaa"): only the first counts
     - sequences of 3+ ("abc", "321", "qwerty"): only the first counts
     - a chunk of 3+ characters already typed earlier ("abcabc",
       "Summer2024Summer2024"): the repeat counts as zero
     - a well-known password embedded in a longer one ("dragon2024xyz",
       "p@ssw0rd..."): the whole word counts as one character
4. Hard caps:
     - an exact match with the built-in common-password list (also after
       undoing simple substitutions like @->a, 0->o and stripping up to four
       leading/trailing digits or symbols) caps the score at 5
     - fewer than 8 characters caps the score at 19 (Very Weak)

Labels: 0-19 Very Weak, 20-39 Weak, 40-59 Fair, 60-79 Strong, 80-100 Very Strong.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MAX_LENGTH = 128
MIN_LENGTH = 8
TARGET_LENGTH = 15

TOO_LONG_MESSAGE = f"Passwords must be {MAX_LENGTH} characters or fewer."

# A short built-in list of very common passwords, drawn from widely published
# "most common password" rankings. Stored lowercase.
COMMON_PASSWORDS = frozenset(
    {
        "123456", "123456789", "12345678", "12345", "1234567", "1234567890",
        "123123", "111111", "000000", "654321", "666666", "121212", "112233",
        "123321", "159753", "987654321", "1q2w3e4r", "1qaz2wsx", "qwerty",
        "qwerty123", "qwertyuiop", "asdfgh", "asdfghjkl", "zxcvbnm", "azerty",
        "password", "password1", "password123", "passw0rd", "pass", "admin",
        "admin123", "administrator", "root", "toor", "guest", "login",
        "welcome", "welcome1", "letmein", "iloveyou", "abc123", "abcdef",
        "monkey", "dragon", "master", "shadow", "sunshine", "princess",
        "football", "baseball", "soccer", "hockey", "basketball", "superman",
        "batman", "trustno1", "michael", "jordan", "jennifer", "hunter",
        "hunter2", "ranger", "buster", "thomas", "robert", "daniel", "charlie",
        "andrew", "jessica", "ashley", "michelle", "nicole", "harley",
        "starwars", "pokemon", "computer", "internet", "whatever", "freedom",
        "secret", "access", "flower", "cheese", "summer", "winter", "spring",
        "autumn", "love", "lovely", "loveme", "killer", "pepper", "ginger",
        "chocolate", "cookie", "banana", "orange", "purple", "silver",
        "golden", "matrix", "mustang", "ferrari", "corvette", "qazwsx",
        "zaq12wsx", "changeme", "default", "test", "test123", "user",
        "google", "facebook", "samsung", "apple", "microsoft",
    }
)

# Common words of 5+ characters are also searched for *inside* longer
# passwords; shorter ones would match too much innocent text.
_EMBEDDED_WORDS = tuple(sorted(w for w in COMMON_PASSWORDS if len(w) >= 5 and w.isalpha()))

_SEQUENCES = (
    "abcdefghijklmnopqrstuvwxyz",
    "01234567890",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
)
_SEQUENCES = _SEQUENCES + tuple(s[::-1] for s in _SEQUENCES)

# Two leetspeak maps because "1" stands in for both "i" and "l".
_LEET_I = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
                         "7": "t", "@": "a", "$": "s", "!": "i"})
_LEET_L = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s",
                         "7": "t", "@": "a", "$": "s", "!": "i"})

_PADDING = re.compile(r"[\d\W_]{0,4}(.*?)[\d\W_]{0,4}", re.DOTALL)

LABELS = ((80, "Very Strong"), (60, "Strong"), (40, "Fair"), (20, "Weak"), (0, "Very Weak"))


class PasswordTooLongError(ValueError):
    """Raised for input over MAX_LENGTH. The message never contains the input."""

    def __init__(self) -> None:
        super().__init__(TOO_LONG_MESSAGE)


@dataclass(frozen=True)
class StrengthResult:
    score: int                    # 0-100
    label: str                    # Very Weak / Weak / Fair / Strong / Very Strong
    suggestions: tuple[str, ...]  # short, actionable, never contain the password


def evaluate(password: str) -> StrengthResult:
    """Score a password. Pure function: no side effects, no stored state."""
    if len(password) > MAX_LENGTH:
        raise PasswordTooLongError()
    if not password:
        return StrengthResult(0, "Very Weak", ("Enter a password to check its strength.",))

    lower = password.lower()
    weights = [1.0] * len(password)

    repeated = _zero_spans(weights, _same_char_runs(lower) + _repeated_chunks(lower))
    sequential = _zero_spans(weights, _sequence_runs(lower))
    is_common = _is_common(lower)
    embedded = not is_common and _zero_spans(weights, _embedded_common(lower))

    effective = sum(weights)
    length_points = 4 * min(effective, 16) + 1.5 * max(0.0, min(effective, 30) - 16)

    classes = {_char_class(c) for c, w in zip(password, weights) if w > 0}
    variety_points = min(15, 5 * (len(classes) - 1)) * min(1.0, effective / 12)

    score = length_points + variety_points
    if len(password) < MIN_LENGTH:
        score = min(score, 19)
    if is_common:
        score = min(score, 5)
    score = int(round(max(0, min(100, score))))
    label = next(name for threshold, name in LABELS if score >= threshold)

    suggestions: list[str] = []
    if len(password) < MIN_LENGTH:
        suggestions.append(
            f"Use at least {MIN_LENGTH} characters; {TARGET_LENGTH} or more is much better."
        )
    elif label != "Very Strong" and not (len(password) >= TARGET_LENGTH and (repeated or sequential)):
        suggestions.append(
            f"Make it longer: aim for {TARGET_LENGTH}+ characters. A passphrase of several "
            "unrelated words is long, strong, and easy to remember."
        )
    if is_common:
        suggestions.append(
            "This is one of the most common passwords and would be guessed almost "
            "instantly. Choose something unique to you."
        )
    elif embedded:
        suggestions.append(
            "Avoid building on a well-known password (like 'password' or 'dragon'); "
            "attackers try those first, even with small changes."
        )
    if repeated:
        suggestions.append(
            "Avoid repeated characters or chunks (like 'aaa' or 'abcabc'); repeats add "
            "almost no strength, so longer isn't stronger if it's repetitive."
        )
    if sequential:
        suggestions.append(
            "Avoid sequences such as 'abc', '123', or keyboard runs like 'qwerty'."
        )
    if score < 60 and len(classes) == 1 and not is_common and effective >= MIN_LENGTH:
        suggestions.append(
            "Optional: an unexpected space, digit, or symbol adds a little extra "
            "strength, but extra length helps more."
        )

    return StrengthResult(score, label, tuple(suggestions))


def _char_class(c: str) -> str:
    if c.isdigit():
        return "digit"
    if c.isupper():
        return "upper"
    if c.islower():
        return "lower"
    return "other"  # symbols, spaces, and caseless unicode characters


def _zero_spans(weights: list[float], spans: list[tuple[int, int]]) -> bool:
    """Set weight 0 for each span except its first character. Returns True if any span."""
    for start, end in spans:
        for i in range(start + 1, end):
            weights[i] = 0.0
    return bool(spans)


def _same_char_runs(s: str) -> list[tuple[int, int]]:
    """Runs of 3+ identical characters, e.g. 'aaa' or '!!!!'."""
    return [(m.start(), m.end()) for m in re.finditer(r"(.)\1{2,}", s, re.DOTALL)]


def _repeated_chunks(s: str) -> list[tuple[int, int]]:
    """Chunks of 3+ characters that repeat text appearing earlier (overlap allowed).

    The span starts one character *before* the repeat so that `_zero_spans`
    zeroes the entire repeated chunk.
    """
    spans, i, n = [], 1, len(s)
    while i < n:
        best = 0
        for j in range(i):
            k = 0
            while i + k < n and s[j + k] == s[i + k]:
                k += 1
            best = max(best, k)
        if best >= 3:
            spans.append((i - 1, i + best))
            i += best
        else:
            i += 1
    return spans


def _sequence_runs(s: str) -> list[tuple[int, int]]:
    """Runs of 3+ consecutive characters along the alphabet, digits, or a keyboard row."""
    spans = []
    for seq in _SEQUENCES:
        following = {seq[k]: seq[k + 1] for k in range(len(seq) - 1)}
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and following.get(s[j]) == s[j + 1]:
                j += 1
            if j - i + 1 >= 3:
                spans.append((i, j + 1))
                i = j + 1
            else:
                i += 1
    return spans


def _variants(s: str) -> set[str]:
    return {s, s.translate(_LEET_I), s.translate(_LEET_L)}


def _is_common(lower: str) -> bool:
    """Exact match with the list, allowing leetspeak and up to 4 padding chars each side."""
    core = _PADDING.fullmatch(lower).group(1)
    candidates = _variants(lower) | (_variants(core) if core else set())
    return not candidates.isdisjoint(COMMON_PASSWORDS)


def _embedded_common(lower: str) -> list[tuple[int, int]]:
    """Positions of well-known passwords (5+ letters) inside a longer password."""
    spans = []
    for variant in _variants(lower):  # each translation is 1:1, so indices line up
        for word in _EMBEDDED_WORDS:
            start = variant.find(word)
            while start != -1:
                spans.append((start, start + len(word)))
                start = variant.find(word, start + 1)
    return spans
