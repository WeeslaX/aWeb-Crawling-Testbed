from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import os
from datetime import datetime
import argparse
import shutil
import yaml

# Initialise global variables
email = ''
pw = ''
root = ''
login_sleep_time = 0
page_forward_transition_sleep_time = 0
page_backward_transition_sleep_time = 0

# Variable to keep track of the screenshot count
screenshot_count = 0

# Hardcoded XPaths
xpath_email = '//*[@id="identifierId"]'
xpath_email_next = '//*[@id="identifierNext"]/div/button/span'
xpath_pw = '//*[@id="password"]/div[1]/div/div[1]/input'
xpath_pw_next = '//*[@id="passwordNext"]/div/button/span'

# Text file info
file_name = 'screenshot_urls.txt'
# Create the file path by appending the file name to the current directory
file_path = f'./{file_name}'

# Create new folder 'screenshots'
screenshot_dir = 'screenshots'

# Initialise Chrome Driver
driver = webdriver.Chrome()

# Core Methods
def setup(clear_flag):
    print("========================")
    # Print Transition Info:
    print("Page forward transition time set at: " + str(page_forward_transition_sleep_time) + " seconds")
    print("Page backwards transition time set at: " + str(page_backward_transition_sleep_time) + " seconds")
    # Print start timestamp
    start_time = datetime.now()
    print("Test started at:", start_time)    
    # Create a directory for saving screenshots
    os.makedirs(screenshot_dir, exist_ok=True)
    # Clear urls text file if --clear flag enabled
    ss_path = f"./{screenshot_dir}"
   
    if clear_flag:
        check_and_clear_file(file_path)
        clear_folder(ss_path)
    
    # Open a website using Selenium and ChromeDriver
    driver.get(root)
    
    print("========================")
    
    return start_time

def close(start_time):
    print("========================")
    # Print end timestamp
    end_time = datetime.now()
    print("Test ended at:", end_time)

    # Calculate duration in minutes
    duration = end_time - start_time
    duration_minutes = duration.total_seconds() / 60

    print("Test duration in minutes:", duration_minutes)
    print("========================")
    
def login():
    # Find email textbox element
    textbox = driver.find_element('xpath', xpath_email)
    # Type email
    textbox.send_keys(email)

    # Find and click the button element by XPath
    button = driver.find_element('xpath', xpath_email_next)
    button.click()

    # Wait for page to transition
    time.sleep(login_sleep_time)

    # Find pw textbox element
    textbox = driver.find_element('xpath', xpath_pw)
    textbox.send_keys(pw)
    # Find and click the button element by XPath
    button = driver.find_element('xpath', xpath_pw_next)
    button.click()

    time.sleep(login_sleep_time)

def process_page():
    global screenshot_count
    # Get the page source
    page_source = driver.page_source

    # Create a BeautifulSoup object with the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all div elements with the specified class and aria-label attribute
    folder_elements = soup.find_all('div', class_='KL4NAf')

    # Extract the folder names
    folder_names = []
    for element in folder_elements:
        aria_label = element.get('aria-label')
        if aria_label and aria_label.startswith('Google Drive Folder:'):
            folder_name = aria_label.replace('Google Drive Folder: ', '')
            folder_names.append(folder_name)
    
    # A page where there are no folders       
    if not folder_names:
        print("Transitioned to a page with only files, screenshot taken and saved in screenshots folder as screenshot" + str(screenshot_count) + ".png.")
        
        # Take a screenshot of the current page
        screenshot_path = f"./{screenshot_dir}/screenshot {screenshot_count}.png"
        driver.save_screenshot(screenshot_path)
        
        # Get the current URL
        current_url = driver.current_url
        
        # Map screenshot name to URL to the file
        with open(file_path, 'a') as file:
            file.write("screenshot "+ str(screenshot_count) + ": " + str(current_url) + "\n")
        
        screenshot_count = screenshot_count + 1
        
        runBack()
        return
        
    else:
        print("Transitioned to a page with the following folders: " + str(folder_names))
        # Double-click on an element not yet visited
        for folder_name in folder_names:
            element = driver.find_element(By.XPATH, f"//div[@aria-label='Google Drive Folder: {folder_name}']")
            actions = ActionChains(driver)
            actions.double_click(element)
            actions.perform()
            
            print("Selected: " + str(folder_name))
            
            # Wait for page to transition
            time.sleep(page_forward_transition_sleep_time)
            
            process_page()
            
        runBack()

# Helper Methods
def runBack():
    print("Going back to previous page.")
    # Return to previous page
    driver.back()
    # Wait for page to transition
    time.sleep(page_backward_transition_sleep_time)

def check_and_clear_file(file_path):
    # Check if the file exists
    if os.path.exists(file_path):
        # Check if the file is empty
        if os.path.getsize(file_path) == 0:
            print("The text file is empty.")
        else:
            print("The text file is not empty.")
        
        # Clear the file by opening it in write mode
        with open(file_path, 'w') as file:
            file.truncate(0)
            print("The text file has been cleared.")
    else:
        print("The file does not exist.")
            
def clear_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Iterate over all files and subfolders in the folder
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                # Remove the file
                os.remove(file_path)
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                # Remove the subfolder and its content
                shutil.rmtree(dir_path)
        print("Folder cleared successfully.")
    else:
        print("Folder does not exist.")

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

# For debugging purposes            
def page_printer():
    # Get the page source
    page_source = driver.page_source

    # Create a BeautifulSoup object with the page source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Print html
    print(soup)

if __name__ == '__main__':
    
    # YAML control
    # Load the configuration from the YAML file
    config = load_config('config.yaml')
    email = config['email']
    pw = config['pw']
    root = config['root']
    login_sleep_time = config['login_sleep_time']
    page_forward_transition_sleep_time = config['page_forward_transition_sleep_time']
    page_backward_transition_sleep_time = config['page_backward_transition_sleep_time']
    screenshot_count = config['screenshot_count']
    
    # Argument Control
    parser = argparse.ArgumentParser(description='GDrive Crawler')
    parser.add_argument('--clear', action='store_true', help='Clear urls text file and screenshot folder.')
    args = parser.parse_args()

    # Setup
    start_time = setup(args.clear)
    # Login
    login()
    # Recursive function to find all folders with only files
    process_page()
    # Closing
    close(start_time)

    # Wait for user input before closing the browser
    input("Press Enter to close the browser...")

    # Close the browser
    driver.quit()
