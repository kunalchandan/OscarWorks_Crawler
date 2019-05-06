from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import argparse
import os

from typing import List

Login = List[str]
Keywords = List[str]

OSCAR: str = 'OSCAR'
WORKS: str = 'WORKS'

oscar_home_url: str = "https://cap.mcmaster.ca/mcauth/login.jsp?app_id=783&app_name=orbis"
water_home_url: str = "https://cas.uwaterloo.ca/cas/login?service=https://waterlooworks.uwaterloo.ca/waterloo.htm"

oscar_postings_url: str = "https://www.oscarplusmcmaster.ca/myAccount/jobPostings/general/postings.htm"
water_postings_url: str = "https://waterlooworks.uwaterloo.ca/myAccount/co-op/coop-postings.htm"


def define_parser() -> argparse.ArgumentParser:
    # Define CLI Parser arguments
    parser = argparse.ArgumentParser(
        description='OscarWorks Crawler (https://github.com/kunalchandan/OscarWorks_Crawler) is a command line tool '
                    'for extracting the job descriptions from Waterloo Works or Oscar Plus (as of 2019 Feb) '
                    'that contain the keywords specified in keywords.csv the authorization to enter the sites is user '
                    'provided in the auth.txt file')
    req = parser.add_argument_group('Required Arguments')

    parser.add_argument('-k', '--keywords',
                        help='The keywords comma separated values file, default value is "keywords.csv".',
                        default='keywords.csv',
                        metavar='CSV_FILE')
    parser.add_argument('-l', '--login',
                        help='The login file, default value is "auth.txt".',
                        default='auth.txt',
                        metavar='LOGIN_FILE')
    parser.add_argument('-o', '--output-folder',
                        help='The output folder, default value is "query_find/".',
                        default='query_find\\',
                        metavar='OUTPUT_FOLDER')
    req.add_argument('-m', '--mcmaster',
                     help='Flag specifies to log into McMaster\'s OscarPlus',
                     action='store_true')
    req.add_argument('-w', '--waterloo',
                     help='Flag specifies to log into Waterloo\'s WaterlooWorks',
                     action='store_true')
    return parser


def define_driver(site: str) -> webdriver:
    driver = webdriver.Chrome(ChromeDriverManager().install())
    if site == OSCAR:
        driver.get(oscar_home_url)
    elif site == WORKS:
        driver.get(water_home_url)
    return driver


def retrieve_auth(args: argparse.Namespace) -> Login:
    location = '{}\\{}'.format(os.path.dirname(os.path.realpath(__file__)), args.login)
    try:
        f = open(location, 'r')
        use = f.readline().split('=')[1].strip()
        pas = f.readline().split('=')[1].strip()
    except IOError:
        raise IOError('ERROR:: {} file not found, does it have a wrong name? or does it even exist?'.format(args.login))
    return [use, pas]


def retrieve_keywords(args: argparse.Namespace) -> Keywords:
    location = '{}\\{}'.format(os.path.dirname(os.path.realpath(__file__)), args.keywords)
    try:
        f = open(location, 'r')
        contents = f.read().replace('\n', ',')
        contents.strip(',')
        contents = contents.split(',')
    except IOError:
        raise IOError('ERROR:: {} file not found, does it have a wrong name? or does it exist?'.format(args.keywords))
    return contents


def go_to_nth_page(web_driver: webdriver, counter: int) -> None:
    # STEP THROUGH TO Nth PAGE
    for _ in range(counter):
        # \xc2 is used because python is in utf-8 encoding.
        step_forward = web_driver.find_element_by_link_text('\xc2')
        step_forward.click()
        time.sleep(.5)


def go_to_postings(web_driver: webdriver, site: str) -> None:
    if site == OSCAR:
        web_driver.get(oscar_postings_url)
        web_driver.find_element_by_link_text("View all available postings").click()
    if site == WORKS:
        web_driver.get(water_postings_url)
        web_driver.find_element_by_link_text("View all available postings").click()


