import sys
import time
import builtins
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class GeneralFuncs:
    def display_error() -> str:
        """ Mostrar mensagem de erro com detalhes """

        exctp, exc, exctb = sys.exc_info()
        print(
            f'\n\033[033mtraceback\033[0m:\033[031m{exc}\033[0m' +
            f'{exctb.tb_frame.f_code.co_name}:{exctb.tb_lineno}:{exctp}:'
        )

    def measure_time(func):
        """ Operador para calcular quanto tempo uma funcao leva para iniciar e terminar """

        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            total_time = end_time - start_time
            hours, rem = divmod(total_time, 3600)
            minutes, seconds = divmod(rem, 60)

            if hours > 0:
                print(f"Function '{func.__name__}' took {int(hours)} hours, {int(minutes)} minutes, e {seconds:.2f} seconds to execute.")
            elif minutes > 0:
                print(f"Function '{func.__name__}' took {int(minutes)} minutes, e {seconds:.2f} seconds to execute.")
            else:
                print(f"Function '{func.__name__}' took {total_time:.2f} seconds to execute.")
            return result
        return wrapper
    
    def set_output():
        """ Printar datetime atual e funcao onde esta o print """
        
        original_print = builtins.print
        def costumized_output(*args, **kwargs):
            current_time = datetime.now().strftime("%H:%M:%S")
            frame = sys._getframe()
            output_msg = f'\033[95m[{current_time}]:\033[0m \033[94m{frame.f_back.f_code.co_name}:\033[0m'
            original_print(output_msg, *args, **kwargs)
        builtins.print = costumized_output

    def element_handler(driver, xpath, operacao, seconds=5, click=False, extract=False, sendkeys=''):
        """
            element_to_be_selected: Waits for an element to be selected, such as a checkbox or an option in a dropdown menu.
            title_is: Waits for the page title to match a specific value.
            title_contains: Waits for the page title to contain a specific substring.
            text_to_be_present_in_element: Waits for specific text to be present in the element.
            text_to_be_present_in_element_value: Waits for specific text to be present in the value of the element, such as an input field.
            alert_is_present: Waits for an alert to be present. Useful when interacting with JavaScript alerts.
            invisibility_of_element_located: Waits for an element to be invisible.
            element_located_selection_state_to_be: Waits for the element's selection state to match a specified value.
            element_located_to_be_selected: Waits for an element to be selected (e.g., in a dropdown) with a specific value.
            frame_to_be_available_and_switch_to_it: Waits for a frame to be available and switches the driver's context to that frame.
        """

        if operacao == 1:
            try:
                WebDriverWait(driver, seconds).until(EC.visibility_of_element_located((By.XPATH, f'{xpath}')))
                if click is True:
                    driver.find_element('xpath', f'{xpath}').click()
                if sendkeys != '':
                    driver.find_element('xpath', f'{xpath}').send_keys(f'{sendkeys}')
                elif extract is True:
                    return driver.find_element('xpath', f'{xpath}').text
            except:
                GeneralFuncs.display_error()
        elif operacao == 2:
            try:
                WebDriverWait(driver, seconds).until(EC.presence_of_element_located((By.XPATH, f'{xpath}')))
                if click is True:
                    driver.find_element('xpath', f'{xpath}').click()
                if sendkeys != '':
                    driver.find_element('xpath', f'{xpath}').send_keys(f'{sendkeys}')
                elif extract is True:
                    return driver.find_element('xpath', f'{xpath}').text
            except:
                GeneralFuncs.display_error()
        elif operacao == 3:
            try:
                WebDriverWait(driver, seconds).until(EC.element_to_be_clickable((By.XPATH, f'{xpath}')))
                if click is True:
                    driver.find_element('xpath', f'{xpath}').click()
                if sendkeys != '':
                    driver.find_element('xpath', f'{xpath}').send_keys(f'{sendkeys}')
                elif extract is True:
                    return driver.find_element('xpath', f'{xpath}').text
            except:
                GeneralFuncs.display_error()



