from lakeshore import Model336
import time
import os
import datetime
from influxdb import InfluxDBClient


class dataManager:
    def __init__(self, client):
        self.client = client
        
    def send_payload(self, data_point):
        self.client.write_points(data_point)
        return data_point
        
    def pull_data(self, timeframe):
        query = f'SELECT * FROM "336 Temperature Control" WHERE time >= now() - {timeframe}'
        result = self.client.query(query)
        points = result.get_points()
        return points
    
    def delete_data(self, timeframe):
        query = f'DELETE FROM "336 Temperature Control" WHERE time >= now() - {timeframe}'
        self.client.query(query)
        print(f"Deleted info for the last {timeframe}")
