import requests
import pandas as pd
from time import sleep
from datetime import *
import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv('.env')


def get_lat_long():
    """Gets long/lat for the location entered and inserts it into label"""
    get_location = input("what location would you like the lat and long for?")

    parameters = {
        'address': get_location,
        'key': os.getenv("KEY")
    }
    r = requests.get(os.getenv("geocoding_api_url"), params=parameters)
    r.raise_for_status()
    data = r.json()
    results = data['results'][0]['geometry']['location']
    return [results['lat'], results['lng']]

def get_data():
    OMW_API_KEY = os.getenv('OMW_API_KEY')
    endpoint = 'http://api.openweathermap.org/data/2.5/onecall'
    location = get_lat_long()
    lat = location[0]
    long = location[-1]

    parameters = {
            'lat': lat,
            'lon': long,
            'exclude': 'current,daily,minutely,alerts',
            'appid': OMW_API_KEY
        }
        r = requests.get(url=endpoint, params=parameters).json()['hourly'][:12]
        return r


def need_umbrella():
    for i in get_data():
        weather_id = i['weather'][0]['id']
        if weather_id < 700:
            return True


def send_text(to, message):
    """Sends text message via twilio"""
    twilio_sid = os.getenv('TWILIO_SID')
    twilio_token = os.getenv('TWILIO_TOKEN')
    client = Client(twilio_sid, twilio_token)
    message_info = client.messages.create(body=message, from_=os.getenv('TWILIO_PHONE'), to=f'+1{to}')
    return message_info.sid


def time_till_7am():
    """Calculates time til 7am so we can send out notification"""
    utx_timestamp = int(datetime.now().timestamp())
    t1 = (datetime.now() + timedelta(days=1)).replace(hour=7, minute=0, microsecond=0, second=0)
    seconds_till_7 = (t1 - datetime.now()).seconds
    return seconds_till_7


def start_program():
    while True:
        sleep(time_till_7am())
        if need_umbrella():
            text_message = 'Looks like its going to rain today'
            send_text(to=os.getenv('PHONE_NUMBER'), message=text_message)

        else:
            text_message = 'its going to be clear skys, Enjoy'
            send_text(to=os.getenv('PHONE_NUMBER'), message=text_message)




start_program()