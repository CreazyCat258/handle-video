# 网站：https://user.tikhub.io/zh-hans/users/overview
# API 接口文档：https://api.tikhub.io/#/TikTok-App-V3-API/fetch_one_video_by_share_url_api_v1_tiktok_app_v3_fetch_one_video_by_share_url_get
import requests
import json
from datetime import datetime

url = "https://api.tikhub.io/api/v1/tiktok/app/v3/fetch_one_video_by_share_url"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer 11"  # Replace with your actual API key
}
params = {
    "share_url": "https://vt.tiktok.com/ZSkpHt9Ps/"
}

response = requests.get(url, headers=headers, params=params)

print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    
    # 保存为格式化的 JSON 文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"download/tiktok_data_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到: {filename}")
    print(f"请求ID: {data.get('request_id', 'N/A')}")
    print(f"视频ID: {data.get('data', {}).get('aweme_detail', {}).get('aweme_id', 'N/A')}")
else:
    print(f"请求失败: {response.text}")