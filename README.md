# OscarWorks Crawler
Welcome to the OscarWorks Crawler. 

This is a web crawler designed to crawl through Waterloo Works and/or Oscar Plus.

This project has been made because it is difficult to quickly find the jobs that have the matching keywords you want.

~~The WaterlooWorks Crawler is still an in-progress project. It does not work, but I will have it working once I get back on my study term.~~

The WaterlooWorks Crawler is COMPLETE!!! 

I still need to figure out a nice way for running both crawlers in parallel.
## What does it do?
Run it with:
~~~
python crawl.py -k keywords.csv --login auth.txt -o output_folder/ --waterloo
or
python crawl.py -k keywords.csv --login auth.txt -o output_folder/ --mcmaster --waterloo
~~~
This will run through all the job postings on Waterloo Works or Oscar Plus with your authentication and download all the job postings and descriptions of the jobs that contain the keywords in the _keywords.csv_ file

Running help with:
~~~
$ python crawl.py -h
~~~
Will get you help that looks like this:

~~~
OscarWorks Crawler (https://github.com/kunalchandan/OscarWorks_Crawler) is a
command line tool for extracting the job descriptions from Waterloo Works or
Oscar Plus (as of 2019 Feb) that contain the keywords specified in
keywords.csv the authorization to enter the sites is user provided in the
auth.txt file

optional arguments:
  -h, --help            show this help message and exit
  -k CSV_FILE, --keywords CSV_FILE
                        The keywords comma separated values file, default
                        value is "keywords.csv".
  -l LOGIN_FILE, --login LOGIN_FILE
                        The login file, default value is "auth.txt".
  -o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                        The output folder, default value is "query_find/".

Required Arguments:
  -m, --mcmaster        Flag specifies to log into McMaster's OscarPlus
  -w, --waterloo        Flag specifies to log into Waterloo's WaterlooWorks
~~~

# Requirements
```
pip install selenium bs4 httplib2
```
