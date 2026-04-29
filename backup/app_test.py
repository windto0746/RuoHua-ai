#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
短视频AI文案生成器 - 简化测试版
用于测试Gradio是否正常工作
"""

import gradio as gr
import os
from dotenv import load_dotenv

# 加载.env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

print("API Key:", os.environ.get('DASHSCOPE_API_KEY', '未找到')[:10] + "...")

def test_function(name):
    return f"你好，{name}！这是测试。"

# 最简单的界面
demo = gr.Interface(
    fn=test_function,
    inputs="text",
    outputs="text",
    title="测试程序"
)

if __name__ == "__main__":
    print("=" * 50)
    print("测试Gradio启动...")
    print("=" * 50)
    demo.launch(server_name="127.0.0.1", server_port=7862)
