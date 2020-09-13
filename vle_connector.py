import os
from pathlib import Path
from pathlib import PureWindowsPath
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from uuid import UUID

class VLEConnector:
    def __init__(self, headless=True, downloadPath=None):
        self.headless = headless
        self.downloadPath = downloadPath
        self.driver = self.new_chrome_browser()
        print("Initialised a new driver with download path: "+ downloadPath)

    def new_chrome_browser(self):
        """ Helper function that creates a new Selenium browser """
        options = webdriver.ChromeOptions()
        prefs = {}
        prefs["download.prompt_for_download"] = False        
        if self.headless:
            options.add_argument('headless')
            options.add_argument('verbose')
        if self.downloadPath is not None:
            if not os.path.exists(Path(self.downloadPath)):
                os.makedirs(Path(self.downloadPath))
            prefs["download.default_directory"]=str(PureWindowsPath(self.downloadPath))
        
        options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(chrome_options=options) #usually executable_path should be set to driver.exe, but ours is on the PATH var
        return browser

    def login(self,credentials, is_panopto = False):
        if(is_panopto):
            try:
                self.driver.find_element_by_xpath('//*[@id="PageContentPlaceholder_loginControl_externalLoginButton"]').click()
                WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located((By.ID,'user_id')))
                username = self.driver.find_element_by_id("user_id")
                password = self.driver.find_element_by_id("password")

                username.send_keys(credentials.username)
                password.send_keys(credentials.password)

                self.driver.find_element_by_id('entry-login').click()
            except TimeoutException:
                pass
            
        else:
            self.driver.find_element_by_xpath("//p/a[1]/img[1]").click()

            username = self.driver.find_element_by_id("username")
            password = self.driver.find_element_by_id("password")
            
            username.send_keys(credentials['username'])
            password.send_keys(credentials['password'])

            self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div/div/form/div[3]/button").click()

    def get_panopto_video_by_uuid(self,uuid_string):
        UUID(uuid_string, version=4) #will throw an exception if UUID is invalid
        URL = "https://york.cloud.panopto.eu/Panopto/Podcast/Download/"+uuid_string+".mp4?mediaTargetType=videoPodcast"
        print("Now querying: "+URL)
        self.driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': str(PureWindowsPath(self.downloadPath))}}
        command_result = self.driver.execute("send_command", params)
        print(command_result)
        self.driver.get(URL)
       