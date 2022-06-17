import os

import logging
import datetime as dt

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO)
logging.captureWarnings(True)


class MAXMINTEMP:
    """Maintains a record of input temperatures and uses these to track the
     current maximum daytime and minimum nighttime temperature"""
    def __init__(self):
        self.day_max = None
        self.night_min = None
        self.day_temps = []
        self.night_temps = []
        self.maxmin_data = dict(day_max=None, night_min=None)
        # Set the hour when 'daytime' starts and ends
        self.day_start = int(os.getenv('DAY_START', '09'))
        self.day_end = int(os.getenv('DAY_END', '21'))

        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(timezone='Europe/London')

        # Setup scheduled reset of max/min temperature (uses the system time).
        self.scheduler.add_job(
            self.reset_max_temps, CronTrigger(hour=self.day_start, minute=00))
        self.scheduler.add_job(
            self.reset_min_temps, CronTrigger(hour=self.day_end, minute=00))
        self.scheduler.start()

    def add_temp(self, temp):
        """
        Add a temperature reading to the list of either daytime or nighttime
        temperatures if the
        time is between 0900 UTC and 0859 UTC, update the current maximum
        daytime or minimum nighttime temperature.
        param temp: The temperature reading to be added.
        :return: A dictionary containing the latest max daytime and min
        nighttime temperatures if available.
        """
        if isNowInTimePeriod(dt.time(
                self.day_start, 00), dt.time(
                self.day_end, 00), dt.datetime.now().time()):
            self.day_temps.append(temp)
        else:
            self.night_temps.append(temp)

        if len(self.day_temps) > 0:
            self.day_max = max(self.day_temps)
        else:
            self.day_max = None

        if len(self.night_temps) > 0:
            self.night_min = min(self.night_temps)
        else:
            self.night_min = None

        self.maxmin_data.update(dict(
            day_max=self.day_max, night_min=self.night_min, day_readings=len(
                self.day_temps), night_readings=len(self.night_temps)))

        # day_data_points = len(self.day_temps)
        # night_data_points = len(self.night_temps)
        return self.maxmin_data

    def reset_max_temps(self):
        """Reset the list of daytime temperatures"""
        self.day_temps.clear()

    def reset_min_temps(self):
        """Reset the list of nighttime temperatures"""
        self.night_temps.clear()


def isNowInTimePeriod(start_time, end_time, now_time):
    """Determine if the specified 'now time' lies between the specified
    start time and end time. The function works with Python datetime
    objects."""
    if start_time < end_time:
        return start_time <= now_time <= end_time
    else:
        # Over midnight:
        return now_time >= start_time or now_time <= end_time
