import click
import csv
import datetime
import urllib.request, urllib.error
from bs4 import BeautifulSoup


def simple_get(url, verbose=False):
    try:
        request = urllib.request.Request(
            url,
            data=None,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
        response = urllib.request.urlopen(request, timeout=10)
        status = response.status
        if verbose:
            print(f"Status: {response.status}")
        content = response.read() if status == 200 else None
        return status, content

    except urllib.error.URLError as e:
        print(f"Error with request to {url}: {e}")
        return -1, e


def data_from_table(soup, attrs):
    data = []
    table = soup.find("table", attrs=attrs)
    tbody = table.find("tbody")
    col_names = [elt.text.strip() for elt in table.find_all("th")]
    rows = tbody.find_all("tr")
    # to grab only columnized data from table
    num_cols = None
    for row in rows:
        cols = row.find_all("td")
        cols = [elt.text.strip() for elt in cols]
        if num_cols is None:
            num_cols = len(cols)
        # don't append if not formatted properly (i.e. last column)
        if num_cols == len(cols):
            data.append([elt for elt in cols if elt])
    return col_names, data


def process_dates_inplace(row_dicts, year, iso_format=True):
    date_key = "Date"
    for row in row_dicts:
        # this is pretty much the whole point of the script
        assert (
            date_key in row.keys()
        ), "Website format has changed! Manual inspection required!"
        date_obj = datetime.datetime.strptime(row["Date"] + str(year), "%d %b%Y")
        if iso_format:
            date_obj = date_obj.isoformat()
        row[date_key] = date_obj
    return row_dicts


def row_lst_to_row_dicts(col_names, rows):
    # all rows must be of same length, and same as number of columns
    if len(rows):
        num_cols = len(col_names)
        assert not sum([not (len(row) == num_cols) for row in rows])
    return [{cname: elt for cname, elt in zip(col_names, row)} for row in rows]


def get_link_year(year):
    return f"https://publicholidays.de/berlin/{year}-dates/"


def get_bound_year(bound_type, max_year=3000, min_year=1990, verbose=False):
    # ping the link until we hit an error multiple times
    curr_year = 2019
    status = 200
    assert bound_type in ["max", "min"]
    while status == 200 and curr_year < max_year and curr_year > min_year:
        url = get_link_year(curr_year)
        status, content = simple_get(url, verbose=verbose)
        if status == -1:
            print(f"{content} raised, returning current year")
            if bound_type == "max":
                return curr_year - 1
            else:
                return curr_year + 1
        if bound_type == "max":
            curr_year += 1
        else:
            curr_year -= 1
    return curr_year


def get_min_year():
    # ping the link until we hit an error multiple times
    curr_year = 2019
    status = 200
    max_year = 3000
    while status == 200 and curr_year < max_year:
        url = get_link_year(curr_year)
        status, content = simple_get(url)
        if status == -1:
            print(f"{content} raised, returning current year")
            return curr_year - 1
        curr_year += 1
    return curr_year


def get_berlin_holidays(years):
    tbl_attrs = {"class": ("publicholidays", "phgtable")}
    holidays_data = []
    all_colnames = set()
    for year in years:
        print(f"Processing year {year}")
        url = get_link_year(year)
        status, content = simple_get(url)
        if content is not None:
            col_names, data = data_from_table(
                BeautifulSoup(content, "html.parser"), tbl_attrs
            )
            # tracking all column names that have appeared makes for easier null handling
            all_colnames.update(col_names)
            row_dicts = row_lst_to_row_dicts(col_names, data)
            row_dicts = process_dates_inplace(row_dicts, year)
            holidays_data.extend(row_dicts)

    return all_colnames, holidays_data


@click.command()
@click.argument("fpath_out", type=click.Path(exists=False))
@click.argument("years", nargs=-1, default=None)
def get_berlin_holidays_as_csv(fpath_out, years):
    if not years:
        # default to all years possible
        print("Getting range of valid years")
        min_year, max_year = get_bound_year("min"), get_bound_year("max")
        years = list(range(min_year, max_year + 1))
        print(f"Running for years {', '.join(str(y) for y in years)}")
    all_colnames, holidays_data = get_berlin_holidays(years)
    with open(fpath_out, "w") as csv_outfile:
        holidays_writer = csv.DictWriter(csv_outfile, fieldnames=sorted(all_colnames))
        holidays_writer.writerows(holidays_data)
