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
  distance = request.args.get('distance', 0, type=float)
  date = request.args.get('date', 0, type=str)
  time = request.args.get('time', 0, type=str)
  unit = request.args.get('unit', 0, type=str)
  brevet = request.args.get('brevet', 0, type=int)

  if unit == 'Miles':     #unit conversion
    distance *= 1.60934

  if format_arrow_date(date) != "(bad date)":                 #Validate date and set date otherwise
    date = format_arrow_date(date).format('ddd MM/DD/YYYY')
  else:
    date = arrow.get('12/31/2012', 'MM/DD/YYYY').format('ddd MM/DD/YYYY')

  if format_arrow_time(time) != "(bad time)":                 #Validate time and set time otherwise
    time = format_arrow_time(time).format("HH:mm")
  else:
    time = arrow.get('00:00', 'HH:mm').format("HH:mm")

  start_o = arrow.get(date + " " + time, "ddd MM/DD/YYYY HH:mm")
  start_c = start_o

  final_calc = [(200, 13.5), (300, 20.0), (400, 27.0), (600, 40.0),   (1000, 75.0)]
  open_calc =  [(200, 34.0), (200, 32.0), (200, 30.0), (400, 28.0),   (300,  26.0)]
  close_calc = [(200, 15.0), (200, 15.0), (200, 15.0), (400, 11.428), (300,  13.333)]

  def close_times(distance, brevet):
    end_time = 0
    if distance == 0:
      return 60
    if int(distance) >= brevet:
      for group, time in final_calc:
        if brevet == group:
          return time*60
    else:
      for group, time in close_calc:
        if group <= distance and distance > 0:
          end_time += (group/time)*60
          distance -= group
        elif distance == 0:
          return end_time
        else:
          return end_time + (distance/time)*60

  def open_times(distance, brevet):
    end_time = 0
    over = False
    if distance > brevet:
      over = True
    for group, time in open_calc:
      if group <= distance and distance > 0:
        end_time += (group/time)*60
        distance -= group
      elif distance == 0 or over == True:
          return end_time
      else:
        return end_time + (distance/time)*60

  o_min = open_times(distance, brevet)
  c_min = close_times(distance, brevet)

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

    
