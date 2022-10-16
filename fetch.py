# Load Env Vars
from dotenv import load_dotenv
import os

import gtfs_realtime_pb2
import gtfs_realtime_realcity_pb2

load_dotenv()
BKK_API_KEY = os.getenv('BKK_API_KEY')

import requests as http
BKK_API_URL = f"https://go.bkk.hu/api/query/v1/ws/gtfs-rt/full/VehiclePositions.pb?key={BKK_API_KEY}"

def fetch() -> gtfs_realtime_pb2.FeedMessage:
    res = http.get(BKK_API_URL)
    if res.status_code == 200:
        m = gtfs_realtime_pb2.FeedMessage()
        m.ParseFromString(res.content)
        

        return m
