import pyautogui
import win32gui
import win32process

def get_metin_needle_path():
    return 'C:/Virtuals/MCxMeTiNcze/Metin2-Bot-main/needles/needle_metin.png'

def get_tesseract_path():
    return r'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'

def get_respawn_needle_path():
    return 'C:/Virtuals/MCxMeTiNcze/Metin2-Bot-main/needles/needle_respawn.png'

def get_login_needle_path():
    return 'C:/Virtuals/MCxMeTiNcze/Metin2-Bot-main/needles/needle_login.png'

def get_empty_img_1024_path():
    return 'C:/Virtuals/MCxMeTiNcze/Metin2-Bot-main/needles/emptyImg1024.png'

def countdown():
    pyautogui.countdown(3)

def get_hwnds_for_pid(pid):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0]