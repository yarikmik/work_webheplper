from django.db import models
from datetime import datetime, date, time, timedelta



class DutyTime:

    def __init__(self):
        self.now = datetime.today().replace(microsecond=0)

    # @staticmethod
    def start_duty(self):
        if self.now.hour >= 20:
            start_duty = self.now.replace(hour=0, minute=0, second=0) + timedelta(hours=20)
        elif self.now.hour < 8:
            start_duty = self.now.replace(hour=0, minute=0, second=0)+ timedelta(day=1, hours=20)
        else:
            start_duty = self.now.replace(hour=0, minute=0, second=0) + timedelta(hours=8)

        return start_duty.timestamp()

    # @staticmethod
    def end_duty(self):
        if self.now.hour >= 20:
            end_duty = self.now.replace(hour=0, minute=0, second=0)  + timedelta(days=1, hours=8)
        elif self.now.hour < 8:
            end_duty = self.now.replace(hour=0, minute=0, second=0)  + timedelta(hours=8)
        else:
            end_duty = self.now.replace(hour=0, minute=0, second=0)  + timedelta(hours=20)

        return end_duty.timestamp()


if __name__ == "__main__":
    time = DutyTime()
    print(DutyTime().start_duty())

