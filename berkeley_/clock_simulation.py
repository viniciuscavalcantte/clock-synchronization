import time
import threading
import random

class SimulatedClock:
    def __init__(self, initial_offset_seconds=0):
        self._current_time = int(time.time()) + initial_offset_seconds
        self._lock = threading.Lock()
        self._running = True
        self._tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        self._tick_thread.start()

    def _tick_loop(self):
        while self._running:
            time.sleep(1) 
            with self._lock:
                self._current_time += 1

    def get_time(self):
        with self._lock:
            return self._current_time

    def adjust_time(self, adjustment_seconds):
        with self._lock:
            self._current_time += adjustment_seconds
            print(f"Clock adjusted by {adjustment_seconds}s. New time: {self._current_time}")

    def stop(self):
        self._running = False
        if self._tick_thread.is_alive():
            self._tick_thread.join(timeout=1.1) 

    def get_formatted_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.get_time()))