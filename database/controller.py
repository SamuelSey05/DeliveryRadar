import mysql.connector as connector
from os import getenv as env
test_data = True

class DBConnectionFailure(Exception):
    pass
            
class DBController:
    
    def __init__(self):
        self.connection = self.connect()
        
    def __del__(self):
        self.disconnect()
            
    def connect(self) -> connector.MySQLConnection:
        if self.connection == None:
            self.connection = connector.connect(host="cstdeliveryradar.soc.srcf.net", user="deliveryradar", password=env("DELIVERYRADAR_DB_PWD"))
        return self.connection
    
    def disconnect(self) -> None:
        if not self.connection.is_connected():
            raise DBConnectionFailure
        else:
            self.connection.disconnect()
        
        