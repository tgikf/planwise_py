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

from planner import get_allocation_proposals, get_region_holidays
from params import get_holiday_locales

application = Flask(__name__)

# random key that flask will use to generate and authenticate cookies
application.secret_key = (
    "5b3e0ea670dd36807b72acb9045ddb547f8fd331aac48d1e2099a364b66c8025"
)


# index landing point
@application.route("/")
def index():
    return render_template("plan.html")


# index landing point
@application.route("/about")
def about():
    return render_template("about.html")


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
        budget = int(request.args.get("budget", default=15))
        region = request.args.get("region", default="SG")

        # response
        response["start_date"] = start_date.isoformat()
        response["end_date"] = end_date.isoformat()
        response["region"] = region
        response["budget"] = budget

        # add public holidays to response
        pub_hd = []
        ph_object = get_region_holidays(pd.date_range(start_date, end_date), region)
        for raw_ph in ph_object:
            pub_hd.append(
                {"date": raw_ph.isoformat(), "description": ph_object[raw_ph]}
            )
        response["public_holidays"] = json.dumps(pub_hd)

        response["proposals"] = get_allocation_proposals(
            budget, start_date, end_date, region
        )

    except ValueError as ex:
        alerts.append(str(ex))

    # add alerts to response
    response["alerts"] = json.dumps(alerts)
    return json.dumps(response)


# API for holiday locales
@application.route("/api/getLocales", methods=["GET"])
def params_api():
    response = {}
    alerts = []

    response["locales"] = json.dumps(get_holiday_locales())

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
