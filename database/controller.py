import mysql.connector as connector
from os import getenv as env
from typing import List, TypedDict
from datetime import datetime

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
        self.connect()
        
    def __del__(self):
        self.disconnect()
            
    def connect(self) -> connector.MySQLConnection:
        if self.connection == None:
            self.connection = connector.connect(host="mysql.internal.srcf.net", user="deliveryradar", password=env("DELIVERYRADAR_DB_PWD"), database="cstdeliveryradar")
        return self.connection
    
    def disconnect(self) -> None:
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
            cursor.close()
            return data
        
def test():
    controller = DBController()
    controller.getIncidents()
    
if __name__ == "__main__":
    test()