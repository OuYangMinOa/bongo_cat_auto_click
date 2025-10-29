from typing import Optional

import numpy as np
import win32gui
import json
import cv2
import sys
import os

def get_template_filename(num : int = 2) -> str:
    filename      = f'template{num}.png'
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


