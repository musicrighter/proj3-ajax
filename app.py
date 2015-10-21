"""
Very simple Flask web site, with one page
displaying a course schedule.

"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify # For AJAX transactions

import json
import logging

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Our own module
# import acp_limits


###
# Globals
###
app = flask.Flask(__name__)
import CONFIG

import uuid
app.secret_key = str(uuid.uuid4())
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)


###
# Pages
###

@app.route("/")
@app.route("/index")
@app.route("/calc")
def index():
  app.logger.debug("Main page entry")
  return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("calc")
    return flask.render_template('page_not_found.html'), 404


###############
#
# AJAX request handlers 
#   These return JSON, rather than rendering pages. 
#
###############
@app.route("/_calc_times")
def calc_times():
  """
  Calculates open/close times from miles, using rules 
  described at http://www.rusa.org/octime_alg.html.
  Expects one URL-encoded argument, the number of miles. 
  """
  app.logger.debug("Got a JSON request");
  miles = request.args.get('miles', 0, type=float)
  date = request.args.get('date', 0, type=str)
  time = request.args.get('time', 0, type=str)

  if format_arrow_date(date) != "(bad date)":
    date = format_arrow_date(date).format('ddd MM/DD/YYYY')
  else:
    date = arrow.get('12/31/2012', 'MM/DD/YYYY').format('ddd MM/DD/YYYY')

  if format_arrow_time(time) != "(bad time)":
    time = format_arrow_time(time).format("HH:mm")
  else:
    time = arrow.get('00:00', 'HH:mm').format("HH:mm")

  start_o = arrow.get(date + " " + time, "ddd MM/DD/YYYY HH:mm")
  start_c = start_o

  if miles < 200:
    o_min = (miles/34)*60
    c_min = (miles/15)*60

  elif miles == 200:
    o_min = (miles/34)*60
    c_min = 13*60 + 30

  elif miles < 400:
    o_min = (200/34 + ((miles-200)/32))*60
    c_min = (miles/15)*60

  elif miles == 400:
    o_min = (200/34 + ((miles-200)/32))*60
    c_min = 27*60

  elif miles < 600:
    o_min = (200/34 + 200/32 + ((miles-400)/30))*60
    c_min = (miles/15)*60

  elif miles == 600:
    o_min = (200/34 + 200/32 + ((miles-400)/30))*60
    c_min = 40*60

  elif miles < 1000:
    o_min = (200/34 + 200/32 + 200/30 + ((miles-600)/28))*60
    c_min = (600/15 + ((miles-600)/11.428))*60

  elif miles == 1000:
    o_min = (200/34 + 200/32 + 200/30 + ((miles-600)/28))*60
    c_min = 75*60

  elif miles < 1300:
    o_min = (200/34 + 200/32 + 200/30 + 200/28 + ((miles-1000)/26))*60
    c_min = (600/15 + 200/11.428 + ((miles-1000)/13.333))*60

  # elif miles == 1300:
  #   o_min = (200/34 + 200/32 + 200/30 + 200/28 + ((miles-1000)/26))*60
  #   c_min = 75*60

  else:
    o_fin = c_fin = "Error: check distance!"
    return jsonify(open_times=o_fin, close_times=c_fin)

  o_fin = str(start_o.replace(minutes=+o_min, seconds=+30).format("ddd MM/DD/YYYY HH:mm"))
  c_fin = str(start_c.replace(minutes=+c_min, seconds=+30).format("ddd MM/DD/YYYY HH:mm"))
  return jsonify(open_times=o_fin, close_times=c_fin)
 
#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try: 
        return arrow.get(date, "MM/DD/YYYY")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try: 
        return arrow.get(time, "HH:mm")
    except:
        return "(bad time)"



#############


if __name__ == "__main__":
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT)

    