def login(user_id: str, pin: str, site: str, web_driver: webdriver) -> None:
    if site == OSCAR:
        field = web_driver.find_element_by_id("user_id")
        field.send_keys(user_id)

        field = web_driver.find_element_by_id("pin")
        field.send_keys(pin)

        field.send_keys(Keys.RETURN)
    if site == WORKS:
        field = web_driver.find_element_by_id("user_id")
        field.send_keys(user_id)

        field = web_driver.find_element_by_id("pin")
        field.send_keys(pin)

        field.send_keys(Keys.RETURN)


def gather_postings(web_driver: webdriver) -> Keywords:
    pattern = re.compile("posting[0-9]{4,}")

    src = web_driver.page_source
    matches = pattern.findall(src)
    matches = list(set(str(i) for i in matches))
    return matches


def get_total_postings(driver: webdriver) -> int:
    total = driver.find_element_by_css_selector("span[class='badge badge-info']")
    return int(total.text)


def save_posting(args: argparse.Namespace, description: str, job_id: str, job_name: str) -> None:
    try:
        location = '{}\\{}{}-{}.txt'.format(os.path.dirname(os.path.realpath(__file__)),
                                            args.output_folder,
                                            job_id,
                                            job_name)
        output = open(location, 'w+')
        output.write(description)
        output.close()
    except IOError:
        try:
            os.mkdir('{}\\{}'.format(os.path.dirname(os.path.realpath(__file__)), args.output_folder))
        except (IOError, OSError):
            print('ERROR:: There was some problem in making the output folder? Please create it manually and/or make ' \
                  'sure you have Read/Write Access')
            raise OSError('Refer to message above')


def main():
    args = define_parser().parse_args()
    if not (args.mcmaster or args.waterloo):
        raise SyntaxError('You have not specified which site to log into')
    driver = ''
    if args.mcmaster:
        driver = define_driver(OSCAR)
    if args.waterloo:
        driver = define_driver(WORKS)
    # TODO:: Complete definitions  for waterloo works
    # TODO:: Consider redesigning code for parallel login of both systems

    # GET KEYWORDS
    keywords = retrieve_keywords(args)
    # GET LOGIN
    username, password = retrieve_auth(args)

    # LOGIN
    if args.mcmaster:
        login(username, password, OSCAR, driver)
        # GET TO POSTINGS
        go_to_postings(driver, OSCAR)
    if args.waterloo:
        login(username, password, WORKS, driver)
        # GET TO POSTINGS
        go_to_postings(driver, WORKS)

    total = get_total_postings(driver)
    # STEP THROUGH EACH POSTING
    counter: int = 0
    while counter * 100 < total:
        go_to_nth_page(driver, counter)

        # GATHER POSTING IDS ON PAGE
        matches = gather_postings(driver)

        # STEP THROUGH POSTINGS ON PAGE
        for each_id in matches:
            each_id = each_id[7:]
            driver.get('{}?action=displayPosting&postingId={}&npfGroup='.format(oscar_postings_url, each_id))
            # SEE IF PAGE CONTAINS ANYTHING FROM KEYWORDS
            tables = driver.find_elements_by_css_selector("table[class='table table-bordered']")
            job_name = driver.find_element_by_class_name('span7').text.replace('\n', ' ').strip('.')
            description: str = ''
            for table in tables:
                description += '\n' + str(table.text.encode('ascii', 'ignore'))
            if any(keys in description for keys in keywords):
                # Save job to output folder
                print('lel, this job aight; Posting ID: {}'.format(each_id))
                print(job_name)
                job_name = (''.join(e for e in job_name if e.isalnum())).encode('ascii', 'ignore').strip()

                save_posting(args, description, each_id, str(job_name))
        go_back = driver.find_element_by_link_text('Back to Search Results')
        go_back.send_keys(Keys.ENTER)
        counter += 1
        print('Finished Page {}'.format(counter))
    # Parsing strings can be avoided since all links match pattern
    # element = driver.find_element_by_id(matches[0])
    # inner_html = element.get_attribute('innerHTML')
    # print inner_html

    time.sleep(5)
    driver.close()


if __name__ == "__main__":
    main()
