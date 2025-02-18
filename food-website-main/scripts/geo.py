import requests


def fetch_geo(user_ip):
    ip_api_url = f"http://ip-api.com/json/{user_ip}"
    response = requests.get(ip_api_url)
    ip_data = response.json()

    # Extract relevant geolocation data
    query_status = ip_data.get('status')
    user_country = ip_data.get('country')
    user_region = ip_data.get('regionName')
    user_city = ip_data.get('city')
    user_zip = ip_data.get('zip')
    user_latitude = ip_data.get('lat')
    user_longitude = ip_data.get('lon')
    user_isp = ip_data.get('isp')
    user_timezone = ip_data.get('timezone')
    return query_status, user_country, user_region, user_city, user_zip, user_latitude, user_longitude, user_isp, user_timezone
