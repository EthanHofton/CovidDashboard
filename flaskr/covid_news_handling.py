# compleated
"""
    this file handels:
        - shceduling news updates
        - updating news data
        - removing scheduled news updates
        - closing news articles
        - news article API requests (https://newsapi.org/)
"""

import json
import time
import logging
from datetime import date
from datetime import timedelta
import requests
from flaskr import config
from flaskr import scheduler

ARTICLES = []
DELETED_ARTICLES = []
NEWS_UPDATE_EVENTS = {}

# compleated (tested)
def schedule_news_updates(update_interval: int, update_name: str) -> None:
    """
        schedule a covid news update with given interval and name

        Arguments:
            update_interval (int) -- the interval of time at which the update should be triggered
            update_name (str) -- the name of the update the event will be indexed by

        Returns:
            None (None)
    """

    # add covid update to scheduler queue with time interval
    event = scheduler.SCHEDULER.enterabs(time.time()+update_interval,1,update_news,(update_name,))

    # log the event has been added to the scheduler
    logging.info("covid news scheduler added to queue with title: %s", update_name)

    # store the update event incase it needs to be cancelled
    NEWS_UPDATE_EVENTS[update_name] = event

# compleated
def update_news(update_label: str = None) -> None:
    """
        function to fetch news articles and update the articles data strucrure

        Arguemnts:
            update_label (str) -- if update_label is not None, then the covid
                                  update event with that label is cancelled (defulat = None)

        Returns:
            None (None)
    """

    # clear the old articles array
    ARTICLES.clear()

    # fetch articles from API using news_API_request() function
    articles_request = news_API_request(config.data["dashboard"]["search_terms"])

    # check if news news_API_request() function returned None
    if articles_request is None:
        # log warning that no news articles were returned
        logging.warning("no news articles returned")
        logging.info("news articles updated")
        return

    # loop through each news article and check its title is not in the deleted articles array
    # if title not in deleted articles array, add to news article data structure
    for article in articles_request:
        if article["title"] not in DELETED_ARTICLES:
            ARTICLES.append(article)

    # log that news articles were succsefuly updated
    logging.info("news articles updated")

    # check if an update news event should be deleted
    # event triggered, therefor remove update from NEWS_UPDATE_EVENTS data structure
    if update_label is not None:
        # remove update for NEWS_UPDATE_EVENTS data strucutre
        # check update label is key
        if update_label in NEWS_UPDATE_EVENTS.keys():
            del NEWS_UPDATE_EVENTS[update_label]

            # log event was removed from data structure
            logging.info("NEWS_UPDATE_EVENTS removed event with title: %s", update_label)

# compleated
def remove_sheduler_news_update_event(update_label: str) -> None:
    """
        function to remove the sheduler event with title from news_update_events

        Arguments:
            update_label (str) -- label index used to remove the scheduled update

        Returns:
            None (None)
    """

    # check if event exists
    if update_label not in NEWS_UPDATE_EVENTS.keys():
        logging.warning("title not found in covid news update event list: %s", update_label)
        return

    # cancell the event in the scheduller
    scheduler.SCHEDULER.cancel(NEWS_UPDATE_EVENTS[update_label])

    # remove update for NEWS_UPDATE_EVENTS data strucutre
    del NEWS_UPDATE_EVENTS[update_label]
    logging.info("scheduler canncled covid data update event with title: %s", update_label)

# compleated
def news_close(title: str) -> None:
    """
        function to add a news article title to the deleted article list

        Arguments:
            title (str) -- the title of the news article to close

        Returns:
            None (None)

    """

    # append the article title to the deleted article list
    if title in DELETED_ARTICLES:
        logging.warning("news article allready deleted: %s", title)
        return

    DELETED_ARTICLES.append(title)

    # update the articles data structureso that the deleted article is not shown
    new_articles = []
    global ARTICLES
    for article in ARTICLES:
        # loop through each article in article list and check there title
        # is not the deleted aritcles list
        if article["title"] not in DELETED_ARTICLES:
            # append to new articles array if not in deleted articles list
            new_articles.append(article)

    # update old article list to new list
    ARTICLES = new_articles

    # log that the article was succsefully deleted
    logging.info("news article deleted with title: %s", title)

# compleated
def news_API_request(covid_terms: str = "Covid COVID-19 coronavirus") -> list:
    """
        function to pull covid news articles from news API given the search terms

        Arguments:
            covid_terms (str) -- the search terms the news article titles should contain

        Returns:
            a list of article dictionarys (list[dict])

    """

    # form the search query by splitting the covid terms by space
    # then seperate the seperated terms with OR
    search_query = ""
    for term in covid_terms.split(" "):
        if search_query == "":
            search_query += term
        else:
            search_query += " OR " + term

    # get news_api config file data
    language = config.data["news_api"]["language"]
    sort_by = config.data["news_api"]["sortBy"]
    api_key = config.data["news_api"]["api_key"]
    page_size = config.data["news_api"]["pageSize"]

    # calculate the from date by subtracting
    # config.data["news_api"]["from"] (in days) to the current date
    now = date.today()
    prev_days = timedelta(days=config.data["news_api"]["from"])
    from_date = now - prev_days

    # form the payload
    payload = {
        "q" : search_query,
        "language" : language,
        "pageSize" : page_size,
        "sortBy" : sort_by,
        "from" : from_date.isoformat(),
        "apiKey" : api_key
    }

    # get the url from the config file
    url = config.data["news_api"]["api_url"]

    # try do a get request to the news api
    try:
        # commit get request
        data = requests.get(url, params=payload)

        # get responnce and json parce it
        responce = json.loads(data.text)

        # log a sucsessful fetch
        logging.info("covid news fetched from API")

        # return a list of articles
        return responce["articles"]

    except requests.exceptions.ConnectionError as error:
        # catch a connection error and report to logfile
        logging.error("could not fetch news articles: %s", str(error))
        return None
