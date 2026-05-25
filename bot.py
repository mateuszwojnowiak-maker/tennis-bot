import os
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")

CHECK_INTERVAL = 60
already_sent = set()


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    }, timeout=15)


def get_live_matches():
    url = "https://v1.tennis.api-sports.io/games"

    headers = {
        "x-apisports-key": API_KEY
    }

    params = {
        "live": "all"
    }

    r = requests.get(url, headers=headers, params=params, timeout=20)

    print("API status:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return []

    data = r.json()
    return data.get("response", [])


def check_matches():
    matches = get_live_matches()
    print("Live matches:", len(matches))

    for match in matches:
        try:
            match_id = str(match.get("id"))

            players = match.get("players", {})
            home = players.get("home", {}).get("name", "Player 1")
            away = players.get("away", {}).get("name", "Player 2")

            scores = match.get("scores", {})

            home_sets = scores.get("home", {})
            away_sets = scores.get("away", {})

            home_first_set = home_sets.get("set_1")
            away_first_set = away_sets.get("set_1")

            if home_first_set is None or away_first_set is None:
                continue

            home_score = int(home_first_set)
            away_score = int(away_first_set)

            is_bagel = (
                (home_score == 6 and away_score == 0)
                or
                (home_score == 0 and away_score == 6)
            )

            if is_bagel and match_id not in already_sent:
                message = (
                    f"🎾 BAGEL ALERT\n\n"
                    f"{home} vs {away}\n"
                    f"1. set: {home_score}:{away_score}"
                )

                send_telegram(message)
                already_sent.add(match_id)

                print("Alert wysłany:", message)

        except Exception as e:
            print("Błąd meczu:", e)


print("Bot uruchomiony — API Tennis")

while True:
    try:
        check_matches()
    except Exception as e:
        print("Błąd główny:", e)

    time.sleep(CHECK_INTERVAL)
