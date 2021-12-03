"""
    this file handels the config file loading. Defulat config data is
    used if the config file is not found
"""

import json
import logging

DEFULAT_CONFIG = {
    "dashboard" : {
        "title" : "Covid19 Dashboard",
        "local_location" : "Exeter",
        "local_location_type" : "ltla",
        "national_location" : "England",
        "national_location_type" : "nation",
        "favicon" : "favicon.ico"
    },

    "logging" : {
        "format" : "%(levelname)s:%(name)s: [%(asctime)s] - %(message)s",
        "logfile" : "flaskr/logs/data.log",
        "level" : 20,
        "flask_logger_level" : 40
    },

    "news_api" : {
        "api_key" : "a6a851dc7d5849f893e85cba7d2d9a6f",
        "api_url" : "https://newsapi.org/v2/everything",
        "language" : "en",
        "pageSize" : 2,
        "from" : 5,
        "sortBy" : "publishedAt"
    }
}

# create a shared instance of the config data
data = {}
try:
    # open the config file and load the json to the data variable
    with open("flaskr/config.json", encoding="utf-8") as json_file:
        data = json.load(json_file)

    # log that the config file loaded
    logging.info("config file loaded")
except FileNotFoundError:
    # log a file not found error
    logging.warning("config file not found")

    # set the data to the defualt config
    data = DEFULAT_CONFIG

    # log that the default config used
    logging.info("defualt config used")
