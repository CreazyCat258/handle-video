# 视频文件重命名脚本

根据视频字幕的第一句内容自动重命名视频文件。支持两种方式：
1. **从内嵌字幕提取**（如果视频有字幕轨道）
2. **语音识别**（使用Whisper AI进行语音转文字）

## 功能说明

- 优先从MP4视频文件中提取内嵌字幕的第一句内容
- 如果没有字幕，自动使用Whisper进行语音识别
- 使用识别出的第一句话重命名视频文件
- **不会修改视频内容，仅重命名文件**

## 前置要求

1. **Python 3.6+**
2. **ffmpeg** - 用于提取视频字幕和处理视频
   - macOS: `brew install ffmpeg`
   - Linux: `apt-get install ffmpeg` 或 `yum install ffmpeg`
   - Windows: 从 [ffmpeg官网](https://ffmpeg.org/download.html) 下载安装
3. **openai-whisper** - Python语音识别库
   - 安装方法: `pip install openai-whisper`
   - 或使用: `pip install -r requirements.txt`

## 使用方法

1. 确保视频文件位于 `test/test1.mp4`
2. 安装依赖（如果还没安装）：
   ```bash
   pip install openai-whisper
   ```
3. 运行脚本：
   ```bash
   python3 rename_video_by_subtitle.py
   ```

## 脚本说明

脚本会按以下步骤执行：
1. **步骤1**: 尝试从视频内嵌字幕提取第一句
2. **步骤2**: 如果没有字幕，使用Whisper进行语音识别
   - 首次运行会下载Whisper模型（base模型，约139MB）
   - 语音识别可能需要一些时间，请耐心等待
3. **步骤3**: 提取第一句话并清理特殊字符
4. **步骤4**: 重命名视频文件

## 注意事项

- 视频文件必须包含音频轨道（用于语音识别）
- 如果视频没有字幕也没有清晰的语音，脚本会提示错误信息
- 文件名长度限制为100个字符
- 如果目标文件名已存在，会自动添加序号后缀
- Whisper模型首次使用会自动下载，需要网络连接
- 语音识别支持自动检测语言（中英文等）

## 示例

假设视频中的第一句话是 "Hello, welcome to this video"，则：
- 原文件名: `test/test1.mp4`
- 新文件名: `test/Hello, welcome to this video.mp4`

## 技术说明

- 使用 **OpenAI Whisper** 进行语音识别
- 使用 **ffmpeg** 处理视频和音频
- 支持多种字幕格式（SRT等）
- 自动清理文件名中的非法字符

