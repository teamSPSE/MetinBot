import pyautogui
from time import sleep

# vypise pozici kurzoru mysi na obrazovce
def main():
    while True:
        print("x:",pyautogui.position()[0], "y:", pyautogui.position()[1]-30)
        sleep(1)


if __name__ == '__main__':
    main()
