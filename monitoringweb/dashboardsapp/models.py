from django.db import models
from datetime import datetime, date, time, timedelta



class DutyTime:
    now = datetime.today().replace(microsecond=0)

    @staticmethod
    def start_duty():
        now = DutyTime.now
        if now.hour >= 20:
            start_duty = now.replace(hour=0, minute=0, second=0) + timedelta(hours=20)
        elif now.hour < 8:
            start_duty = now.replace(hour=0, minute=0, second=0)+ timedelta(day=1, hours=20)
        else:
            start_duty = now.replace(hour=0, minute=0, second=0) + timedelta(hours=8)

        return start_duty.timestamp()

    @staticmethod
    def end_duty():
        now = DutyTime.now
        if now.hour >= 20:
            end_duty = now.replace(hour=0, minute=0, second=0)  + timedelta(days=1, hours=8)
        elif now.hour < 8:
            end_duty = now.replace(hour=0, minute=0, second=0)  + timedelta(hours=8)
        else:
            end_duty = now.replace(hour=0, minute=0, second=0)  + timedelta(hours=20)

        return end_duty.timestamp()



