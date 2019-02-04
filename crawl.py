from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import argparse
import os


oscar_postings_url = "https://www.oscarplusmcmaster.ca/myAccount/jobPostings/general/postings.htm"


def define_parser():
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


def define_driver_oscar():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://cap.mcmaster.ca/mcauth/login.jsp?app_id=783&app_name=orbis")
    return driver


def define_driver_works():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://cas.uwaterloo.ca/cas/login?service=https://waterlooworks.uwaterloo.ca/waterloo.htm")
    return driver


def retrieve_auth(args):
    location = '{}\\{}'.format(os.path.dirname(os.path.realpath(__file__)), args.login)
    try:
        f = open(location, 'r')
        use = f.readline().split('=')[1].strip()
        pas = f.readline().split('=')[1].strip()
    except IOError:
        print 'ERROR:: {} file not found, does it have the wrong name? or does it even exist?'.format(args.login)
    return use, pas


def retrieve_keywords(args):
    location = '{}\\{}'.format(os.path.dirname(os.path.realpath(__file__)), args.keywords)
    try:
        f = open(location, 'r')
        contents = f.read().replace('\n', ',')
        contents.strip(',')
        contents.split(',')
    except IOError:
        print 'ERROR:: {} file not found, does it have the wrong name? or does it even exist?'.format(args.login)
    return contents


def go_to_nth_page(web_driver, counter):
    # STEP THROUGH TO Nth PAGE
    for _ in range(counter):
        step_forward = web_driver.find_element_by_link_text('\xc2')
        step_forward.click()
        time.sleep(.5)


def go_to_postings(web_driver):
    web_driver.get(oscar_postings_url)
    web_driver.find_element_by_link_text("View all available postings").click()


def login(user_id, pin, web_driver):
    field = web_driver.find_element_by_id("user_id")
    field.send_keys(user_id)

    field = web_driver.find_element_by_id("pin")
    field.send_keys(pin)

    field.send_keys(Keys.RETURN)


def gather_postings(web_driver):
    pattern = re.compile("posting[0-9]{4,}")

    src = web_driver.page_source
    matches = pattern.findall(src)
    matches = list(set(str(i) for i in matches))
    return matches


def get_total_postings(driver):
    total = driver.find_element_by_css_selector("span[class='badge badge-info']")
    return int(total.text)


def save_posting(args, description, job_id, job_name):
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
            print 'ERROR:: There was some problem in making the output folder? Please create it manually and/or make ' \
                  'sure you have Read/Write Access'
            raise OSError('Refer to message above')


def main():
    args = define_parser().parse_args()
    if args.mcmaster:
        driver = define_driver_oscar()
    if args.waterloo:
        driver = define_driver_works()
    if not (args.mcmaster or args.waterloo):
        raise SyntaxError('You have not specified which site to log into')
    # TODO:: Complete defintions for waterloo works
    # TODO:: Consider redesigning code for parallel login of both systems

    keywords = retrieve_keywords(args)

    # GET LOGIN
    username, password = retrieve_auth(args)
    # LOGIN
    login(username, password, driver)
    # GET TO POSTINGS
    go_to_postings(driver)

    total = get_total_postings(driver)
    # STEP THROUGH EACH POSTING
    counter = 0
    while counter*100 < total:
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
            description = ''
            for table in tables:
                description += '\n' + table.text.encode('ascii', 'ignore')
            if any(keys in description for keys in keywords):
                # Save job to output folder
                print 'lel, this job aight; Posting ID: {}'.format(each_id)
                print job_name
                job_name = (''.join(e for e in job_name if e.isalnum())).encode('ascii', 'ignore').strip()

                save_posting(args, description, each_id, job_name)
        go_back = driver.find_element_by_link_text('Back to Search Results')
        go_back.send_keys(Keys.ENTER)
        counter += 1
        print 'Finished Page {}'.format(counter)
    # Parsing strings can be avoided since all links match pattern
    # element = driver.find_element_by_id(matches[0])
    # inner_html = element.get_attribute('innerHTML')
    # print inner_html

    time.sleep(5)
    driver.close()

# https://www.oscarplusmcmaster.ca/myAccount/jobPostings/general/postings.htm?action=displayPosting&postingId=101926&npfGroup=


if __name__ == "__main__":
    main()
