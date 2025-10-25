import json
import logging
import os
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

import cv2
import magicgui
import mss
import numpy as np
import pyautogui
import win32gui

import src.utils as ut
from src.logger import MyLog


class Config: 
    target_window_title : str   = "BongoCat"
    screenshot_interval : float = 0.1          # 截圖間隔時間（秒）
    match_threshold     : float = 0.8          # 模板匹配閾值
    move_duration       : float = 0.7          # 移動到目標位置的時間（秒）
    click_time          : int   = 5
    click_interval      : float = 0.5          # 點擊間隔時間（秒）
    back_2_original_pos : bool  = True         # 點擊後返回原位置
    offset_x            : int   = 0
    offset_y            : int   = 0

    @classmethod
    def save(cls, filename : str):
        config_dict = {
            "target_window_title": cls.target_window_title,
            "screenshot_interval": cls.screenshot_interval,
            "match_threshold"    : cls.match_threshold,
            "move_duration"      : cls.move_duration,
            "click_time"         : cls.click_time,
            "click_interval"     : cls.click_interval,
            "back_2_original_pos": cls.back_2_original_pos,
            "offset_x"           : cls.offset_x,
            "offset_y"           : cls.offset_y
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=4)

    @classmethod
    def load(cls, filename : str):
        if not os.path.exists(filename):
            return
        with open(filename, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)

        cls.target_window_title = config_dict.get("target_window_title", cls.target_window_title)
        cls.screenshot_interval = config_dict.get("screenshot_interval", cls.screenshot_interval)
        cls.match_threshold     = config_dict.get("match_threshold", cls.match_threshold)
        cls.move_duration       = config_dict.get("move_duration", cls.move_duration)
        cls.click_time          = config_dict.get("click_time", cls.click_time)
        cls.click_interval      = config_dict.get("click_interval", cls.click_interval)
        cls.back_2_original_pos = config_dict.get("back_2_original_pos", cls.back_2_original_pos)
        cls.offset_x            = config_dict.get("offset_x", cls.offset_x)
        cls.offset_y            = config_dict.get("offset_y", cls.offset_y)


class TemplateInfo:

    def __init__(self, filename : str) :
        self.template_list : list[np.ndarray] = []
        self.w             : int = None
        self.h             : int = None

        self.load_template(filename)

    def load_template(self, filename):
        template = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        self.template_list.append(template)
        for ratio in Application.ratio_list[1:]:
            resized_template = cv2.resize(template, None, fx=ratio/2, fy=ratio/2, interpolation=cv2.INTER_LANCZOS4)
            self.template_list.append(resized_template)
        self.w, self.h = template.shape[::-1]


class Application:
    
    ratio_list          : list[float]        = [2,1.75,1.5,1.25,1,0.75,0.5]
    template_info_list  : list[TemplateInfo] = []
    target_window_title : str                = "BongoCat"
    logger              = MyLog.get_logger()

    def __init__(self):
        self.alive = True
        self.setup_template_by_num(3)
        self.setup_template_by_num(4)

    def setup_template_by_num(self, num : int = 1):
        filename = ut.get_template_filename(num = num)
        _template = TemplateInfo(filename)
        self.template_info_list.append(_template)

    def get_max_match_template(self, screenshot_gray : np.ndarray) -> tuple[float, tuple[int, int], int]:
        max_val = 0
        max_loc = (0, 0)
        max_template_idx = -1
        for idx, template_info in enumerate(self.template_info_list):
            for template in template_info.template_list:
                res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
                min_val, current_max_val, min_loc, current_max_loc = cv2.minMaxLoc(res)
                if current_max_val > max_val:
                    max_val = current_max_val
                    max_loc = current_max_loc
                    max_template_idx = idx
        return max_val, max_loc, max_template_idx
    
    def loop_capture(self):
        with mss.mss() as sct:
            hwnd = ut.find_window_by_title(self.target_window_title)
            if hwnd is None:
                self.logger.error(f"找不到視窗: {self.target_window_title}")
                return
            while self.alive:
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
                max_val, max_loc, idx = self.get_max_match_template(screenshot_gray)
                template_info = self.template_info_list[idx]
                if max_val >= Config.match_threshold:
                    click_x = left + (max_loc[0] + template_info.w // 2) + Config.offset_x
                    click_y = top  + (max_loc[1] + template_info.h // 2) + Config.offset_y
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
