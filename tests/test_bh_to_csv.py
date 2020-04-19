import bh_to_csv
import datetime


def test_simple_get():
    test_url = "http://www.google.com"
    status, content = bh_to_csv.simple_get(test_url)
    assert status == 200
    assert content


def test_simple_get_bh_data():
    """ Provide a very simple means of running + debugging the core function. """
    # check that it works for the current year
    curr_year = datetime.datetime.now().year
    all_colnames, data = bh_to_csv.get_berlin_holidays([curr_year])
    assert "Date" in all_colnames


def test_get_bound_year():
    max_year = bh_to_csv.get_bound_year("max", verbose=True)
    min_year = bh_to_csv.get_bound_year("min", verbose=True)
    assert min_year < max_year
