from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

def get_after_month_date():
    # Define the San Francisco timezone
    sf_timezone = pytz.timezone("America/Los_Angeles")

    # Get the current date and time in San Francisco timezone
    current_date = datetime.now(sf_timezone)

    # Calculate the date one month from now
    one_month_later = current_date + relativedelta(months=1)

    # Format the dates
    formatted_current_date = current_date.strftime("%A %B %d")
    formatted_one_month_later = one_month_later.strftime("%A %B %d")

    return formatted_current_date, formatted_one_month_later