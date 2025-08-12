import time

from datetime import datetime

import os
import sys
import cv2
import mss
import logging
from logging.handlers import RotatingFileHandler

import numpy as np
import pyautogui
import win32gui

# 設定日誌
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # 設定 logger 的級別
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = RotatingFileHandler(
    'app.log',
    maxBytes=1024*1024*5, # 5 MB
    backupCount=5,
    encoding='utf-8' # 建議加上編碼，避免中文亂碼
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 載入模板圖像

ratio_list = [2,1.75,1.5,1.25,1,0.75,0.5]

filename = 'template2.png'
if os.path.exists(filename):
    print(f"✅ 成功載入模板圖像：{filename}") 
else:
    if hasattr(sys, '_MEIPASS'):
        filename = os.path.join(sys._MEIPASS, filename)
        if os.path.exists(filename):
            print(f"✅ 成功載入打包後的模板圖像：{filename}")
        else:
            print(f"✅ 'template.png'不存在，用預設模板圖像") 

template = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
template_w, template_h = template.shape[::-1]

# 指定視窗名稱
target_window_title = "BongoCat"

def find_window_by_title(title_keyword):
    matched_hwnd = None
    def enum_handler(hwnd, _):
        nonlocal matched_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_keyword.lower() in title.lower():
                matched_hwnd = hwnd
    win32gui.EnumWindows(enum_handler, None)
    return matched_hwnd

def get_window_rect(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    # rect: (left, top, right, bottom)
    return rect

with mss.mss() as sct:
    hwnd = find_window_by_title(target_window_title)
    if hwnd is None:
        print(f"❌ 找不到視窗：{target_window_title}")
    else:
        print(f"✅ 找到視窗：{target_window_title} (HWND: { get_window_rect(hwnd)})")

    while True:
        hwnd = find_window_by_title(target_window_title)
        if hwnd is None:
            print("❌ 找不到視窗")
            time.sleep(1)
            continue

        left, top, right, bottom = get_window_rect(hwnd)
        width, height = right - left, bottom - top
        if width <= 0 or height <= 0:
            print("❌ 視窗尺寸錯誤")
            time.sleep(1)
            continue

        # mss 擷取畫面 (支援多螢幕 & 負座標)
        monitor = {"left": left, "top": top, "width": width, "height": height}
        screenshot = np.array(sct.grab(monitor))
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)

        # print(screenshot_gray.shape)
        # old_X  = screenshot_gray.shape[1]
        # screenshot_gray = cv2.resize(screenshot_gray, (664 ,1080), interpolation=cv2.INTER_LANCZOS4)
        # increase_ratio = screenshot_gray.shape[1] / old_X # 計算寬度縮放比例…
        cv2.imwrite('img.png', screenshot_gray)

        # 模板匹配
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        threshold = 0.8
        if max_val >= threshold:
            print(f"✅ 偵測到寶箱！位置：{max_loc}, 相似度：{max_val:.2f}, 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"偵測到寶箱！位置：{max_loc}, 相似度：{max_val:.2f}, 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            # 點擊位置（視窗起點 + 匹配點 + 模板中心）
            click_x = left + (max_loc[0] + template_w // 2) 
            click_y = top  + (max_loc[1] + template_h // 2) 
            original_pos = pyautogui.position()
            # 點擊
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            pyautogui.click(click_x, click_y)
            time.sleep(0.05)
            pyautogui.click(click_x, click_y)
            # 回到原位
            pyautogui.moveTo(original_pos)
            time.sleep(5)

        else:
            # print(f"未偵測到圖案, 相似度 {max_val}")
            logger.info(f"未偵測到寶箱, 視窗位置 : {left, top, right, bottom}, 相似度 {max_val:.2f}, 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            ...

        time.sleep(1)
