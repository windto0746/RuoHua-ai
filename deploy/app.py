# -*- coding: utf-8 -*-
"""
短视频AI文案生成器 v9.0
Hugging Face Spaces 部署版本
"""
import gradio as gr
import json
import os
from datetime import datetime
import dashscope
from dashscope import Generation

# 配置
API_KEY = os.environ.get('DASHSCOPE_API_KEY', 'your-api-key')
dashscope.api_key = API_KEY
HISTORY_FILE = "/tmp/history.json"

# 敏感词库
SENSITIVE_WORDS = {
    '政治': ['领导', '国家主席', '总理', '总统', '抗议', '示威', '反动', '颠覆'],
    '医疗': ['根治', '治愈', '药到病除', '保证治愈', '无效退款', '神医'],
    '投资': ['稳赚', '保本', '高收益', '天天涨', '翻倍', '内幕消息'],
    '夸大': ['第一', '最好', '最强', '顶级', '独家', '全网最低'],
    '低俗': ['约', '泡', '撩', '上床', '做爱', '性感', '诱惑'],
    '平台': ['加我', '微信', 'QQ群', '购买链接', '私信', '加群']
}

PLATFORM_WARNING_WORDS = ['最', '绝对', '彻底', '完美', '一定', '保证', '必须']

def content_audit(text):
    warnings = []
    filtered_text = text
    for category, words in SENSITIVE_WORDS.items():
        for word in words:
            if word in filtered_text:
                filtered_text = filtered_text.replace(word, '*' * len(word))
                warnings.append(f"[{category}] 已替换: {word}")
    for word in PLATFORM_WARNING_WORDS:
        if word in text:
            count = text.count(word)
            warnings.append(f"[平台规则] 建议减少 '{word}' (出现{count}次)")
    return filtered_text, warnings

# Prompt模板库
PROMPTS = {
    ('narrative', '感情系'): """你是一个资深情感博主。请写80-150字的情感叙事文案，要有具体细节和情感共鸣。""",
    ('narrative', '抽象系'): """你是一个抽象文化创作者。请写60-100字的无厘头反转文案。""",
    ('narrative', '启发系'): """你是一个治愈系博主。请写80-120字的温柔治愈文案。""",
    ('narrative', '种草系'): """你是一个种草博主。请写100-150字的推荐文案。""",
    ('summary', '感情系'): """请写10-20字的情感金句。""",
    ('summary', '抽象系'): """请写10-20字的抽象金句。""",
    ('summary', '启发系'): """请写10-20字的治愈金句。""",
    ('summary', '种草系'): """请写10-20字的种草金句。""",
    ('story', '感情系'): """请写500-2000字的完整情感故事，要有起承转合。""",
    ('story', '抽象系'): """请写300-1500字的抽象反转故事。""",
    ('story', '启发系'): """请写500-2000字的治愈成长故事。""",
    ('story', '种草系'): """请写500-2000字的体验种草故事。""",
}

SCENARIOS = {
    "📖 重叙述型": {"desc": "视频配文", "words": "80-150字", "key": "narrative"},
    "✨ 重总结型": {"desc": "金句升华", "words": "10-20字", "key": "summary"},
    "📚 长篇故事型": {"desc": "故事主线", "words": "500-2000字", "key": "story"}
}

STYLES = {
    "💔 感情系": "感情系",
    "🤪 抽象系": "抽象系",
    "✨ 启发系": "启发系",
    "🛒 种草系": "种草系"
}

def call_llm(messages):
    try:
        response = Generation.call(model='qwen-plus', messages=messages)
        if response.get('status_code') == 200:
            return response['output']['text']
        return f"调用失败: {response.get('message', '未知错误')}"
    except Exception as e:
        return f"系统异常: {str(e)}"

def save_history(topic, script, scenario, style):
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
    except:
        history = []
    history.insert(0, {"topic": topic, "script": script, "scenario": scenario, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
    history = history[:20]
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

def generate_script(scenario, style, topic, history_text=""):
    if not topic or not topic.strip():
        return "请输入视频主题", "", ""
    
    try:
        scenario_info = SCENARIOS.get(scenario, SCENARIOS["📖 重叙述型"])
        scene_key = scenario_info["key"]
        style_name = STYLES.get(style, "启发系")
        system_prompt = PROMPTS.get((scene_key, style_name), PROMPTS[('narrative', '启发系')])
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'主题：{topic}，风格：{style_name}，请生成文案'}
        ]
        
        result = call_llm(messages)
        filtered_result, warnings = content_audit(result)
        save_history(topic, filtered_result, scenario, style)
        
        hint = f"{scenario} | {scenario_info['words']}"
        warning_text = "\n".join([f"⚠️ {w}" for w in warnings]) if warnings else ""
        messages_json = json.dumps(messages, ensure_ascii=False)
        
        return filtered_result, hint, warning_text, messages_json
    except Exception as e:
        return f"生成失败: {str(e)}", "", ""

