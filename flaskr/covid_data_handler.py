# compleated
"""
    this file handels:
        - parcing csv data from file
        - covid data loading from public health england API
          (https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/)
        - covid data processing
        - updating covid data
        - schedule covid data update events
        - cancell scheduled covid data update events
"""

import time
import csv
import logging
import requests
from uk_covid19 import Cov19API

from flaskr import scheduler
from flaskr import config

COVID_DATA = {
    "local_7_day_cases" : 0,
    "national_7_day_cases" : 0,
    "national_current_hospital_cases" : 0,
    "national_total_deaths" : 0
}
COVID_UPDATE_EVENTS = {}

# sample data function (tested)
def parse_csv_data(csv_filename: str) -> list:
    """
        split the csv file into list of string

        Arguments:
            csv_filename (str) -- the filename of the csv file to parce

        Returns:
            a list of strings contaning each line of the input file (list[str])

    """
    rows = []
    try:
        with open(csv_filename, 'r', encoding='utf-8') as csv_file:
            for line in csv_file:
                rows.append(line.strip('\n'))

    except FileNotFoundError as error:
        logging.error("coild not find csv file: %s", error)
        return []

    logging.info("csv data parsed succsefully")
    return rows

# compleated (tested)
def first_not_null_value(covid_data : list) -> int:
    """
        returns the first not null value in list

        Arguments:
            covid_data (list[str]) -- the input list data

        Returns:
            the first not null value in the list (int)
    """

    # loop throguh data and store the first not null value
    value = 0
    for data in covid_data:
        if data != 0:
            value = float(data)
            break

    return value

# compleated (tested)
def get_seven_day_cases(covid_data : list) -> int:
    """
        sum the first 7 values from first null value excluding the first not null value

        Arguments:
            covid_data (list[str]) -- the input list data

        Returns:
            the sum of the next 7 days after the first not null day (int)
    """

    # find the first not null day
    # skip it
    # sum the remaining 7 days
    seven_day_cases = 0
    skip_incompleate_data = True
    index = 0
    days = 0
    while days < 7:
        if index >= len(covid_data):
            break
        data = covid_data[index]

        if not skip_incompleate_data:
            seven_day_cases += data
            days += 1

        if data != 0:
            if skip_incompleate_data:
                skip_incompleate_data = False
                index += 1
                continue

        index += 1

    return seven_day_cases

# sample data function (tested)
def process_covid_csv_data(covid_csv_data: str) -> tuple:
    """
        extracts number of cases in last 7 days, current number of hospital cases,
        cumulative number of deaths
        note:   - first row of csv data should be a list of headers

        Arguments:
            covid_csv_data (str) -- the input csv data. list of strings
                                    (each string represents one csv line)

        Returns:
            a tuple of the seven day cases, total hospital cases and total
            deaths for the given csv data (tuple)
    """

    # define the hard coded values for the cum_death_index, hosipital cases index
    # and new cases index
    # values hard coded as function will only be used for sample csv data
    cum_death_index = 4
    hospital_cases_index = 5
    new_cases_index = 6

    # format the data
    if covid_csv_data == "":
        logging.error("could not parse covid data")
        return 0,0,0

    # parces the first line of the csv data
    # get the headers from the first line of the csv data and split into each header
    headers = list(csv.reader([covid_csv_data[0]]))[0]
    covid_data = []

    # get the indexing name for each of the coulmns (based of function inputs)
    new_cases_name = headers[new_cases_index]
    hospital_cases_name = headers[hospital_cases_index]
    cum_death_name = headers[cum_death_index]

    # parces the rest of the csv data
    # skips the first row of data as that has been parced allready
    # stores covid data in format:
    #   [{ [header name 1] : value, [header name 2] : value, ... }, ...]
    pass_row = True
    for row in covid_csv_data:
        if pass_row:
            pass_row = False
            continue

        row_csv = list(csv.reader([row]))[0]

        row_data = {}
        index = 0
        for header in headers:
            row_data[header] = row_csv[index]

            index += 1

        covid_data.append(row_data)

    #assume dates are in order of newst data first

    #caluclate 7 day cases
    #loop through the first 7 not null items in new cases column
    #skip first incompleate day
    seven_day_cases = 0
    skip_incompleate_data = True
    index = 0
    days = 0
    while days < 7:
        data = covid_data[index]
        if data[new_cases_name] != "":
            if skip_incompleate_data:
                skip_incompleate_data = False
                index += 1
                continue

            seven_day_cases += int(data[new_cases_name])
            days += 1

        index += 1

    #get total hospital cases
    #get first item from hospital cases list that is not null
    total_hospital_cases = 0
    for data in covid_data:
        if data[hospital_cases_name] != "":
            total_hospital_cases = int(data[hospital_cases_name])
            break

    #get total deaths
    #get first item from cum deaths list that is not null
    total_deaths = 0
    for data in covid_data:
        if data[cum_death_name] != "":
            total_deaths = int(data[cum_death_name])
            break

    # log succseful proccessed
    logging.info("covid data proccessed succsefully")

    #return calucluated values
    return seven_day_cases,total_hospital_cases,total_deaths

