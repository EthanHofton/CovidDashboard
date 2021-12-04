""" file handels testing all functions in covid_news_handling.py """

import time

from flaskr import scheduler
from flaskr.covid_news_handling import schedule_news_updates
from flaskr.covid_news_handling import ARTICLES
from flaskr.covid_news_handling import NEWS_UPDATE_EVENTS
def test_schedule_news_updates() -> None:
    """
        test schedule_news_updates()

        NOTE: function will wait 3 seconds to check event executed properly

        testing crieria:
            - news update function added to event queue
            - news articles data structure updates correctly
            - event added to NEWS_UPDATE_EVENTS data structure
            - when event triggered, event removed from NEWS_UPDATE_EVENTS
    """

    # empty articles list
    ARTICLES.clear()

    # check scheduler queue empty
    assert len(scheduler.SCHEDULER.queue) == 0

    # schedule news update
    schedule_news_updates(3, 'test_news_update')

    # check news update event added to event queue
    assert len(scheduler.SCHEDULER.queue) == 1

    # check event added to NEWS_UPDATE_EVENTS data strucutre
    assert 'test_news_update' in NEWS_UPDATE_EVENTS.keys()

    # run schdeulder to check event will not run as 3 seconds havnt passed
    scheduler.SCHEDULER.run(blocking=False)

    # check event still in event queue
    assert len(scheduler.SCHEDULER.queue) == 1

    # wait 3 seconds to check if event has run
    time.sleep(3)

    # run schdeulder to check event will run as 3 seconds have passed
    scheduler.SCHEDULER.run(blocking=False)

    # check event has ran
    assert len(scheduler.SCHEDULER.queue) == 0

    # check event was removed from NEWS_UPDATE_EVENTS data structure
    assert 'test_news_update' not in NEWS_UPDATE_EVENTS.keys()

    # check news articles updated correctly
    assert len(ARTICLES) != 0

from flaskr.covid_news_handling import update_news
def test_update_news() -> None:
    """
        test update_news()

        testing crieria:
            - ARTICLES data structure updates correctly
            - ARTICLES data structure does not inclue blacklisted titles (removed)
    """

    # clear ARTICLES list
    ARTICLES.clear()

    # check articles is empty
    assert len(ARTICLES) == 0

    # update the news articles
    update_news()

    # check there are news articles in the list
    assert len(ARTICLES) != 0

from flaskr.covid_news_handling import remove_sheduler_news_update_event
def test_remove_sheduler_news_update_event() -> None:
    """
        test remove_sheduler_news_update_event()

        testing crieria:
            - add a covid update event, and remove it
            - removed covid event is removed from NEWS_UPDATE_EVENTS data structure
            - function should be able to deal with keys that do not belong to an event
    """

    # check event queue is empty
    assert len(scheduler.SCHEDULER.queue) == 0

    # schedule a news update (function allready tested)
    schedule_news_updates(3, 'test_update')

    # check the event was added to the event queue
    assert len(scheduler.SCHEDULER.queue) == 1

    # check the event was added to COVID_UPDATE_EVENTS data structure
    assert 'test_update' in NEWS_UPDATE_EVENTS.keys()

    # remove the event from the event queue
    remove_sheduler_news_update_event('test_update')

    # check event was removed from event queue
    assert len(scheduler.SCHEDULER.queue) == 0

    # check event was removed from COVID_UPDATE_EVENTS data strucutre
    assert 'test_update' not in NEWS_UPDATE_EVENTS.keys()

    # check the function can deal with non-existant event labels
    try:
        # run in try-except block, if exception triggered, function failed
        remove_sheduler_news_update_event('not_test_update')
    except Exception as e:
        # exception caught, function failed to deal with non-existant labels
        assert 0

from flaskr.covid_news_handling import news_close
from flaskr.covid_news_handling import DELETED_ARTICLES
import flaskr.covid_news_handling
def test_news_close() -> None:
    """
        test news_close()

        testing crieria:
            - given title added to deleted list
            - given title will be removed from news update (if it is in)
    """

    # clear ARTICLES
    ARTICLES.clear()

    # clear DELETED_ARTICLES
    DELETED_ARTICLES.clear()

    # add an enrty to ARTICLES with title test
    ARTICLES.append({"title" : "test"})

    # close news article
    news_close("test")

    # check test is in deleted articles
    assert "test" in DELETED_ARTICLES

    # check the article with title test has been removed
    assert len(flaskr.covid_news_handling.ARTICLES) == 0

from flaskr.covid_news_handling import news_API_request
def test_news_API_request() -> None:
    """
        test news_API_request()

        testing crieria:
            - defulat argument is 'Covid COVID-19 coronavirus'
            - return value is list
            - function returns a list of news articles
    """

    # check default argument
    assert news_API_request("Covid COVID-19 coronavirus") == news_API_request()

    # check returned value is a list
    assert isinstance(news_API_request(), list)

    # check values returned is not zero
    assert len(news_API_request()) != 0
