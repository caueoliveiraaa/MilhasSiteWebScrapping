from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

from destinations import NOMES_SIGLAS
from destinations_miles import NATIONAL_MILES
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
import re


class TotalAzulBot():
    def __init__(self) -> None:
        """ Handle driver and run bot """

        try:
            self.main()
        except:
            funcs.display_error()


    def display_data(self, data: dict) -> None:
        """ Display data found in terminal"""

        if data:
            print_cyan(f'{EMOJIS["checkMark"]} Extracted data: ')
            for key, value in data.items(): print_green(f'"{key}": "{value}"')


    def get_json_data(self) -> dict:
        json_data: dict = {}
        with open('bot_info.json', 'r') as json_file:
            json_data = json.load(json_file)

        return json_data
    

    def validate_total_budget(self, total_value: str, limit_value: float) -> bool:
        """ Check if value found is lower than verification value """

        total_value = str(total_value).replace('.', '').strip()
        total_value = int(total_value)
        print(f'\033[035mR$ {total_value} less than or equal to R$ {limit_value}: \033[0m', end=' ')
        print_cyan(f'{(total_value <= limit_value)}') if (total_value <= limit_value) else print_red(f'{(total_value <= limit_value)}')
        return (total_value <= limit_value)


    def get_total_value(self, value_1, value_2) -> float:
        """ Return the sum of both tickets' values """

        value_1 = value_1.replace('.', '')
        value_1 = int(value_1)
        value_2 = value_2.replace('.', '')
        value_2 = int(value_2)
        return (value_1 + value_2)
    

    def create_message_telegram(self, data_telegram: dict) -> str:
        """ Set up message to be sent to Telegram groups """

        try:
            message = f"{EMOJIS['botHead']} Olá. Seguem dados da passagem aérea:\n\n"
            message += f"{EMOJIS['earthGlobeAmericas']} Origem:   {data_telegram['origem']}\n"
            message += f"{EMOJIS['calendar']} Ida:  {data_telegram['data_ida']}\n"
            message += f"{EMOJIS['wallClock']} Hora de Saída:   {data_telegram['ida_hora_saida']} hrs\n"   
            message += f"{EMOJIS['wallClock']} Hora de Chegada:   {data_telegram['ida_hora_chegada']} hrs\n"
            message += f"{EMOJIS['earthGlobeAfrica']} Destino:   {data_telegram['destino']}\n"
            message += f"{EMOJIS['calendar']} Volta:  {data_telegram['data_volta']}\n"
            message += f"{EMOJIS['wallClock']} Hora de Saída:   {data_telegram['volta_hora_saida']} hrs\n"
            message += f"{EMOJIS['wallClock']} Hora de Chegada:   {data_telegram['volta_hora_chegada']} hrs\n\n"
            message += f"{EMOJIS['moneyBag']} Milhas por pessoa:   {data_telegram['milhas_pessoa']}\n"
            message += f"{EMOJIS['moneyBag']} Milhas pacote:   {data_telegram['milhas_pacote']}\n"
            message += f"{EMOJIS['earthGlobeEuropeAfrica']} Link: {data_telegram['link_ticket']}"
            return message
        except:
            funcs.display_error()


    def delete_via_actions(self):
        actions = ActionChains(self.driver)
        for i in range(50):
            actions.send_keys(Keys.BACKSPACE)
            actions.send_keys(Keys.DELETE)
        actions.perform()


    def select_via_actions(self):
        actions = ActionChains(self.driver)
        # actions.send_keys(Keys.DOWN)
        actions.send_keys(Keys.ENTER)
        actions.perform()


    def insert_data_into_page(self, data_insert) -> bool:
        for i in range(5):
            try:
                # click options of payment
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="main"]/div[1]/div/div/div[2]/div/div/div/div/div/div/div/div[2]/div[1]/div[1]/div/div/div/div/div/i')))
                self.driver.find_element('xpath', f'//*[@id="main"]/div[1]/div/div/div[2]/div/div/div/div/div/div/div/div[2]/div[1]/div[1]/div/div/div/div/div/i').click()
                p.sleep(0.2)
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.UP)
                actions.send_keys(Keys.UP)
                actions.send_keys(Keys.ENTER)
                actions.perform()
                print('Selected points')

                # inform origin
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="flights-booking-id-1-input"]')))
                self.driver.find_element('xpath', f'//*[@id="flights-booking-id-1-input"]').send_keys(data_insert['str_origin'])
                self.select_via_actions()
                print('Informed trip origin')

                # inform destination
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="flights-booking-id-2-input"]')))
                self.driver.find_element('xpath', f'//*[@id="flights-booking-id-2-input"]').send_keys(data_insert['str_destination'])
                self.select_via_actions()
                print('Informed trip destination')

                # open dates
                self.driver.find_element('xpath', f'//*[@id="headlessui-popover-button-16"]/div/div/div/div/div/div').click()
                p.sleep(0.7)

                # inform departure date
                self.driver.find_element('xpath', f'//*[@id="headlessui-popover-panel-18"]/div/div[1]/div[1]/div/div/div/div/div/div/div/input').click()
                self.delete_via_actions()
                self.driver.find_element('xpath', f'//*[@id="headlessui-popover-panel-18"]/div/div[1]/div[1]/div/div/div/div/div/div/div/input').send_keys(data_insert['date_departure'].strftime('%d/%m/%Y'))
                print('Informed first date')

                # inform return date
                self.driver.find_element('xpath', f'//*[@id="headlessui-popover-panel-18"]/div/div[1]/div[2]/div/div/div/div/div/div/div/input').click()
                self.delete_via_actions()
                self.driver.find_element('xpath', f'//*[@id="headlessui-popover-panel-18"]/div/div[1]/div[2]/div/div/div/div/div/div/div/input').send_keys(data_insert['date_return'].strftime('%d/%m/%Y'))
                print('Informed second date')
                p.sleep(0.7)

                # click concluido
                self.driver.find_element('xpath', f'//*[@id="headlessui-popover-panel-18"]/div/div[3]/div/button[2]').click()
                print('Clicked concluido btn')

                # click search
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="main"]/div[1]/div/div/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/div[3]/button')))
                self.driver.find_element('xpath', f'//*[@id="main"]/div[1]/div/div/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/div[3]/button').click()
                print('Clicked search btn')

                return True
            except:
                funcs.display_error()
                self.driver.refresh()
                self.driver.refresh()
                self.driver.refresh()
                p.sleep(2)

        return False


    def extract_times(self, input_string):
        pattern = r'\b\d{2}:\d{2}\b'
        times = re.findall(pattern, input_string)
        if len(times) == 2:
            return tuple(times)
        else:
            return None


    def get_data_from_current_page(self) -> dict:
        """ Extract trip data from current departure/return page """

        found_data = False
        data_extracted = {}

        for i in range(20):
            print(f'Searching for results {i + 1}')
            p.sleep(2)

            try:
                try:
                    # click accept all cookies
                    self.driver.find_element('xpath', f'//*[@id="onetrust-accept-btn-handler"]').click()
                    print('clicked accept all cookies')
                except:
                    pass

                text = self.driver.find_element('xpath', f'//*[@id="results-list"]/div[2]/div').text
                if 'Não há pacotes' in text:
                    print_yellow('No tickets for this trip')
                    return data_extracted, found_data
                
                departure_times = self.driver.find_element('xpath', f'//*[@id="main-content"]/div/div[2]/div[1]/div/div/div/article/section[1]/div/div[1]/div[1]/div[1]/div[1]/div[1]').text
                return_times = self.driver.find_element('xpath', f'//*[@id="main-content"]/div/div[2]/div[1]/div/div/div/article/section[1]/div/div[1]/div[1]/div[1]/div[2]/div[1]').text
                person_price = self.driver.find_element('xpath', f'//*[@id="main-content"]/div/div[2]/div[1]/div/div/div/article/section[2]/div[1]/div[1]/div/span').text
                package_price = self.driver.find_element('xpath', f'//*[@id="main-content"]/div/div[2]/div[1]/div/div/div/article/section[2]/div[1]/div[2]/div[2]/span[1]').text

                data_extracted['milhas_ida_pessoal'] = str(person_price).replace('Pontos', '')
                data_extracted['milhas_ida_pacote'] = str(package_price).replace('Pontos', '')

                times_departure = self.extract_times(departure_times)
                times_return = self.extract_times(return_times)

                data_extracted['ida_hora_saida'] = times_departure[0]
                data_extracted['ida_hora_chegada'] = times_departure[1]
                data_extracted['volta_hora_saida'] = times_return[0]
                data_extracted['volta_hora_chegada'] = times_return[1]

                found_data = True
                break
            except:
                p.sleep(1)

        return data_extracted, found_data


    @funcs.measure_time
    def main(self) -> None:
        """ Run main script bot """

        os.system('cls')
        json_data = self.get_json_data()

        """ Chrome / driver config """
        path_chrome = r'..\\driver_web\\chromedriver.exe'
        service = Service(executable_path=path_chrome)
        options = webdriver.ChromeOptions()
        # gecko_driver_path = r'..\\driver_web\\geckodriver.exe'
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable=popup-block')
        options.add_argument('--no-defaut-browser-check')
        options.add_argument('--force-device-scale-factor=0.6')
        # options.add_argument('--headless')


        for index_main in range(1, 185):
            # search dates
            date_departure = datetime.now() + timedelta(days=index_main)
            date_return = datetime.now() + timedelta(days=(index_main + 7))

            for key_index, value in NATIONAL_MILES.items():
                data_insert = {
                    'date_departure': date_departure,
                    'date_return': date_return,
                    'str_origin': value[0],
                    'str_destination': value[1],
                }

                print(f'\n{key_index + 1}º iteration of 185 with dates: ', end=' ')
                print(f'{date_departure.strftime("%d/%m/%Y")}', end=' ')
                print(f'and {date_return.strftime("%d/%m/%Y")}')
                print(f'{key_index + 1}º trip of {len(NATIONAL_MILES)}: {value[0]} -> {value[1]}')
                miles_limit: int = value[2]

                try:
                    with webdriver.Chrome(service=service, options=options) as driver:
                        # base_url = "https://tudoazul.azulviagens.com.br/"
                        self.driver = driver
                        base_url = "https://passagens.voeazul.com.br/pt/melhores-ofertas"
                        self.driver.get(base_url)

                        if self.insert_data_into_page(data_insert) is True:

                            #########################
                            p.alert('extract')
                            #########################

                            # FIX EXTRACTION AND AJUST DATA

                            data_extracted, found_data = self.get_data_from_current_page()

                            if found_data is True:
                                data_telegram = {
                                    'milhas_pessoa': data_extracted['milhas_ida_pessoal'],
                                    'milhas_pacote': data_extracted['milhas_ida_pacote'],
                                    'origem': data_insert['str_origin'],
                                    'data_ida': data_insert['date_departure'].strftime("%d/%m/%Y"),
                                    'ida_hora_saida': (data_extracted['ida_hora_saida'] + ' horas'),
                                    'ida_hora_chegada': (data_extracted['ida_hora_chegada'] + ' horas'),
                                    'destino': data_insert['str_destination'],
                                    'data_volta': data_insert['date_return'].strftime("%d/%m/%Y"),
                                    'volta_hora_saida': (data_extracted['volta_hora_saida'] + ' horas'),
                                    'volta_hora_chegada': (data_extracted['volta_hora_chegada'] + ' horas'),
                                    'link_ticket': self.driver.current_url,
                                }

                                # Send message to Telegram
                                bot_message = self.create_message_telegram(data_telegram)

                                #########################
                                p.alert(f'{bot_message}')
                                #########################

                                if (self.validate_total_budget(data_telegram['milhas_pessoa'], miles_limit) is True
                                or self.validate_total_budget(data_telegram['milhas_pacote'], miles_limit) is True):

                                    #########################
                                    p.alert('send')
                                    #########################

                                    bot.send_message_to_group(json_data['channelNacional'], bot_message)

                except (KeyboardInterrupt, SystemExit):
                    exit()
                except:     
                    funcs.display_error()


if __name__ == '__main__':
    bot = TotalAzulBot()
