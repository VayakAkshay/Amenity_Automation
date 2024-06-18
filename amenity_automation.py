import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from getting_date import get_after_month_date
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import re
import pandas as pd
from send_message import send_telegram_message

# Read the CSV file and drop the "Unnamed" column if it exists
df = pd.read_csv('mydata.csv').drop(columns=['Unnamed: 0'], errors='ignore')
print(df)
last_saved_date = list(df["Date"])[-1]

# Initialize WebDriver (this example uses Chrome)
service = Service(executable_path=r'/Users/akshay/Downloads/chromedriver-mac-x64-3/chromedriver')
options = webdriver.ChromeOptions()
options.page_load_strategy = 'none'
options.add_argument("--window-size=1920x1080")
# options.add_argument("--headless")
# options.add_argument('--no-sandbox')

driver = webdriver.Chrome(service=service, options=options)

driver.get("https://amenitypass.app/properties/kpq3hfxg595e962wda2acanff0/amenities/jvdthen1z106xdrsb36b2ptc4m")

scroll_script = """
var element = arguments[0];
var halfHeight = element.scrollHeight;
element.scrollTop = halfHeight;
"""

# Define the date range
date_format = "%A %B %d"
range_start_date = datetime.strptime("Monday July 01", date_format)
range_end_date = datetime.strptime("Wednesday July 31", date_format)

apartment = "50-0404"
passcode = "244628"
name = "Oliver"
phone = "8594203301"

def extract_time(time_str):
    match = re.search(r"(\d{1,2}:\d{2} [APM]{2})", time_str)
    return match.group(1) if match else None

def is_within_range(start_time_str, end_time_str, range_start, range_end):
    start_time = datetime.strptime(start_time_str, "%I:%M %p")
    end_time = datetime.strptime(end_time_str, "%I:%M %p")
    return range_start <= start_time <= range_end and range_start <= end_time <= range_end

