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
from latam_bot_xpaths import xpaths
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


class LatamBot():
    def __init__(self) -> None:
        """ Handle driver and run bot """

        try:
            self.build_driver()
            self.main()
        except:
            funcs.display_error()
        finally:
            self.driver.close()


    def get_month_in_ptbr(self, month_english):
        """ Return name of month in Brazilian Portuguese """

        months = {
            'January': 'Janeiro',
            'February': 'Fevereiro',
            'March': 'Março',
            'April': 'Abril',
            'May': 'Maio',
            'June': 'Junho',
            'July': 'Julho',
            'August': 'Agosto',
            'September': 'Setembro',
            'October': 'Outubro',
            'November': 'Novembro',
            'December': 'Dezembro',
        }

        # print(f'Returning month {months[month_english]}')
        return months[month_english]


    def loop_through_dates(self, date: datetime) -> bool:
        """ Loop though all the months and days to find match """

        for div in range(1, 4):
            # Validate month
            month_found = self.driver.find_element('xpath', f'//*[@id="calendarContainer"]/div/div/div/div/div[2]/div[2]/div/div[{div}]/div/div/strong').text
            if len(month_found):
                month_found = str(month_found).split(' ')[0].strip()

            if str(month_found).lower().strip() != self.get_month_in_ptbr(date.strftime('%B')).lower().strip():
                print_yellow(
                    f'Invalid month! Month {month_found} not in {self.get_month_in_ptbr(date.strftime("%B"))}'
                )
                continue

            print(f'Valid month {month_found}')
            # Find day
            for tr in range(1, 7):
                for td in range(1, 33):
                    try:
                        day_extracted = self.driver.find_element('xpath', f'//*[@id="calendarContainer"]/div/div/div/div/div[2]/div[2]/div/div[{div}]/div/table/tbody/tr[{tr}]/td[{td}]').text
                        # print(f'found day {day_extracted}')

                        if str(date.day) in str(day_extracted):
                            self.driver.find_element('xpath', f'//*[@id="calendarContainer"]/div/div/div/div/div[2]/div[2]/div/div[{div}]/div/table/tbody/tr[{tr}]/td[{td}]').click()
                            print(f'Selected {month_found}, {day_extracted}')
                            return True
                    except:
                        pass

        return False


    def insert_data_homepage(self, data_insert: dict) -> bool:
        """ Insert data into home page to search for tickets """
     

        try:
            print('Inserting trip data')

            # Inser origin
            self.driver.find_element('xpath', xpaths['origin_input']).clear()
            self.driver.find_element('xpath', xpaths['origin_input']).send_keys(data_insert['str_origin'])
            print('Found origin input')
            time.sleep(0.5)

            found_origin = False
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lstItem_0"]')))
            for i in range(3): 
                try:
                    result_found = self.driver.find_element('xpath', f'//*[@id="lstItem_{i}"]').text
                    if data_insert['str_origin'] in str(result_found):
                        self.driver.find_element('xpath', f'//*[@id="lstItem_{i}"]').click()
                        print(f'Selected origin {result_found}')
                        found_origin = True
                        break
                except:
                    print(f'')
            
            if not found_origin:
                raise ValueError('Origin not found')
            

            # Destination
            self.driver.find_element('xpath', xpaths['destination_input']).clear()
            self.driver.find_element('xpath', xpaths['destination_input']).send_keys(data_insert['str_destination'])
            print('Found destination input')
            time.sleep(0.5)

            found_dest = False
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lstItem_0"]')))
            for i in range(3): 
                try:
                    result_found = self.driver.find_element('xpath', f'//*[@id="lstItem_{i}"]').text
                    if data_insert['str_destination'] in str(result_found):
                        self.driver.find_element('xpath', f'//*[@id="lstItem_{i}"]').click()
                        print(f'Selected destination {result_found}')
                        found_dest = True
                        break
                except:
                    print(f'')

            if not found_dest:
                raise ValueError('Origin not found')


            # Departure date
            self.driver.find_element('xpath', xpaths['date_departure_input']).click()
            p.sleep(1)
            if not self.loop_through_dates(data_insert['date_departure']):
                raise ValueError(f'Date {data_insert["date_departure"]} not found')

            # Return date
            self.driver.find_element('xpath', xpaths['return_date']).click()
            p.sleep(1)
            if not self.loop_through_dates(data_insert['date_return']):
                raise ValueError(f'Date {data_insert["date_return"]} not found')

            self.driver.find_element('xpath', '//*[@id="btnSearchCTA"]').click()
            print_green('Clicked search btn')

            return True
        except:
            funcs.display_error()
            return False


    def switch_to_new_tab(self):
        current_window = self.driver.current_window_handle
        windows_active = self.driver.window_handles

        for window_temp in windows_active:
            if window_temp != current_window:
                self.driver.switch_to.window(window_temp)
                self.driver.switch_to.window(current_window)
                self.driver.close()
                self.driver.switch_to.window(window_temp)


    def display_data(self, data: dict) -> None:
        """ Display data found in terminal"""

        print_cyan(f'{EMOJIS["checkMark"]} Extracted data: ')
        for key, value in data.items(): print_green(f'"{key}": "{value}"')


    # Finish
    def create_message_telegram(self, message_data: dict) -> str:
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
    def get_departure_data(self) -> Tuple[dict, bool]:
        """ Extract data from departure page """

        found = False
        data = {
            'departure_value': '',
            'departure_duration': '',
            'flight_time': '',
            'arrival_time': '',
            'trip_type_departure': '',
            'company': '',
        }

        for _ in range(3):
            try:
                departure_value = self.driver.find_element('xpath', xpaths['departure_value']).text
                if len(str(departure_value)):
                    data['departure_value'] = departure_value
                else:
                    print('Value not found')
                    continue

                arrival_time = self.driver.find_element('xpath', xpaths['arrival_time']).text
                if len(str(arrival_time)):
                    data['arrival_time'] = arrival_time
                else:
                    print('Arrival time found')
                    continue

                departure_duration = self.driver.find_element('xpath', xpaths['departure_duration']).text
                if len(str(departure_duration)):
                    data['departure_duration'] = departure_duration
                else:
                    print('Duration found')
                    continue
                    
                flight_time = self.driver.find_element('xpath', xpaths['flight_time']).text
                if len(str(flight_time)):
                    data['flight_time'] = flight_time
                else:
                    print('Departure time found')
                    continue

                trip_type_departure = self.driver.find_element('xpath', xpaths['trip_type_departure']).text
                if len(str(trip_type_departure)):
                    data['trip_type_departure'] = trip_type_departure
                else:
                    print('Type found')
                    continue

                company = self.driver.find_element('xpath', xpaths['company']).text
                if len(str(company)):
                    data['company'] = company
                else:
                    print('Company found')
                    continue

                found = True
                break
            except:
                funcs.display_error()

        return data, found


    # Finish
    def get_return_data(self) -> Tuple[dict, bool]:
        """ Extract data from return trip page """
        
        found = False
        data = {
            'return_value': '',
            'return_duration': '',
            'returnflight_time': '',
            'return_arrival_time': '',
            'trip_type_return': '',
            'company': '',
        }

        for _ in range(3):
            try:
                return_value = self.driver.find_element('xpath', xpaths['return_value']).text
                if len(str(return_value)):
                    data['return_value'] = return_value
                else:
                    print('Value not found')
                    continue


                found = True
                break
            except:
                funcs.display_error()

        return data, found


    # Finish
    @funcs.measure_time 
    def main(self) -> None:
        """ Run main script bot """
        os.system('cls')

        def accept_cookies():
            try:
                self.driver.find_element('xpath', xpaths['all_cookies']).click()
                print_yellow('Clicked "accept all cookies"')
            except:
                pass

        # Run one year in dates
        for index_date in range(1, 366):
            # search dates
            date_departure = datetime.now() + timedelta(days=index_date)
            date_return = datetime.now() + timedelta(days=(index_date + 7))


            for key_index, trip_values in DESTS_NATIONAL.items():

                data_insert = {
                    'date_departure': date_departure,
                    'date_return': date_return,
                    'str_origin': trip_values[0],
                    'str_destination': trip_values[1],
                }

                os.system('cls')
                print(f'\n{key_index + 1}º iteration with dates ', end=' ')
                print(f'{date_departure.strftime("%d/%m/%Y")}', end=' ')
                print(f'and {date_return.strftime("%d/%m/%Y")}')
                print(f'Trip: {trip_values[0]} -> {trip_values[1]}')


                try:
                    # open site
                    website_url = 'https://www.latamairlines.com/br/pt'
                    self.driver.get(website_url)

                    # Insert search data
                    homepage_counter = 0
                    while homepage_counter < 60:    
                        homepage_counter += 1
                        print(f'Attemp {homepage_counter}')

                        p.sleep(1)
                        accept_cookies()

                        # insert data 
                        if not self.insert_data_homepage(data_insert):
                            accept_cookies()
                            continue
                        
                        # Go to new tab and continue process
                        self.switch_to_new_tab()
                        print('Entered new tab')
                        break
                    
                    # Extract values from departure page]
                    data_departure = {}
                    departure_counter = 0
                    while departure_counter < 60:
                        departure_counter += 1
                        print(f'Searching for departure data {departure_counter}')
                        p.sleep(1)

                        data_departure, found_data = self.get_departure_data()
                        if found_data:
                            self.display_data(data_departure)
                            break
                        else:
                            print('Data not found')

                    input(f'here')

                    # Extract values from destination page
                    data_return = {}
                    return_counter = 0
                    while return_counter < 60:
                        return_counter += 1
                        print(f'Searching for return data {return_counter}')
                        p.sleep(1)

                        data_return, found_data = self.get_departure_data()
                        if found_data:
                            self.display_data(data_return)
                            break
                        else:
                            print('Data not found')

                    # Verify values and send message

                    cash_limit: float = trip_values[2]


                except (KeyboardInterrupt, SystemExit):
                    quit()
                except:     
                    funcs.display_error()


    def build_driver(self) -> None:
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
    bot = LatamBot()