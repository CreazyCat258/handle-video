import requests
import os
import time
from urllib.parse import urlparse, unquote


def download_video(video_url, output_dir="download", max_retries=3, timeout=60):
    """
    从指定 URL 下载视频并保存到指定文件夹
    
    Args:
        video_url: 视频下载链接
        output_dir: 输出文件夹，默认为 "download"
        max_retries: 最大重试次数，默认为 3
        timeout: 超时时间（秒），默认为 60
    
    Returns:
        str: 下载文件的完整路径，如果失败返回 None
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建文件夹: {output_dir}")
    
    # 从 URL 中提取文件名
    parsed_url = urlparse(video_url)
    # 获取 URL 路径部分，去掉查询参数
    path = parsed_url.path
    # 解码 URL 编码
    path = unquote(path)
    # 提取文件名（最后一个 '/' 之后的部分）
    filename = os.path.basename(path)
    
    # 如果没有文件名或文件名无效，使用默认名称
    if not filename or '.' not in filename:
        filename = "downloaded_video.mp4"
    
    # 构建完整的文件路径
    file_path = os.path.join(output_dir, filename)
    
    print(f"开始下载: {video_url}")
    print(f"保存到: {file_path}")
    
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.tiktok.com/',
    }
    
    # 重试机制
    for attempt in range(max_retries):
        try:
            print(f"\n尝试 {attempt + 1}/{max_retries}...")
            
            # 发送 GET 请求下载文件
            response = requests.get(
                video_url, 
                stream=True, 
                timeout=timeout,
                headers=headers,
                allow_redirects=True
            )
            response.raise_for_status()  # 如果状态码不是 200，会抛出异常
            
            # 获取文件大小（如果服务器提供了 Content-Length）
            total_size = int(response.headers.get('content-length', 0))
            if total_size > 0:
                print(f"文件大小: {total_size / 1024 / 1024:.2f} MB")
            
            # 写入文件
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        # 显示下载进度
                        if total_size > 0:
                            percent = (downloaded_size / total_size) * 100
                            print(f"\r下载进度: {percent:.1f}% ({downloaded_size / 1024 / 1024:.2f} MB / {total_size / 1024 / 1024:.2f} MB)", end='', flush=True)
            
            print(f"\n下载完成: {file_path}")
            return file_path
            
        except requests.exceptions.Timeout:
            print(f"请求超时 (超时时间: {timeout}秒)")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print("达到最大重试次数，下载失败")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"下载失败: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print("达到最大重试次数，下载失败")
                return None
                
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return None
    
    return None


if __name__ == "__main__":
    # 视频下载链接
    VIDEO_URL = "https://v16m.tiktokcdn-us.com/d95dc52509d09bff599c3f67a5d9dd32/690e206e/video/tos/useast2a/tos-useast2a-ve-0068-euttp/oISybAHeLeAuyIRPJLLeGEgehG9WgIgyjPGtIH/?a=1233&bti=OUBzOTg7QGo6OjZAL3AjLTAzYCMxNDNg&ch=0&cr=13&dr=0&er=0&lr=all&net=0&cd=0%7C0%7C0%7C&cv=1&br=3060&bt=1530&cs=0&ds=3&ft=arR-Iq4fmbdPD12F6xWs3wUvBcZAMeF~O5&mime_type=video_mp4&qs=0&rc=MzM1ZTg1PDk3ZGgzOWc2ZEBpM3JsPHU5cjM4eDMzZjczM0BiYjRgXzEwNTIxLzFhLl4xYSM2MDJiMmRzbF9gLS1kMWNzcw%3D%3D&vvpl=1&l=20251107103746D9EF318E801461018BB8&btag=e000b8000"
    
    # 下载视频
    download_video(VIDEO_URL, output_dir="download")

