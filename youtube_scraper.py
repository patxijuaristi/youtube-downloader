# -*- coding: utf-8 -*-

import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from video import Video

class YoutubeScraper:

    def __init__(self, ruta):
        self.rutaFicheros = ruta
        self.driver = None
    
    def initDriver(self):
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            s=Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=s, options=chrome_options)
            self.driver.get('https://www.google.com/')            
            try:
                self.driver.find_element_by_xpath('//*[@id="L2AGLb"]').click()
            except:
                pass
            return True
        except Exception as e:
            print(e)
            print('Error with the Chrome Driver')
            return False
    
    def scrapearVideo(self, kw):
        video = Video(kw)
        try:
            time.sleep(2)
            url = 'https://www.youtube.com/results?search_query='+kw.replace(' ','+')
            self.driver.get(url)
            
            try:
                self.driver.implicitly_wait(5)
                enlace = self.driver.find_element_by_xpath('//*[@id="video-title"]').get_attribute('href')
                titulo = self.driver.find_element_by_xpath('//*[@id="video-title"]').text
                video.titulo = titulo
                video.url = enlace
                time.sleep(2)
            except Exception as e:
                print(e)
                print(' - Error with this keyword: '+kw+'. Retrying')
                pass
            return video
        except:
            print('Some error occurred')
            return None
    
    def endDriver(self):
        if(self.driver != None):
            self.driver.quit()