# Wait until the element with class name "agenda" is present
try:
    telegram_message = "Pickleball Pass Booked\n"
    current_date, one_month_after_date = get_after_month_date()
    
    figure_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "agenda"))
    )
    time.sleep(3)

    article_element = driver.find_element(By.CSS_SELECTOR, "article.policy")
    driver.execute_script(scroll_script, article_element)
    time.sleep(1)
    driver.execute_script(scroll_script, article_element)
    time.sleep(1)

    ul_element = figure_element.find_element(By.CSS_SELECTOR, 'ul.dates')
    ul_element.click()
    time.sleep(3)
    
    all_lis = figure_element.find_elements(By.TAG_NAME, "li")
    
    all_dates = []
    all_link_elements = []
    for li in all_lis: 
        try: 
            link_element = li
            date_text = li.find_element(By.TAG_NAME, "a").find_element(By.TAG_NAME, "time").get_attribute("innerText")
            all_dates.append(date_text)
            all_link_elements.append(link_element)
        except Exception as e:
            print(e)
            continue
    
    if all_dates:
        found_date = all_dates[-1]
        link_of_element = all_link_elements[-1]
        
        found_date_obj = datetime.strptime(found_date, date_format)
        
        if range_start_date <= found_date_obj <= range_end_date:
            if found_date != last_saved_date:
                telegram_message += "Date: " + found_date + "\n"
                actions = ActionChains(driver)
                actions.move_to_element(ul_element).perform()
                driver.execute_script(scroll_script, article_element)
                time.sleep(1)
                link_element.click()
                time.sleep(2)
                
                available_slots_elements = figure_element.find_elements(By.CSS_SELECTOR, "data.available")
                available_slots = []
                time.sleep(4)
                for available_slot in available_slots_elements:
                    if available_slot.get_attribute("value") == "1":
                        available_slots.append(available_slot)
                
                all_time_elements = []
                all_upper_elements = []
                all_bottom_elements = []
                all_radio_button_elements = []
                for time_element in available_slots:
                    parent_element = time_element.find_element(By.XPATH, "..")
                    grandparent_element = parent_element.find_element(By.XPATH, "..")
                    all_time_elements.append(grandparent_element)
                    upper_element = grandparent_element.find_element(By.XPATH, "preceding-sibling::*[1]")
                    bottom_element = grandparent_element.find_element(By.XPATH, 'following-sibling::*[1]')
                    radio_element = parent_element.find_element(By.XPATH, 'following-sibling::*[1]')
                    all_upper_elements.append(upper_element)
                    all_bottom_elements.append(bottom_element)
                    all_radio_button_elements.append(radio_element)
                
                start_times = []
                end_times = []
                for i in range(len(all_upper_elements)):
                    start_times.append(all_upper_elements[i].get_attribute("innerText"))
                    end_times.append(all_bottom_elements[i].get_attribute("innerText"))
                
                cleaned_start_times = [extract_time(time) for time in start_times if extract_time(time)]
                cleaned_end_times = [extract_time(time) for time in end_times if extract_time(time)]
                filtered_times = [(start, end) for start, end in zip(cleaned_start_times, cleaned_end_times) if is_within_range(start, end, range_start, range_end)]
                
                if filtered_times:
                    first_time_range = filtered_times[0]
                    telegram_message += f"Time: {first_time_range}\nApartment: {apartment}\nPasscode: {passcode}\nName: {name}\nPhone: {phone}"
                    filtered_time_start = first_time_range[0]
                    filtered_time_end  = first_time_range[1]
                    index_of_element = start_times.index(filtered_time_start)
                    radio_button = all_radio_button_elements[index_of_element]
                    radio_button.click()
                    time.sleep(3)
                    footer_elements = driver.find_elements(By.TAG_NAME, "footer")
                    footer_element = footer_elements[1]
                    footer_button_element = footer_element.find_element(By.TAG_NAME, "a")
                    footer_button_element.click()
                    time.sleep(3)
                    apartment_label_element = driver.find_element(By.XPATH, '//label[contains(text(), "Apartment")]')
                    apartment_input_field = apartment_label_element.find_element(By.XPATH, "following-sibling::*[1]")
                    apartment_input_field.send_keys(apartment)
                    time.sleep(1)

                    passcode_label_element = driver.find_element(By.XPATH, '//label[contains(text(), "Passcode")]')
                    passcode_input_field = passcode_label_element.find_element(By.XPATH, "following-sibling::*[1]")
                    passcode_input_field.send_keys(passcode)
                    time.sleep(1)

                    name_label_element = driver.find_element(By.XPATH, '//label[contains(text(), "Name")]')
                    name_input_field = name_label_element.find_element(By.XPATH, "following-sibling::*[1]")
                    name_input_field.send_keys(name)
                    time.sleep(1)

                    phone_label_element = driver.find_element(By.XPATH, '//label[contains(text(), "Phone")]')
                    phone_input_field = phone_label_element.find_element(By.XPATH, "following-sibling::*[1]")
                    phone_input_field.send_keys(phone)

                    new_article_element = driver.find_element(By.CSS_SELECTOR, "article.policy")
                    driver.execute_script(scroll_script, new_article_element)
                    time.sleep(1)
                    driver.execute_script(scroll_script, new_article_element)
                    time.sleep(1)
                    driver.execute_script(scroll_script, new_article_element)

                    permission_element = driver.find_element(By.ID, "permit-agreement")
                    permission_element.click()
                    time.sleep(1)

                    new_footer_element = driver.find_elements(By.TAG_NAME, "footer")[0]
                    get_pass_btn = new_footer_element.find_element(By.TAG_NAME, "button")
                    get_pass_btn.click()

                    add_data = {
                        "Date": found_date
                    }

                    df.loc[len(df)] = add_data
                    df.to_csv("mydata.csv", index=False)
                    send_telegram_message(telegram_message)
                    time.sleep(2)
                else:
                    print("No item found in given time range")
            else:
                print("Already Booked for this date")
        else:
            print("Date not in range")
    print("Element found")
except Exception as e:
    print(e)
    print("Element not found")

# Close the browser
driver.quit()
