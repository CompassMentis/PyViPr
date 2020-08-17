import time
import functools

import pyautogui

from settings import Settings


@functools.lru_cache()
def get_button_box(name):
    return pyautogui.locateOnScreen(f'{Settings.home_path}images/{name}.png')


def press_button(name, ignore_not_found=False):
    time.sleep(0.1)
    button_box = get_button_box(name)

    # Button can't be found
    if button_box is None:
        if ignore_not_found:
            # Allowed to ignore - maybe already selected, so window looks different
            return
        raise RuntimeError

    button_location = pyautogui.center(button_box)
    pyautogui.click(*button_location)


def select_terminal():
    press_button('terminal', ignore_not_found=True)


def execute_line(line):
    select_terminal()
    pyautogui.typewrite(line)
    pyautogui.press(['enter', ])


def set_size(width, height):
    execute_line(rf'echo -n -e "\033[8;{height};{width}t"')


def run_python_code(lines, character_delay=0, line_delay=0):
    for line in lines:
        if '¬' in line:
            line, delay = line.split('¬')
            line, line_delay = line.rstrip(), float(delay)
        pyautogui.typewrite(line, character_delay)
        pyautogui.press(['enter', ])
        if line_delay:
            time.sleep(abs(line_delay))
        if line_delay < 0:
            for _ in range(3):
                pyautogui.keyDown('ctrl')
                pyautogui.write('c')
                pyautogui.keyUp('ctrl')
