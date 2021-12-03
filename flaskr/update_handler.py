# compleated
"""
    This file handels:
        - the updates[] data strutues
        - adding updates to the data scturue
        - removing updates from the data sctureu
        - scheduleing repeting updates
        - scheduleing remove updates
        - cancelling all update events assosated with an update label
"""

import logging
import time
from datetime import datetime
from markupsafe import Markup

from flaskr import scheduler
from flaskr.covid_data_handler import schedule_covid_updates
from flaskr.covid_news_handling import schedule_news_updates
from flaskr.covid_data_handler import remove_sheduler_covid_data_update_event
from flaskr.covid_news_handling import remove_sheduler_news_update_event

UPDATES = []
REPETE_UPDATE_EVENTS = {}
REMOVE_UPDATE_EVENTS = {}

#compleated
def add_update(label: str, str_time: str, repeat: bool,
    should_update_covid_data: bool, should_update_news_articles: bool) -> None:
    """
        adds an update to the updates list and also (if specified) schedules a covid and news update

        Arguments:
            label (str) -- the name of the update label to be added
            str_time (str) -- the time the update should trigger in format (H:M)
            repeat (bool) -- if the update should be repeting
            should_update_covid_data (bool) -- if the update should update the covid data
            should_update_news_articles (bool) -- if the update should update the news articles

        Returns:
            None (None)
    """
    # cheak if time string is in correct format
    update_time = str_time
    try:
        update_time = datetime.strptime(str_time, "%H:%M")
    except ValueError as error:
        logging.error("cannot create update: time format not valid. ERROR: %s", str(error))
        return

    # cheak if update title is allready in update list
    for update in UPDATES:
        if update["title"] == label:
            logging.error("cannot create update: name is not unique")
            return

    # create content body html with given data
    content = "<strong>Scheduled: </strong> " + str_time
    content += "<br><strong>Repeat: </strong> " + str(repeat)
    content += "<br><strong>Update Covid Data: </strong> " + str(should_update_covid_data)
    content += "<br><strong>Update News Articles: </strong> " + str(should_update_news_articles)

    # create update data structure to add to update list
    update = {
        "title" : label,
        "time" : str_time,
        "repeat" : repeat,
        "update_covid_data" : should_update_covid_data,
        "update_news_articles" : should_update_news_articles,
        "content" : Markup(content)
    }

    UPDATES.append(update)

    # get time interval between now and the update time
    now = datetime.now()
    delta = update_time - now
    time_interval = delta.seconds

    # create scheduler update if should update covid data
    if should_update_covid_data:
        schedule_covid_updates(time_interval, label)

    # create scheduler update if should update covid news
    if should_update_news_articles:
        schedule_news_updates(time_interval, label)

    # schedule a remove update
    schedule_remove_updates(time_interval, label)

    # if repete, also scedule a repete update
    # note: in order for add_update to work, the name must be unique
    #       therefore, a remove update should be squeduled aswell as a repete update
    #       so that the old update gets removed, and repaced with a new one
    if repeat:
        schedule_repeat_updates(time_interval, label)

    # log update added succsefully
    logging.info("update alarm added with title: %s", label)

#compleated
def schedule_repeat_updates(update_interval: int, update_name: str) -> None:
    """
        schedule a repete update with given interval and name

        Arguments:
            update_interval (int) -- the time interval (in seconds)
                                     the update should be triggered in
            update_name (str) -- the name the update event will be indexed by

        Returns:
            None (None)
    """

    # get update details from update array
    str_time = ""
    update_found = repeat = should_update_covid_data = should_update_news_articles = False
    for update in UPDATES:
        if update["title"] == update_name:
            update_found = True
            str_time = update["time"]
            repeat = update["repeat"]
            should_update_covid_data = update["update_covid_data"]
            should_update_news_articles = update["update_news_articles"]
            break

    # check if update was found, if not log an error
    if not update_found:
        # log an error that the update was not found and exit function
        logging.error("update with label '%s' not found in update list", update_name)
        return

    # add covid update to scheduler queue with time interval
    event = scheduler.SCHEDULER.enterabs(
        time.time()+update_interval, 1, add_update,
        (update_name, str_time, repeat, should_update_covid_data,
        should_update_news_articles, ))

    # log the event has been added to the scheduler
    logging.info("repete update scheduler added to queue with title: %s", update_name)

    # store the update event incase it needs to be cancelled
    REPETE_UPDATE_EVENTS[update_name] = event

#compleated
def schedule_remove_updates(update_interval: int, update_name: str) -> None:
    """
        schedule a delete update with given interval and name

        Arguments:
            update_interval (int) -- the time interval (seconds) the update should be triggered in
            update_name (str) -- the name the update event will be indexed by

        Returns:
            None (None)
    """

    # add remove update to scheduler queue with time interval
    event = scheduler.SCHEDULER.enterabs(
        time.time()+update_interval, 1,
        remove_update_from_updates, (update_name, ))

    # log that the event has been added to the scheduler
    logging.info("remove update event added to queue with title: %s", update_name)

    # store the update event incase it needs to be cancelled
    REMOVE_UPDATE_EVENTS[update_name] = event

#compleated
def remove_update_from_updates(remove_alarm_title: str) -> None:
    """
        remove the update from updates list if title matches

        Arguments:
            remove_alarm_title (str) -- the label of the update['title'] to be removed

        Returns:
            None (None)
    """

    # loop throuhg update list and check if title != remove_alarm_title
    # if not maching add to new update list
    global UPDATES
    new_updates = []
    for update in UPDATES:
        if update["title"] != remove_alarm_title:
            new_updates.append(update)

    # log update to logfle
    logging.info("deleted update from updates data structure")

    # update old updates array to new updates array
    UPDATES = new_updates

    # log update to logfle
    logging.info("updates list updated")

# compleated
def remove_update(update_name: str) -> None:
    """
        this function removes updates from the updates data structures and schedulre queue

        Arguments:
            update_name (str) -- the name of the update label to be removed

        Returns:
            None (None)
    """

    # remove update from update data scturucture
    remove_update_from_updates(update_name)

    # remove remove update events from remove_update_events data structure
    if update_name in REMOVE_UPDATE_EVENTS.keys():
        # cancell scheduler event
        scheduler.SCHEDULER.cancel(REMOVE_UPDATE_EVENTS[update_name])

        # delete event from remove update events data structure
        del REMOVE_UPDATE_EVENTS[update_name]

        # log update remove
        logging.info("remove remove event from scheduler with label: %s", update_name)

    # remove repete update events from repete_update_events data structure
    if update_name in REPETE_UPDATE_EVENTS.keys():
        # cancell scheduler event
        scheduler.SCHEDULER.cancel(REPETE_UPDATE_EVENTS[update_name])

        # delete event from repete update events data structure
        del REPETE_UPDATE_EVENTS[update_name]

        # log update remove
        logging.info("remove repete event from scheduler with label: %s", update_name)

    # cancell covid update
    # note: covid_data_handler function remove_sheduler_covid_data_update_event()
    #       handells updates that do not exist so no need to check if there is a covid update event
    remove_sheduler_covid_data_update_event(update_name)

    # cancell news update
    # note: covid_news_handling function remove_sheduler_news_update_event() handells updates
    #       that do not exist so no need to check if there is a news update event
    remove_sheduler_news_update_event(update_name)
