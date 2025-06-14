import time

from datetime import datetime

import os
import sys
import cv2
import mss
import logging
# 設定日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
    ]
)
import numpy as np
import pyautogui
import win32gui

logger = logging.getLogger(__name__)
# 載入模板圖像
filename = 'template.png'
if hasattr(sys, '_MEIPASS'):
    filename = os.path.join(sys._MEIPASS, filename)
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

        cv2.imwrite('img.png', screenshot_gray)

        # 模板匹配
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        res = cv2.resize(res, (1021, 607), interpolation=cv2.INTER_CUBIC)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        threshold = 0.8
        if max_val >= threshold:
            print(f"✅ 偵測到圖案！位置：{max_loc}, 相似度：{max_val:.2f}, 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"偵測到圖案！位置：{max_loc}, 相似度：{max_val:.2f}, 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            # 點擊位置（視窗起點 + 匹配點 + 模板中心）
            click_x = left + max_loc[0] + template_w // 2
            click_y = top + max_loc[1] + template_h // 2        # 記錄當前滑鼠位置
            original_pos = pyautogui.position()

            # 點擊
            pyautogui.click(click_x, click_y)
            pyautogui.click(click_x, click_y)
            pyautogui.click(click_x, click_y)
            time.sleep(0.5)
            pyautogui.click(click_x, click_y)
            pyautogui.click(click_x, click_y)
            pyautogui.click(click_x, click_y)
            # 回到原位
            pyautogui.moveTo(original_pos)
            time.sleep(5)

        else:
            # print(f"未偵測到圖案, 相似度 {max_val}")
            logger.info(f"未偵測到圖案, 視窗位置 : {left, top, right, bottom}, 相似度 {max_val:.2f}, 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            ...

        time.sleep(5)
