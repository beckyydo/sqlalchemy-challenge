import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def main(): 
    return("""<h2>All Available Routes:</h2>
    <b>(1) Precipitation </b><br/>
    URL: base_url/api/v1.0/precipitation <br/>

    <br/><b>(2) Stations </b><br/>
    URL: base_url/api/v1.0/stations <br/>
    
    <br/><b>(3) Temperature Observed </b><br/>
    URL: base_url/api/v1.0/tobs <br/>
    
    <br/><b>(4) Summary Statistics of Temp. Observation With Start Date (YYYY-MM-DD) </b><br/> 
    URL: base_url/api/v1.0/&ltstart&gt <br/>
    
    <br/><b>(5) Summary Statistics of Temp. Observation Between Start & End Date (YYYY-MM-DD) </b><br/>
    URL: base_url/api/v1.0/&ltstart&gt/&ltend&gt""")
    
@app.route("/api/v1.0/precipitation")
def precipitation(): 
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    all_prcp = []
    for m_date, m_prcp in results:
        prcp_dict = {}
        prcp_dict[m_date] = m_prcp
        all_prcp.append(prcp_dict)
    return jsonify(percipitation = all_prcp)

@app.route("/api/v1.0/stations")
def stations(): 
    session = Session(engine)
    results = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    all_station = []
    for stat in results:
        all_station.append(stat[0])
    return jsonify( station = all_station)

@app.route("/api/v1.0/tobs")
def temp_obs(): 
    session = Session(engine)
    sel = [Measurement.station, func.count(Measurement.tobs)]
    station_temp = session.query(*sel).group_by(Measurement.station).order_by(sel[1].desc()).first()
    station_temp = station_temp[0]

    # Determine last date for the most active station
    last_station_date = session.query(Measurement.date).filter(Measurement.station == station_temp).order_by(Measurement.date.desc()).first()
    last_station_date = last_station_date[0]

    # Calculate the last 12 months of last date
    last_station_date = dt.datetime.strptime(last_station_date, '%Y-%m-%d') - dt.timedelta(days = 366)
    temp = session.query(Measurement.tobs).filter(Measurement.station == station_temp).filter(Measurement.date > last_station_date).all()
    session.close()
    all_temp =[]
    for tobs in temp:
        all_temp.append(tobs[0])
    return jsonify( Temp_Observed = all_temp)

@app.route("/api/v1.0/<start>")
def summary_start(start): 
    session = Session(engine)
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs) ]
    results = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()
    return jsonify(min = results[0][0], max = results[0][1], average = results[0][2])

@app.route("/api/v1.0/<start>/<end>")
def summary(start,end):
    session = Session(engine)
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs) ]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    return jsonify(min = results[0][0], max = results[0][1], average = results[0][2])

if __name__ == "__main__":
    app.run(debug=True)

