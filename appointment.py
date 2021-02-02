import os
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

OCHD_MAIN_URL='https://www.ochd.org/'
OCHD_COVID_URL=f'{OCHD_MAIN_URL}covid19-vaccine-update/'
TWILIO_TEXT_TO=os.getenv('TWILIO_TEXT_TO')
TWILIO_TEXT_FROM=os.getenv('TWILIO_TEXT_FROM')
twilio_client = Client()

def scrape_ochd_home():
    home_response = requests.get(OCHD_MAIN_URL)
    home_soup = BeautifulSoup(home_response.text, 'html.parser')
    announcements = home_soup.find_all('rs-layer')

    home_count = 0
    for announcement in announcements:
        if 'VACCINATION APPOINTMENTS ARE FULL' not in announcement:
            home_count = home_count + 1
    return home_count

def scrape_ochd_covid_page():
    covid_response = requests.get(OCHD_COVID_URL)
    covid_soup = BeautifulSoup(covid_response.text, 'html.parser')
    covid_texts = covid_soup.select('.column.mcb-column.two-third.column_column')

    text_count = 0
    for covid_text in covid_texts:
        if 'BOOKED FULL AT THIS TIME' not in covid_text:
            text_count = text_count + 1
    return text_count


def lambda_handler(event, context):
    ochd_home = scrape_ochd_home()
    ochd_covid_page = scrape_ochd_covid_page()
    if ochd_home == 0 or ochd_covid_page == 0:
        message = twilio_client.messages.create(to=TWILIO_TEXT_TO, from_=TWILIO_TEXT_FROM,
            body=f'POTENTIAL AVAILABILITY! home:{ochd_home}, covid:{ochd_covid_page} {OCHD_MAIN_URL}')
    else:
        print('Nothing to see here')

