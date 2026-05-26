import os
import time
import requests
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")

CHECK_INTERVAL = 60
already_sent = set()


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=15)


def get_live_matches():
    url = "https://api.api-tennis.com/tennis/"
    params = {
        "method": "get_livescore",
        "APIkey": API_KEY
    }

    r = requests.get(url, params=params, timeout=20)
    print("API status:", r.status_code)

    if r.status_code != 200:
        print(r.text)
        return []

    data = r.json()
    return data.get("result", [])


def check_matches():
    matches = get_live_matches()
    print("Live matches:", len(matches))

    for match in matches:
        print("RAW MATCH:")
        print(json.dumps(match, ensure_ascii=False))

        try:
            match_id = str(match.get("event_key", ""))

            home = match.get("event_first_player", "Player 1")
            away = match.get("event_second_player", "Player 2")

            scores = match.get("scores", [])

            for s in scores:
                if str(s.get("score_set")) == "1":
                    home_score = int(s.get("score_first"))
                    away_score = int(s.get("score_second"))

                    if (
                        (home_score == 6 and away_score == 0)
                        or
                        (home_score == 0 and away_score == 6)
                    ):
                        if match_id not in already_sent:
                            send_telegram(
                                f"🎾 BAGEL ALERT\n\n"
                                f"{home} vs {away}\n"
                                f"1. set: {home_score}:{away_score}"
                            )
                            already_sent.add(match_id)
                            print("Alert wysłany")

        except Exception as e:
            print("Błąd meczu:", e)


print("Bot uruchomiony — API Tennis")
send_telegram("✅ TEST: bot działa po aktualizacji kodu")

while True:
    try:
        check_matches()
    except Exception as e:
        print("Błąd główny:", e)

    time.sleep(CHECK_INTERVAL)