# compleated (tested)
def process_covid_data(covid_json_data: dict, header_functions: dict) -> dict:
    """
        processes the given csv data and returns metrics based of data
        processing functions

        A more general version of function process_covid_csv_data

        Arguments:
            covid_json_data (dict) -- the data to be processed
            header_functions (dict) -- a dictonary of headers with values of functions
                                       to be used to process the data for that header

        Returns:
            a diconary of data indexed by the header and the value of that header
    """

    # extract the covid data from the covid API data
    covid_json_data = covid_json_data['data']

    # if data is null, return an empty set
    if len(covid_json_data) == 0:
        return {}

    # if header_functions is empty, return an empty dictinary
    if len(header_functions) == 0:
        return {}

    # parces the first line of the csv data
    # get the headers from the first line of the csv data and split into each header
    headers = list(covid_json_data[0].keys())
    covid_data = {}

    for header in headers:
        covid_data[header] = []

    # loop throguh covid json data
    # accumulate data for each header
    for data in covid_json_data:
        for header in headers:
            covid_data[header].append(data[header] if data[header] is not None else 0)

    # loop throguh each header to be returned
    # apply the proccessing function for each header with its corrispondig data
    return_data = {}
    for header in header_functions:
        return_data[header] = header_functions[header](covid_data[header])

    # log succseful proccessed
    logging.info("covid data proccessed succsefully")

    # reutrn the return data
    return return_data

# compleated (tested)
def covid_API_request(location:str="Exeter",location_type:str="ltla",metrics:list=None)->dict:
    """
        fetch covid data based on config file and input locations

        Arguments:
            location (str) -- the location that the data resutlts should be about (default='Exeter')
            location_type (str) -- the location type of the given location (default='ltla')
            metrics (list) -- the headers of the metrics to be requested to the API (defulat=None)

        Returns:
            a diconary of the covid API retrun data (dicr)
    """

    # setup location filter
    location_filter = [
        'areaType='+location_type,
        'areaName='+location
    ]

    # set up defaut metrics if none are provided
    if metrics is None:
        metrics = [
            "hospitalCases", "newCasesBySpecimenDate", "cumDailyNsoDeathsByDeathDate"
        ]

    # setup header params
    headers = {}
    for metric in metrics:
        headers[metric] = metric

    # create api instance with location filters and headers
    api = Cov19API(filters=location_filter, structure=headers)

    # try get api request
    try:
        # get covid json data
        api_covid_data = api.get_json()

        # log succseful api fetch
        logging.info("covid data fetched from API")

        return api_covid_data

    except requests.exceptions.ConnectionError as error:
        # catch and report a connection error
        logging.error("could not fetch covid data: %s", str(error))
        return ""

