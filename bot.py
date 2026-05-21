import requests
import time

BOT_TOKEN = "TU_WKLEJ_TOKEN"
CHAT_ID = "TU_WKLEJ_CHAT_ID"

already_sent = set()


def send_telegram(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })


def get_live_matches():

    url = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return []

    data = r.json()

    return data.get("events", [])


def check_matches():

    matches = get_live_matches()

    for match in matches:

        try:

            match_id = str(match["id"])

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            periods = match.get("periods", {})
            period1 = periods.get("period1")

            if not period1:
                continue

            home_score = period1.get("home")
            away_score = period1.get("away")

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

                print("Alert wysłany")

        except:
            pass


while True:

    check_matches()

    time.sleep(60)
