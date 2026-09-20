from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

#to start reveiving, go to dir w/ main.py and run this command "py -m uvicorn main:app --host 0.0.0.0 --port 8000"
#if adding new reading, delete old .db or renmame, it throws error since it tries fitting new data in old format

#create way of communication between apps
app = FastAPI()


#writes to this
DATABASE = "smoke_detector.db"

#gets sensor readings, float = decimal, int = integer, str= string, bool = boolean
class SensorReading(BaseModel):
    smoke: float
    temperature: float
    humidity: float
    battery: float
    alarm: bool
    confidence: float

#for creating .db file if it does not exist as DATABASE name
def init_database():

    #opens .db file, if it DNE, will create one of DATABASE name assigned to it, /w conn being connection to it
    conn = sqlite3.connect(DATABASE)

    #makes table in SQL, the CREATE TABLE... makes it if one does not exist
    #id is number of data packet, increasing after each one
    #timestamp autorecords when server/device received info
    #rest are for sensors
    #REAL is for decimal, INTEGER for int or bool, bool DNE in SQL, TEXT for string, BLOB for binary data i.e images, files
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (    
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            smoke REAL,
            temperature REAL,
            humidity REAL,
            battery REAL,
            alarm INTEGER,
            confidence REAL
        )
    """)
    # saves /w commit and closes w/ close
    conn.commit()
    conn.close()

#when something sends a request, run the func, this is for inserting new readings after a .db was made
@app.post("/api/readings")
def receive_reading(reading: SensorReading):

    #opens again
    conn = sqlite3.connect(DATABASE)

    #inserts readings w/ received data
    conn.execute("""
        INSERT INTO readings
        (smoke, temperature, humidity, battery, alarm, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        reading.smoke,
        reading.temperature,
        reading.humidity,
        reading.battery,
        reading.alarm,
        reading.confidence
    ))

    #saves and closes
    conn.commit()
    conn.close()

    #sends back a response that tells requestee that data was received and processed
    return {"status": "received"}

#runs func of inserting new data
init_database()
