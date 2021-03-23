import win32gui

from metin_bot.utils import Vision
from metin_bot.utils.window import MetinWindow


def main():
    aeldra = MetinWindow('Aeldra', 0, 0)
    # print(aeldra.x, aeldra.y, aeldra.width, aeldra.height)
    # print(win32gui.GetWindowRect(aeldra.hwnd))
    # win32gui.MoveWindow(aeldra.hwnd, aeldra.x - 8, aeldra.y - 31, aeldra.width + 16, aeldra.height + 39, True)



if __name__ == '__main__':
    main()

