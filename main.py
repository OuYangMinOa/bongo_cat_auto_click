from typing import Literal
import os
import threading

import magicgui

from src.app import Application, Config

os.environ['QT_SCALE_FACTOR'] = '2' 
from magicgui import magicgui

app = Application()
@magicgui(call_button = "設定", result_widget=True, labels = True, tooltips = True,
          x點擊偏移 = {"widget_type": "LogSlider", "max": 200, "min": -200, "tracking": False},
          y點擊偏移 = {"widget_type": "LogSlider", "max": 200, "min": -200, "tracking": False})
def gui(
    開關             : Literal['開', '關'] = '開',
    截圖間隔時間      : float = 5, # 秒
    threshold       : float = 0.8,
    滑鼠移動時間      : float = 0.7,
    點擊次數          : int  = 5,
    點擊間隔時間      : float = 0.5,
    是否要回到滑鼠原處 : bool  = True,
    x點擊偏移 : float = 0,
    y點擊偏移 : float = 0):

    alive_str = None
    if 開關 == '開' and app.alive == False: 
        app.alive = True
        threading.Thread(target=app.loop_capture, daemon=True).start()
        alive_str = "✅ 程式已啟動"
    elif 開關 == '關' and app.alive == True:
        app.alive = False
        alive_str = "❌ 程式已停止"
    
    Config.screenshot_interval   = 截圖間隔時間
    Config.match_threshold       = threshold
    Config.move_duration         = 滑鼠移動時間
    Config.click_time            = 點擊次數
    Config.click_interval        = 點擊間隔時間
    Config.back_2_original_pos   = 是否要回到滑鼠原處
    if alive_str is not None:
        return alive_str
    return f"""🔄️ 設定已更新"""

def main():
    threading.Thread(target=app.loop_capture, daemon=True).start()
    gui.show(run=True)

if __name__ == "__main__":
    main()
