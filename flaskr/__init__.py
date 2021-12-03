"""
    __init__.py tells python this dirictory should be treated as a package
    this file handels:
        - creating the main flask application
        - initalising the logger using the logging data from the conf file
        - initalising the covid and news data
        - registering the index blueprint to the app
"""

import os
import logging
from flask import Flask
from flask import render_template
from flaskr import index
from flaskr import covid_news_handling
from flaskr import covid_data_handler
from flaskr import scheduler
from flaskr import config

def create_app():
    """ flask create app called on server startup. returns flask app """

    # create app instance
    app = Flask(__name__, instance_relative_config=True)

    # setup logging format using conf file data
    logging_format = config.data["logging"]["format"]
    logging_filename = config.data["logging"]["logfile"]
    logging_level = config.data["logging"]["level"]
    logging.basicConfig(filename=logging_filename,
        format=logging_format,
        level=logging_level,
        force=True)

    # log that the application has just started
    logging.info("application started")

    # update covid data and news articles upon startup
    covid_data_handler.update_covid_data()
    covid_news_handling.update_news()

    # register the index blueprint to the app
    app.register_blueprint(index.bp)

    # get and set the app logger levels to the value in the conf file
    app_logger = logging.getLogger('werkzeug')
    app_logger.setLevel(config.data["logging"]["flask_logger_level"])

    # return the app
    return app
