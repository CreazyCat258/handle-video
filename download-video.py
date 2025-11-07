# 网站：https://user.tikhub.io/zh-hans/users/overview
# API 接口文档：https://api.tikhub.io/#/TikTok-App-V3-API/fetch_one_video_by_share_url_api_v1_tiktok_app_v3_fetch_one_video_by_share_url_get
import requests
import json
import os
from datetime import datetime


def fetch_from_api(share_url, api_key):
    """
    从 API 接口获取 TikTok 视频数据
    
    Args:
        share_url: TikTok 分享链接
        api_key: API 密钥
    
    Returns:
        dict: 返回的数据，如果失败返回 None
    """
    url = "https://api.tikhub.io/api/v1/tiktok/app/v3/fetch_one_video_by_share_url"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "share_url": share_url
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("成功从 API 获取数据")
            return data
        else:
            print(f"请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"API 请求出错: {str(e)}")
        return None


def fetch_from_json_file(json_file_path):
    """
    从 JSON 文件中读取 TikTok 视频数据
    
    Args:
        json_file_path: JSON 文件路径
    
    Returns:
        dict: 返回的数据，如果失败返回 None
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"成功从文件读取数据: {json_file_path}")
        return data
    except FileNotFoundError:
        print(f"错误: 找不到文件 {json_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"错误: 文件 {json_file_path} 不是有效的 JSON 格式")
        return None
    except Exception as e:
        print(f"错误: {str(e)}")
        return None


def process_data(data, source="file", output_dir="download", share_url=None, json_file_path=None):
    """
    处理数据：保存为 JSON 文件并打印信息
    
    Args:
        data: 要处理的数据字典
        source: 数据来源，"api" 或 "file"，默认为 "file"
        output_dir: 输出目录，默认为 "download"
        share_url: 当 source="api" 时，用于提取文件名的分享链接
        json_file_path: 当 source="file" 时，用于提取文件名的 JSON 文件路径
    """
    if data is None:
        print("数据为空，无法处理")
        return
    
    # 根据数据来源生成文件名
    if source == "api":
        if share_url is None:
            print("错误: api 模式下需要提供 share_url")
            return
        # 从 share_url 中提取路径部分（倒数第二个 "/" 分割的部分）
        url_parts = share_url.rstrip('/').split('/')
        url_path = url_parts[-1] if len(url_parts) > 0 else "unknown"
        filename = f"{output_dir}/{url_path}.json"
    elif source == "file":
        if json_file_path is None:
            print("错误: file 模式下需要提供 json_file_path")
            return
        # 从 json_file_path 中提取文件名（不含扩展名）
        file_name = os.path.basename(json_file_path)
        file_path = os.path.splitext(file_name)[0]  # 去掉扩展名
        filename = f"{output_dir}/{file_path}.json"
    else:
        print(f"错误: 未知的数据来源 '{source}'，请使用 'api' 或 'file'")
        return
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filename}")
        print(f"请求ID: {data.get('request_id', 'N/A')}")
        print(f"视频ID: {data.get('data', {}).get('aweme_detail', {}).get('aweme_id', 'N/A')}")
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")


if __name__ == "__main__":
    # 配置参数
    MODE = "api"  # 可选: "api" 或 "file"
    
    # API 相关配置（当 MODE = "api" 时使用）
    SHARE_URL = "https://vt.tiktok.com/ZSkpupQRp/"
    API_KEY = "=="
    
    # 文件路径配置（当 MODE = "file" 时使用）
    JSON_FILE_PATH = "base/tiktok_data_20251107_183745.json"
    
    # 根据模式选择获取数据的方式
    if MODE == "api":
        data = fetch_from_api(SHARE_URL, API_KEY)
        # 处理数据
        process_data(data, source="api", share_url=SHARE_URL)
    elif MODE == "file":
        data = fetch_from_json_file(JSON_FILE_PATH)
        # 处理数据
        process_data(data, source="file", json_file_path=JSON_FILE_PATH)
    else:
        print(f"错误: 未知的模式 '{MODE}'，请使用 'api' 或 'file'")
        data = None
