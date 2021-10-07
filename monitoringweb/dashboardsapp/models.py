from django.db import models
from datetime import datetime, date, time, timedelta


class DutyTime:
    now = datetime.today().replace(microsecond=0)

    @staticmethod
    def start_duty():
        now = datetime.today().replace(microsecond=0)
        if now.hour < 8 or now.hour > 20:
            start_duty = now - timedelta(days=1, hours=now.hour,
                                         minutes=now.minute, seconds=now.second) + timedelta(hours=20)
        else:
            start_duty = now - timedelta(hours=now.hour,
                                         minutes=now.minute, seconds=now.second) + timedelta(hours=8)

            return start_duty.timestamp()

    @staticmethod
    def end_duty():
        now = datetime.today().replace(microsecond=0)
        if now.hour < 8 or now.hour > 20:
            end_duty = now - timedelta(hours=now.hour,
                                       minutes=now.minute, seconds=now.second) + timedelta(hours=8)
        else:
            end_duty = now - timedelta(hours=now.hour,
                                       minutes=now.minute, seconds=now.second) + timedelta(hours=20)

            return end_duty.timestamp()
