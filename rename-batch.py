#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频文件重命名脚本
根据视频字幕的第一句内容重命名视频文件
支持从内嵌字幕提取，如果没有字幕则使用语音识别
"""

import os
import subprocess
import re
import sys
from pathlib import Path

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


def extract_subtitle_first_line(video_path):
    """
    从视频文件中提取字幕的第一句内容
    
    Args:
        video_path: 视频文件路径
        
    Returns:
        str: 字幕的第一句内容，如果提取失败返回None
    """
    try:
        # 使用ffmpeg提取字幕到临时文件
        temp_srt = video_path.replace('.mp4', '_temp.srt')
        
        # 提取字幕（假设视频有内嵌字幕轨道）
        # 尝试提取第一个字幕轨道
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-map', '0:s:0',  # 提取第一个字幕轨道
            '-c', 'copy',
            temp_srt,
            '-y'  # 覆盖已存在的文件
        ]
        
        # 执行命令，忽略错误输出（字幕可能不存在）
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 如果提取失败，尝试其他方法
        if not os.path.exists(temp_srt) or os.path.getsize(temp_srt) == 0:
            # 尝试使用ffmpeg的subtitles过滤器提取文本
            cmd_text = [
                'ffmpeg',
                '-i', video_path,
                '-vf', 'subtitles=' + video_path,
                '-an',  # 禁用音频
                '-f', 'null',
                '-'
            ]
            
            # 或者尝试提取所有字幕流
            cmd_all = [
                'ffmpeg',
                '-i', video_path,
                '-map', '0:s?',  # 提取所有字幕轨道（如果存在）
                '-c', 'copy',
                temp_srt,
                '-y'
            ]
            
            result = subprocess.run(
                cmd_all,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        # 读取SRT文件并提取第一句
        if os.path.exists(temp_srt) and os.path.getsize(temp_srt) > 0:
            # 尝试多种编码
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1']
            content = None
            for encoding in encodings:
                try:
                    with open(temp_srt, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                os.remove(temp_srt)
                return None
            
            # 清理临时文件
            os.remove(temp_srt)
            
            # 解析SRT格式，提取第一句文本
            # SRT格式: 序号\n时间码\n文本内容\n\n
            # 使用正则表达式匹配SRT条目
            srt_pattern = r'\d+\s*\n\s*\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}\s*\n\s*(.+?)(?=\n\s*\n|\n\s*\d+\s*\n|$)'
            matches = re.findall(srt_pattern, content, re.MULTILINE | re.DOTALL)
            
            if matches:
                first_line = matches[0].strip()
                # 移除HTML标签（如果有）
                first_line = re.sub(r'<[^>]+>', '', first_line)
                # 清理特殊字符，使其适合作为文件名
                first_line = re.sub(r'[<>:"/\\|?*]', '', first_line)
                first_line = first_line.replace('\n', ' ').replace('\r', ' ')
                # 合并多个空格
                first_line = re.sub(r'\s+', ' ', first_line).strip()
                # 限制文件名长度
                if len(first_line) > 100:
                    first_line = first_line[:100]
                return first_line if first_line else None
            
            # 如果正则匹配失败，使用逐行解析
            lines = content.split('\n')
            in_subtitle_text = False
            subtitle_texts = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                # 跳过空行
                if not line:
                    in_subtitle_text = False
                    continue
                # 跳过序号行
                if re.match(r'^\d+$', line):
                    in_subtitle_text = False
                    continue
                # 跳过时间码行
                if '-->' in line:
                    in_subtitle_text = True
                    continue
                # 收集字幕文本
                if in_subtitle_text and line:
                    subtitle_texts.append(line)
            
            if subtitle_texts:
                first_line = ' '.join(subtitle_texts[:1])  # 只取第一行
                # 移除HTML标签
                first_line = re.sub(r'<[^>]+>', '', first_line)
                # 清理特殊字符
                first_line = re.sub(r'[<>:"/\\|?*]', '', first_line)
                first_line = re.sub(r'\s+', ' ', first_line).strip()
                # 限制文件名长度
                if len(first_line) > 100:
                    first_line = first_line[:100]
                return first_line if first_line else None
        
        # 如果SRT提取失败，尝试从ffmpeg输出中提取
        # 检查视频信息，看是否有字幕流
        cmd_info = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 's:0',
            '-show_entries', 'stream=codec_name',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        
        result = subprocess.run(
            cmd_info,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # 有字幕流，尝试提取
            print(f"检测到字幕流: {result.stdout.strip()}")
            print("提示: 如果自动提取失败，可能需要手动指定字幕轨道或使用外部字幕文件")
        
        return None
        
    except Exception as e:
        print(f"提取字幕时出错: {e}")
        if 'temp_srt' in locals() and os.path.exists(temp_srt):
            os.remove(temp_srt)
        return None


def extract_audio_from_video(video_path, output_audio_path):
    """
    从视频文件中提取音频
    
    Args:
        video_path: 视频文件路径
        output_audio_path: 输出音频文件路径
        
    Returns:
        bool: 是否成功提取
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # 不包含视频
            '-acodec', 'pcm_s16le',  # 使用PCM编码
            '-ar', '16000',  # 采样率16kHz（whisper推荐）
            '-ac', '1',  # 单声道
            '-y',  # 覆盖已存在的文件
            output_audio_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 0
        
    except Exception as e:
        print(f"提取音频时出错: {e}")
        return False


