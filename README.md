# OscarWorks Crawler
Welcome to the OscarWorks Crawler. 

This is a web crawler designed to crawl through Waterloo Works and/or Oscar Plus.

This project has been made because it is difficult to quickly find the jobs that have the matching keywords you want.

## What does it do?
Run it with:
~~~
python crawl.py -k keywords.csv --auth auth.txt -o output_folder/ --waterloo
or
python crawl.py -k keywords.csv --auth auth.txt -o output_folder/ --mcmaster --waterloo
~~~
This will run through all the job postings on Waterloo Works or Oscar Plus with your authentication and download all the job postings and descriptions of the jobs that contain the keywords in the _keywords.csv_ file
# Requirements
```
pip install selenium bs4 httplib2
```