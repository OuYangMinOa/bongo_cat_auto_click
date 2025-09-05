import os
import threading

import magicgui

from src.app import Application, Config

os.environ['QT_SCALE_FACTOR'] = '2' 
from magicgui import magicgui


@magicgui(call_button = "設定", result_widget=True, labels = True, tooltips = True)
def gui(
    截圖間隔時間      : float = 5, # 秒
    threshold       : float = 0.8,
    滑鼠移動時間      : float = 0.7,
    點擊次數          : int  = 5,
    點擊間隔時間      : float = 0.5,
    是否要回到滑鼠原處 : bool  = True):
    
    Config.screenshot_interval   = 截圖間隔時間
    Config.match_threshold       = threshold
    Config.move_duration         = 滑鼠移動時間
    Config.click_time            = 點擊次數
    Config.click_interval        = 點擊間隔時間
    Config.back_2_original_pos   = 是否要回到滑鼠原處

    print("✅ 設定已更新")

    return f"""✅ 設定已更新"""

def main():
    app = Application()
    threading.Thread(target=app.loop_capture, daemon=True).start()
    gui.show(run=True)

if __name__ == "__main__":
    main()