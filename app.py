import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('18f4033a6230a17069326fad3988c225')  
API_URL = 'https://api.openweathermap.org/data/2.5/weather'

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    # Use 'request.args' to retrieve the city & units from the query parameters.
    city = request.args.get('city', '')
    units = request.args.get('units', 'metric')

    params = {
        'q': city,
        'units': units,
        'appid': API_KEY
    }

    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    # pp.pprint(result_json)

    # Replace the empty variables below with their appropriate values.
    context = {
        'date': datetime.now(),
        'city': city,
        'description': result_json.get('weather', [{'description': 'N/A'}])[0].get('description', 'N/A'),
        'temp': result_json.get('main', {}).get('temp', 'N/A'),
        'humidity': result_json.get('main', {}).get('humidity', 'N/A'),
        'wind_speed': result_json.get('wind', {}).get('speed', 'N/A'),
        'sunrise': datetime.fromtimestamp(result_json.get('sys', {}).get('sunrise', 0)).strftime('%Y-%m-%d %H:%M:%S'),
        'sunset': datetime.fromtimestamp(result_json.get('sys', {}).get('sunset', 0)).strftime('%Y-%m-%d %H:%M:%S'),
        'units_letter': get_letter_for_units(units)
    }

    # Pass the 'context' variable to the template
    return render_template('results.html', context=context)

@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # Use 'request.args' to retrieve the cities & units from the query parameters.
    city1 = request.args.get('city1', 'San Francisco')  # Default to San Francisco if not provided
    city2 = request.args.get('city2', 'New York')  # Default to New York if not provided
    units = request.args.get('units', 'metric')  # Default to metric if not provided

    # Make 2 API calls, one for each city.
    params_city1 = {
        'q': city1,
        'units': units,
        'appid': API_KEY
    }

    params_city2 = {
        'q': city2,
        'units': units,
        'appid': API_KEY
    }

    result_json_city1 = requests.get(API_URL, params=params_city1).json()
    result_json_city2 = requests.get(API_URL, params=params_city2).json()

    # Extract information for both cities
    city1_info = {
        'name': result_json_city1.get('name', ''),
        'temperature': result_json_city1.get('main', {}).get('temp', 0),
        'humidity': result_json_city1.get('main', {}).get('humidity', 0),
        'wind_speed': result_json_city1.get('wind', {}).get('speed', 0),
        'sunset': datetime.utcfromtimestamp(result_json_city1.get('sys', {}).get('sunset', 0))
    }

    city2_info = {
        'name': result_json_city2.get('name', ''),
        'temperature': result_json_city2.get('main', {}).get('temp', 0),
        'humidity': result_json_city2.get('main', {}).get('humidity', 0),
        'wind_speed': result_json_city2.get('wind', {}).get('speed', 0),
        'sunset': datetime.utcfromtimestamp(result_json_city2.get('sys', {}).get('sunset', 0))
    }

    context = {
        'today_date': datetime.now(),
        'city1': city1_info['name'],
        'city2': city2_info['name'],
        'units': get_letter_for_units(units),
    }

    return render_template('comparison_results.html', **context)

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
