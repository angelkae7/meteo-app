from flask import Flask, render_template
import requests
import json
from datetime import datetime
from redis import Redis

app = Flask(__name__)
redis = Redis(host='localhost', port=6379)


WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude=-22.125&longitude=166.375&current=temperature_2m&timezone=Pacific/Noumea"

def get_weather_icon(temp):
    if temp is None:
        return "❓"
    elif temp >= 30:
        return "🥵 ☀️"
    elif temp >= 25:
        return "😎 🌤️"
    elif temp >= 20:
        return "😊 ⛅"
    elif temp >= 15:
        return "😐 🌥️"
    elif temp >= 10:
        return "🥶 🌫️"
    else:
        return "❄️ 🧊"

@app.route('/')
def index():
    try:
        cached = redis.get("weather_data")

        if cached:
            data = json.loads(cached)
            source = "Redis (cache)"
        else:
            response = requests.get(WEATHER_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            # On stocke dans Redis avec expiration (10 min)
            redis.setex("weather_data", 600, json.dumps(data))
            source = "API météo (live)"

        temperature = data.get("current", {}).get("temperature_2m")
        timestamp = data.get("current", {}).get("time")
        icon = get_weather_icon(temperature)
        time_local = datetime.fromisoformat(timestamp).strftime("%d/%m/%Y %H:%M")

    except Exception as e:
        temperature = "Erreur"
        icon = "⚠️"
        time_local = "-"
        source = f"Erreur : {e}"

    return render_template("index.html", temperature=temperature, icon=icon, time=time_local, source=source)

if __name__ == '__main__':
    app.run(debug=True)
