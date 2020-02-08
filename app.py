from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, send_from_directory
from functools import wraps
import pandas as pd
import numpy as np
import datetime
import json
import os

application = Flask(__name__)

#random key that flask will use to generate and authenticate cookies
application.secret_key = 'e37ecc1a6bf54eae4c13f54621315d77aa5fe704c084e0f27f7ce1057ed4cdd0'


#index landing point
@application.route('/')
def index():
    return render_template('base.html')


#API for weekly forecast
@application.route('/api/getWeeklyForecast', methods=['GET'])
def api_weekly():
    response = {'hello'}
    return (json.dumps(response))

if __name__ == '__main__':
    application.run(debug=False)