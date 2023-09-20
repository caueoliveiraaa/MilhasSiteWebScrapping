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


    @funcs.measure_time 
    def main(self) -> None:
        """ Run main script bot """
        os.system('cls')
        json_data = self.get_json_data()

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
                    
                    # Extract values from departure page
                    data_departure = {}
                    departure_counter = 0
                    while departure_counter < 60:
                        departure_counter += 1
                        print(f'Searching for departure data {departure_counter}')
                        p.sleep(1)

                        data_departure, found_data = self.click_and_get_trip_data()
                        if found_data:
                            self.display_data(data_departure)
                            break
                        else:
                            print('Data not found')

                    # Verify if departure time is less the total limit
                    cash_limit: float = trip_values[2]
                    if not self.validate_total_budget(data_departure['departure_value'], cash_limit):
                        print_red(f'Departure value {data_departure["departure_value"]} less than limit {cash_limit}')
                        continue

                    # Extract values from destination page
                    data_return = {}
                    return_counter = 0
                    while return_counter < 60:
                        return_counter += 1
                        print(f'Searching for return data {return_counter}')
                        p.sleep(1)

                        data_return, found_data = self.click_and_get_trip_data()
                        if found_data:
                            self.display_data(data_return)
                            break
                        else:
                            print('Data not found')

                    # Verify if return value is less than limit
                    if not self.validate_total_budget(data_return['departure_value'], cash_limit):
                        print_red(f'Departure value {data_return["departure_value"]} less than lim   it {cash_limit}')
                        continue

                    # Wait for seats button to load
                    WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="button9"]')))
                    print_green('Got to trip url')

                    # Sum both tickets' price
                    total_value = self.get_total_value(
                        value_1=data_departure['departure_value'],
                        value_2=data_return['departure_value']
                    )

                    telegram_data = {
                        'company': data_departure['company'],
                        'origem': f"{data_insert['str_origin']},  {NOMES_SIGLAS.get(data_insert['str_origin'], '')}",
                        'destino': f"{data_insert['str_origin']},  {NOMES_SIGLAS.get(data_insert['str_destination'], '')}",
                        'valor_ida': data_departure['departure_value'],
                        'valor_volta': data_return['departure_value'],
                        'valor_total': total_value,
                        'data_ida': data_insert['date_departure'],
                        'ida_hora_saida': data_departure['flight_time'],
                        'ida_hora_chegada': data_departure['arrival_time'],
                        'ida_duracao': data_departure['departure_duration'],
                        'tipo_voo': data_departure['trip_type_departure'],
                        'data_volta': data_insert['date_return'],
                        'volta_hora_saida': data_return['flight_time'],
                        'volta_hora_chegada': data_return['arrival_time'],
                        'volta_Duracao': data_return['departure_duration'],
                        'volta_tipo': data_return['trip_type_departure'],
                        'company_return': data_return['company'],
                        'link_ticket': self.driver.current_url,
                    }
                
                    # Send message to Telegram
                    bot_message = self.create_message_telegram(telegram_data)
                    bot.send_message_to_group(json_data['channelNacional'], bot_message)

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
        options.add_argument('--force-device-scale-factor=0.8')
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(service=service, options=options)


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


    def create_message_telegram(self, data_telegram: dict) -> str:
        """ Set up message to be sent to Telegram groups """

        try:
            message = f"{EMOJIS['botHead']} Olá. Seguem dados da passagem aérea:\n\n"
            message += f"{EMOJIS['airPlane']} Companhia Aérea Ida:   {data_telegram['company']}\n"
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
            message += f"{EMOJIS['coffeeMug']} Paradas:   {data_telegram['volta_tipo']}\n"
            message += f"{EMOJIS['airPlane']} Companhia Aérea Volta:  {data_telegram['company_return']}\n"
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


    def click_and_get_trip_data(self) -> Tuple[dict, bool]:
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

        for i in range(3):
            print(f'Searching data attemp {i + 1}')
            p.sleep(3)

            try:
                # Get value with div value
                WebDriverWait(self.driver, 35).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="WrapperCardFlight0"]/div/div[1]')))
                var_div = self.driver.find_element('xpath', '//*[@id="WrapperCardFlight0"]/div/div[1]').text
                if len(str(var_div)):
                    value = ''
                    string_list = str(var_div).split('BRL')
                    data['departure_value'] = string_list[-1]
                else:
                    raise ValueError('Value not found')
                
                # Get arrival time
                arrival_time = self.driver.find_element('xpath', xpaths['arrival_time']).text
                if len(str(arrival_time)):
                    data['arrival_time'] = arrival_time
                else:
                    raise ValueError('Arrival time found')

                # Get trip duraton
                departure_duration = self.driver.find_element('xpath', xpaths['departure_duration']).text
                if len(str(departure_duration)):
                    data['departure_duration'] = departure_duration
                else:
                    raise ValueError('Duration found')
                    
                # Get departure time
                flight_time = self.driver.find_element('xpath', xpaths['flight_time']).text
                if len(str(flight_time)):
                    data['flight_time'] = flight_time
                else:
                    raise ValueError('Departure time found')

                # Get type of trip
                trip_type_departure = self.driver.find_element('xpath', xpaths['trip_type_departure']).text
                if len(str(trip_type_departure)):
                    data['trip_type_departure'] = trip_type_departure
                else:
                    raise ValueError('Type found')
                
                # Get company
                company_temp = self.driver.find_element('xpath', xpaths['company']).text
                if len(str(company_temp)):
                    temp_list = str(company_temp).split('pela')
                    data['company'] = temp_list[-1].strip()
                else:
                    raise ValueError('Company found')
                
                print('Extracted all data')

                # Click div
                p.sleep(1)
                self.driver.find_element('xpath', xpaths['frist_div_departure']).click()
                print_green('Clicked div where data has been found')
                p.sleep(2)

                # Click Continue with light ticket
                WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpaths['light_departure'])))
                p.sleep(3)
                self.driver.find_element('xpath', xpaths['light_departure']).click()
                print_green('Clicked Continue with light ticket')

                found = True
                break
            except:
                funcs.display_error()

        return data, found


    def get_json_data(self) -> dict:
        JSON_DATA: dict = {}
        with open('bot_info.json', 'r') as json_file:
            JSON_DATA = json.load(json_file)

        return JSON_DATA


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


if __name__ == '__main__':
    bot = LatamBot()