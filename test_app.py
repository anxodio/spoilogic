import json
from freezegun import freeze_time
from app import (
    Word,
    get_nth_big_word,
    get_position_by_datetime,
    download_solutions,
    get_diec_definition_html,
    build_words_from_raw_response,
    get_number_of_tutis,
    WORDS_KEY,
    LETERS_KEY,
)


def get_example_json():
    return json.load(open("example_response.json"))


def test_build_word():
    assert Word.build("des", "des", {"d", "e", "g", "a", "v", "l", "s"}) == Word(
        "des", "des", 1, False
    )
    assert Word.build("dese", "dese", {"d", "e", "g", "a", "v", "l", "s"}) == Word(
        "dese", "dese", 2, False
    )
    assert Word.build("desgel", "desgel", {"d", "e", "g", "a", "v", "l", "s"}) == Word(
        "desgel", "desgel", 6, False
    )
    assert Word.build(
        "desgavell", "desgavell", {"d", "e", "g", "a", "v", "l", "s"}
    ) == Word("desgavell", "desgavell", 19, True)


def test_get_nth_big_word():
    raw_response = get_example_json()
    assert get_nth_big_word(raw_response[WORDS_KEY].keys(), 3) == "deessa"


@freeze_time("2021-12-21T08:01:22")
def test_get_position_by_datetime_0():
    assert get_position_by_datetime() == 0


@freeze_time("2021-12-21T09:32:54")
def test_get_position_by_datetime_4():
    assert get_position_by_datetime() == 4


@freeze_time("2021-12-21T10:59:11")
def test_get_position_by_datetime_8():
    assert get_position_by_datetime() == 8


def test_download_solutions():
    raw_response = download_solutions()
    assert LETERS_KEY in raw_response
    assert WORDS_KEY in raw_response


def test_get_diec_definition_html():
    response = get_diec_definition_html(Word.build("angel", "àngel", set()))
    assert "div" in response


def test_build_words_from_raw_response():
    raw_response = get_example_json()
    words = build_words_from_raw_response(raw_response)
    assert len(words) == 73
    assert isinstance(words[0], Word)


def test_get_number_of_tutis():
    raw_response = get_example_json()
    words = build_words_from_raw_response(raw_response)
    total_tutis = get_number_of_tutis(words)
    assert total_tutis == 1
