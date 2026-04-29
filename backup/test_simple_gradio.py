#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最简单的Gradio测试"""
import gradio as gr

def greet(name):
    return f"你好, {name}!"

if __name__ == "__main__":
    print("开始测试Gradio...")
    print("尝试端口: 7872")
    
    # 使用Interface
    demo = gr.Interface(fn=greet, inputs="text", outputs="text")
    
    # 启动
    demo.launch(
        server_name="0.0.0.0",
        server_port=7872,
        show_error=True
    )
