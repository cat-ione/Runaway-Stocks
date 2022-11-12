import time

class ComplexTimer:
    instances = []
    
    @staticmethod
    def pause_all():
        for instance in __class__.instances:
            instance.pause_start = time.time()

    def __init__(self, max_time: int) -> None:
        __class__.instances.append(self)
        self.max_time = max_time
        self.start_time = time.time()
        self.current_time = self.max_time - (time.time() - self.start_time)
        self.ended = False
        self.pause_start = None

    def update(self) -> None:
        if self.pause_start is not None:
            self.start_time += time.time() - self.pause_start
            self.pause_start = None
        self.current_time = self.max_time - (time.time() - self.start_time)
        if self.current_time <= 0:
            self.ended = True