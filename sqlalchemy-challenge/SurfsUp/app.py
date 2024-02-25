# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
app = Flask(__name__)
#################################################


#################################################
# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "<h1>Welcome to the API</h1>"
        "<p>Available Routes for App<br/><br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1/0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1/0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1/0/tobs</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;'>/api/v1/0/&lt;start&gt</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;/&lt;end&gt;'>/api/v1/0/&lt;start&gt;/&lt;end&gt</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the precipitation values
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23', Measurement.date <= '2017-08-23').order_by(Measurement.date).all()

    session.close()

    precipitation = []

    for date, prcp in data:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    data = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Create a Dictonary of the row fata and append to station_list
    stations = []

    for (station,name,latitude,longitude,elevation) in data:
        station_dic={
            "ID" : station,
            "Name": name,
            "Latitude": latitude,
            "Longitude": longitude,
            "Elevation": elevation
        }
        stations.append(station_dic)

    return jsonify(stations)
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most active station 
    most_query = [Measurement.station, func.count(Measurement.station)]
    
    station_active = session.query(*most_query).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    #Isolate the ID of the most active station
    most_active = station_active[0][0]

    # Query the temperatures of the most active station for the previous year data
    data = session.query( Measurement.date, Measurement.tobs).filter(Measurement.station==most_active).filter(Measurement.date>='2016-08-23').all()
    
    session.close()

    tob = []
    for date, tobs in data:
         tobs_dict = {}
         tobs_dict["Date"] = date
         tobs_dict["Tobs"] = tobs
         tob.append(tobs_dict)

    return jsonify(tob)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    session.close()

    start = []

    for min, avg, max in data:
        start_dict = {}
        start_dict['min'] = min
        start_dict['avg'] = avg
        start_dict['max'] = max
        start.append(start_dict)

    return jsonify(start)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the temperatures
    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    start_end = []

    for min, avg, max in data:
        start_end_dict = {}
        start_end_dict['min'] = min
        start_end_dict['avg'] = avg
        start_end_dict['max'] = max
        start_end.append(start_end_dict)

    return jsonify(start_end)

#################################################
# Flask Main
#################################################

if __name__ == '__main__':
    app.run(debug=True)
#################################################
