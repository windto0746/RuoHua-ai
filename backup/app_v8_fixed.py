#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
短视频AI文案生成器 v8.0 - 修复版
"""
import gradio as gr
import json
import os
from datetime import datetime
import dashscope
from dashscope import Generation
from dotenv import load_dotenv

# 加载.env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

# API Key
dashscope.api_key = os.environ.get('DASHSCOPE_API_KEY', '')
if not dashscope.api_key:
    raise ValueError('请在.env文件中设置DASHSCOPE_API_KEY')

HISTORY_FILE = "history.json"

# 敏感词库
SENSITIVE_WORDS = {
    '政治': ['领导', '国家主席', '总理', '总统', '抗议', '示威'],
    '医疗': ['根治', '治愈', '保证治愈'],
    '夸大': ['第一', '最好', '最强', '顶级'],
    '低俗': ['上床', '做爱', '诱惑'],
    '平台': ['加我', '微信', 'QQ群']
}

def content_audit(text):
    warnings = []
    filtered_text = text
    for category, words in SENSITIVE_WORDS.items():
        for word in words:
            if word in filtered_text:
                filtered_text = filtered_text.replace(word, '*' * len(word))
                warnings.append(f"[{category}] 已替换: {word}")
    return filtered_text, warnings

# Prompt模板
PROMPTS = {
    ('narrative', '感情系'): """你是一个资深的小红书情感博主，擅长写能引发共鸣的叙事型文案。字数要求80-150字，要有完整的叙事弧度。请根据用户给的主题，写一篇符合要求的文案。""",
    ('narrative', '启发系'): """你是一个小红书治愈系博主，擅长写温柔治愈的叙事。字数要求80-120字。请根据用户给的主题，写一篇符合要求的文案。""",
    ('summary', '感情系'): """你是一个情感博主，擅长写精炼的情感金句。字数要求10-20字。请根据用户给的主题，写一句符合要求的金句。""",
    ('summary', '启发系'): """你是一个治愈成长类博主，擅长写温暖的金句。字数要求10-20字。请根据用户给的主题，写一句符合要求的金句。""",
}

SCENARIOS = {
    "重叙述型": {"desc": "视频配文", "words": "80-150字", "key": "narrative"},
    "重总结型": {"desc": "金句升华", "words": "10-20字", "key": "summary"},
}

STYLES = ["感情系", "启发系"]

def generate_script(scenario, style, topic):
    if not topic or not topic.strip():
        return "请输入视频主题"

    try:
        scenario_info = SCENARIOS.get(scenario, SCENARIOS["重叙述型"])
        scene_key = scenario_info["key"]
        system_prompt = PROMPTS.get((scene_key, style), PROMPTS[('narrative', '启发系')])

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'请根据主题"{topic}"生成文案。'}
        ]

        response = Generation.call(model='qwen-plus', messages=messages)

        if response.get('status_code') == 200:
            result = response['output']['text']
            filtered_result, warnings = content_audit(result)
            hint = f"{scenario} | {scenario_info['words']}"
            if warnings:
                hint += "\n" + "\n".join([f"⚠️ {w}" for w in warnings])
            return filtered_result, hint
        else:
            return f"生成失败: {response.get('message', '未知错误')}", ""
    except Exception as e:
        return f"生成失败: {str(e)}", ""

# 界面
with gr.Blocks(title="短视频AI文案生成器 v8.0") as app:
    gr.Markdown("""<div style="background:linear-gradient(135deg,#4A90E2,#67B8F5);border-radius:20px;padding:30px;text-align:center;margin-bottom:25px;">
        <h1 style="color:white;margin:0;">短视频AI文案生成器 v8.0</h1>
        <p style="color:rgba(255,255,255,0.9);">通义千问AI | 专业Prompt</p>
    </div>""")

    with gr.Row():
        with gr.Column(scale=2):
            scenario = gr.Dropdown(choices=list(SCENARIOS.keys()), value="重叙述型", label="场景类型")
            style = gr.Dropdown(choices=STYLES, value="启发系", label="文案风格")
            topic_input = gr.Textbox(label="视频主题", placeholder="输入你想创作的主题...")
            generate_btn = gr.Button("🚀 开始生成", variant="primary")
            result_output = gr.Textbox(label="生成结果", lines=8)
            hint_output = gr.Textbox(label="", lines=2, interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("### 🔥 热门话题")
            gr.Examples(
                examples=[["职场PUA"], ["裸辞"], ["极简生活"], ["分手治愈"]],
                inputs=topic_input,
            )

    generate_btn.click(fn=generate_script, inputs=[scenario, style, topic_input], outputs=[result_output, hint_output])

if __name__ == "__main__":
    print("=" * 50)
    print("短视频AI文案生成器 v8.0")
    print("访问地址：http://127.0.0.1:7863")
    print("=" * 50)
    app.launch(server_name="127.0.0.1", server_port=7863, show_error=True)
