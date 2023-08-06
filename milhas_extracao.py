# from httpx import AsyncClient
import os
from selenium import webdriver
import requests
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
from general import GeneralFuncs as func
from selenium_vars import XPATHS
from selenium.webdriver.remote.webdriver import WebDriver
import time


class MainScrappy:
    @staticmethod
    def find_compania(driver: WebDriver, data_ida: datetime, data_volta: datetime) -> str:
        contador = 0
        while contador < 60:
            contador += 1
            time.sleep(1)

            try:
                compania: str = driver.find_element('xpath', XPATHS['compania_aerea']).text
                print(f'achou compania: {compania}')
                print(' ')
                return compania
            except:
                print(f'\033[033m Não achou compania! secs = {contador} \033[0m', end='\r')

            try:
                driver.find_element('xpath', XPATHS['ah_nao_msg'])
                print(
                    '\033[033m' + 
                    f'\nNão existem vôos para dia "{data_ida.strftime("%d/%m/%Y")}" ' +
                    f'com volta "{data_volta.strftime("%d/%m/%Y")}"' +
                    '\033[0m'
                )
                return ''
            except:
                pass
        
        return ''


    @staticmethod
    def get_dados(driver: WebDriver, compania: str) -> dict:
        valor_liquido: str = func.element_handler(driver, xpath=XPATHS['valor_liquido'], operacao=2, extract=True)
        valor_total: str = func.element_handler(driver, xpath=XPATHS['valor_total'], operacao=2, extract=True)
        ida_hora_saida: str = func.element_handler(driver, xpath=XPATHS['ida_hora_saida'], operacao=2, extract=True)
        ida_hora_chegada: str = func.element_handler(driver, xpath=XPATHS['ida_hora_chegada'], operacao=2, extract=True)
        ida_duracao: str = func.element_handler(driver, xpath=XPATHS['ida_duracao'], operacao=2, extract=True)
        ida_parada: str = func.element_handler(driver, xpath=XPATHS['ida_parada'], operacao=2, extract=True)
        volta_hora_saida: str = func.element_handler(driver, xpath=XPATHS['volta_hora_saida'], operacao=2, extract=True)
        volta_hora_chegada: str = func.element_handler(driver, xpath=XPATHS['volta_hora_chegada'], operacao=2, extract=True)
        volta_duracao: str = func.element_handler(driver, xpath=XPATHS['volta_duracao'], operacao=2, extract=True)
        volta_parada: str = func.element_handler(driver, xpath=XPATHS['volta_parada'], operacao=2, extract=True)

        dados_milhas: dict = {
            'compania': str(compania),
            'valor_liquido': str(valor_liquido),
            'valor_total': str(valor_total),
            'ida_hora_saida': str(ida_hora_saida),
            'ida_hora_chegada': str(ida_hora_chegada),
            'ida_duracao': str(ida_duracao),
            'ida_parada': str(ida_parada),
            'volta_hora_saida': str(volta_hora_saida),
            'volta_hora_chegada': str(volta_hora_chegada),
            'volta_duracao': str(volta_duracao),
            'volta_parada': str(volta_parada),
        }

        return dados_milhas


    @staticmethod
    def mostrar_dados(dados_milhas: dict) -> None:
        print('\033[036m Dados extraídos: \033[0m')
        for chave, valor in dados_milhas.items():
            valor_temp = valor
            print('\033[032m' + f'{chave}: ' + valor_temp.replace("\n", "") + '\033[0m')


    @staticmethod
    def envia_dados_to_telegram(chat_id: str, message) -> None:  
        api_token = '6673695581:AAH2sG_-V3TgSxuo2_zkdfpvbWysBCZcOaQ'
        url = f'https://api.telegram.org/bot{api_token}/sendMessage'
        params = {'chat_id': chat_id, 'text': message}
        response = requests.post(url, params=params)

        if response.ok:
            print("Message sent to Telegram successfully.")
        else:
            print("Failed to send the message to Telegram.")


    @func.measure_time
    def main() -> None:
        base_url = 'https://www.maxmilhas.com.br/busca-passagens-aereas'
        cod_ori = 'GRU'
        cod_dest = 'DXB'
        chrome_path = r'..\\driver_web\\chromedriver.exe'
        service = Service(executable_path=chrome_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-block')
        options.add_argument("no-default-browser-check")
        # options.add_argument('--headless')

        try:
            with webdriver.Chrome(service=service, options=options) as driver:
                os.system('cls')
                data_ida = datetime.now()
                data_volta = data_ida + timedelta(days=7)
                data_ida_temp: str = data_ida.strftime('%Y-%m-%d')
                data_volta_temp: str = data_volta.strftime('%Y-%m-%d')
                
                for i in range(0, 60):
                    print(f'{i+1}° iteration: {data_ida_temp} to {data_volta_temp}')

                    if i != 0:
                        data_ida = data_ida + timedelta(days=1)
                        data_volta = data_ida + timedelta(days=7)
                        data_ida_temp: str = data_ida.strftime('%Y-%m-%d')
                        data_volta_temp: str = data_volta.strftime('%Y-%m-%d')
                    
                    driver.get(
                        base_url + f'''/RT/{cod_ori}/{cod_dest}/{data_ida_temp}/{data_volta_temp}/1/0/0/EC'''
                    )
                    
                    compania: str = MainScrappy.find_compania(driver, data_ida, data_volta)
                    if not len(compania):
                        continue

                    dados_milhas: dict = MainScrappy.get_dados(driver, compania)
                    MainScrappy.mostrar_dados(dados_milhas)

                    ############################
                    # input('next looping = enter: ')
                    # os.system('cls')
                    ############################
        except KeyboardInterrupt:
            print('program has stopped.')
            exit()
        except:
            func.display_error()


if __name__ == '__main__':
    os.system('cls')
    func.set_output()
    # MainScrappy.main()
    MainScrappy.envia_dados_to_telegram(chat_id='https://t.me/tele_orsq_py_conn_bot', message='hi')
