""" file handels testing all functions in update_handler.py """

from flaskr.update_handler import add_update
import flaskr.update_handler
import flaskr.covid_data_handler
import flaskr.covid_news_handling
from flaskr import scheduler
def test_add_update():
    """
        test add_update()

        testing crieria:
            - function call adds update to relevent update lists
    """

    # cancell all events in event queue
    list(map(scheduler.SCHEDULER.cancel, scheduler.SCHEDULER.queue))

    # clear covid data update list
    flaskr.covid_data_handler.COVID_UPDATE_EVENTS.clear()

    # clear covid news update list
    flaskr.covid_news_handling.NEWS_UPDATE_EVENTS.clear()

    # clear update list
    flaskr.update_handler.UPDATES.clear()

    # clear remove update list
    flaskr.update_handler.REMOVE_UPDATE_EVENTS.clear()

    # clear repete update list
    flaskr.update_handler.REPETE_UPDATE_EVENTS.clear()

    # add an update
    add_update("test", "10:10", True, True, True)

    # check the update lists and all the event queues have been added to
    assert len(flaskr.covid_data_handler.COVID_UPDATE_EVENTS) != 0
    assert len(flaskr.covid_news_handling.NEWS_UPDATE_EVENTS) != 0
    assert len(flaskr.update_handler.UPDATES) != 0
    assert len(flaskr.update_handler.REMOVE_UPDATE_EVENTS) != 0
    assert len(flaskr.update_handler.REPETE_UPDATE_EVENTS) != 0

from flaskr.update_handler import remove_update_from_updates
def test_remove_update_from_updates():
    """
        test remove_update_from_updates()

        testing crieria:
            - function succsefuly removes update from UPDATES data strucure
    """

    # clear update queue
    flaskr.update_handler.UPDATES.clear()

    # add a test update to the updates data strucutre
    flaskr.update_handler.UPDATES.append({"title" : "test"})

    # check update was added
    assert len(flaskr.update_handler.UPDATES) == 1

    remove_update_from_updates("test")

    # check update was removed
    assert len(flaskr.update_handler.UPDATES) == 0
