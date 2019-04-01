import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()

    year_prcp = {date: prcp for date, prcp in results}
    return jsonify(year_prcp)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == 'USC00519281').all()

    year_temp = list(np.ravel(results))
    return jsonify(year_temp)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def range(start= None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if end == None:
        results = session.query(*sel).filter(Measurement.date >= start).all()
        temp = list(np.ravel(results))
        return jsonify(temp)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temp = list(np.ravel(results))
    return jsonify(temp)


if __name__ == '__main__':
    app.run()
