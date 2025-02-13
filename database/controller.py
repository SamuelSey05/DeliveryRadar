import mysql.connector as connector
from common.db_types import *
from os import getenv as env
import os.path
from typing import List
from datetime import datetime
import sys
import traceback
from json import dumps, loads
 
def dump_time(time:datetime)->str:
    return time.isoformat()

def load_time(timestr:str)->datetime:
    return datetime.fromisoformat(timestr)

def dump_location(location:locationClass)->str:
    return dumps(location)

def load_location(jsons:str)->locationClass:
    return loads(jsons)
    
def prepare_insert(id:str, speeds:List[float], time:datetime, location:locationClass)->str:
    res = ""
    for speed in speeds:
        res += f"('{id}', '{speed}', '{dump_time(time)}', '{dump_location(location)}', '{int(test_data)}'),"
    return res.removesuffix(",")

class DBConnectionFailure(Exception):
    pass
            
class DBController:
    
    def __init__(self):
        self.connection = None
        try:
            self.connect()
        except DBConnectionFailure:
            print("Error: Failed to Connect to Database", file=sys.stderr)
            traceback.print_exc()
            quit()
        
    def __del__(self):
        self.disconnect()
            
    def connect(self) -> connector.MySQLConnection:
        if self.connection == None:
            try:
                con = lambda pwd: connector.connect(host="mysql.internal.srcf.net", user="cstdeliveryradar", password=pwd, database="cstdeliveryradar")
                if os.path.isfile(os.path.abspath("db_pwd")):
                    with open(os.path.abspath("db_pwd"), "r") as f:
                        self.connection = con(f.read())
                else:
                    self.connection = con(env("DELIVERYRADAR_DB_PWD"))
            except:
                
                raise DBConnectionFailure
        return self.connection
    
    def disconnect(self) -> None:
        if self.connection != None:
            if not self.connection.is_connected():
                raise DBConnectionFailure
            else:
                self.connection.disconnect()
        
    # def _sqlCommand(self, command:str) -> List[connector.RowType]:
    #     if not self.connection.is_connected():
    #         raise DBConnectionFailure
    #     else:
    #         cursor = self.connection.cursor()
    #         cursor.execute(command)
    #         tmp = cursor.fetchall()
    #         cursor.close()
    #         self.connection.commit()
        
    def getIncidents(self) -> List[DBRow]: 
        if not self.connection.is_connected():
            raise DBConnectionFailure
        else:
            cursor = self.connection.cursor()
            cursor.execute("SELECT hash AS id, speed, time, location FROM Incidents;")
            data = []
            row = cursor.fetchone()
            while row is not None:
                print( row )
                tmp = DBRow(id = row[0], speed=row[1], time=row[2], location=load_location(row[3]))
                print(tmp)
                data.append(tmp)
                row = cursor.fetchone()
            cursor.fetchall()
            cursor.close()
            self.connection.commit()
            return data
        
    def addIncident(self, id:str, speed:float, time:datetime, location:locationClass)->bool:
        if self.connection == None or not self.connection.is_connected():
            raise DBConnectionFailure
        else:
            cursor = self.connection.cursor()
            command = f"INSERT INTO Incidents (hash, speed, time, location, isTest) VALUES {prepare_insert(id, [speed], time, location)};"
            print (command)
            cursor.execute(command)
            print(cursor.fetchwarnings(), file=sys.stderr)
            cursor.fetchall()
            self.connection.commit()
            return True
            
    def addIncidents(self, id:str, speeds:List[float], time:datetime, location:locationClass):
        if self.connection == None or not self.connection.is_connected():
            raise DBConnectionFailure
        else:
            cursor = self.connection.cursor()
            command = f"INSERT INTO Incidents (hash, speed, time, location, isTest) VALUES {prepare_insert(id, speeds, time, location)};"
            print (command)
            cursor.execute(command)
            print(cursor.fetchwarnings(), file=sys.stderr)
            cursor.fetchall()
            self.connection.commit()
            return True
    
def test():
    controller = DBController()
    #controller.addIncident("test", 21.4, datetime.now(), locationClass(lat = 52.205276, lon = 0.119167))
    tmp = controller.getIncidents()
    input()
    
if __name__ == "__main__":
    test()