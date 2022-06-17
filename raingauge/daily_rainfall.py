import os
import logging
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO)
logging.captureWarnings(True)


class DAILY_RAINFALL:
    def __init__(self):
        self.daily_total = 0.0
        self.scheduler = BackgroundScheduler()
        reset_hour = int(os.getenv('RESET_HOUR', '9'))

        # Setup scheduled reset of daily rain amount, uses the system time
        self.scheduler.add_job(self.reset_total, CronTrigger(
            hour=reset_hour, minute=0))
        self.scheduler.start()

    def reset_total(self):
        logging.info('Resetting daily rain total to zero')
        self.daily_total = 0.0

    def get_total(self, tip_amount=0.0):
        """
        Get the latest daily rainfall total, adding a tip amount if this
        has just occurred.
        :return: Current total rainfall (same units tip amount).
        """
        self.daily_total = self.daily_total + float(tip_amount)
        return round(self.daily_total, 1)
