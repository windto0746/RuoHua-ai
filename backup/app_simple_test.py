#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
短视频AI文案生成器 - Gradio 6.x 兼容版
"""
import gradio as gr
import os
from dotenv import load_dotenv

# 加载.env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

api_key = os.environ.get('DASHSCOPE_API_KEY', '')
print("API Key:", api_key[:10] + "..." if api_key else "未找到")

def test_function(name):
    return f"你好，{name}！Gradio工作正常！"

# 简单界面
with gr.Blocks() as demo:
    gr.Markdown("# 测试程序")
    name_input = gr.Textbox(label="输入名字")
    output = gr.Textbox(label="输出结果")
    btn = gr.Button("测试")
    btn.click(fn=test_function, inputs=name_input, outputs=output)

if __name__ == "__main__":
    print("=" * 50)
    print("启动中...")
    print("访问: http://127.0.0.1:7863")
    print("=" * 50)
    demo.launch(server_name="127.0.0.1", server_port=7863, show_error=True)
