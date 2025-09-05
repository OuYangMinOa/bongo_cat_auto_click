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

import src.utils as ut
from src.logger import MyLog
import magicgui

class Config: 

    target_window_title : str   = "BongoCat"
    screenshot_interval : float = 0.1          # 截圖間隔時間（秒）
    match_threshold     : float = 0.8          # 模板匹配閾值
    move_duration       : float = 0.7          # 移動到目標位置的時間（秒）
    click_time          : int   = 5        
    click_interval      : float = 0.5          # 點擊間隔時間（秒）
    back_2_original_pos : bool  = True         # 點擊後返回原位置

    # @magicgui(call_button="calculate")
    # def GUI()


class Application:
    ratio_list          = [2,1.75,1.5,1.25,1,0.75,0.5]
    template_list       = []
    target_window_title = "BongoCat"
    logger              = MyLog.get_logger()
    template_w          = None
    template_h          = None

    def __init__(self):
        self.setup_template()

    def setup_template(self):
        filename = ut.get_template_filenmae()
        template = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        self.template_list.append(template)
        for ratio in self.ratio_list[1:]:
            resized_template = cv2.resize(template, None, fx=ratio/2, fy=ratio/2, interpolation=cv2.INTER_LANCZOS4)
            self.template_list.append(resized_template)
        self.template_w, self.template_h = template.shape[::-1]

    def loop_capture(self):
        with mss.mss() as sct:
            hwnd = ut.find_window_by_title(self.target_window_title)
            if hwnd is None:
                self.logger.error(f"找不到視窗: {self.target_window_title}")
                return
            while True:
                hwnd = ut.find_window_by_title(self.target_window_title)
                if hwnd is None:
                    print("❌ 找不到視窗")
                    time.sleep(1)
                    continue
                left, top, right, bottom = ut.get_window_rect(hwnd)
                width, height = right - left, bottom - top
                if width <= 0 or height <= 0:
                    print("❌ 視窗尺寸錯誤")
                    time.sleep(1)
                    continue
                monitor = {"left": left, "top": top, "width": width, "height": height}
                screenshot = np.array(sct.grab(monitor))
                screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)
                cv2.imwrite('img.png', screenshot_gray)
                # 模板匹配
                max_val, max_loc = ut.get_max_match_template(self.template_list, screenshot_gray)
                if max_val >= Config.match_threshold:
                    click_x = left + (max_loc[0] + self.template_w // 2) 
                    click_y = top  + (max_loc[1] + self.template_h // 2) 
                    self.logger.info(f"偵測到寶箱！位置：{(click_x,click_y)}, 相似度：{max_val:.2f}, 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"✅ 偵測到寶箱！位置：{(click_x,click_y)}, 相似度：{max_val:.2f}, 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    original_pos = pyautogui.position()
                    pyautogui.moveTo(click_x, click_y, duration = Config.move_duration)
                    for _ in range(Config.click_time):
                        pyautogui.click()
                        time.sleep(Config.click_interval)
                    if Config.back_2_original_pos:
                        pyautogui.moveTo(original_pos, duration = Config.move_duration)
                else:
                    # print(f"未偵測到圖案, 相似度 {max_val}")
                    self.logger.info(f"未偵測到寶箱, 視窗位置 : {left, top, right, bottom}, 相似度 {max_val:.2f}, 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(Config.screenshot_interval)