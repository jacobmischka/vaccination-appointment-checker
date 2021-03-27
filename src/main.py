from datetime import date, datetime, timedelta
import os
from typing import Tuple, Optional

from bs4 import BeautifulSoup
import requests
from requests.cookies import RequestsCookieJar
from telebot import TeleBot
from telebot.types import Message as TelegramMessage
from twilio.base.deserialize import ISO8601_DATE_FORMAT, ISO8601_DATETIME_FORMAT
from twilio.rest import Client
from twilio.rest.api.v2010.account.message import MessageInstance

AVAILABILITY_ENDPOINT = (
    "https://www.walgreens.com/hcschedulersvc/svc/v1/immunizationLocations/availability"
)
SCREENING_URL = (
    "https://www.walgreens.com/findcare/vaccination/covid-19/location-screening/"
)


def main():
    if check_appointments_available():
        body = os.environ.get("ALERT_BODY", "Appointments available!")
        print(datetime.now().strftime(ISO8601_DATETIME_FORMAT), body)

        try:
            bot = TeleBot(os.environ["TELEGRAM_BOT_TOKEN"])
            send_telegram_message(bot, os.environ["TELEGRAM_CHANNEL_ID"], body)
        except KeyError:
            pass

        try:
            client = Client(
                os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"]
            )
            alert_sms_numbers = os.environ["SMS_ALERT_NUMBERS"].split(",")
            for to in alert_sms_numbers:
                send_sms(client, to, body)
        except KeyError:
            pass


def get_xsrf() -> Tuple[RequestsCookieJar, str, str]:
    response = requests.get(SCREENING_URL)
    soup = BeautifulSoup(response.text, features="html.parser")
    header_name = soup.find("meta", attrs={"name": "_csrf_header"})["content"]
    token = soup.find("meta", attrs={"name": "_csrf"})["content"]

    return response.cookies, header_name, token


def check_appointments_available() -> bool:
    start_date_time = date.today() + timedelta(days=1)

    cookies, header_name, token = get_xsrf()
    response_body = requests.post(
        AVAILABILITY_ENDPOINT,
        json={
            "appointmentAvailability": {
                "startDateTime": start_date_time.strftime(ISO8601_DATE_FORMAT)
            },
            "position": {
                "latitude": float(os.environ["POSITION_LAT"]),
                "longitude": float(os.environ["POSITION_LON"]),
            },
            "radius": 25,
            "serviceId": "99",
        },
        cookies=cookies,
        headers={header_name: token},
    ).json()

    return response_body["appointmentsAvailable"]


def send_sms(client: Client, to: str, body: str) -> MessageInstance:
    return client.messages.create(
        body=body, from_=os.environ["TWILIO_PHONE_NUMBER"], to=to
    )


def send_telegram_message(
    bot: TeleBot, to: str, body: str
) -> Optional[TelegramMessage]:
    return bot.send_message(to, body)


if __name__ == "__main__":
    main()
