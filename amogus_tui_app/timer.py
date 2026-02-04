import threading
import time
from datetime import datetime


class BackgroundTimer:
    def __init__(self, hour, minute, func, *args, **kwargs):
        self.hour = int(hour)
        self.minute = int(minute)
        self.func = func
        self.args = args
        self.kwargs = kwargs
        t = threading.Thread(target=self.wait_time, daemon=True)
        t.start()

    def wait_time(self):
        while True:
            now = datetime.now()
            if now.hour >= self.hour and now.minute >= self.minute:
                self.func(*self.args, **self.kwargs)
                break
            time.sleep(1)
