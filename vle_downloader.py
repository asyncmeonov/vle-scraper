import os
import sys
import requests
import file_utils
import time
import math
import logging
from vle_connector import VLEConnector
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import argparse

logging.basicConfig(level=logging.INFO)

LOGIN_URL = "https://vle.york.ac.uk/"
conn = None

def download_all_videos(credentials):
    #initial login to VLE, acquiring a session cookie
    conn.driver.get(LOGIN_URL)
    conn.login(credentials)

    ## Get first page and login
    conn.driver.get('https://york.cloud.panopto.eu/Panopto/Pages/Sessions/List.aspx#isSharedWithMe=true&maxResults=464&page=0') #! non update agnostic (hardcoded pages)
    conn.login(credentials, True)
    
    WebDriverWait(conn.driver,10).until( #wait until all things are loaded
        EC.visibility_of_element_located((By.ID,'resultsDiv'))
    )
    table = conn.driver.find_element_by_id('detailsTable')
    rows = table.find_elements_by_tag_name('tr')
    
    WebDriverWait(conn.driver,5).until( #wait until all links are loaded
            EC.visibility_of_element_located((By.CLASS_NAME,'detail-title'))
    )
    ## loop through all the rows
    for row in rows:
        ### find all the download links
        link = row.find_element_by_class_name("detail-title")
        if(file_utils.is_downloaded(conn,link.text) != False):
            logging.warn(file_utils.is_downloaded(conn,link.text)+" already exists, skipping...")
        else:
            logging.info(5*'='+"Now looking at: " + link.text + 5*'=')
            href = link.get_attribute('href')
            #### and get their UUIDs
            uuid = href[href.index('id=') + 3 : href.index('id=')+39]
            logging.info("UUID: "+ uuid)

            ##### request to download that video and halt everything until it is downloaded
            conn.get_panopto_video_by_uuid(uuid)
            file_utils.download_wait(conn, 300)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("Downloader of Panopto Videos")
    arg_parser.add_argument('-u', dest ='username', help ='Enter your panopto username')
    arg_parser.add_argument('-p', dest='password', help ='Enter your password')
    arg_parser.add_argument('-PATH', dest='path', default='D:/PanoptoVideos/', help ='Enter the path to where the files will be downloaded to')

    args = arg_parser.parse_args()
    credentials = {'username': args.username, 'password':args.password}
    conn = VLEConnector(True, args.path) #If there is no such folder, the script will create one automatically
    try:
        download_all_videos(credentials)
    except KeyboardInterrupt:
        logging.warn("Keyboard Interrupt detected, stopping...")
    finally:
        if conn.driver is not None:
            conn.driver.close()
            conn.driver.quit()
            logging.info("Driver closed successfully.")