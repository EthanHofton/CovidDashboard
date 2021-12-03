""" This file handels testing all the functions in covid_data_handler.py """

import time

def covid_data_check() -> None:
    """
        function to check the data in the COVID_DATA data structure is correct

        function pulls the correct data from the api using allready tested functions:
            - covid_API_request()
            - process_covid_data()
        in order to check that the data in the COVID_DATA data structure is up-to-date and
        correct using a series of assert satatments
    """

    # get local, nation location and location types from conf file
    local_location = config_data["dashboard"]["local_location"]
    local_location_type = config_data["dashboard"]["local_location_type"]
    national_location = config_data["dashboard"]["national_location"]
    national_location_type = config_data["dashboard"]["national_location_type"]

    # get local seven day data, process and test against covid data
    local_seven_day_cases_api_request = covid_API_request(local_location, local_location_type, ["newCasesBySpecimenDate"])
    assert COVID_DATA['local_7_day_cases'] == process_covid_data(local_seven_day_cases_api_request, {"newCasesBySpecimenDate" : get_seven_day_cases})["newCasesBySpecimenDate"]

    # get national seven day data, process and test against covid data
    national_seven_day_cases_api_request = covid_API_request(national_location, national_location_type, ["newCasesBySpecimenDate"])
    assert COVID_DATA['national_7_day_cases'] == process_covid_data(national_seven_day_cases_api_request, {"newCasesBySpecimenDate" : get_seven_day_cases})["newCasesBySpecimenDate"]

    # get national hospital cases data, process and test against covid data
    national_hospital_cases_api_request = covid_API_request(national_location, national_location_type, ["hospitalCases"])
    assert COVID_DATA['national_current_hospital_cases'] == process_covid_data(national_hospital_cases_api_request, {"hospitalCases" : first_not_null_value})["hospitalCases"]

    # get national total deaths data, process and test against covid data
    national_total_deaths_cases_api_request = covid_API_request(national_location, national_location_type, ["cumDailyNsoDeathsByDeathDate"])
    assert COVID_DATA['national_total_deaths'] == process_covid_data(national_total_deaths_cases_api_request, {"cumDailyNsoDeathsByDeathDate" : first_not_null_value})["cumDailyNsoDeathsByDeathDate"]

# sample testing functions from spec
from flaskr.covid_data_handler import parse_csv_data
def test_parse_csv_data() -> None:
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

# sample testing functions from spec
from flaskr.covid_data_handler import process_covid_csv_data
def test_process_covid_csv_data() -> None:
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

from flaskr.covid_data_handler import covid_API_request
def test_covid_API_request() -> None:
    """
        testing function for test_covid_API_request

        testing critera:
            - function returns dict
            - function returns data (list size is grater then 1 (just headers))
            - function returns the correct requested headers
    """

    # covid api test requests
    api_data_test_1 = covid_API_request("England", "nation", ["newCasesBySpecimenDate"])
    api_data_test_2 = covid_API_request("England", "nation", ["newCasesBySpecimenDate", "hospitalCases"])

    # check type is dict
    assert isinstance(api_data_test_1, dict)

    # check type is dict
    assert isinstance(api_data_test_2, dict)

    # check the returned data is not empty
    assert len(api_data_test_1["data"]) > 1
    assert len(api_data_test_1["data"]) > 1

    # check headers are correct
    assert list(api_data_test_1["data"][0].keys())[0] == "newCasesBySpecimenDate"

from flaskr.covid_data_handler import process_covid_data
from flaskr.covid_data_handler import first_not_null_value
from flaskr.covid_data_handler import get_seven_day_cases
def test_process_covid_data() -> None:
    """
        test the process_covid_data function

        testing critera:
            - function can take api result and process that data without crashing
    """

    # get the csv data
    api_data_test_1 = covid_API_request("England", "nation", ["newCasesBySpecimenDate"])
    api_data_test_2 = covid_API_request("England", "nation", ["newCasesBySpecimenDate"])

    # create the dict of return matrics and how there data should be processed
    metric_functions_test_1 = {
        "newCasesBySpecimenDate" : get_seven_day_cases
    }
    metric_functions_test_2 = {
        "newCasesBySpecimenDate" : first_not_null_value
    }

    # process the data
    return_data_test_1 = process_covid_data(api_data_test_1, metric_functions_test_1)
    return_data_test_2 = process_covid_data(api_data_test_2, metric_functions_test_2)

    # test it does not return the same value for 2 different processing functions
    assert return_data_test_1["newCasesBySpecimenDate"] != return_data_test_2["newCasesBySpecimenDate"]

from flaskr.covid_data_handler import first_not_null_value
def test_first_not_null_value() -> None:
    """
        tests first_not_null_value

        testing critera:
            - function correctly returns the correct value from examples

        reason for testing:
            test_case_1 -- expected data
            test_case_2 -- no first not null value
            test_case_3 -- no data after first not null value
            test_case_4 -- no data
    """

    # all test cases
    test_case_1 = [0,0,0,0,0,0,0,0,98,42,57,59]
    test_case_2 = [67,84,103,12,14]
    test_case_3 = [0,0,77,0,0]
    test_case_4 = [0,0,0,0,0]

    # test all test cases against hand calculated correct values
    assert first_not_null_value(test_case_1) == 98
    assert first_not_null_value(test_case_2) == 67
    assert first_not_null_value(test_case_3) == 77
    assert first_not_null_value(test_case_4) == 0

