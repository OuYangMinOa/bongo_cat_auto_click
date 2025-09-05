from typing import Optional

import numpy as np
import win32gui
import cv2
import sys
import os

def get_template_filenmae() -> str:
    filename      = 'template2.png'
    if os.path.exists(filename):
        print(f"✅ 成功載入模板圖像：{filename}") 
    else:
        if hasattr(sys, '_MEIPASS'):
            filename = os.path.join(sys._MEIPASS, filename)
            if os.path.exists(filename):
                print(f"✅ 成功載入打包後的模板圖像：{filename}")
            else:
                print(f"✅ 'template.png'不存在，用預設模板圖像") 
    return filename

def find_window_by_title(title_keyword : str) -> Optional[int]:
    matched_hwnd = None
    def enum_handler(hwnd, _):
        nonlocal matched_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_keyword.lower() in title.lower():
                matched_hwnd = hwnd
    win32gui.EnumWindows(enum_handler, None)
    return matched_hwnd

def get_window_rect(hwnd : Optional[int]) -> tuple[int, int, int, int]:
    rect = win32gui.GetWindowRect(hwnd)
    return rect


def get_max_match_template(template_list : list[np.ndarray], screenshot_gray : np.ndarray) -> tuple[float, tuple[int, int]]:
    max_val = 0
    max_loc = (0, 0)
    for template in template_list:
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, current_max_val, min_loc, current_max_loc = cv2.minMaxLoc(res)
        if current_max_val > max_val:
            max_val = current_max_val
            max_loc = current_max_loc
    return max_val, max_loc