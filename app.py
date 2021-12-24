import os
import random
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Set, List

from chalice import Chalice, Cron
from dotenv import load_dotenv
import requests
from requests_oauthlib import OAuth1


SOLUTION_URL = "https://paraulogic.rodamots.cat/?solucions="
TWITTER_URL = "https://api.twitter.com/2/tweets"
PUBLIC_TOKEN = "Y29udHJhc2VueWE="
BIG_WORD_MIN_LENGTH = 6
START_HOUR = 9


load_dotenv()
app = Chalice(app_name="spoilogic")


@dataclass
class Word:
    word: str
    score: int
    is_tuti: bool

    @staticmethod
    def build(word: str, today_letters: Set[str]) -> "Word":
        score = len(word) if len(word) > 4 else len(word) - 2
        is_tuti = today_letters.issubset(set(word))
        if is_tuti:
            score += 10
        return Word(word, score, is_tuti)


@app.route("/")
def index():
    word = get_current_word()
    return {"Current word": word.word}


@app.route("/tweet")
def tweet():
    word = get_current_word()
    created_id = make_tweet(word)
    paraulogic_tweets = search_last_paraulogic_tweets()
    reply_to_paraulogic_tweets(paraulogic_tweets, created_id)


@app.schedule(Cron("*/20", "9-23", "*", "*", "?", "*"))
def scheduled_tweet(event):
    tweet()


def get_current_word() -> Word:
    raw_solutions = download_solutions()
    actual_position = get_position_by_datetime()
    raw_word = get_nth_big_word(raw_solutions["paraules"].keys(), actual_position)
    return Word.build(raw_word, set(raw_solutions["lletres"]))


def download_solutions() -> dict:
    return requests.get(
        SOLUTION_URL + "{:%Y-%m-%d}".format(datetime.now()),
        headers={"Authorization": "Basic " + PUBLIC_TOKEN},
    ).json()


def get_position_by_datetime() -> int:
    # Every twenty minutes position increments by one
    now = datetime.now()
    start_datetime = datetime(now.year, now.month, now.day, START_HOUR, 0, 0)
    return (now - start_datetime).seconds // 1200


def get_nth_big_word(words: List[str], position: int) -> str:
    big_words = [word for word in words if len(word) >= BIG_WORD_MIN_LENGTH]
    return big_words[position]


def get_tweeter_auth() -> OAuth1:
    return OAuth1(
        os.getenv("TWITTER_API_KEY"),
        client_secret=os.getenv("TWITTER_API_SECRET"),
        resource_owner_key=os.getenv("TWITTER_OAUTH_ACCESS_TOKEN"),
        resource_owner_secret=os.getenv("TWITTER_OAUTH_ACCESS_TOKEN_SECRET"),
    )


def make_tweet(word: Word) -> int:
    text = word.word.upper()
    if word.is_tuti:
        text += "\n\n 🆃🆄🆃🅸"

    auth = get_tweeter_auth()
    response = requests.post(
        TWITTER_URL,
        auth=auth,
        json={"text": text},
    )
    return response.json()["data"]["id"]


def search_last_paraulogic_tweets() -> List[dict]:
    auth = get_tweeter_auth()
    twenty_minutes_ago = datetime.now() - timedelta(minutes=20)
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/recent",
        auth=auth,
        params={
            "query": "paraulogic",
            "start_time": twenty_minutes_ago.isoformat(timespec="seconds") + "Z",
        },
    )
    return response.json()["data"]


def reply_to_paraulogic_tweets(tweet_list: List[dict], created_id: int) -> None:
    emoji_replies = "😅😇🙃🥰😘😛😝😜🤪😎🤩😏🥺🤯😳😱😨😰😥🤗🤔🤭🤫😶😬🙄😯😵🤐🥴😈👻🤖🙀👋🖖🤟🤘🤙👆✊🙌💪"
    random_emojis = "".join(random.sample(emoji_replies, len(emoji_replies)))
    auth = get_tweeter_auth()
    for i, tweet in enumerate(tweet_list):
        response = requests.post(
            TWITTER_URL,
            auth=auth,
            json={
                "text": random_emojis[i],
                "reply": {"in_reply_to_tweet_id": tweet["id"]},
                "quote_tweet_id": created_id,
            },
        )
        print(response.text)


if __name__ == "__main__":
    # tweet()
    # print(search_last_paraulogic_tweets())
    print(get_current_word().word)
