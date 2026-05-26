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


def get_first_set_score(match):
    scores = match.get("scores", [])

    for s in scores:
        if str(s.get("score_set")) == "1":
            return int(s.get("score_first", -1)), int(s.get("score_second", -1))

    return None, None


def check_matches():
    
    matches = get_live_matches()
    print("Live matches:", len(matches))

    for m in matches:
        print(
           "MATCH:",
           m.get("event_first_player"),
           "vs",
           m.get("event_second_player"),
           "| score:",
           m.get("event_final_result")
       )

    for match in matches:
        try:
            match_id = str(match.get("event_key"))

            home = match.get("event_first_player", "Player 1")
            away = match.get("event_second_player", "Player 2")

            home_score, away_score = get_first_set_score(match)

            if home_score is None or away_score is None:
                continue

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
send_telegram("✅ TEST: bot działa i Telegram odbiera wiadomości")

while True:
    try:
        check_matches()
    except Exception as e:
        print("Błąd główny:", e)

    time.sleep(CHECK_INTERVAL)
