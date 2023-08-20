from destinations import NOMES_SIGLAS, DESTS_NATIONAL
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
from general import GeneralFuncs as func
from selenium_vars import XPATHS
from selenium.webdriver.remote.webdriver import WebDriver
import pyautogui as p
import telegram_bot as bot 
from emojis import EMOJIS
from milhas_internacionais import Miles
import sys


class MilhasNacionais(Miles):
    @func.measure_time
    def scrape_maxmilhas_first_three_months() -> None:
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
            options.add_argument('--headless')

            with webdriver.Chrome(service=service, options=options) as driver:
                os.system('cls')

                for i in range(1, 92):
                    date_ini: datetime = datetime.now() + timedelta(days=i)
                    date_return: datetime = datetime.now() + timedelta(days=(i + 7))
                    date_ini_temp: str = date_ini.strftime('%Y-%m-%d')
                    date_return_temp: str = date_return.strftime('%Y-%m-%d')
                    extra_info: dict = {}
                    cod_orig: str = ''
                    cod_dest: str = ''
                    vlr_limt: str = ''
                    compania: str = ''

                    try:
                        for index in range(len(DESTS_NATIONAL)):
                            cod_orig: str = DESTS_NATIONAL[index][0]
                            cod_dest: str = DESTS_NATIONAL[index][1]
                            vlr_limt: float = DESTS_NATIONAL[index][2]

                            print('\n')
                            print(f'--> {EMOJIS["botHead"]} {i}º iteration: {date_ini_temp} to {date_return_temp}')
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
                                    extra_info = {
                                        'origem': f'{cod_orig}  {NOMES_SIGLAS.get(cod_orig, "")}',
                                        'destino': f'{cod_dest}  {NOMES_SIGLAS.get(cod_dest, "")}',
                                        'dataIda': date_ini,
                                        'dataVolta': date_return,
                                        'linkTicket': driver.current_url,
                                    }
                                    
                                    BOT_MSG = Miles.create_message_telegram(extracted_data_miles, extra_info)
                                    JSON_DATA = Miles.get_json_data()
                                    bot.send_message_to_group(JSON_DATA['channelNacional'], BOT_MSG)
                            except:
                                print(
                                    f'--> {EMOJIS["botHead"]} Error extracting data in iteration {i}: ' + 
                                    f'{cod_orig} - {cod_dest} - {vlr_limt} - {date_ini_temp} - {date_return_temp}'
                                )
                                func.display_error()
                            finally:
                                cod_orig = ''
                                cod_dest = ''
                                vlr_limt = ''
                                compania = ''
                                extra_info = {}
                                continue
                    except:
                        print(f'--> {EMOJIS["botHead"]} Error extracting data in iteration {i}: ')
                        func.display_error()
                        continue

        except KeyboardInterrupt:   
            print('Program has stopped.')
            exit()
        except:
            func.display_error()


    @func.measure_time
    def scrape_maxmilhas_next_three_months() -> None:
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
            options.add_argument('--headless')

            with webdriver.Chrome(service=service, options=options) as driver:
                os.system('cls')
                cont = 0

                for i in range(92, 183):
                    date_ini: datetime = datetime.now() + timedelta(days=i)
                    date_return: datetime = datetime.now() + timedelta(days=(i + 7))
                    date_ini_temp: str = date_ini.strftime('%Y-%m-%d')
                    date_return_temp: str = date_return.strftime('%Y-%m-%d')
                    extra_info: dict = {}
                    cod_orig: str = ''
                    cod_dest: str = ''
                    vlr_limt: str = ''
                    compania: str = ''
                    cont += 1
                    
                    try:
                        for index in range(len(DESTS_NATIONAL)):
                            cod_orig: str = DESTS_NATIONAL[index][0]
                            cod_dest: str = DESTS_NATIONAL[index][1]
                            vlr_limt: float = DESTS_NATIONAL[index][2]

                            print('\n')
                            print(f'--> {EMOJIS["botHead"]} {cont}º iteration: {date_ini_temp} to {date_return_temp}')
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
                                    extra_info = {
                                        'origem': f'{cod_orig}  {NOMES_SIGLAS.get(cod_orig, "")}',
                                        'destino': f'{cod_dest}  {NOMES_SIGLAS.get(cod_dest, "")}',
                                        'dataIda': date_ini,
                                        'dataVolta': date_return,
                                        'linkTicket': driver.current_url,
                                    }
                                    
                                    BOT_MSG = Miles.create_message_telegram(extracted_data_miles, extra_info)
                                    JSON_DATA = Miles.get_json_data()
                                    bot.send_message_to_group(JSON_DATA['channelNacional'], BOT_MSG)
                            except:
                                print(
                                    f'--> {EMOJIS["botHead"]} Error extracting data in iteration {cont}: ' + 
                                    f'{cod_orig} - {cod_dest} - {vlr_limt} - {date_ini_temp} - {date_return_temp}'
                                )
                                func.display_error()
                            finally:
                                cod_orig = ''
                                cod_dest = ''
                                vlr_limt = ''
                                compania = ''
                                extra_info = {}
                                continue
                    except:
                        print(f'--> {EMOJIS["botHead"]} Error extracting data in iteration {i}: ')
                        func.display_error()
                        continue

        except KeyboardInterrupt:   
            print('Program has stopped.')
            exit()
        except:
            func.display_error()


if __name__ == '__main__':
    os.system('cls')
    func.set_output()
    print(sys.argv)

    if str(sys.argv[1]).strip() == '0':
        MilhasNacionais.scrape_maxmilhas_first_three_months()
    elif str(sys.argv[1]).strip() == '1':
        MilhasNacionais.scrape_maxmilhas_next_three_months()

