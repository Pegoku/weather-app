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
    c.execute('''CREATE TABLE IF NOT EXISTS weather_week
                 (date TEXT, city TEXT, temperature REAL, description TEXT)''')
    conn.commit()
    conn.close()

def get_weather_today_api():

    complete_url = f"{BASE_URL}forecast?q={CITY_NAME}&appid={API_KEY}&units=metric&cnt=9"
    response = requests.get(complete_url)
    weather_data = response.json()

    print("Pulling data from API")

    if weather_data['cod'] == "200":
        conn = sqlite3.connect('weather.db')
        c = conn.cursor()

        c.execute("DELETE FROM weather_today")
        conn.commit()

        for forecast in weather_data['list']:
            date = forecast['dt_txt']
            temperature = forecast['main']['temp']
            description = forecast['weather'][0]['description']
            city = CITY_NAME
            c.execute("INSERT INTO weather_today (date, city, temperature, description) VALUES (?, ?, ?, ?)",
                      (date, city, temperature, description))

        conn.commit()
        conn.close()
        print("Data stored in DB")

        first_forecast = weather_data['list'][0]
        return {"temperature": first_forecast['main']['temp'], "description": first_forecast['weather'][0]['description']}
    else:
        return None


def get_weather_today_db():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()

    # Execute the SELECT query to fetch all records from weather_today table
    c.execute("SELECT date, city, temperature, description FROM weather_today")
    
    # Fetch all rows of the query result
    weather_data = c.fetchall()

    conn.close()

    # Convert the fetched data into a structured format
    weather_list = []
    for row in weather_data:
        weather_dict = {
            "date": row[0],
            "city": row[1],
            "temperature": row[2],
            "description": row[3]
        }
        weather_list.append(weather_dict)

    return weather_list
    

def get_weather_today():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("SELECT date FROM weather_today ORDER BY date ASC LIMIT 1") 
    first_entry = c.fetchone()
    conn.close()

    if first_entry:
        first_date = datetime.strptime(first_entry[0], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now()
        time_difference = current_date - first_date
        if time_difference.total_seconds() < 18000:  # 5 hours
            print("Data is up to date")
            return get_weather_today_db()
        else:
            print("Data is not up to date")
            return get_weather_today_api()
    
    return get_weather_today_api()


def get_weather_week_db():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()

    c.execute("SELECT date, city, temperature, description FROM weather_week")
    
    weather_data = c.fetchall()

    conn.close()

    # Convert the fetched data into a structured format
    weather_list = []
    for row in weather_data:
        weather_dict = {
            "date": row[0],
            "city": row[1],
            "temperature": row[2],
            "description": row[3]
        }
        weather_list.append(weather_dict)

    return weather_list

def get_weather_week_api():
    complete_url = f"{BASE_URL}forecast?q={CITY_NAME}&appid={API_KEY}&units=metric"
    response = requests.get(complete_url)
    weather_data = response.json()

    print("Pulling data from API")

    if weather_data['cod'] == "200":
        conn = sqlite3.connect('weather.db')
        c = conn.cursor()

        # Clear existing data
        c.execute("DELETE FROM weather_week")
        conn.commit()

        # Filter forecasts for 09:00 and 18:00 only
        filtered_forecasts = [forecast for forecast in weather_data['list'] if forecast['dt_txt'].endswith("09:00:00") or forecast['dt_txt'].endswith("18:00:00")]

        for forecast in filtered_forecasts:
            date = forecast['dt_txt']
            temperature = forecast['main']['temp']
            description = forecast['weather'][0]['description']
            city = CITY_NAME
            c.execute("INSERT INTO weather_week (date, city, temperature, description) VALUES (?, ?, ?, ?)",
                      (date, city, temperature, description))

        conn.commit()
        conn.close()
        print("Data stored in DB")

        return filtered_forecasts  # Return the filtered list of forecasts
    else:
        return None

def get_weather_week():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("SELECT date FROM weather_week ORDER BY date ASC LIMIT 1") 
    first_entry = c.fetchone()
    conn.close()

    if first_entry:
        first_date = datetime.strptime(first_entry[0], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now()
        time_difference = current_date - first_date
        if time_difference.total_seconds() < 604800:  # 7 days
            print("Data is up to date")
            return get_weather_week_db()
        else:
            print("Data is not up to date")
            return get_weather_week_api()
    
    return get_weather_week_api()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/today')
def today_weather():
    weather_data = get_weather_today()
    if weather_data is None:
        # Handle the case where weather_data is None by using an empty list
        weather_data = []
    print(weather_data)
    return render_template('today.html', weather_data=weather_data)

@app.route('/week')
def week_weather():
    weather_data = get_weather_week()
    if weather_data is None:
        # Handle the case where weather_data is None by using an empty list
        weather_data = []
    print(weather_data)
    return render_template('week.html', weather_data=weather_data)

# if weather.db doesn't exist
# if not os.path.exists('weather.db'):
create_db_and_table()

# get_weather_today()






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)