# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt 

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
Measurement = base.classes.measurement
Station = base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Available Honolulu, Hawaii Climate APIs."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


# Returns the date fone year from the most recent date
def date_prev_year():
    session = Session(engine)
    recent_date = session.query(func.max(Measurement.date)).first()[0]
    date_one = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    session.close()
    return(date_one)

# Precipitation URL 

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_prev_year()).all()
    session.close()

    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp 
        prcp_list.append(prcp_dict)
    return jsonify(prcp_list)

# Stations URL 

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    stations_data = session.query(Station.station).all()
    session.close()
    
    stations_list = list(np.ravel(stations_data))
    return jsonify(stations_list)

# Tobs URL

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= date_prev_year()).all()
    session.close()

    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

# Start URL

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    start_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    start_values = []
    for min, avg, max in start_results:
        start_dict = {}
        start_dict["min"] = min
        start_dict["average"] = avg
        start_dict["max"] = max
        start_values.append(start_dict)
    return jsonify(start_values)



# Start/End URL

@app.route("/api/v1.0/<start>/<end>")
def stat_temp(start=None, end=None):
    session = Session(engine)
    start_end_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    start_end_values = []
    for min, avg, max in start_end_results:
        start_end_dict = {}
        start_end_dict["min"] = min 
        start_end_dict["average"] = avg
        start_end_dict["max"] = max 
        start_end_values.append(start_end_dict)
    return jsonify(start_end_values) 


if __name__ == '__main__':
    app.run(debug=True) 
