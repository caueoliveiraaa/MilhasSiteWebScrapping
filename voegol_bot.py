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
from voegol_bot_xpaths import xpaths
from emojis import EMOJIS
import telegram_bot as bot 
from print_colors import *

from datetime import datetime, timedelta
import pyautogui as p
from typing import Tuple
import time
import json
import sys
import os



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


    def get_json_data(self) -> dict:
        json_data: dict = {}
        with open('bot_info.json', 'r') as json_file:
            json_data = json.load(json_file)

        return json_data


    def display_data(self, data: dict) -> None:
        """ Display data found in terminal"""

        print_cyan(f'{EMOJIS["checkMark"]} Extracted data: ')
        for key, value in data.items(): print_green(f'"{key}": "{value}"')


    # Finish
    def create_message_telegram(self, data_telegram: dict) -> str:
        """ Set up message to be sent to Telegram groups """

        try:
            message = f"{EMOJIS['botHead']} Olá. Seguem dados da passagem aérea:\n\n"
            message += f"{EMOJIS['airPlane']} Companhia Aérea:   {data_telegram['company']}\n"
            message += f"{EMOJIS['earthGlobeAmericas']} Origem:   {data_telegram['origem']}\n"
            message += f"{EMOJIS['earthGlobeAfrica']} Destino:   {data_telegram['destino']}\n"
            message += f"{EMOJIS['moneyBag']} Valor ida:   {data_telegram['valor_ida']}\n"

            message += f"{EMOJIS['moneyBag']} Valor volta:   {data_telegram['valor_volta']}\n"
            message += f"{EMOJIS['checkMark']} Valor Total:   {data_telegram['valor_total']}\n\n"

            message += f"{EMOJIS['calendar']} Ida:  {data_telegram['data_ida'].strftime('%d/%m/%Y')}\n"
            message += f"{EMOJIS['wallClock']} Hora de Saída:   {data_telegram['ida_hora_saida']} hrs\n"   
            message += f"{EMOJIS['wallClock']} Hora de Chegada:   {data_telegram['ida_hora_chegada']} hrs\n"
            message += f"{EMOJIS['sandGlass']} Duração do Voo:   {data_telegram['ida_duracao']}\n"
            message += f"{EMOJIS['coffeeMug']} {data_telegram['tipo_voo']}\n\n"
            message += f"{EMOJIS['calendar']} Volta:  {data_telegram['data_volta'].strftime('%d/%m/%Y')}\n"

            message += f"{EMOJIS['wallClock']} Hora de Saída:   {data_telegram['volta_hora_saida']} hrs\n"

            message += f"{EMOJIS['wallClock']} Hora de Chegada:   {data_telegram['volta_hora_chegada']} hrs\n"

            message += f"{EMOJIS['sandGlass']} Duração do Voo:   {data_telegram['volta_Duracao']}\n"

            message += f"{EMOJIS['coffeeMug']} Paradas:   {data_telegram['volta_parada']}\n"

            message += f"{EMOJIS['earthGlobeEuropeAfrica']} Link: {data_telegram['link_ticket']}"
        except:
            funcs.display_error()

        return message


    def validate_total_budget(self, total_value: str, limit_value: float) -> bool:
        """ Check if value found is lower than verification value """

        total_value = total_value.replace('.', '')
        total_value = float(str(total_value).replace(',', '.').replace('R$', '').strip())
        print(f'\033[035mR$ {total_value} less than or equal to R$ {limit_value}: \033[0m', end=' ')
        print_cyan(f'{(total_value <= limit_value)}') if (total_value <= limit_value) else print_red(f'{(total_value <= limit_value)}')
        return (total_value <= limit_value)


    # Finish
    def get_data_departure(self) -> dict:
        """ Extract data from page """

        website_data = {
            'value_departure': '',
            'duration_departure': '',
            'company': '',
            'type_flight': '',
            'time_departure': '',
            'time_arrival': '',
        }

        try:
            # Extract data
            value_departure = self.driver.find_element('xpath', '//*[@id="lbl_priceValue_1_emission"]').text
            if len(str(value_departure)) > 1:
                website_data['value_departure'] = value_departure

            duration_departure = self.driver.find_element('xpath', '//*[@id="lbl_operationBy_1_emission"]').text
            if len(str(duration_departure)) > 1:
                website_data['duration_departure'] = duration_departure
            
            company = self.driver.find_element('xpath', '//*[@id="lbl_operationBy_1_emission"]').text
            if len(str(company)) > 1:
                website_data['company'] = company

            type_flight = self.driver.find_element('xpath', '//*[@id="lbl_segment_1_emission"]').text
            if len(str(type_flight)) > 1:
                website_data['type_flight'] = type_flight

            time_departure = self.driver.find_element('xpath', '//*[@id="lbl_origin_1_emission"]').text
            if len(str(time_departure)) > 1:
                list_strs = str(time_departure).split(' ')
                time_departure = list_strs[-1]
                website_data['time_departure'] = time_departure

            time_arrival = self.driver.find_element('xpath', '//*[@id="lbl_destination_1_emission"]').text
            if len(str(time_arrival)) > 1:
                list_strs = str(time_arrival).split(' ')
                time_arrival = list_strs[-1]
                website_data['time_arrival'] = time_arrival

            return website_data

        except (KeyboardInterrupt, SystemExit):
            quit()
        except:     
            funcs.display_error()

        print('Data not found')
        return {}


    def insert_data_homepage(self, data_insert) -> Tuple[bool, datetime]:
        """ Insert data into home page to search for tickets """

        def close_popup():
            """ Close ad pop-up """

            try:
                self.driver.find_element('xpath', '/html/body/div[10]/div[2]/div/div[1]/button').click()
                print('Closed pop-up')
            except:
                pass

        for _ in range(3):
            try:
                # Insert origin
                WebDriverWait(self.driver, 25).until(EC.element_to_be_clickable((By.XPATH, xpaths['input_origin'])))
                self.driver.find_element('xpath', xpaths['input_origin']).clear()
                self.driver.find_element('xpath', xpaths['input_origin']).send_keys(data_insert['str_origin'])
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dropdown-saindo-de"]/b2c-list-cta/div/ul/li')))
                message_ori = self.driver.find_element('xpath', '//*[@id="dropdown-saindo-de"]/b2c-list-cta/div/ul/li').text

                if 'Não foram encontrados resultados' in message_ori:
                    print(f'Origin {data_insert["str_origin"]} not found')
                    return False
                self.driver.find_element('xpath', '//*[@id="dropdown-saindo-de"]/b2c-list-cta/div/ul/li').click()
                close_popup()


                # Insert destination
                self.driver.find_element('xpath', xpaths['input_destination']).clear()
                self.driver.find_element('xpath', xpaths['input_destination']).send_keys(data_insert['str_destination'])
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dropdown-indo-para"]/b2c-list-cta/div/ul/li')))
                message_dest = self.driver.find_element('xpath', '//*[@id="dropdown-indo-para"]/b2c-list-cta/div/ul/li').text

                if 'Não foram encontrados resultados' in message_dest:
                    print(f'Destination {data_insert["str_destination"]} not found')
                    return False
                self.driver.find_element('xpath', '//*[@id="dropdown-indo-para"]/b2c-list-cta/div/ul/li').click()
                print(f'Trip has been set up')
                close_popup()


                # Insert departure date
                self.driver.find_element('xpath', xpaths['date_departure_click']).click()
                p.sleep(1)
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="departureDate{data_insert["date_departure"]}"]')))
                p.sleep(0.5)
                self.driver.find_element('xpath', f'//*[@id="departureDate{data_insert["date_departure"]}"]').click()
                p.sleep(1)
                close_popup()
                print(f'Selected date {data_insert["date_departure_datetime"].strftime("%d/%m/%Y")}')

                # Insert return date
                date_return = data_insert['date_return_datetime']
                for i in range(20):
                    try:
                        if i != 0:
                            date_return += timedelta(days=i)

                        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="returnDate{date_return.strftime("%d%m%Y")}"]')))
                        p.sleep(0.5)  
                        close_popup()
                        self.driver.find_element('xpath', f'//*[@id="returnDate{date_return.strftime("%d%m%Y")}"]').click()
                        p.sleep(0.5)
                        close_popup()
                        self.driver.find_element('xpath', '//*[@id="datePicker-returnDate"]/b2c-calendar/div/div[3]/div[1]/div[2]').click()
                        print(f'Selected date {date_return.strftime("%d/%m/%Y")}')
                        close_popup()
                        return True, date_return
                    except:
                        print_yellow(f'Date {date_return.strftime("%d/%m/%Y")} not found')
                
                return False, date_return
            except (KeyboardInterrupt, SystemExit):
                quit()
            except:
                funcs.display_error()
                close_popup()
                

    # Finish
    @funcs.measure_time
    def main(self) -> None:
        """ Run main script bot """

        os.system('cls')
        json_data = self.get_json_data()


        for index_main in range(1, 366):
            # search dates
            date_departure = datetime.now() + timedelta(days=index_main)
            date_return = datetime.now() + timedelta(days=(index_main + 7))


            for key_index, data_trip_lst in DESTS_NATIONAL.items():
                data_insert = {
                    'date_departure': date_departure.strftime("%d%m%Y"),
                    'date_departure_datetime': date_departure,
                    'date_return_datetime': date_return,
                    'str_origin': data_trip_lst[0],
                    'str_destination': data_trip_lst[1],
                }

                print(f'\n{key_index + 1}º iteration with dates ', end=' ')
                print(f'{date_departure.strftime("%d/%m/%Y")}', end=' ')
                print(f'and {date_return.strftime("%d/%m/%Y")}')
                print(f'Trip: {data_trip_lst[0]} -> {data_trip_lst[1]}')


                try:
                    # Open site
                    website_url = 'https://b2c.voegol.com.br/compra'
                    self.driver.get(website_url)

                    # Insert data
                    inserted, date_return = self.insert_data_homepage(data_insert)
                    if not inserted:
                        continue
                    
                    data_telegram = {
                        'origem': data_trip_lst[0],
                        'destino': data_trip_lst[1],
                        'data_ida': date_departure,
                        'data_volta': date_return,
                    }

                    # Search for tickets
                    departure_is_valid = False
                    counter = 0
                    while counter < 80:
                        counter += 1
                        time.sleep(1)
                        print(f'{counter} - Searching for tickets')

                        try:
                            self.driver.find_element('xpath', '//*[@id="btn_searchFlights_emission"]').click()
                            print('Clicked on search button, id="btn_searchFlights_emission" ')
                            time.sleep(8)
                        except:
                            pass

                        data_site = self.get_data_departure()
                        if len(data_site) > 0:
                            self.display_data(data_site)
                            cash_limit: float = data_trip_lst[2]
                            if self.validate_total_budget(data_site['value_departure'], cash_limit):
                                data_telegram['valor_ida'] = data_site['value_departure']
                                data_telegram['ida_hora_saida'] = data_site['time_departure']
                                data_telegram['ida_hora_chegada'] = data_site['time_arrival']
                                data_telegram['ida_duracao'] = data_site['duration_departure']
                                data_telegram['tipo_voo'] = data_site['type_flight']
                                departure_is_valid = True
                            break

                    if not departure_is_valid:
                        continue

                    input('click')
                    
                    self.driver.find_element('xpath', '/html/body/app-root/b2c-flow/main/b2c-select-flight/section/div/section/form/div[1]').click()
                    print('Clicked departure ticket found')

                    input('next')

                except (KeyboardInterrupt, SystemExit):
                    quit()
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
        options.add_argument('--force-device-scale-factor=0.8')
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(service=service, options=options)


if __name__ == '__main__':
    bot = VoeGolBot()