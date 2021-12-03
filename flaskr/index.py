"""
    This file creates a blueprint for the /index page
    This file handels:
        - GET requests in URL
        - running scheduled events upon refresh
        - displaying the index.html webpage
        - getting covid and news data and rendering to webpage
"""

import logging
from flask import Blueprint
from flask import render_template
from flask import request
from flaskr import config
from flaskr import covid_data_handler
from flaskr import covid_news_handling
from flaskr import scheduler
from flaskr import update_handler

bp = Blueprint("index", __name__)

#compleated
def handel_get_request() -> None:
    """ function to handel all the get requests """

    # check if 'notif' param exists, if so close a news article
    title = request.args.get("notif")
    if title is not None:
        # log that a 'notif' get request was triggered
        logging.info("'notif' GET request")

        # close news article
        covid_news_handling.news_close(title)
        return

    # check if 'two' param exists, if so add a new alarm
    update_label = request.args.get("two")
    if update_label is not None:
        # log that a 'two' get request was triggered
        logging.info("'two' GET request")

        update_time = request.args.get("alarm")
        repeat_update = (request.args.get("repeat") is not None)
        should_update_covid_data = (request.args.get("covid-data") is not None)
        should_update_news_articles = (request.args.get("news") is not None)

        # add a new alarm using the update handler
        update_handler.add_update(update_label, update_time, repeat_update,
            should_update_covid_data, should_update_news_articles)
        return

    # check if 'alarm_item' param exists, if so remove update
    remove_alarm_title = request.args.get("alarm_item")
    if remove_alarm_title is not None:
        # log that an 'alarm_item' get request was triggered
        logging.info("'alarm_item' GET request")

        # remove update using update handler
        update_handler.remove_update(remove_alarm_title)
        return

    logging.info("GET requests handeled")

#compleated
@bp.route("/index", methods=['GET'])
def index():
    """ function called when /index in url """

    # handel url GET requests
    handel_get_request()

    # debugging scheduler event queue
    logging.debug("scheduler queue before run: %s", str(scheduler.SCHEDULER.queue))

    logging.info("scheduler run events")
    scheduler.SCHEDULER.run(blocking=False)

    logging.debug("scheduler queue after run: %s", str(scheduler.SCHEDULER.queue))

    # get news articles and covid data data structures
    news_articles = covid_news_handling.ARTICLES
    covid_data = covid_data_handler.COVID_DATA
    updates = update_handler.UPDATES

    # return the html and render with variables
    return render_template("index.html",
        title=config.data["dashboard"]["title"],
        location=config.data["dashboard"]["local_location"],
        nation_location=config.data["dashboard"]["national_location"],
        local_7day_infections=covid_data["local_7_day_cases"],
        national_7day_infections=covid_data["national_7_day_cases"],
        hospital_cases=covid_data["national_current_hospital_cases"],
        deaths_total=covid_data["national_total_deaths"],
        image=config.data["dashboard"]["favicon"],
        news_articles=news_articles,
        updates=updates)