def modify_script(feedback, current_script, messages_json, topic, scenario, style):
    if not feedback or not feedback.strip():
        return current_script, "请输入修改意见", ""
    try:
        messages = json.loads(messages_json) if messages_json else []
        if not messages:
            return current_script, "无历史记录", ""
        messages.append({'role': 'assistant', 'content': current_script})
        messages.append({'role': 'user', 'content': f'修改意见：{feedback}'})
        
        result = call_llm(messages)
        filtered_result, warnings = content_audit(result)
        
        hint = "✅ 已根据意见修改"
        warning_text = "\n".join([f"⚠️ {w}" for w in warnings]) if warnings else ""
        messages_json = json.dumps(messages, ensure_ascii=False)
        
        return filtered_result, hint, warning_text, messages_json
    except Exception as e:
        return current_script, f"修改失败: {str(e)}", ""

# 界面
css = """
body { background: linear-gradient(135deg, #E8F4FD 0%, #D6EBFF 100%) !important; }
.header { background: linear-gradient(135deg, #4A90E2 0%, #67B8F5 100%); border-radius: 20px; padding: 30px; text-align: center; margin-bottom: 25px; }
.result { background: #F0FFF4; border-radius: 14px; padding: 20px; margin-top: 20px; border: 2px solid #90EE90; }
.modify { background: #FFF5F5; border-radius: 14px; padding: 20px; margin-top: 15px; border: 2px solid #FFB4B4; }
"""

with gr.Blocks(css=css, title="短视频AI文案生成器") as app:
    gr.HTML('<div class="header"><h1 style="color:white">短视频AI文案生成器</h1><p style="color:rgba(255,255,255,0.9)">v9.0 | 通义千问AI | 支持交互修改</p></div>')
    
    with gr.Row():
        with gr.Column(scale=2):
            scenario = gr.Dropdown(choices=list(SCENARIOS.keys()), value=list(SCENARIOS.keys())[0], label="📌 场景类型")
            style = gr.Dropdown(choices=list(STYLES.keys()), value=list(STYLES.keys())[2], label="💫 文案风格")
            topic_input = gr.Textbox(placeholder="输入视频主题...", label="📝 主题", lines=2)
            
            gr.HTML('<div style="text-align:center"><button class="generate-btn" onclick="document.querySelector(\'.primary-btn\').click()">🚀 开始生成</button></div>')
            generate_btn = gr.Button("🚀 开始生成", elem_classes="primary-btn")
            
            gr.HTML('<div class="result"><b>✏️ 生成结果</b></div>')
            result_output = gr.Textbox(placeholder="生成的文案将显示在这里...", label="", lines=10)
            hint_output = gr.Textbox(label="", lines=1, interactive=False)
            warning_output = gr.Textbox(label="", lines=2, interactive=False)
            messages_state = gr.Textbox(visible=False)
            
            gr.HTML('<div class="modify"><b>🔧 修改反馈</b></div>')
            feedback_input = gr.Textbox(placeholder="输入修改意见...", label="修改意见", lines=2)
            modify_btn = gr.Button("✨ 应用修改")
            regenerate_btn = gr.Button("🔄 重新生成")
            modify_status = gr.Textbox(label="", lines=1, interactive=False)
        
        with gr.Column(scale=1):
            gr.HTML('<div style="background:white; border-radius:16px; padding:20px; margin-bottom:18px;"><b>🔥 热门话题</b><br><br>职场：职场PUA、裸辞、打工人<br>情感：原生家庭、分手治愈、独居<br>生活：极简生活、自律打卡、断舍离<br>颜值：早C晚A、减肥逆袭、穿搭</div>')
            gr.HTML('<div style="background:white; border-radius:16px; padding:20px;"><b>📜 历史记录</b></div>')
            history_list = gr.JSON(value=load_history(), label="")
            refresh_btn = gr.Button("🔄 刷新历史")
    
    generate_btn.click(fn=generate_script, inputs=[scenario, style, topic_input, messages_state], 
                      outputs=[result_output, hint_output, warning_output, messages_state])
    refresh_btn.click(fn=load_history, outputs=[history_list])
    modify_btn.click(fn=modify_script, inputs=[feedback_input, result_output, messages_state, topic_input, scenario, style],
                   outputs=[result_output, modify_status, warning_output, messages_state])
    regenerate_btn.click(fn=generate_script, inputs=[scenario, style, topic_input, messages_state],
                       outputs=[result_output, hint_output, warning_output, messages_state])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
