# common.py
import random
import time
from datetime import datetime, timedelta

PORT_BASE = 5000
NUM_CLIENTS = 4

def get_clock_offset():
    return random.randint(-10, 10)  # desvio inicial em segundos

def current_time_with_offset(offset):
    return datetime.now() + timedelta(seconds=offset)

def str_to_datetime(timestr):
    return datetime.strptime(timestr, "%H:%M:%S")

def datetime_to_str(dt):
    return dt.strftime("%H:%M:%S")
