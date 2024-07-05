import requests
import sqlite3
from datetime import datetime
from flask import Flask, render_template
import os

app = Flask(__name__)

API_KEY = '2ea88dbcf3f6cba047b97ebf0a2eb70e'
BASE_URL = 'http://api.openweathermap.org/data/2.5/'
CITY_NAME = 'Mao,es'


def create_db_and_table():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weather_today
                 (date TEXT, city TEXT, temperature REAL, description TEXT)''')
    conn.commit()
    conn.close()

def get_weather_today():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("SELECT date FROM weather_today ORDER BY date DESC LIMIT 1")
    last_entry = c.fetchone()
    conn.close()

    if last_entry:
        # Adjusted to match the format including hours, minutes, and seconds
        last_date = datetime.strptime(last_entry[0], "%Y-%m-%d %H")
        current_date = datetime.now()
        time_difference = current_date - last_date
        if time_difference.total_seconds() < 18000:  # 5 hours
            return None

    complete_url = f"{BASE_URL}weather?q={CITY_NAME}&appid={API_KEY}&units=metric"
    response = requests.get(complete_url)
    weather_data = response.json()
    if weather_data['cod'] == 200:
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        # Adjusted to include hours, minutes, and seconds
        date = datetime.now().strftime("%Y-%m-%d %H")
        city = CITY_NAME
        # Store in DB
        conn = sqlite3.connect('weather.db')
        c = conn.cursor()
        c.execute("INSERT INTO weather_today (date, city, temperature, description) VALUES (?, ?, ?, ?)",
                  (date, city, temperature, description))
        conn.commit()
        conn.close()
        return {"temperature": temperature, "description": description}
    else:
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/today')
def today_weather():
    weather_data = get_weather_today()
    return render_template('today.html', weather_data=weather_data)

@app.route('/week')
def week_weather():
    weather_data = get_weather_week()
    return render_template('week.html', weather_data=weather_data)

# if weather.db doesn't exist
# if not os.path.exists('weather.db'):
create_db_and_table()

# get_weather_today()






if __name__ == '__main__':
    app.run(debug=True)