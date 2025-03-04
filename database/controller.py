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
    """
    Dump a Datetime object to ISO Format for Database Storage

    Args:
        time (datetime): DateTime object to be dumped

    Returns:
        str: ISO Formatted Date/Time string
    """    
    return time.isoformat()

def dump_location(location:locationClass)->str:
    """
    Dump a locationClass object to JSON

    Args:
        location (locationClass): locationClass Object to be dumped

    Returns:
        str: JSON Object String
    """    
    return dumps(location)

def load_location(jsons:str)->locationClass:
    """
    Load a locationClass Object from it's previously dumped JSON Object string

    Args:
        jsons (str): JSON Object String to be loaded

    Returns:
        locationClass: locationClass Object previously stored reloaded into Python
    """    
    return loads(jsons)
    
def prepare_insert(id:str, speeds:List[float], time:datetime, location:locationClass)->str:
    """
    Prepares an Incident to be input to the Database, formatting the String into the VALUES component of the SQL Query

    Args:
        id (str): sha256 hash of the Incident Submission
        speeds (List[float]): List of the speeds of the Vehicles in the submission
        time (datetime): Date and Time of the Incident
        location (locationClass): Location of the Incident

    Returns:
        str: SQL VALUES String
    """    
    res = ""
    for speed in speeds:
        res += f"('{id}', '{speed}', '{dump_time(time)}', '{dump_location(location)}', '{int(test_data)}'),"
    return res.removesuffix(",")

class DBConnectionFailure(Exception):
    """
    Exception to be thrown if the DataBase connection Fails
    """    
    pass
            
class DBController:
    """
    DataBase Controller Class
    """    
    def __init__(self):
        """
        Instantiator attempts to connect to the DataBase, failing and Killing the program if the connection fails
        """        
        self.connection = None
        try:
            self.connect()
        except DBConnectionFailure:
            print("Error: Failed to Connect to Database", file=sys.stderr)
            traceback.print_exc()
            quit()
        
    def __del__(self):
        """
        Guaranteed to close the connection on program end
        """        
        self.disconnect()
            
    def connect(self) -> None:
        """
        Attempts to connect to the SRCF Database

        Raises:
            DBConnectionFailure: Error if connection fails
            
        Returns: 
            None
        """        
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
    
    def disconnect(self) -> None:
        """
        Disconnect from database

        Raises:
            DBConnectionFailure: Already Disconnected
        """        
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
        """
        Returns a list of all Incidents stored in the database

        Raises:
            DBConnectionFailure: Disconnected from the database

        Returns:
            List[DBRow]: List of Incidents Recorded
        """        
        if not self.connection.is_connected():
            raise DBConnectionFailure
        else:
            cursor = self.connection.cursor()
            cursor.execute("SELECT hash AS id, speed, time, location FROM Incidents;")
            data = []
            row = cursor.fetchone()
            while row is not None:
                print( row )
                tmp = DBRow(id = row[0].decode("ascii"), speed=row[1], time=row[2], location=load_location(row[3])) 
                print(tmp)
                data.append(tmp)
                row = cursor.fetchone()
            cursor.fetchall()
            cursor.close()
            self.connection.commit()
            return data
        
    def addIncident(self, id:str, speed:float, time:datetime, location:locationClass)-> None:
        """
        Add a single incident to the database

        Args:
            id (str): ID of the Video the incident is from
            speed (float): Speed of the vehicle in the incident
            time (datetime): Date and Time of the incident
            location (locationClass): Location of the Incident

        Raises:
            DBConnectionFailure: Database connection failed
        """        
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
            
    def addIncidents(self, id:str, speeds:List[float], time:datetime, location:locationClass)-> None:
        """
        Add all the incidents from a single video to the database

        Args:
            id (str): ID of the submission video
            speeds (List[float]): list of speeds of vehicles in the incident
            time (datetime): Time of the incident
            location (locationClass): Location of the incident

        Raises:
            DBConnectionFailure: Database connection failed
        """        
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
    
def test():
    controller = DBController()
    #controller.addIncident("test", 21.4, datetime.now(), locationClass(lat = 52.205276, lon = 0.119167))
    tmp = controller.getIncidents()
    input()
    
if __name__ == "__main__":
    test()