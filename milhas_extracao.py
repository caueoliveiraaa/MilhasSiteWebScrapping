# from httpx import AsyncClient
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from general import GeneralFuncs as g
from selenium_vars import XPATHS
from selenium.common.exceptions import TimeoutException
import time


class MainScrappy:
    @g.measure_time
    def main():
        try:
            base_url = 'https://www.maxmilhas.com.br/busca-passagens-aereas'
            codigo_origem = 'GRU'
            codigo_destino = 'DXB'
            chrome_path = r'..\\driver_web\\chromedriver.exe'
            service = Service(executable_path=chrome_path)
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-infobars')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-block')
            options.add_argument("no-default-browser-check")
            # options.add_argument('--headless')
            data_ida = datetime.now()
            data_volta = data_ida + timedelta(days=7)

            with webdriver.Chrome(service=service, options=options) as driver:
                os.system('cls')
                
                # Percorre todas as datas 
                for i in range(0, 60):
                    if i != 0:
                        data_ida = data_ida + timedelta(days=1)
                        data_volta = data_ida + timedelta(days=7)
                    
                    driver.get(base_url + f'''/RT/{codigo_origem}/{codigo_destino}/{data_ida.strftime('%Y-%m-%d')}/{data_volta.strftime('%Y-%m-%d')}/1/0/0/EC''')
                    print(i+1, '° Looping')

                    # Verificar se existem dados ou não
                    contador = 0
                    found_compania = False
                    while contador < 60 and found_compania == False:
                        contador += 1
                        time.sleep(1)

                        try:
                            compania = driver.find_element('xpath', XPATHS['compania_aerea']).text
                            found_compania = True
                            print('\n')
                            continue
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
                            break
                        except:
                            ...

                    if not found_compania:
                        continue

                    # Extrair dados
                    valor_liquido = g.element_handler(driver, xpath=XPATHS['valor_liquido'], operacao=2, extract=True)
                    valor_total = g.element_handler(driver, xpath=XPATHS['valor_total'], operacao=2, extract=True)
                    ida_hora_saida = g.element_handler(driver, xpath=XPATHS['ida_hora_saida'], operacao=2, extract=True)
                    ida_hora_chegada = g.element_handler(driver, xpath=XPATHS['ida_hora_chegada'], operacao=2, extract=True)
                    ida_duracao = g.element_handler(driver, xpath=XPATHS['ida_duracao'], operacao=2, extract=True)
                    ida_parada = g.element_handler(driver, xpath=XPATHS['ida_parada'], operacao=2, extract=True)
                    volta_hora_saida = g.element_handler(driver, xpath=XPATHS['volta_hora_saida'], operacao=2, extract=True)
                    volta_hora_chegada = g.element_handler(driver, xpath=XPATHS['volta_hora_chegada'], operacao=2, extract=True)
                    volta_duracao = g.element_handler(driver, xpath=XPATHS['volta_duracao'], operacao=2, extract=True)
                    volta_parada = g.element_handler(driver, xpath=XPATHS['volta_parada'], operacao=2, extract=True)

                    all_data = {
                        'compania': compania,
                        'valor_liquido': valor_liquido,
                        'valor_total': valor_total,
                        'ida_hora_saida': ida_hora_saida,
                        'ida_hora_chegada': ida_hora_chegada,
                        'ida_duracao': ida_duracao,
                        'ida_parada': ida_parada,
                        'volta_hora_saida': volta_hora_saida,
                        'volta_hora_chegada': volta_hora_chegada,
                        'volta_duracao': volta_duracao,
                        'volta_parada': volta_parada,
                    }

                    print('\033[036m Dados extraidos: \033[0m')
                    for chave, valor in all_data.items():
                        valor_temp = valor
                        print('\033[032m' + f'{chave}: ' + valor_temp.replace("\n", "") + '\033[0m')

                    # input('next looping = enter: ')
                    # os.system('cls')
                    input('')

        except:
            g.display_error()


if __name__ == '__main__':
    os.system('cls')
    g.set_output()
    MainScrappy.main()
