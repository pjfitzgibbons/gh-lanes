"""Item IDs: draw a word for a new item, and resolve what is typed to an ID (design 0001 *Identity*).

An ID is `<prefix>-<word>`, such as `wa-tunep`, and is the item file's stem. The word is five letters,
consonant and vowel alternating (CVCVC). This module spawns nothing: the current branch's name comes
in as an argument, from `git.current_branch`.
"""

import hashlib
import itertools
import random
import re
from collections.abc import Collection, Iterable, Mapping
from importlib.resources import files
from pathlib import Path

from ghplan.store import read_markdown

# c and q sound like k, x is two sounds, and w and y act as vowels.
CONSONANTS = "bdfghjklmnprstvz"
VOWELS = "aeiou"
WORDS = len(CONSONANTS) ** 3 * len(VOWELS) ** 2  # 102,400

_C, _V = f"[{CONSONANTS}]", f"[{VOWELS}]"
WORD = re.compile(_C + _V + _C + _V + _C)
ID = re.compile(rf"(?P<prefix>[a-z]+)-(?P<word>{WORD.pattern})")
# A branch named for an item: `<type>/<id>-<slug>`, or `<type>/<id>` with no slug.
BRANCH = re.compile(rf"[a-z]+/(?P<id>{ID.pattern})(?:-.*)?")

BLOCKLIST_FILE = "blocklist.sha256"
_TITLE_WORD = re.compile(r"\w+")


class ResolveError(Exception):
    """What was typed names no item, or more than one. The CLI exits 1 on this."""

    exit_code = 1


class NoMatchError(ResolveError):
    pass


class AmbiguousError(ResolveError):
    def __init__(self, typed: str, candidates: Mapping[str, str]):
        self.candidates = dict(sorted(candidates.items()))
        lines = "\n".join(f"  {id}  {title}" for id, title in self.candidates.items())
        super().__init__(f"{typed!r} matches {len(candidates)} items:\n{lines}")


def digest(word: str) -> str:
    return hashlib.sha256(word.encode()).hexdigest()


def load_blocklist() -> frozenset[str]:
    """The digests of the words a drawn ID never uses. Hashed, so the words aren't in the repo."""
    text = files("ghplan").joinpath(BLOCKLIST_FILE).read_text(encoding="utf-8")
    return frozenset(
        line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")
    )


def all_words() -> Iterable[str]:
    for c1, v1, c2, v2, c3 in itertools.product(CONSONANTS, VOWELS, CONSONANTS, VOWELS, CONSONANTS):
        yield c1 + v1 + c2 + v2 + c3


def draw_word(rng: random.Random, taken: Collection[str], blocklist: Collection[str]) -> str:
    """A random word that isn't taken and whose digest isn't on the blocklist.

    Random draws find one almost at once while the repo is sparse; past that, the words still free
    are listed and one is picked, so a nearly full repo still gets a word and a full one fails.
    """

    def free(word: str) -> bool:
        return word not in taken and digest(word) not in blocklist

    for _ in range(100):
        word = "".join(rng.choice(s) for s in (CONSONANTS, VOWELS, CONSONANTS, VOWELS, CONSONANTS))
        if free(word):
            return word
    left = [w for w in all_words() if free(w)]
    if not left:
        raise ValueError(f"all {WORDS:,} words are taken or blocklisted")
    return rng.choice(left)


def item_ids(items_dir: Path) -> list[str]:
    """The IDs of the item files in `.tracker/items/`: their stems."""
    if not items_dir.is_dir():
        return []
    return sorted(p.stem for p in items_dir.glob("*.md"))


def new_id(prefix: str, items_dir: Path, rng: random.Random | None = None) -> str:
    """An ID for a new item, drawn as design 0001 *Identity* says. There is no counter to merge."""
    taken = {m["word"] for id in item_ids(items_dir) if (m := ID.fullmatch(id))}
    word = draw_word(rng or random.SystemRandom(), taken, load_blocklist())
    return f"{prefix}-{word}"


def read_titles(items_dir: Path) -> dict[str, str]:
    """Each item's ID and title, for resolving and for listing candidates."""
    titles = {}
    for id in item_ids(items_dir):
        front, _ = read_markdown(items_dir / f"{id}.md")
        titles[id] = str(front.get("title", ""))
    return titles


def resolve(typed: str | None, items: Mapping[str, str], prefix: str, branch: str | None = None) -> str:
    """The one item ID that `typed` names, among `items` (ID to title) in the repo with `prefix`.

    The rules are tried in order and the first that matches exactly one item wins: a full ID; a word
    without the prefix; a unique prefix of a word; a unique word from a title. With nothing typed,
    the ID comes from `branch`, `<type>/<id>-<slug>`. When no rule wins, the first rule that matched
    several items is reported with its candidates.
    """
    if not (typed and typed.strip()):
        m = BRANCH.fullmatch(branch or "")
        if m and m["id"] in items:
            return m["id"]
        where = f"branch {branch!r} names no item" if branch else "not on a branch"
        raise NoMatchError(f"no item given, and {where}")

    text = typed.strip().lower()
    own = f"{prefix}-"
    if "-" in text:
        given_prefix, _, start = text.partition("-")
    else:
        given_prefix, start = prefix, text
    rules = (
        [id for id in items if id == text],
        [id for id in items if id == own + text],
        [id for id in items if id.startswith(f"{given_prefix}-{start}")],
        [id for id in items if text in (w.lower() for w in _TITLE_WORD.findall(items[id]))],
    )
    ambiguous = None
    for matches in rules:
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1 and ambiguous is None:
            ambiguous = matches
    if ambiguous:
        raise AmbiguousError(typed, {id: items[id] for id in ambiguous})
    raise NoMatchError(f"no item matches {typed!r}")
