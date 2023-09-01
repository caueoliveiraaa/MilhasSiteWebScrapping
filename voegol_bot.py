from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

from destinations import DESTS_INTERNATIONAL, NOMES_SIGLAS
from general import GeneralFuncs as funcs
from voegol_bot_xpaths import xpaths
from emojis import EMOJIS

from datetime import datetime, timedelta
import os
import time
import pyautogui as p
import telegram_bot as bot 
import json
import sys


# actions = ActionChains(self.driver)
# actions.send_keys(Keys.DOWN)
# actions.send_keys(Keys.ENTER)


class VoeGolBot():
    def __init__(self) -> None:
        """ Handle driver and run bot """

        try:
            self.build_driver()
            self.main()
        except:
            funcs.display_error()
        finally:
            self.driver.close()


    def insert_data_homepage(self, data_insert: dict):
        """ Insert data into home page to search for tickets """

        for i in range(3):
            try:
                break
            except:
                funcs.display_error()


    def display_data(self, data: dict) -> None:
        """ Display data found in terminal"""

        ...


    def create_message_telegram(self, message_data: dict) -> str:
        """ Set up message to be sent to Telegram groups """

        return ''


    def validate_total_budget(self, total_value: str, limit_value: float) -> bool:
        """ Check if value found is lower than verification value """

        return True


    def get_data_from_current_page(self) -> dict:
        """ Extract data from page """

        return {}


    def insert_data_homepage(self, data_insert):
        """ Insert data into home page to search for tickets """

        for i in range(3):
            try:
                # Insert origin
                WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH, xpaths['input_origin'])))
                self.driver.find_element('xpath', xpaths['input_origin']).clear()
                self.driver.find_element('xpath', xpaths['input_origin']).send_keys(data_insert['str_origin'])
                WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dropdown-saindo-de"]/b2c-list-cta/div/ul/li')))
                self.driver.find_element('xpath', '//*[@id="dropdown-saindo-de"]/b2c-list-cta/div/ul/li').click()

                # .....

                self.driver.find_element('xpath', xpaths['input_destination']).send_keys(data_insert['str_destination'])
                print(f'Set up trip')

                # .....

                self.driver.find_element('xpath', xpaths['date_departure_click']).click()
                WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="departureDate{data_insert["date_departure"]}"]')))
                self.driver.find_element('xpath', f'//*[@id="departureDate{data_insert["date_departure"]}"]').click()
                print('Set up departure date')

                # .....
                
                self.driver.find_element('xpath', xpaths['date_return_click']).click()
                WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="departureDate{data_insert["date_return"]}"]')))
                self.driver.find_element('xpath', f'//*[@id="departureDate{data_insert["date_return"]}"]').click()
                print('Set up return date')
                break
            except:
                funcs.display_error()


    @funcs.measure_time
    def main(self) -> None:
        """ Run main script bot """
        os.system('cls')
        

        try:
            for index_main in range(1, 366):
                # search dates
                date_departure = datetime.now() + timedelta(days=index_main)
                date_return = datetime.now() + timedelta(days=(index_main + 7))


                try:
                    for key_index, value in DESTS_INTERNATIONAL.items(): 
                        cash_limit: float = value[2]

                        data_insert = {
                            'date_departure': date_departure.strftime("%d%m%Y"),
                            'date_return': date_return.strftime("%d%m%Y"),
                            'str_origin': value[0],
                            'str_destination': value[1],
                        }

                        print(f'\n{key_index + 1}º iteration with dates ', end=' ')
                        print(f'{date_departure.strftime("%d/%m/%Y")}', end=' ')
                        print(f'and {date_return.strftime("%d/%m/%Y")}')
                        print(f'Trip: {value[0]} -> {value[1]}')


                        try:
                            # open site
                            website_url = 'https://b2c.voegol.com.br/compra'
                            self.driver.get(website_url)
                            # insert data 
                            self.insert_data_homepage(data_insert)
                            

                            input('here')

                        except (KeyboardInterrupt, SystemExit):
                            exit()
                        except:     
                            funcs.display_error()

                except (KeyboardInterrupt, SystemExit):
                    exit()
                except:     
                    funcs.display_error()

        except (KeyboardInterrupt, SystemExit):
            print('Exited program')
            exit()
        except:
            funcs.display_error()


    def build_driver(self):
        """ Chrome / driver config """

        path_chrome = r'..\\driver_web\\chromedriver.exe'
        service = Service(executable_path=path_chrome)

        options = webdriver.ChromeOptions()
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable=popup-block')
        options.add_argument('--no-defaut-browser-check')
        # options.add_argument('--force-device-scale-factor=9.0')
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(service=service, options=options)


if __name__ == '__main__':
    bot = VoeGolBot()