def speech_to_text_whisper(video_path):
    """
    使用Whisper进行语音识别（可以直接处理视频文件）
    
    Args:
        video_path: 视频文件路径（whisper可以直接处理）
        
    Returns:
        str: 识别出的第一句话，如果失败返回None
    """
    if not WHISPER_AVAILABLE:
        print("错误: 未安装whisper库，请运行: pip install openai-whisper")
        return None
    
    try:
        print("正在加载Whisper模型（首次使用会下载模型，请耐心等待）...")
        # 使用base模型，平衡速度和准确性
        # 可选模型: tiny(最快但准确度低), base(推荐), small, medium, large(最准确但慢)
        model = whisper.load_model("base")
        
        print("正在进行语音识别（这可能需要一些时间，请耐心等待）...")
        # whisper可以直接处理视频文件，language=None表示自动检测语言
        result = model.transcribe(video_path, language=None, task="transcribe")
        
        # 提取第一句话
        if result and 'text' in result:
            text = result['text'].strip()
            if text:
                # 按句号、问号、感叹号等分割，取第一句（中英文标点）
                sentences = re.split(r'[。！？\.!?\n]', text)
                first_sentence = sentences[0].strip() if sentences else text
                
                # 如果第一句为空或太长，尝试按逗号、分号分割
                if not first_sentence or len(first_sentence) > 100:
                    sentences = re.split(r'[，,;；]', text)
                    first_sentence = sentences[0].strip() if sentences else text[:100]
                
                # 如果第一句太长，截取前100个字符（文件名长度限制）
                if len(first_sentence) > 100:
                    first_sentence = first_sentence[:100]
                
                return first_sentence if first_sentence else text[:100]
        
        return None
        
    except Exception as e:
        print(f"语音识别时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def rename_video_by_subtitle(video_path):
    """
    根据字幕第一句重命名视频文件
    
    Args:
        video_path: 视频文件路径
    """
    if not os.path.exists(video_path):
        print(f"错误: 文件不存在: {video_path}")
        return False
    
    print(f"正在处理视频文件: {video_path}")
    
    # 首先尝试从内嵌字幕提取
    print("步骤1: 尝试从内嵌字幕提取...")
    first_line = extract_subtitle_first_line(video_path)
    
    # 如果没有字幕，尝试语音识别
    if not first_line:
        print("未找到内嵌字幕，尝试使用语音识别...")
        
        if not WHISPER_AVAILABLE:
            print("错误: 未安装whisper库")
            print("安装方法: pip install openai-whisper")
            print("或者: pip install -r requirements.txt")
            return False
        
        # 直接使用whisper处理视频文件（whisper会自动提取音频）
        print("步骤2: 进行语音识别（直接处理视频文件）...")
        first_line = speech_to_text_whisper(video_path)
        
        if not first_line:
            print("警告: 语音识别失败，可能原因：")
            print("1. 视频中没有清晰的语音")
            print("2. 音频质量较差")
            print("3. 视频文件损坏或格式不支持")
            return False
    
    print(f"提取到的第一句字幕: {first_line}")
    
    # 获取文件目录和扩展名
    file_dir = os.path.dirname(video_path)
    file_ext = os.path.splitext(video_path)[1]
    
    # 生成新文件名
    new_filename = first_line + file_ext
    new_path = os.path.join(file_dir, new_filename)
    
    # 检查新文件名是否已存在
    if os.path.exists(new_path):
        print(f"警告: 目标文件已存在: {new_path}")
        # 添加序号
        base_name = first_line
        counter = 1
        while os.path.exists(new_path):
            new_filename = f"{base_name}_{counter}{file_ext}"
            new_path = os.path.join(file_dir, new_filename)
            counter += 1
        print(f"使用新名称: {new_filename}")
    
    # 重命名文件
    try:
        os.rename(video_path, new_path)
        print(f"成功重命名: {os.path.basename(video_path)} -> {os.path.basename(new_path)}")
        return True
    except Exception as e:
        print(f"重命名失败: {e}")
        return False


def main():
    """主函数"""
    # 设置要处理的视频文件路径
    video_file = os.path.join('test', 'test1.mp4')
    
    # 检查ffmpeg是否安装
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到ffmpeg，请先安装ffmpeg")
        print("安装方法: brew install ffmpeg (macOS) 或 apt-get install ffmpeg (Linux)")
        sys.exit(1)
    
    # 检查whisper是否安装
    if not WHISPER_AVAILABLE:
        print("警告: 未安装whisper库，将无法使用语音识别功能")
        print("安装方法: pip install openai-whisper")
        print("或者: pip install -r requirements.txt")
        print("继续执行，但如果视频没有字幕将无法处理...")
    
    # 执行重命名
    success = rename_video_by_subtitle(video_file)
    
    if success:
        print("处理完成！")
    else:
        print("处理失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()

