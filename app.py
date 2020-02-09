from flask import (
    Flask,
    render_template,
    flash,
    redirect,
    url_for,
    session,
    request,
    logging,
    send_from_directory,
)
from functools import wraps
import pandas as pd
import numpy as np
import datetime
import json
import os

from planner import get_allocation_proposals

application = Flask(__name__)

# random key that flask will use to generate and authenticate cookies
application.secret_key = (
    "5b3e0ea670dd36807b72acb9045ddb547f8fd331aac48d1e2099a364b66c8025"
)


# index landing point
@application.route("/")
def index():
    return render_template("base.html")


# API for planning requests
@application.route("/api/plan", methods=["GET"])
def planning_api():
    response = {}
    alerts = []
    try:
        start_date = to_date(
            request.args.get("start", default=datetime.date.today().isoformat())
        )
        end_date = to_date(
            request.args.get("end", default=datetime.date.today().isoformat())
        )
        budget = request.args.get("budget", default=15)
        country = request.args.get("country", default="CH")
        response["start_date"] = start_date.isoformat()
        response["end_date"] = end_date.isoformat()
        response["ph_country"] = country
        response["budget"] = budget
        response["public_holidays"] = [1, 2, 3]
        response["options"] = get_allocation_proposals(budget, start_date, end_date, country)

    except ValueError as ex:
        alerts.append(str(ex))

    # add alerts to response
    response["alerts"] = json.dumps(alerts)
    return json.dumps(response)


def to_date(date_string):
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(
            "{} is not valid date in the format YYYY-MM-DD".format(date_string)
        )


if __name__ == "__main__":
    application.run(debug=False)
