from milhas_internacionais import Miles
from milhas_nacionais import MilhasNacionais
from general import GeneralFuncs as func
import threading
import os


def main():
    try:
        # Instances
        thread1 = threading.Thread(target=Miles.scrape_maxmilhas_first_six_months)
        thread2 = threading.Thread(target=Miles.scrape_maxmilhas_next_six_months)
        thread3 = threading.Thread(target=MilhasNacionais.scrape_maxmilhas_first_three_months)
        thread4 = threading.Thread(target=MilhasNacionais.scrape_maxmilhas_next_three_months)
        # Run
        while True:
            thread1.start()
            thread2.start()
            thread3.start()
            thread4.start()
    except:
        func.display_error()


if __name__ == '__main__':
    os.system('cls')
    main()