from flaskr.covid_data_handler import get_seven_day_cases
def test_get_seven_day_cases() -> None:
    """
        tests get_seven_day_cases

        testing critera:
            - function correctly returns the correct value from examples

        reason for testing:
            test_case_1 -- expected data to be processing
            test_case_2 -- some data missing after first not null value
            test_case_3 -- no not null first value
            test_case_4 -- not enough data for 7 day
            test_case_4 -- no data
    """

    # all test cases to be tested
    test_case_1 = [0,0,0,0,98,42,57,59,76,43,76,84,32]
    test_case_2 = [0,0,0,0,98,42,57,59,0,0,76,0,32,18,55,41]
    test_case_3 = [67,84,103,12,14,76,21,45,2,1,6]
    test_case_4 = [0,0,77,45,34]
    test_case_5 = [0,0,0,0,0]

    # check the test is equal to the hand calculated correct value
    assert get_seven_day_cases(test_case_1) == 437

    # check the test is equal to the hand calculated correct value
    assert get_seven_day_cases(test_case_2) == 234

    # check the test is equal to the hand calculated correct value
    assert get_seven_day_cases(test_case_3) == 355

    # check the test is equal to the hand calculated correct value
    assert get_seven_day_cases(test_case_4) == 79

    # check the test is equal to the hand calculated correct value
    assert get_seven_day_cases(test_case_5) == 0

from flaskr.covid_data_handler import COVID_DATA
from flaskr.covid_data_handler import update_covid_data
from flaskr.config import data as config_data
def test_update_covid_data() -> None:
    """
        test update_covid_data()

        testing critera:
            - 'local_7_day_cases' updated correctly
            - 'national_7_day_cases' updated correctly
            - 'national_current_hospital_cases' updated correctly
            - 'national_total_deaths' updated correctly
    """

    # check all covid data is initalised to 0
    assert COVID_DATA['local_7_day_cases'] == 0
    assert COVID_DATA['national_7_day_cases'] == 0
    assert COVID_DATA['national_current_hospital_cases'] == 0
    assert COVID_DATA['national_total_deaths'] == 0

    # update covid data
    update_covid_data()

    # check the data in COVID_DATA data structure is correct
    # see covid_data_check() docstring for more info
    covid_data_check()

from flaskr.covid_data_handler import schedule_covid_updates
from flaskr.covid_data_handler import scheduler
from flaskr.covid_data_handler import COVID_UPDATE_EVENTS
def test_schedule_covid_updates() -> None:
    """
        test schedule_covid_updates()

        NOTE: function will take over 3 seconds to run due to having to wait for
              event to trigger

        testing critera:
            - event queue empty before schedule
            - after event schedule, event added to event queue
            - event was added to COVID_UPDATE_EVENTS
            - event still in event queue after scheduler.run() before 3 seconds has passed
            - wait 3 seconds, run events again and check event was ran and event queue empty
            - triggered event removed event from COVID_UPDATE_EVENTS data structure
    """

    # check event queue is 0 before schedule event
    assert len(scheduler.SCHEDULER.queue) == 0

    # schedule a covid update with label 'test_update' to run in 3 seconds
    schedule_covid_updates(3, 'test_update')

    # check the event has been added to the event queue
    assert len(scheduler.SCHEDULER.queue) == 1

    # check the event has been added to the COVID_UPDATE_EVENTS data structure
    assert 'test_update' in COVID_UPDATE_EVENTS.keys()

    # run the scheduler
    scheduler.SCHEDULER.run(blocking=False)

    # check the event is still in the event queue (3 seconds not passed)
    assert len(scheduler.SCHEDULER.queue) == 1

    # sleep 3 seconds (wait for event to be valid)
    time.sleep(3)

    # run the scheduler
    scheduler.SCHEDULER.run(blocking=False)

    # check the event is not in the event queue (3 seconds passed)
    assert len(scheduler.SCHEDULER.queue) == 0

    # check the event triggered removed the event from COVID_UPDATE_EVENTS data structure
    assert 'test_update' not in COVID_UPDATE_EVENTS.keys()

    # check data in COVID_DATA data structure was updated correctly
    # see covid_data_check() docstring for more info
    covid_data_check()

from flaskr.covid_data_handler import remove_sheduler_covid_data_update_event
def test_remove_sheduler_covid_data_update_event() -> None:
    """
        test remove_sheduler_covid_data_update_event()

        testing critera:
            - add a covid update event, and remove it
            - removed covid event is removed from COVID_UPDATE_EVENTS data structure
            - function should be able to deal with keys that do not belong to an event
    """

    # check event queue is empty
    assert len(scheduler.SCHEDULER.queue) == 0

    # schedule a covid update (function allready tested)
    schedule_covid_updates(3, 'test_update')

    # check the event was added to the event queue
    assert len(scheduler.SCHEDULER.queue) == 1

    # check the event was added to COVID_UPDATE_EVENTS data structure
    assert 'test_update' in COVID_UPDATE_EVENTS.keys()

    # remove the event from the event queue
    remove_sheduler_covid_data_update_event('test_update')

    # check event was removed from event queue
    assert len(scheduler.SCHEDULER.queue) == 0

    # check event was removed from COVID_UPDATE_EVENTS data strucutre
    assert 'test_update' not in COVID_UPDATE_EVENTS.keys()

    # check the function can deal with non-existant event labels
    try:
        # run in try-except block, if exception triggered, function failed
        remove_sheduler_covid_data_update_event('not_test_update')
    except Exception as e:
        # exception caught, function failed to deal with non-existant labels
        assert 0
