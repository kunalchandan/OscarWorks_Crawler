from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


password = '--'
username = '--'
postings_url = "https://www.oscarplusmcmaster.ca/myAccount/jobPostings/general/postings.htm"


def login(user_id, pin, web_driver):
    field = web_driver.find_element_by_id("user_id")
    field.send_keys(user_id)

    field = web_driver.find_element_by_id("pin")
    field.send_keys(pin)

    field.send_keys(Keys.RETURN)


def go_to_postings(web_driver):
    web_driver.get(postings_url)
    web_driver.find_element_by_link_text("View all available postings").click()


def gather_postings(web_driver):
    pattern = re.compile("posting[0-9]{4,}")

    src = web_driver.page_source
    matches = pattern.findall(src)
    matches = list(set(str(i) for i in matches))
    return matches


def main():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://cap.mcmaster.ca/mcauth/login.jsp?app_id=783&app_name=orbis")

    login(username, password, driver)
    go_to_postings(driver)
    matches = gather_postings(driver)
    counter = 0
    runnable = True
    while runnable:
        total = driver.find_elements_by_css_selector("span[class='badge badge-info']")
        print total.text
        time.sleep(90)
        for _ in range(counter):
            step_forward = driver.find_element_by_link_text('»')
            step_forward.click()
            time.sleep(.5)
        for each in matches:
            each = each[7:]
            driver.get('{}?action=displayPosting&postingId={}&npfGroup='.format(postings_url, each))
            # print postings_url + ('?action=displayPosting&postingId={}&npfGroup='.format(each))
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
