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
API_URL = 'http://api.openweathermap.org/data/2.5/weather'

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
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        'appid': API_KEY,
        'q': city,
        'units': units
    }
    result_json = requests.get(API_URL, params=params).json()

    # Extract relevant information from the API response
    if 'main' in result_json and 'weather' in result_json:
        temperature = result_json['main'].get('temp')
        humidity = result_json['main'].get('humidity')
        description = result_json['weather'][0]['description']
        # ... (similar checks for other keys)

        # Convert sunrise and sunset to datetime objects
        sunrise_timestamp = result_json['sys']['sunrise']
        sunset_timestamp = result_json['sys']['sunset']
        sunrise = datetime.fromtimestamp(sunrise_timestamp)
        sunset = datetime.fromtimestamp(sunset_timestamp)
    else:
        # Handle the case where 'main' or 'weather' key is missing in the response
        temperature = humidity = sunrise = sunset = description = None  # Or set default values

    context = {
        'date': datetime.now(),
        'city': city,
        'description': description,
        'temp': temperature,
        'humidity': humidity,
        'wind_speed': result_json.get('wind', {}).get('speed'),  # Check for 'wind' key
        'sunrise': sunrise,
        'sunset': sunset,
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', context=context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1', '')
    city2 = request.args.get('city2', '')
    units = request.args.get('units', 'metric')

    # Make API call for City 1
    params_city1 = {
        'appid': API_KEY,
        'q': city1,
        'units': units
    }
    result_json_city1 = requests.get(API_URL, params=params_city1).json()

    # Make API call for City 2
    params_city2 = {
        'appid': API_KEY,
        'q': city2,
        'units': units
    }
    result_json_city2 = requests.get(API_URL, params=params_city2).json()

    # Initialize the context dictionary
    context = {
        'city1': {
            'name': city1,
            'description': result_json_city1['weather'][0]['description'],
            'temp': result_json_city1['main']['temp'],
            'humidity': result_json_city1['main']['humidity'],
            'wind_speed': result_json_city1.get('wind', {}).get('speed', ''),
            'sunset': datetime.fromtimestamp(result_json_city1['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S'),
        },
        'city2': {
            'name': city2,
            'description': result_json_city2['weather'][0]['description'],
            'temp': result_json_city2['main']['temp'],
            'humidity': result_json_city2['main']['humidity'],
            'wind_speed': result_json_city2.get('wind', {}).get('speed', ''),
            'sunset': datetime.fromtimestamp(result_json_city2['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S'),
        },
        'units_letter': get_letter_for_units(units)
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
