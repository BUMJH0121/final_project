import requests
import json
from .IP import IP

# Icon dictionary for relative images
icon_lookup = {
	'01d':'assets/01d@2x.png',
	'01n':'assets/01n@2x.png',
	'02d':'assets/02d@2x.png',
	'02n':'assets/02n@2x.png',
	'03d':'assets/03d@2x.png',
	'03n':'assets/03n@2x.png',
	'04d':'assets/04d@2x.png',
	'04n':'assets/04n@2x.png',
	'09d':'assets/09d@2x.png',
	'09n':'assets/09n@2x.png',
	'10d':'assets/10d@2x.png',
	'10n':'assets/10n@2x.png',
	'11d':'assets/11d@2x.png',
	'11n':'assets/11n@2x.png',
	'13d':'assets/13d@2x.png',
	'13n':'assets/13n@2x.png',
	'50d':'assets/50d@2x.png',
	'50n':'assets/50n@2x.png'
}

def get_weather():
	'''
	Get formatted json of weather data for current day
	'''
	ip = IP()  # Get current location information

	# Get json from openweather api
	APIKEY = '1d76ad95a3c6c918fb7335c192134683'
	# CITY = ip.region
	CITY = 'seoul'

	URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}'.format(CITY, APIKEY)
	r = requests.get(URL)
	json = r.json()

	temperatureHigh = round(json['main']['temp_max']- 273.15, 1)
	temperatureLow = round(json['main']['temp_min']- 273.15, 1)

	# Fetch important information for display
	title = json['weather'][0]['main']
	icon = icon_lookup[json['weather'][0]['icon']]
	temperature = round(json['main']['temp']- 273.15, 1)
	desc = json['weather'][0]['description']

	return {'title':title, 'icon':icon, 'temperature':temperature, 'desc':desc, 'temperatureHigh':temperatureHigh, 'temperatureLow':temperatureLow}
	
def get_weather_script():
	'''
	Return formatted news update for the day
	'''
	data = get_weather()
	script = """It is currently {0} at {1} degrees fahrenheit today with a high of {2} degrees fahrenheit and a low of {3} 
	degrees fahrenheit. Today it will be {4}.""".format(data['title'], data['temperature'], data['temperatureHigh'], data['temperatureLow'], data['desc'])
	return ' '.join(script.lower().split())  # Format and remove whitespace from string


if __name__ == "__main__":
	print(get_weather_script())
