from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3

#to start reveiving, go to dir w/ main.py and run this command "py -m uvicorn main:app --host 0.0.0.0 --port 8000"
#if adding new reading, delete old .db or renmame, it throws error since it tries fitting new data in old format

#create way of communication between apps
app = FastAPI()

@app.get("/")
def home():
    return RedirectResponse(url="/frontend/index.html")

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

#writes to this
DATABASE = "smoke_detector.db"

#gets sensor readings, float = decimal, int = integer, str= string, bool = boolean
class SensorReading(BaseModel):
    smoke: float
    temperature: float
    humidity: float
    co: float
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
    #this one makes for all readings

    #output last received timestamp, smoke, temp, humidity, CO ppm, battery %, confidence %, and alarm state
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (    
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            smoke REAL,
            temperature REAL,
            humidity REAL,
            co REAL,
            battery REAL,
            alarm INTEGER,
            confidence REAL
        )
    """)
    #this one makes for just latest reading
    conn.execute("""
        CREATE TABLE IF NOT EXISTS latest (    
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            smoke REAL,
            temperature REAL,
            humidity REAL,
            co REAL,
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
        (smoke, temperature, humidity, co, battery, alarm, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        reading.smoke,
        reading.temperature,
        reading.humidity,
        reading.co,
        reading.battery,
        reading.alarm,
        reading.confidence
    ))
    
    #removes old latest reading
    conn.execute("""
        DELETE FROM latest
    """)

    #puts in new reading into latest
    conn.execute("""
        INSERT INTO latest
        (id, smoke, temperature, humidity, co, battery, alarm, confidence)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reading.smoke,
        reading.temperature,
        reading.humidity,
        reading.co,
        reading.battery,
        reading.alarm,
        reading.confidence
    ))

    #saves and closes
    conn.commit()
    conn.close()

    #sends back a response that tells requestee that data was received and processed
    return {"status": "received"}

#for sending data to other devices/apps
@app.get("/api/readings")
def get_readings():

    #connects/opend .db file
    conn = sqlite3.connect(DATABASE)

    #gives access to rows/datapackets by name rather thatn list of values
    conn.row_factory = sqlite3.Row

    #fetching reading of each row by order of descending timestamp
    rows = conn.execute("""
        SELECT *
        FROM readings
        ORDER BY timestamp DESC
    """).fetchall()

    #closes .db
    conn.close()

    #returns data for each row cleanly
    return [dict(row) for row in rows]

#is only the latest reading
@app.get("/api/latest")
def get_latest():

    #connect and split into readable sections
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    #fetching only one/latest reading
    row = conn.execute("""
        SELECT *
        FROM latest
        WHERE id = 1
    """).fetchone()

    conn.close()

    if row is None:
        return {"message": "No readings available"}

    return dict(row)

#runs func of inserting new data
init_database()
