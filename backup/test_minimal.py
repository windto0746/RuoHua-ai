#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最小化Gradio测试"""
import gradio as gr

def hello(name):
    return f"你好, {name}!"

app = gr.Interface(fn=hello, inputs="text", outputs="text")
app.launch(server_name="127.0.0.1", server_port=7870)
