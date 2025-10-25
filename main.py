import threading
from typing import Literal
from magicgui import magicgui
from src.app import Application, Config

logic_app = Application()
this_magicgui = magicgui(call_button = "設定", result_widget=True, labels = True, tooltips = True,
          x點擊偏移 = {"widget_type": "Slider", "max": 50, "min": -50, "step": 0.25},
          y點擊偏移 = {"widget_type": "Slider", "max": 50, "min": -50, "step": 0.25},
          )

config_file = 'config.json'
Config.load(config_file)

@this_magicgui
def gui(
    開關             : Literal['開', '關'] = '開',
    截圖間隔時間     : float = Config.screenshot_interval, # 秒
    threshold       : float = Config.match_threshold,
    滑鼠移動時間      : float = Config.move_duration, # 秒
    點擊次數          : int  = Config.click_time,
    點擊間隔時間      : float = Config.click_interval, # 秒
    是否要回到滑鼠原處 : bool  = Config.back_2_original_pos,
    x點擊偏移 : int = Config.offset_x,
    y點擊偏移 : int = Config.offset_y,):

    alive_str = None
    if 開關 == '開' and logic_app.alive == False: 
        logic_app.alive = True
        threading.Thread(target=logic_app.loop_capture, daemon=True).start()
        alive_str = "✅ 程式已啟動"
    elif 開關 == '關' and logic_app.alive == True:
        logic_app.alive = False
        alive_str = "❌ 程式已停止"
    
    Config.screenshot_interval   = 截圖間隔時間
    Config.match_threshold       = threshold
    Config.move_duration         = 滑鼠移動時間
    Config.click_time            = 點擊次數
    Config.click_interval        = 點擊間隔時間
    Config.back_2_original_pos   = 是否要回到滑鼠原處
    Config.offset_x              = x點擊偏移
    Config.offset_y              = y點擊偏移
    if alive_str is not None:
        return alive_str
    Config.save(config_file)
    return f"""🔄️ 設定已更新"""

def main():
    # 【程式邏輯修正】這裡應該使用 logic_app
    threading.Thread(target=logic_app.loop_capture, daemon=True).start()
    gui.show(run=True)

if __name__ == "__main__":
    main()
