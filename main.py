import requests
import json
import os

# 1. 富山市の位置情報
LAT = 36.6953
LON = 137.2113

# 2. 富山市の気象データ取得 (Open-Meteo API)
def get_toyama_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=cloud_cover,weather_code&timezone=Asia%2FTokyo"
    res = requests.get(url).json()
    return res.get("hourly", {})

# 3. 衛星通過判定 (N2YO API または 自前SGP4計算)
def check_iss_pass():
    # N2YO API Key (要無料登録)
    API_KEY = os.environ.get("N2YO_API_KEY", "DEMO_KEY")
    NORAD_ISS = 25544 # ISS NORAD ID
    url = f"https://api.n2yo.com/rest/v1/satellite/visualpasses/{NORAD_ISS}/{LAT}/{LON}/10/2/20/&apiKey={API_KEY}"
    res = requests.get(url).json()
    passes = res.get("passes", [])
    return passes

# 4. LINE / Discord 通知送信
def send_notification(message):
    WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": message})
    print("Notification Sent:", message)

def main():
    weather = get_toyama_weather()
    passes = check_iss_pass()
    
    # 本日の通過イベントと時刻の雲量を照合
    for p in passes:
        # 例: 雲量が 20% 以下で、最高仰角 25度以上なら通知!
        cloud = 10 # 該当時刻の雲量取得
        if p["maxEl"] >= 25 and cloud <= 20:
            msg = f"🌟 【富山・天体観測アラート】\nISSが富山県上空を通過します！\n通過時刻: {p['startUTC']}\n最大仰角: {p['maxEl']}° (方向: {p['startAzCompass']}➔{p['endAzCompass']})\n富山市の天気: 快晴 (雲量 {cloud}%)"
            send_notification(msg)

if __name__ == "__main__":
    main()
