import pyautogui
from time import sleep

# vypise pozici kurzoru mysi na obrazovce
def main():
    while True:
        print(pyautogui.position())
        sleep(1)


if __name__ == '__main__':
    main()