# compleated (tested)
def update_covid_data(update_label: str = None) -> None:
    """
        fetch covid data from api and update covid_data data structure with new data

        Arguments:
            update_label (str) -- if update_label is not None, then the covid update
                                  event with that label is cancelled (defulat = None)

        Returns:
            None (None)
    """

    # pull constants from config file
    local_location = config.data["dashboard"]["local_location"]
    local_location_type = config.data["dashboard"]["local_location_type"]

    national_location = config.data["dashboard"]["national_location"]
    national_location_type = config.data["dashboard"]["national_location_type"]

    # get local and national covid data
    local_headers = ["newCasesBySpecimenDate"]
    national_headers = ["newCasesBySpecimenDate", "hospitalCases", "cumDailyNsoDeathsByDeathDate"]

    covid_local_csv_data = covid_API_request(local_location, local_location_type, local_headers)
    covid_national_csv_data = covid_API_request(national_location,
        national_location_type,
        national_headers)

    local_header_functions = {"newCasesBySpecimenDate" : get_seven_day_cases}
    national_headers_function = {
        "newCasesBySpecimenDate" : get_seven_day_cases,
        "hospitalCases" : first_not_null_value,
        "cumDailyNsoDeathsByDeathDate" : first_not_null_value
    }

    # get local and national covid statistics from process_covid_csv_data() function
    local_results = process_covid_data(covid_local_csv_data, local_header_functions)
    national_results = process_covid_data(covid_national_csv_data,national_headers_function)

    # update covid_data data structure with new covid data
    COVID_DATA["local_7_day_cases"] = int(local_results["newCasesBySpecimenDate"])
    COVID_DATA["national_7_day_cases"] = int(national_results["newCasesBySpecimenDate"])
    COVID_DATA["national_current_hospital_cases"] = int(national_results["hospitalCases"])
    COVID_DATA["national_total_deaths"] = int(national_results["cumDailyNsoDeathsByDeathDate"])

    # log that the covid_data data structure was updated
    logging.info("covid data updated")

    # check if update label is in covid_update_events data structure
    # event triggered, so remove from COVID_UPDATE_EVENTS data structure
    if update_label is not None:
        # remove event from COVID_UPDATE_EVENTS data structure
        # check if update label is a valid key
        if update_label in COVID_UPDATE_EVENTS.keys():
            del COVID_UPDATE_EVENTS[update_label]

            # log event was removed from data structure
            logging.info("COVID_UPDATE_EVENTS removed event with title: %s", update_label)

# compleated (tested)
def schedule_covid_updates(update_interval: int, update_name: str) -> None:
    """
        schedule a covid data update with given interval and name

        Arguments:
            update_interval (int) -- the time interval at which the updated should be scheduled for
            update_name (str) -- the name of the update the event will be indexed by

        Returns:
            None (None)
    """

    # add covid update to scheduler queue with time interval
    event=scheduler.SCHEDULER.enterabs(
        time.time()+update_interval,1,update_covid_data,(update_name,))

    # log the event has been added to the scheduler
    logging.info("covid data scheduler added to queue with title: %s", update_name)

    # store the update event incase it needs to be cancelled
    COVID_UPDATE_EVENTS[update_name] = event

# compleated (tested)
def remove_sheduler_covid_data_update_event(update_label: str) -> None:
    """
        function to remove the sheduler event with title from covid_update_events

        Arguments:
            update_label (str) -- the name of the update label is binded to

        Returns:
            None (None)
    """

    # check if event exists
    if update_label not in COVID_UPDATE_EVENTS.keys():
        logging.warning("title not found in covid data update event list: %s", update_label)
        return

    # cancell the event in the scheduller
    scheduler.SCHEDULER.cancel(COVID_UPDATE_EVENTS[update_label])

    # remove update for covid_update_events data strucutre
    del COVID_UPDATE_EVENTS[update_label]
    logging.info("scheduler canncled covid data update event with title: %s", update_label)
