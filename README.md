# Vaccination appointment availability checker

Scrapes Walgreens immunization availability website, sending alerts if
appointments are available in the configured area.
Alerts can be sent via SMS or Telegram messages, with configuration specified below.

The script will only check once, it's intended to be run periodically, like via a cron job.

Dependencies are specified using [Poetry](https://python-poetry.org/), run `poetry install` to install,
`poetry shell` to activate the environment, and `python src/main.py` to run the script.

## Configuration

Configuration is done via environment variables.

### Required

- `POSITION_LAT`: Latitude coordinate floating point number to search for available appointments
- `POSITION_LON`: Longitude coordinate floating point number to search for available appointments

### Optional

- `ALERT_BODY`: Used to customize the alert body text, defaults to "Appointments available!"

#### SMS alerts

If the following environment variables are all set, SMS alerts will be sent if an appointment is available.

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`: The Twilio number to send SMS messages from, including country code (eg "+15555555555")
- `SMS_ALERT_NUMBERS`: A comma-separated list of numbers to send alerts to (eg "+15555555555,+15555555556")

#### Telegram alerts

If the following are all set, alerts will be sent via telegram to the configured channel.
The bot must exist and already be added to the configured channel.

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`
