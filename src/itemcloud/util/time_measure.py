import datetime

class TimeMeasure:
    def __init__(self):
        self.start()

    def start(self) -> datetime.datetime:
        self._start = datetime.datetime.now()
        self._stop = None
        return self._start
    
    def stop(self) -> datetime.datetime:
        self._stop = datetime.datetime.now()
        return self._stop

    def latency(self) -> datetime.timedelta:
        stop = self._stop if self._stop is not None else datetime.datetime.now()
        return stop - self._start
    
    def latency_ms(self) -> float:
        return self.latency().total_seconds() * 1000.0

    def latency_str(self) -> str:
        return format_ms_duration(self.latency_ms())

def format_ms_duration(duration_ms: float) -> str:
    seconds, milliseconds = divmod(duration_ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '{0:03}H_{1:02}M_{2:02}S_{3:03}MS'.format(
        int(hours), 
        int(minutes), 
        int(seconds),
        int(milliseconds)
    )
