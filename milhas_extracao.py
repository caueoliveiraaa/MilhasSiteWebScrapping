from destinations import DESTS_INTERNATIONAL, NOMES_SIGLAS, DESTS_NATIONAL
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
from general import GeneralFuncs as func
from selenium_vars import XPATHS
from selenium.webdriver.remote.webdriver import WebDriver
import time
import pyautogui as p
import telegram_bot as bot 
from emojis import EMOJIS
import json


class Miles:
    @staticmethod
    def find_company(driver: WebDriver, date_ini: datetime, date_return: datetime) -> str:
        contador = 0
        while contador < 60:
            contador += 1
            time.sleep(1)

            try:
                compania: str = driver.find_element('xpath', XPATHS['companiaAerea']).text
                print('\n')
                print(f'Found company {EMOJIS["airPlane"]}: {compania}')
                return compania
            except:
                print(f'\033[033m Searching... secs = {contador} \033[0m', end='\r')

            try:
                driver.find_element('xpath', XPATHS['ahNaoMessage'])
                print('\n')
                print(
                    '\033[033m' + 
                    f'No flights between "{date_ini.strftime("%d/%m/%Y")}" ' +
                    f'and "{date_return.strftime("%d/%m/%Y")}"' +
                    '\033[0m'
                )
                return ''
            except:
                pass
        
        return ''


    @staticmethod
    def get_data_from_current_page(driver: WebDriver, compania: str) -> dict:
        valor_liquido: str = func.element_handler(driver, xpath=XPATHS['valorLiquido'], operacao=2, extract=True)
        valor_total: str = func.element_handler(driver, xpath=XPATHS['valorTotal'], operacao=2, extract=True)
        ida_hora_saida: str = func.element_handler(driver, xpath=XPATHS['idaHoraSaida'], operacao=2, extract=True)
        ida_hora_chegada: str = func.element_handler(driver, xpath=XPATHS['idaHoraChegada'], operacao=2, extract=True)
        ida_duracao: str = func.element_handler(driver, xpath=XPATHS['idaDuracao'], operacao=2, extract=True)
        ida_parada: str = func.element_handler(driver, xpath=XPATHS['idaParada'], operacao=2, extract=True)
        volta_hora_saida: str = func.element_handler(driver, xpath=XPATHS['voltaHoraSaida'], operacao=2, extract=True)
        volta_hora_chegada: str = func.element_handler(driver, xpath=XPATHS['voltaHoraChegada'], operacao=2, extract=True)
        volta_duracao: str = func.element_handler(driver, xpath=XPATHS['voltaDuracao'], operacao=2, extract=True)
        volta_parada: str = func.element_handler(driver, xpath=XPATHS['voltaParada'], operacao=2, extract=True)

        extracted_data_miles: dict = {
            'companiaAerea': str(compania).replace("\n", ""),
            'valorLiquido': str(valor_liquido).replace("\n", ""),
            'valorTotal': str(valor_total).replace("\n", ""),
            'idaHoraSaida': str(ida_hora_saida).replace("\n", "").split('+')[0],
            'idaHoraChegada': str(ida_hora_chegada).replace("\n", "").split('+')[0],
            'idaDuracao': str(ida_duracao).replace("\n", ""),
            'idaParada': str(ida_parada).replace("\n", ""),
            'voltaHoraSaida': str(volta_hora_saida).replace("\n", "").split('+')[0],
            'voltaHoraChegada': str(volta_hora_chegada).replace("\n", "").split('+')[0],
            'voltaDuracao': str(volta_duracao).replace("\n", ""),
            'voltaParada': str(volta_parada).replace("\n", ""),
        }

        return extracted_data_miles, (len(extracted_data_miles) == 11)


    @staticmethod
    def display_data(extracted_data_miles: dict) -> None:
        print(f'\033[036m{EMOJIS["checkMark"]} Extracted data: \033[0m')
        for key, value in extracted_data_miles.items():
            value_temp = value
            print('\033[032m' + f'{key}: ' + value_temp + '\033[0m')


    @staticmethod
    def validate_total_budget(total_value: str, limit_value: float) -> bool:
        total_value = total_value.replace('.', '')
        total_value = float(str(total_value).replace(',', '.').replace('R$', '').strip())
        print(f'R$ {total_value} less than or equal to R$ {limit_value}: {(total_value <= limit_value)}')
        return (total_value <= limit_value)


    @staticmethod
    def create_message_telegram(extracted_data_miles: dict, extra_info: dict) -> str:
        message = f"{EMOJIS['botHead']} Olá. Seguem dados da passagem aérea:\n\n"
        message += f"{EMOJIS['airPlane']} Companhia Aérea:   {extracted_data_miles['companiaAerea']}\n"
        message += f"{EMOJIS['earthGlobeAmericas']} Origem:   {extra_info['origem']}\n"
        message += f"{EMOJIS['earthGlobeAfrica']} Destino:   {extra_info['destino']}\n"
        message += f"{EMOJIS['moneyBag']} Valor Líquido:   {extracted_data_miles['valorLiquido']}\n"
        message += f"{EMOJIS['checkMark']} Valor Total:   {extracted_data_miles['valorTotal']}\n\n"
        message += f"{EMOJIS['calendar']} Ida:  {extra_info['dataIda'].strftime('%d/%m/%Y')}\n"
        message += f"{EMOJIS['wallClock']} Hora de Saída:   {extracted_data_miles['idaHoraSaida']} hrs\n"
        message += f"{EMOJIS['wallClock']} Hora de Chegada:   {extracted_data_miles['idaHoraChegada']} hrs\n"
        message += f"{EMOJIS['sandGlass']} Duração do Voo:   {extracted_data_miles['idaDuracao']}\n"
        message += f"{EMOJIS['coffeeMug']} Paradas:   {extracted_data_miles['idaParada']}\n\n"
        message += f"{EMOJIS['calendar']} Volta:  {extra_info['dataVolta'].strftime('%d/%m/%Y')}\n"
        message += f"{EMOJIS['wallClock']} Hora de Saída:   {extracted_data_miles['voltaHoraSaida']} hrs\n"
        message += f"{EMOJIS['wallClock']} Hora de Chegada:   {extracted_data_miles['voltaHoraChegada']} hrs\n"
        message += f"{EMOJIS['sandGlass']} Duração do Voo:   {extracted_data_miles['voltaDuracao']}\n"
        message += f"{EMOJIS['coffeeMug']} Paradas:   {extracted_data_miles['voltaParada']}\n"
        message += f"{EMOJIS['earthGlobeEuropeAfrica']} Link: {extra_info['linkTicket']}"

        return message


    @staticmethod
    def get_json_data() -> dict:
        JSON_DATA: dict = {}
        with open('bot_info.json', 'r') as json_file:
            JSON_DATA = json.load(json_file)

        return JSON_DATA


    @func.measure_time
    def scrape_max_miles_site() -> None:
        try:
            base_url: str = 'https://www.maxmilhas.com.br/busca-passagens-aereas/RT/'
            ending: str = '/1/0/0/EC'
            chrome_path = r'..\\driver_web\\chromedriver.exe'
            service = Service(executable_path=chrome_path)
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-infobars')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-block')
            options.add_argument("no-default-browser-check")
            options.add_argument("--force-device-scale-factor=0.9")
            # options.add_argument('--headless')

            with webdriver.Chrome(service=service, options=options) as driver:
                os.system('cls')
                for i in range(0, 365):
                    date_ini: datetime = datetime.now() + timedelta(days=1)
                    date_return: datetime = datetime.now() + timedelta(days=7)
                    date_ini_temp: str = date_ini.strftime('%Y-%m-%d')
                    date_return_temp: str = date_return.strftime('%Y-%m-%d')
                    
                    for index in range(len(DESTS_INTERNATIONAL)):
                        cod_orig: str = DESTS_INTERNATIONAL[index][0]
                        cod_dest: str = DESTS_INTERNATIONAL[index][1]
                        vlr_limt: float = DESTS_INTERNATIONAL[index][2]

                        print('\n')
                        print(f'--> {EMOJIS["botHead"]} {i+1}º iteration: {date_ini_temp} to {date_return_temp}')
                        print(f'--> {EMOJIS["botHead"]} searching for origin: {cod_orig} - destination: {cod_dest}')

                        try:
                            driver.get(base_url + f'{cod_orig}/{cod_dest}/{date_ini_temp}/{date_return_temp}{ending}')
                            compania: str = Miles.find_company(driver, date_ini, date_return)
                            if not len(compania):
                                continue
                            
                            extracted_data_miles, correct_len = Miles.get_data_from_current_page(driver, compania)
                            Miles.display_data(extracted_data_miles)

                            if not correct_len:
                                print('--> Could not extract data correctly')
                                continue
                            
                            if Miles.validate_total_budget(extracted_data_miles['valorTotal'], limit_value=vlr_limt):
                                try:
                                    func.element_handler(driver, XPATHS['comprarBtn'], operacao=3, seconds=60, click=True)
                                    p.sleep(1.5)
                                    func.element_handler(driver, XPATHS['comprarAgoraBtn'], operacao=3, seconds=60, click=True)
                                    p.sleep(1.5)
                                    func.element_handler(driver, XPATHS['inputEmail'], operacao=3, seconds=120)
                                except:
                                    print('\033[031m--> Erro clicking on buttons to find link!\033[0m')
                                    continue

                                extra_info = {
                                    'origem': cod_orig + '  ' + NOMES_SIGLAS.get(cod_orig, ''),
                                    'destino': cod_dest + '  ' + NOMES_SIGLAS.get(cod_dest, ''),
                                    'dataIda': date_ini,
                                    'dataVolta': date_return,
                                    'linkTicket': driver.current_url,
                                }
                                
                                BOT_MSG = Miles.create_message_telegram(extracted_data_miles, extra_info)
                                JSON_DATA = Miles.get_json_data()
                                bot.send_message_to_group(JSON_DATA['chatTestChannel'], BOT_MSG)
                        except:
                            print(
                                f'--> {EMOJIS["botHead"]} Error extracting data: ' + 
                                f'{cod_orig} - {cod_dest} - {vlr_limt} - {date_ini_temp} - {date_return_temp}'
                            )
                            func.display_error()
                        finally:
                            cod_orig = ''
                            cod_dest = ''
                            vlr_limt = ''
                            compania = ''
                            extra_info = {}

        except KeyboardInterrupt:   
            print('Program has stopped.')
            exit()
        except:
            func.display_error()


if __name__ == '__main__':
    os.system('cls')
    func.set_output()
    Miles.scrape_max_miles_site()
