import json
from freezegun import freeze_time
from app import Word, get_nth_big_word, get_position_by_datetime, download_solutions


def get_example_json():
    return json.load(open("example_response.json"))


def test_build_word():
    assert Word.build("des", {"d", "e", "g", "a", "v", "l", "s"}) == Word(
        "des", 1, False
    )
    assert Word.build("dese", {"d", "e", "g", "a", "v", "l", "s"}) == Word(
        "dese", 2, False
    )
    assert Word.build("desgel", {"d", "e", "g", "a", "v", "l", "s"}) == Word(
        "desgel", 6, False
    )
    assert Word.build("desgavell", {"d", "e", "g", "a", "v", "l", "s"}) == Word(
        "desgavell", 19, True
    )


def test_get_nth_big_word():
    raw_response = get_example_json()
    assert get_nth_big_word(raw_response["paraules"].keys(), 3) == "deessa"


@freeze_time("2021-12-21T09:01:22")
def test_get_position_by_datetime_0():
    assert get_position_by_datetime() == 0


@freeze_time("2021-12-21T10:32:54")
def test_get_position_by_datetime_4():
    assert get_position_by_datetime() == 4


@freeze_time("2021-12-21T11:59:11")
def test_get_position_by_datetime_8():
    assert get_position_by_datetime() == 8


def test_download_solutions():
    raw_response = download_solutions()
    assert "lletres" in raw_response
    assert "paraules" in raw_response
