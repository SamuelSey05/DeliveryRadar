from typing import TypedDict
import datetime

class LatLon(TypedDict):
    lat: float
    lon: float

class W3W(TypedDict):
    word1:str
    word2:str
    word3:str

locationClass = LatLon
test_data = True

class DBRow(TypedDict):
    id:str
    speed:float
    time:datetime
    location:locationClass