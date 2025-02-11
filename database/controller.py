import mysql.connector as connector
from os import getenv as env
import os.path
from typing import List, TypedDict
from datetime import datetime
import sys
import traceback


class W3W(TypedDict):
    word1:str
    word2:str
    word3:str

class DBRow(TypedDict):
    id:str
    speed:float
    time:datetime
    location:W3W

test_data = True

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
                if os.path.isfile(os.path.abspath("db_pwd")):
                    with open(os.path.abspath("db_pwd"), "r") as f:
                        self.connection = connector.connect(host="mysql.internal.srcf.net", user="cstdeliveryradar", password=f.read(), database="cstdeliveryradar")
                else:
                    self.connection = connector.connect(host="mysql.internal.srcf.net", user="cstdeliveryradar", password=env("DELIVERYRADAR_DB_PWD"), database="cstdeliveryradar")
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
            cursor.execute("SELECT hash AS id, speed, time, location FROM Incidents")
            data = []
            for i in range(cursor.rowcount):
                row = cursor.fetchone()
                print(row)
                tmp = DBRow(id = row[0], speed=row[1], time=[], )
            cursor.fetchall()
            cursor.close()
            self.connection.commit()
            return data
        
def test():
    controller = DBController()
    controller.getIncidents()
    
if __name__ == "__main__":
    test()