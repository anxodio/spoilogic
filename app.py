from datetime import datetime
from dataclasses import dataclass
from typing import Set, List

from chalice import Chalice
import requests

URL = "https://paraulogic.rodamots.cat/?solucions="
PUBLIC_TOKEN = "Y29udHJhc2VueWE="
BIG_WORD_MIN_LENGTH = 5
START_HOUR = 9

app = Chalice(app_name="spoilerlogic")


@dataclass
class Word:
    word: str
    score: int
    tutti: bool

    @staticmethod
    def build(word: str, today_letters: Set[str]) -> "Word":
        score = len(word) if len(word) > 4 else len(word) - 2
        tutti = today_letters.issubset(set(word))
        if tutti:
            score += 10
        return Word(word, score, tutti)


@app.route("/")
def index():
    word = get_current_word()
    return {"hello": word.word}


def get_current_word() -> Word:
    raw_solutions = download_solutions()
    actual_position = get_position_by_datetime()
    raw_word = get_nth_big_word(raw_solutions["paraules"].keys(), actual_position)
    return Word.build(raw_word, set(raw_solutions["lletres"]))


def download_solutions() -> dict:
    return requests.get(
        URL + "{:%Y-%m-%d}".format(datetime.now()),
        headers={"Authorization": "Basic " + PUBLIC_TOKEN},
    ).json()


def get_position_by_datetime() -> int:
    # Every half and hour position increments by one
    now = datetime.now()
    start_datetime = datetime(now.year, now.month, now.day, START_HOUR, 0, 0)
    return (now - start_datetime).seconds // 1800


def get_nth_big_word(words: List[str], position: int) -> str:
    big_words = [word for word in words if len(word) >= BIG_WORD_MIN_LENGTH]
    return big_words[position]


if __name__ == "__main__":
    print(get_current_word().word)