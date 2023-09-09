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


class SmilesMilhasBot():
    def __init__(self) -> None:
        """ Handle driver and run bot """

        try:
            # self.build_driver()
            self.main()
        except:
            funcs.display_error()
        # finally:
            # try:
            #     self.driver.close()
            # except:
            #     funcs.display_error()


    def get_json_data(self) -> dict:
        json_data: dict = {}
        with open('bot_info.json', 'r') as json_file:
            json_data = json.load(json_file)

        return json_data


    def display_data(self, data: dict) -> None:
        """ Display data found in terminal"""

        if data:
            print_cyan(f'{EMOJIS["checkMark"]} Extracted data: ')
            for key, value in data.items(): print_green(f'"{key}": "{value}"')


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
            message += f"{EMOJIS['airPlane']} Companhia Aérea Ida:   {data_telegram['company']}\n"
            message += f"{EMOJIS['earthGlobeAmericas']} Origem:   {data_telegram['origem']}\n"
            message += f"{EMOJIS['calendar']} Ida:  {data_telegram['data_ida']}\n"
            message += f"{EMOJIS['moneyBag']} Milhas ida:   {data_telegram['milhas_ida']}\n"
            message += f"{EMOJIS['wallClock']} Hora de Saída:   {data_telegram['ida_hora_saida']} hrs\n"   
            message += f"{EMOJIS['wallClock']} Hora de Chegada:   {data_telegram['ida_hora_chegada']} hrs\n"
            message += f"{EMOJIS['sandGlass']} Duração do Voo:   {data_telegram['ida_duracao']}\n"
            message += f"{EMOJIS['coffeeMug']} Paradas: {data_telegram['tipo_voo']}\n\n"
            message += f"{EMOJIS['airPlane']} Companhia Aérea Volta:  {data_telegram['company_return']}\n"
            message += f"{EMOJIS['earthGlobeAfrica']} Destino:   {data_telegram['destino']}\n"
            message += f"{EMOJIS['calendar']} Volta:  {data_telegram['data_volta']}\n"
            message += f"{EMOJIS['moneyBag']} Milhas volta:   {data_telegram['milhas_volta']}\n"
            message += f"{EMOJIS['wallClock']} Hora de Saída:   {data_telegram['volta_hora_saida']} hrs\n"
            message += f"{EMOJIS['wallClock']} Hora de Chegada:   {data_telegram['volta_hora_chegada']} hrs\n"
            message += f"{EMOJIS['sandGlass']} Duração do Voo:   {data_telegram['volta_duracao']}\n"
            message += f"{EMOJIS['coffeeMug']} Paradas:   {data_telegram['volta_tipo']}\n\n"
            message += f"{EMOJIS['moneyBag']} Milhas total:   {data_telegram['miles_total']}\n"
            message += f"{EMOJIS['earthGlobeEuropeAfrica']} Link: {data_telegram['link_ticket']}"
            return message
        except:
            funcs.display_error()


    def close_popups(self):
        try:
            self.driver.find_element('xpath', '//*[@id="sspa-content"]/div[1]/div[1]/div/div/div/div[1]/i').click()
            print_green('Closed popup voos disponiveis')
        except:
            pass
        try:
            self.driver.find_element('xpath', '//*[@id="onetrust-accept-btn-handler"]').click()
            print_green('Clicked accept all cookies btn')
        except:
            pass


    def get_data_from_current_page(self, stage_trip) -> dict:
        """ Extract trip data from current departure/return page """

        found_data = False
        data_extracted = {}

        for i in range(60):
            try:
                print(f'Searching data - attemp {i + 1}')
                p.sleep(2)
                self.close_popups()

                # Wait for div with data
                self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]')
                print('Found div with data')
                # Extract all data                            
                duration = self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/p[2]').text
                miles = self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[1]/div[2]/div[3]/div/div[1]/p/strong').text
                departure_time = self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[1]/div[2]/div[1]/div[3]/p[2]/strong').text
                return_time = self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[1]/div[2]/div[1]/div[3]/p[3]/strong').text
                type_trip = self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/p[1]').text
                company = self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[1]/div[2]/div[1]/div[3]/p[1]/span[1]').text
                p.sleep(1)
                print('Extracted all data')

                # Store data into dict
                data_extracted['duration'] = duration
                data_extracted['miles'] = miles
                data_extracted['departure_time'] = departure_time
                data_extracted['return_time'] = return_time
                data_extracted['type_trip'] = type_trip
                data_extracted['company'] = company

                # Select div with data found
                self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]').click()
                print('Selected div with info')
                # Select miles option
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[2]/div[1]/div/div/div[1]/ul/li[1]/div/div')))
                self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[2]/div[1]/div/div/div[1]/ul/li[1]/div/div').click()
                print('Selected miles')
                p.sleep(1)
                # Confirm selection
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[2]/div[2]/div[3]/div/button')))
                self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-{stage_trip}"]/div[2]/div/div[5]/div[1]/div[1]/div[2]/div[2]/div[3]/div/button').click()
                print('Confriemd selection')

                found_data = True
                return data_extracted, found_data
            except:
                data_extracted = {}
                p.sleep(1)

            if i >= 3:
                try:
                    self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-ida"]/div[2]/div/div[5]/div[2]')
                    print_yellow(f'No tickets found!')
                    return {}, False
                except:
                    pass

                try:
                    self.driver.find_element('xpath', f'//*[@id="select-flight-accordion-ida"]/div[2]/div/div[5]/div[2]/div/span[1]')
                    print_yellow(f'No tickets found!')
                    return {}, False
                except:
                    pass

                try:
                    self.driver.find_element('xpath', f'//*[@id="main-iframe"]')
                    print_red(f'Found error page.')
                    return {}, False
                except:
                    pass

        return data_extracted, found_data


    @funcs.measure_time
    def main(self) -> None:
        """ Run main script bot """

        json_data = self.get_json_data()
        os.system('cls')

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

                print(f'\n{index_main}º iteration of 185 with dates: ', end=' ')
                print(f'{date_departure.strftime("%d/%m/%Y")}', end=' ')
                print(f'and {date_return.strftime("%d/%m/%Y")}')
                print(f'{key_index + 1}º trip of {len(NATIONAL_MILES)}: {value[0]} -> {value[1]}')
                miles_limit: int = value[2]

                try:
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
                    with webdriver.Chrome(service=service, options=options) as driver:
                        self.driver = driver

                        # Criar url
                        departure_date_temp = datetime(date_departure.year, date_departure.month, date_departure.day)
                        departure_timestamp = int(departure_date_temp.timestamp() * 1000)
                        return_date_temp = datetime(date_return.year, date_return.month, date_return.day)
                        return_timestamp = int(return_date_temp.timestamp() * 1000)
                        base_url = "https://www.smiles.com.br/mfe/emissao-passagem/"

                        query_params = {
                            "adults": 1, "cabin": "ALL", "children": 0,
                            "departureDate": departure_timestamp, "infants": 0,
                            "isElegible": False, "isFlexibleDateChecked": False,
                            "returnDate": return_timestamp, "searchType": "g3",
                            "segments": 1, "tripType": 1, "originAirport": data_insert['str_origin'],
                            "originCity": "", "originCountry": "", "originAirportIsAny": False,
                            "destinationAirport": data_insert['str_destination'], "destinCity": "","destinCountry": "",
                            "destinAirportIsAny": False, "novo-resultado-voos": True
                        }

                        # Construct the full URL with the updated departure date
                        website_url = base_url + "?" + "&".join(f"{key}={value}" for key, value in query_params.items())
                        self.driver.get(website_url)
                        print_cyan('Site has been loaded')

                        # get departure and return data 
                        data_extracted_departure, found_data_departure = self.get_data_from_current_page('ida')
                        if found_data_departure is False or self.validate_total_budget(str(data_extracted_departure['miles']).replace('milhas', ''), miles_limit) is False:
                            continue

                        self.display_data(data_extracted_departure)
                        p.sleep(3)

                        data_extracted_return, found_data_return = self.get_data_from_current_page('volta')
                        if found_data_return is False or self.validate_total_budget(str(data_extracted_return['miles']).replace('milhas', '')) is False:
                            continue

                        self.display_data(data_extracted_return)

                        # Check if miles are valid
                        total_value = self.get_total_value(
                            str(data_extracted_departure['miles']).replace('milhas', ''),
                            str(data_extracted_return['miles']).replace('milhas', '')
                        )
                        
                        if self.validate_total_budget(total_value, miles_limit):
                            # Separate data for message
                            data_telegram = {
                                'company': data_extracted_departure['company'],
                                'origem': f'{data_insert["str_origin"]} {NOMES_SIGLAS.get(data_insert["str_origin"], "")}',
                                'data_ida': data_insert['date_departure'].strftime("%d/%m/%Y"),
                                'milhas_ida': data_extracted_departure['miles'],
                                'ida_hora_saida': data_extracted_departure['departure_time'],
                                'ida_hora_chegada': data_extracted_departure['return_time'],
                                'ida_duracao': data_extracted_departure['duration'],
                                'tipo_voo': data_extracted_departure['type_trip'],
                                'company_return': data_extracted_return['company'],
                                'destino': f'{data_insert["str_destination"]} {NOMES_SIGLAS.get(data_insert["str_destination"], "")}',
                                'data_volta': data_insert['date_return'].strftime("%d/%m/%Y"),
                                'milhas_volta': data_extracted_return['miles'],
                                'volta_hora_saida': data_extracted_return['departure_time'],
                                'volta_hora_chegada': data_extracted_return['return_time'],
                                'volta_duracao': data_extracted_return['duration'],
                                'volta_tipo': data_extracted_return['type_trip'],
                                'miles_total': f'{total_value:,} milhas',
                                'link_ticket': self.driver.current_url,
                            }

                            # Check milhas and send message
                            bot_message = self.create_message_telegram(data_telegram)

                            # Send message to Telegram
                            bot.send_message_to_group(json_data['channelNacional'], bot_message)

                except (KeyboardInterrupt, SystemExit):
                    exit()
                except:     
                    funcs.display_error()


    def build_driver(self) -> None:
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
        self.driver = webdriver.Chrome(service=service, options=options)


if __name__ == '__main__':
    bot = SmilesMilhasBot()