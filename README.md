# Motivation
This is simple CLI to scrape Berlin's public holidays as a CSV. It is meant as no more and no less, and the purpose of this was simply because I wanted to automated this simple manual task.
Thanks to `https://publicholidays.de/berlin/` for providing this information in a clean and scrape-able way!

This package is "tread-at-your-own-risk!"  

# Usage
- Tested with python 3.7
- Install requirements via `pip install -r requirements.txt`
- Run from the command line via `python berlin_holidays_to_csv outfile.csv`
- Optionally, include specific years; default is running for all available years.
- Note: with few dependencies, this should run with earlier versions of Python3 as well and with other versions of the required packages. I included version numbers for reproducibility and since I haven't had the time to test + find minimal requirements.

# TODOs:
- real, non-trivial tests
- cleaner package structure...
