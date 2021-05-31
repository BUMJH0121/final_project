import json, requests, socket
from urllib.request import urlopen

class IP:

	def __init__(self):
		IP = requests.get("https://www.wikipedia.org").headers["X-Client-IP"]
		# IP = urlopen('http://ip.42.pl/raw').read()
		# IP = requests.get('http://ip.42.pl/raw').text  # Get the IP

		# Get the location information of IP
		url = 'https://ipapi.co/{}/json/'.format(IP)
		response = urlopen(url)
		data = json.load(response)
		# print(data)

		# Extract individual information from IP
		self.IP = data['ip']
		self.org = data['org']
		self.city = data['city']
		self.country = data['country']
		self.latitude = data['latitude']
		self.longitude = data['longitude']
		self.region = data['region']

# {'ip': '219.250.191.252', 
# 'version': 'IPv4', 
# 'city': 'Nowon-gu', 
# 'region': 'Seoul', 
# 'region_code': '11', 
# 'country': 'KR', 
# 'country_name': 'South Korea', 
# 'country_code': 'KR', 
# 'country_code_iso3': 'KOR', 
# 'country_capital': 'Seoul', 
# 'country_tld': '.kr', 
# 'continent_code': 'AS', 
# 'in_eu': False, 
# 'postal': '01686', 
# 'latitude': 37.6576, 
# 'longitude': 127.072, 
# 'timezone': 'Asia/Seoul', 
# 'utc_offset': '+0900', 
# 'country_calling_code': '+82', 
# 'currency': 'KRW', 
# 'currency_name': 'Won', 
# 'languages': 'ko-KR,en', 
# 'country_area': 98480.0, 
# 'country_population': 51635256.0, 
# 'asn': 'AS9318', 
# 'org': 'SK Broadband Co Ltd'}


if __name__ == "__main__":
	ip = IP()
	print(ip.IP)