from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

from destinations import DESTS_NATIONAL, NOMES_SIGLAS
from general import GeneralFuncs as funcs
from voeazul_bot_xpaths import xpaths
from emojis import EMOJIS
import telegram_bot as bot 
from print_colors import *

from datetime import datetime, timedelta
from typing import Tuple
import pyautogui as p
import os
import time
import json
import sys


class VoeAzulBot():
    def __init__(self) -> None:
        """ Handle driver and run bot """

        try:
            self.build_driver()
            self.main()
        except:
            funcs.display_error()
        finally:
            self.driver.close()


    def display_data(self, data: dict) -> None:
        """ Display data found in terminal"""

        print_cyan(f'{EMOJIS["checkMark"]} Extracted data: ')
        for key, value in data.items(): print_green(f'"{key}": "{value}"')


    def validate_total_budget(self, total_value: str, limit_value: float) -> bool:
        """ Check if value found is lower than verification value """

        total_value = total_value.replace('.', '')
        total_value = float(str(total_value).replace(',', '.').replace('R$', '').strip())
        print(f'\033[035mR$ {total_value} less than or equal to R$ {limit_value}: \033[0m', end=' ')
        print_cyan(f'{(total_value <= limit_value)}') if (total_value <= limit_value) else print_red(f'{(total_value <= limit_value)}')
        return (total_value <= limit_value)


    def get_total_value(self, value_1, value_2) -> float:
        """ Return the sum of both tickets' values """

        value_1 = value_1.replace('.', '')
        value_1 = float(str(value_1).replace(',', '.').replace('R$', '').strip()) 
        value_2 = value_2.replace('.', '')
        value_2 = float(str(value_2).replace(',', '.').replace('R$', '').strip()) 
        result = (value_1 + value_2)
        formatted_result = '{:,.2f}'.format(result)
        formatted_result = formatted_result.replace('.', ',', 1)
        return formatted_result
    

    # Finish
    def create_message_telegram(self, message_data: dict) -> str:
        """ Set up message to be sent to Telegram groups """

        return ''


    # Finish
    def get_data_from_current_page(self) -> dict:
        """ Extract data from page """

        return {}


    # Finish
    def insert_data_homepage(self, data_insert: dict):
        """ Insert data into home page to search for tickets """

        for i in range(3):
            try:
                self.driver.find_element('xpath', xpaths['departure_input']).clear()
                self.driver.find_element('xpath', xpaths['departure_input']).send_keys('GRU')



                break
            except:
                funcs.display_error()


    def click_accept_cookies(self):
        try:
            print('Searching for accept all cookies btn')
            WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH, xpaths['accept_all'])))
            self.driver.find_element('xpath', xpaths['accept_all']).click()
            print_green('Clicked accept all cookies btn')
        except:
            pass


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
                    for key_index, value in DESTS_NATIONAL.items():
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
                            website_url = 'https://www.voeazul.com.br/br/pt/home'
                            self.driver.get(website_url)
                            self.click_accept_cookies()
                            p.sleep(1)
                            
                            # insert data 
                            self.insert_data_homepage(data_insert={})



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
        options.add_argument('--force-device-scale-factor=0.9')
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=service, options=options)


if __name__ == '__main__':
    bot = VoeAzulBot()