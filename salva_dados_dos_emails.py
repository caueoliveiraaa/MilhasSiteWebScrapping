# from httpx import AsyncClient
from datetime import datetime, timedelta
from general import GeneralFuncs as g
import time
import os


class MainClass:
    @g.measure_time
    def main():
        try:
            print('Função main...')
            time.sleep(1)
        except:
            g.display_error()


if __name__ == '__main__':
    os.system('cls')
    print('\033[032m')
    os.system('python --version')
    print(f'Start: {datetime.now().strftime("%d/%m/%Y")}')
    print('\033[0m')
    g.set_output()
    MainClass.main()
