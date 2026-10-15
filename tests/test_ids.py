"""ids.py: drawing a word for a new item, and resolving what is typed (design 0001 *Identity*)."""

import random
from pathlib import Path

import pytest

from ghplan import ids
from ghplan.ids import (
    BRANCH,
    CONSONANTS,
    VOWELS,
    WORD,
    WORDS,
    AmbiguousError,
    DuplicateItemError,
    NoMatchError,
    ResolveError,
    all_words,
    digest,
    draw_word,
    item_ids,
    load_blocklist,
    new_id,
    read_titles,
    resolve,
)

# A synthetic tracker: an ID and its title.
ITEMS = {
    "pl-tunep": "Draw a word for each new item",
    "pl-tunak": "Resolve typed IDs",
    "pl-bakor": "Read the tracker files",
    "pl-dobed": "Docs follow the ADRs",
    "pl-dobim": "Docs for the board",
}
# A Done item lives in `archive/`.
ARCHIVED = {"pl-zefab": "Ship the first release"}


def write_item(directory: Path, id: str, title: str, status: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{id}.md"
    path.write_text(f'---\ntitle: "{title}"\nstatus: {status}\n---\n### Summary\n')
    return path


@pytest.fixture
def tracker(tmp_path: Path) -> Path:
    """A fixture `.tracker/`: ITEMS in `items/`, ARCHIVED in `archive/`."""
    d = tmp_path / ".tracker"
    for id, title in ITEMS.items():
        write_item(d / "items", id, title, "Todo")
    for id, title in ARCHIVED.items():
        write_item(d / "archive", id, title, "Done")
    (d / "items" / "notes.txt").write_text("not an item\n")
    return d


# --- the alphabet ---


def test_the_alphabet_is_16_consonants_and_5_vowels():
    assert len(set(CONSONANTS)) == 16 and len(set(VOWELS)) == 5
    assert not set(CONSONANTS) & set("cqwxy")
    assert WORDS == 102_400 == len(set(all_words()))


def test_every_existing_id_in_this_repo_is_a_word():
    # The alphabet was chosen so that no ID already committed becomes invalid.
    stems = item_ids(Path(__file__).parents[1] / ".tracker")
    assert stems
    assert all(ids.ID.fullmatch(s) for s in stems), stems


# --- the blocklist ---


def test_the_blocklist_holds_sha256_digests_only():
    blocklist = load_blocklist()
    assert blocklist
    assert all(len(d) == 64 and set(d) <= set("0123456789abcdef") for d in blocklist)


def test_every_blocklisted_digest_is_a_drawable_word():
    # A digest no word in the alphabet hashes to blocks nothing: a typo, or a word outside CVCVC.
    words = {digest(w) for w in all_words()}
    assert load_blocklist() <= words


# --- drawing ---


def test_ten_thousand_draws_hold_no_blocklisted_word_and_match_cvcvc():
    rng = random.Random(1)
    blocklist = load_blocklist()
    for _ in range(10_000):
        word = draw_word(rng, (), blocklist)
        assert WORD.fullmatch(word), word
        assert digest(word) not in blocklist, word


def test_a_blocklisted_word_is_drawn_again():
    rng = random.Random(7)
    first = draw_word(random.Random(7), (), frozenset())
    assert draw_word(rng, (), {digest(first)}) != first


def test_a_taken_word_is_drawn_again():
    first = draw_word(random.Random(7), (), frozenset())
    assert draw_word(random.Random(7), {first}, frozenset()) != first


def test_a_nearly_full_repo_still_gets_the_last_free_word():
    last = "zuzuz"
    taken = set(all_words()) - {last}
    assert draw_word(random.Random(3), taken, frozenset()) == last


def test_a_full_repo_fails():
    with pytest.raises(ValueError, match="102,400"):
        draw_word(random.Random(3), set(all_words()), frozenset())


def test_new_id_skips_the_words_already_in_items(tracker: Path, monkeypatch):
    monkeypatch.setattr(ids, "load_blocklist", frozenset)
    first = new_id("pl", tracker, random.Random(5))
    write_item(tracker / "items", first, "Taken", "Todo")
    # The same seed draws the same word first, now taken, so it draws again.
    drawn = new_id("pl", tracker, random.Random(5))
    assert drawn != first and ids.ID.fullmatch(drawn)


def test_new_id_never_draws_an_archived_items_word(tracker: Path, monkeypatch):
    monkeypatch.setattr(ids, "load_blocklist", frozenset)
    first = new_id("pl", tracker, random.Random(5))
    write_item(tracker / "archive", first, "Done long ago", "Done")
    drawn = new_id("pl", tracker, random.Random(5))
    assert drawn != first and ids.ID.fullmatch(drawn)


def test_new_id_in_a_tracker_with_no_items_yet(tmp_path: Path):
    assert ids.ID.fullmatch(new_id("wa", tmp_path / ".tracker"))


# --- reading ---


def test_item_ids_are_the_markdown_stems_of_items_and_archive(tracker: Path):
    assert item_ids(tracker) == sorted(ITEMS | ARCHIVED)


def test_read_titles_finds_an_archived_item(tracker: Path):
    assert read_titles(tracker) == ITEMS | ARCHIVED


def test_resolve_finds_an_archived_item(tracker: Path):
    assert resolve("zefab", read_titles(tracker), "pl") == "pl-zefab"


def test_an_id_in_both_directories_is_an_error_naming_both_paths(tracker: Path):
    write_item(tracker / "archive", "pl-tunep", "Draw a word for each new item", "Done")
    with pytest.raises(DuplicateItemError) as err:
        item_ids(tracker)
    assert str(tracker / "items" / "pl-tunep.md") in str(err.value)
    assert str(tracker / "archive" / "pl-tunep.md") in str(err.value)


# --- resolving ---


@pytest.mark.parametrize(
    ("typed", "expected"),
    [
        ("pl-tunep", "pl-tunep"),  # 1 a full ID
        ("tunep", "pl-tunep"),  # 2 a word without the prefix
        ("tune", "pl-tunep"),  # 3 a unique prefix of a word
        ("pl-tune", "pl-tunep"),  # 3 ... with the repo prefix
        ("b", "pl-bakor"),  # 3 ... down to one letter
        ("resolve", "pl-tunak"),  # 4 a unique word from a title
        ("  TUNEP ", "pl-tunep"),  # case and surrounding space don't matter
    ],
)
def test_each_form_finds_its_item(typed: str, expected: str):
    assert resolve(typed, ITEMS, "pl") == expected


def test_an_ambiguous_prefix_lists_both_candidates_with_titles():
    with pytest.raises(AmbiguousError) as e:
        resolve("tun", ITEMS, "pl")
    assert e.value.candidates == {"pl-tunak": "Resolve typed IDs", "pl-tunep": "Draw a word for each new item"}
    assert "pl-tunak  Resolve typed IDs" in str(e.value)
    assert e.value.exit_code == 1


def test_an_ambiguous_title_word_lists_its_candidates():
    with pytest.raises(AmbiguousError) as e:
        resolve("docs", ITEMS, "pl")
    assert set(e.value.candidates) == {"pl-dobed", "pl-dobim"}


def test_a_later_unique_rule_wins_over_an_earlier_ambiguous_one():
    # "dob" starts two words, but is a whole word in exactly one title.
    items = {**ITEMS, "pl-zifug": "Dob the widgets"}
    assert resolve("dob", items, "pl") == "pl-zifug"


def test_the_prefix_is_needed_outside_its_own_repo():
    assert resolve("bakor", ITEMS, "pl") == "pl-bakor"
    with pytest.raises(NoMatchError):
        resolve("bakor", ITEMS, "wa")


def test_nothing_matching_is_a_resolve_error():
    with pytest.raises(NoMatchError, match="'kipes'") as e:
        resolve("kipes", ITEMS, "pl")
    assert isinstance(e.value, ResolveError) and e.value.exit_code == 1


@pytest.mark.parametrize("typed", [None, "", "  "])
def test_nothing_typed_takes_the_id_from_the_branch(typed):
    assert resolve(typed, ITEMS, "pl", branch="feat/pl-tunak-resolve-typed-ids") == "pl-tunak"
    assert resolve(typed, ITEMS, "pl", branch="fix/pl-bakor") == "pl-bakor"


@pytest.mark.parametrize(
    ("branch", "message"),
    [
        ("main", "branch 'main' names no item"),
        ("feat/pl-kipes-gone", "branch 'feat/pl-kipes-gone' names no item"),
        ("pl-tunep-no-type", "names no item"),
        (None, "not on a branch"),
    ],
)
def test_a_branch_that_names_no_item(branch, message):
    with pytest.raises(NoMatchError, match=message):
        resolve(None, ITEMS, "pl", branch=branch)


def test_typed_text_wins_over_the_branch():
    assert resolve("bakor", ITEMS, "pl", branch="feat/pl-tunep-x") == "pl-bakor"


def test_the_branch_pattern():
    assert BRANCH.fullmatch("feat/pl-jamup-ids-draw-a-word-keep")["id"] == "pl-jamup"
    assert not BRANCH.fullmatch("feat/pl-jamupx")
