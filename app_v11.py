# -*- coding: utf-8 -*-
"""
短视频AI文案生成器 v11.0
分步向导式界面 - 每步完成后才显示下一步
"""

import gradio as gr
import json
import os
from datetime import datetime
import dashscope
from dashscope import Generation

# ===== 配置 =====
API_KEY = 'sk-15d8a880bb6a41e7900e9e8c44bfa398'
dashscope.api_key = API_KEY
HISTORY_FILE = "history.json"

# ===== 敏感词库 =====
SENSITIVE_WORDS = {
    '政治': ['领导', '国家主席', '总理', '总统', '抗议', '示威'],
    '医疗': ['根治', '保证治愈', '无效退款', '神医'],
    '投资': ['稳赚', '保本', '高收益', '内幕消息'],
    '夸大': ['第一', '最好', '最强', '顶级', '独家'],
    '低俗': ['约', '上床', '做爱'],
    '平台': ['加我', '微信', 'QQ群', '购买链接']
}

def content_audit(text):
    warnings = []
    filtered_text = text
    for category, words in SENSITIVE_WORDS.items():
        for word in words:
            if word in filtered_text:
                filtered_text = filtered_text.replace(word, '*' * len(word))
                warnings.append(f"[{category}]已替换")
    return filtered_text, warnings

# ===== Prompt模板 =====
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
    "📖 重叙述型": {"desc": "视频配文型", "words": "80-150字", "key": "narrative"},
    "✨ 重总结型": {"desc": "金句升华型", "words": "10-20字", "key": "summary"},
    "📚 长篇故事型": {"desc": "故事主线型", "words": "500-2000字", "key": "story"}
}

STYLES = {
    "💔 感情系": "感情系",
    "🤪 抽象系": "抽象系",
    "✨ 启发系": "启发系",
    "🛒 种草系": "种草系"
}

TOPICS_BY_STYLE = {
    "感情系": ["分手治愈", "原生家庭", "婚姻焦虑", "独居生活", "职场PUA"],
    "抽象系": ["打工人", "发疯文学", "摆烂", "反内卷", "互联网嘴替"],
    "启发系": ["极简生活", "自律打卡", "自我成长", "心态调整", "活在当下"],
    "种草系": ["护肤心得", "穿搭分享", "减肥逆袭", "好物推荐", "探店打卡"]
}

CASES = {
    "感情系": [
        {"title": "凌晨三点的崩溃", "content": "凌晨三点，房东发来催租信息。\n\n我盯着屏幕看了很久，想起老家打来电话问我攒了多少钱。\n\n那一刻突然明白，成年人的体面，是手机里有余额，卡里有存款，心里有底气。\n\n💔"},
        {"title": "懂事的人", "content": "后来才明白，没人能救赎谁，只能自己放过自己。\n\n不是不想恋爱，是不想随便恋爱后更孤独。\n\n懂事的人，连崩溃都要挑时间。"}
    ],
    "抽象系": [
        {"title": "血统遗传", "content": "我妈问我为什么天天加班还这么穷。\n\n我说我在积累经验。\n\n她说她年轻时也这么骗自己。\n\n🤪那一刻我意识到，血统是真的会遗传的。"},
        {"title": "窗户焊死", "content": "上帝给你关上一扇门，顺便把窗户焊死了。\n\n生活不止眼前的苟且，还有读不懂的诗和去不了的远方。"}
    ],
    "启发系": [
        {"title": "允许自己", "content": "有时候觉得自己像个废物。\n\n一事无成，还挑三拣四。\n\n但转念一想，能在这个年纪意识到这些，本身就是一种清醒吧。\n\n✨允许自己偶尔低落，也是一种成长。"},
        {"title": "慢一点", "content": "慢一点也没关系，你已经在路上了。\n\n不是每件事都要有意义，活着本身就是意义。"}
    ],
    "种草系": [
        {"title": "后悔没早来", "content": "被朋友拉去喝了一次，我承认我后悔了。\n\n后悔为什么没早点来！\n\n藏在老巷子里的小店，装修普通但味道绝了。\n\n排队40分钟，但是，值得！！\n\n🛒地址放评论区了~"},
        {"title": "离不开了", "content": "用了三年了，离不开了。\n\n这个价格这个品质，老板是不是傻？\n\n不夸张，这是我今年买过最值的东西。"}
    ]
}

# ===== API调用 =====
def call_llm(messages):
    try:
        response = Generation.call(model='qwen-plus', messages=messages)
        if response.get('status_code') == 200:
            return response['output']['text']
        return f"调用失败: {response.get('message', '未知错误')}"
    except Exception as e:
        return f"系统异常: {str(e)}"

# ===== 历史记录 =====
def save_history(topic, script, scenario, style):
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
    except:
        history = []
    history.insert(0, {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "topic": topic,
        "script": script,
        "scenario": scenario,
        "style": style,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
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

# ===== 核心功能 =====
def generate_script(scenario, style, topic, messages_json=""):
    if not topic or not topic.strip():
        return "⚠️ 请输入视频主题", "", "", ""
    
    try:
        scenario_info = SCENARIOS.get(scenario, SCENARIOS["📖 重叙述型"])
        scene_key = scenario_info["key"]
        style_name = STYLES.get(style, "启发系")
        system_prompt = PROMPTS.get((scene_key, style_name), PROMPTS[('narrative', '启发系')])
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'主题：{topic}，请生成文案'}
        ]
        
        result = call_llm(messages)
        filtered_result, warnings = content_audit(result)
        save_history(topic, filtered_result, scenario, style)
        
        hint = f"✅ {scenario} | {scenario_info['words']}"
        warning_text = "\n".join([f"⚠️ {w}" for w in warnings]) if warnings else ""
        messages_json = json.dumps(messages, ensure_ascii=False)
        
        return filtered_result, hint, warning_text, messages_json
    except Exception as e:
        return f"生成失败: {str(e)}", "", "", ""

def modify_script(feedback, current_script, messages_json, topic, scenario, style):
    if not feedback or not feedback.strip():
        return current_script, "⚠️ 请输入修改意见", ""
    try:
        messages = json.loads(messages_json) if messages_json else []
        if not messages:
            return current_script, "⚠️ 无历史记录", ""
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

def get_topics_and_cases(style):
    """获取话题和案例"""
    style_name = STYLES.get(style, "启发系")
    topics = TOPICS_BY_STYLE.get(style_name, [])
    cases = CASES.get(style_name, [])
    
    # 生成话题HTML
    topics_html = ""
    for t in topics:
        topics_html += f'<button class="topic-btn" onclick="setTopic(\'{t}\')">{t}</button>'
    
    # 生成案例HTML
    cases_html = ""
    for i, case in enumerate(cases):
        cases_html += f'''
        <div class="case-item" onclick="showCase(\'{case["title"]}\', \'{case["content"].replace(chr(10), "<br>")}\')">
            <div class="case-icon">📄</div>
            <div class="case-info">
                <div class="case-title">{case["title"]}</div>
                <div class="case-preview">{case["content"][:30]}...</div>
            </div>
            <div class="case-arrow">›</div>
        </div>
        '''
    
    return topics_html, cases_html

# ===== 步骤控制函数 =====
def go_to_step2():
    return gr.update(visible=False), gr.update(visible=True)

def go_to_step1_from2():
    return gr.update(visible=True), gr.update(visible=False)

def go_to_step3():
    return gr.update(visible=False), gr.update(visible=True)

def go_to_step2_from3():
    return gr.update(visible=True), gr.update(visible=False)

def go_to_step4():
    return gr.update(visible=False), gr.update(visible=True)

def go_to_step3_from4():
    return gr.update(visible=True), gr.update(visible=False)

def go_to_step5():
    return gr.update(visible=False), gr.update(visible=True)

# ===== 构建界面 =====
def build_ui():
    custom_css = """
    :root {
        --primary: #4A90E2;
        --primary-light: #7EB8F7;
        --bg-color: #EEF6FC;
        --card-bg: #FFFFFF;
        --text-primary: #2C3E50;
        --text-secondary: #7F8C8D;
        --border-radius: 24px;
        --shadow: 0 4px 20px rgba(74, 144, 226, 0.12);
    }
    
    body {
        background: var(--bg-color) !important;
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    }
    
    /* 标题 */
    .header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        border-radius: var(--border-radius);
        padding: 30px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 30px rgba(74, 144, 226, 0.25);
    }
    .header h1 { color: white !important; font-size: 28px !important; margin: 0 0 8px 0 !important; }
    .header p { color: rgba(255,255,255,0.9) !important; margin: 0 !important; font-size: 14px !important; }
    
    /* 步骤卡片 */
    .step-card {
        background: white;
        border-radius: var(--border-radius);
        padding: 28px;
        margin-bottom: 20px;
        box-shadow: var(--shadow);
        opacity: 1;
        transform: translateY(0);
        transition: all 0.4s ease;
    }
    .step-card.hidden { display: none; }
    
    .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .step-num {
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 16px;
    }
    .step-title { font-size: 18px; font-weight: 600; color: var(--text-primary); }
    .step-desc { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
    
    /* 选项卡片 */
    .option-card {
        background: linear-gradient(135deg, #F8FBFF 0%, #EEF6FC 100%);
        border-radius: 18px;
        padding: 18px 22px;
        margin: 10px 0;
        border: 2px solid transparent;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .option-card:hover { border-color: var(--primary-light); transform: translateX(4px); }
    .option-card.selected { border-color: var(--primary); background: linear-gradient(135deg, #E8F4FD 0%, #D6EBFF 100%); }
    .option-name { font-size: 16px; font-weight: 600; color: var(--text-primary); }
    .option-desc { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
    .option-words { font-size: 12px; color: var(--primary); font-weight: 500; margin-top: 4px; }
    
    /* 下一步按钮 */
    .next-btn {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 14px 40px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.35) !important;
        transition: all 0.3s ease !important;
    }
    .next-btn:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(74, 144, 226, 0.45) !important; }
    
    /* 话题按钮 */
    .topic-btn {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        margin: 6px;
        cursor: pointer;
        font-size: 14px;
        border: none;
        box-shadow: 0 3px 10px rgba(74, 144, 226, 0.3);
        transition: all 0.3s ease;
    }
    .topic-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(74, 144, 226, 0.4); }
    
    /* 案例项 */
    .case-item {
        display: flex;
        align-items: center;
        background: linear-gradient(135deg, #FFFBF5 0%, #FFF8EE 100%);
        border-radius: 18px;
        padding: 16px 20px;
        margin: 12px 0;
        cursor: pointer;
        border: 1px solid #FFE4C4;
        transition: all 0.3s ease;
    }
    .case-item:hover { transform: translateX(6px); box-shadow: 0 4px 15px rgba(255, 200, 100, 0.3); }
    .case-icon { font-size: 24px; margin-right: 14px; }
    .case-info { flex: 1; }
    .case-title { font-weight: 600; color: var(--text-primary); font-size: 15px; }
    .case-preview { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
    .case-arrow { font-size: 24px; color: #E67E22; }
    
    /* 结果区域 */
    .result-card {
        background: linear-gradient(135deg, #F0FFF8 0%, #E6FFE6 100%);
        border-radius: var(--border-radius);
        padding: 28px;
        border: 2px solid #90EE90;
        margin-top: 20px;
    }
    
    /* 修改区域 */
    .modify-card {
        background: linear-gradient(135deg, #FFF5F5 0%, #FFE8E8 100%);
        border-radius: var(--border-radius);
        padding: 28px;
        border: 2px solid #FFB4B4;
        margin-top: 20px;
    }
    
    /* 操作按钮 */
    .action-btn {
        border-radius: 25px !important;
        font-size: 14px !important;
        padding: 10px 22px !important;
    }
    
    /* 侧边栏按钮 */
    .sidebar-btn {
        position: fixed;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 20px 14px;
        border-radius: 0 20px 20px 0;
        cursor: pointer;
        font-size: 14px;
        writing-mode: vertical-rl;
        box-shadow: 4px 4px 15px rgba(74, 144, 226, 0.35);
        z-index: 100;
        transition: all 0.3s ease;
    }
    .sidebar-btn:hover { padding-left: 20px; }
    
    /* 弹窗 */
    .modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    }
    .modal.show { opacity: 1; visibility: visible; }
    .modal-content {
        background: white;
        border-radius: 28px;
        padding: 32px;
        max-width: 480px;
        width: 90%;
        max-height: 70vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        transform: scale(0.85);
        transition: all 0.3s ease;
    }
    .modal.show .modal-content { transform: scale(1); }
    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .modal-title { font-size: 18px; font-weight: 600; color: var(--text-primary); }
    .modal-close {
        background: #f5f5f5;
        border: none;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
        transition: all 0.3s ease;
    }
    .modal-close:hover { background: #e0e0e0; transform: rotate(90deg); }
    .modal-body { font-size: 15px; line-height: 1.8; color: var(--text-primary); white-space: pre-wrap; }
    """

    with gr.Blocks(title="短视频AI文案生成器 v11.0") as app:
        # 隐藏的状态用于控制步骤显示
        step_state = gr.State(value=1)
        
        # 侧边历史按钮
        gr.HTML('<div class="sidebar-btn" onclick="toggleHistory()">📜 历史</div>')
        
        # 历史记录弹窗
        gr.HTML('''
        <div class="modal" id="historyModal">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-title">📜 生成历史</div>
                    <button class="modal-close" onclick="closeHistory()">✕</button>
                </div>
                <div class="modal-body" id="historyList">暂无历史记录</div>
            </div>
        </div>
        ''')
        
        # 案例弹窗
        gr.HTML('''
        <div class="modal" id="caseModal">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-title" id="caseModalTitle">案例</div>
                    <button class="modal-close" onclick="closeCase()">✕</button>
                </div>
                <div class="modal-body" id="caseModalContent"></div>
            </div>
        </div>
        ''')
        
        # JS函数
        gr.HTML('''
        <script>
        function setTopic(t) { document.querySelector('#topic-input textarea').value = t; }
        function showCase(title, content) { 
            document.getElementById('caseModalTitle').textContent = title; 
            document.getElementById('caseModalContent').textContent = content.replace(/<br>/g, '\\n'); 
            document.getElementById('caseModal').classList.add('show'); 
        }
        function closeCase() { document.getElementById('caseModal').classList.remove('show'); }
        function closeHistory() { document.getElementById('historyModal').classList.remove('show'); }
        </script>
        ''')
        
        # 标题
        gr.HTML('''
        <div class="header">
            <h1>🎬 短视频AI文案生成器</h1>
            <p>v11.0 分步向导式 | 通义千问AI</p>
        </div>
        ''')
        
        with gr.Column():
            # ===== 步骤1：选择场景 =====
            with gr.Group() as step1:
                gr.HTML('''
                <div class="step-card">
                    <div class="step-header">
                        <div class="step-num">1</div>
                        <div>
                            <div class="step-title">选择场景类型</div>
                            <div class="step-desc">根据你的视频内容选择合适的场景</div>
                        </div>
                    </div>
                ''')
                
                scenario = gr.Dropdown(
                    choices=list(SCENARIOS.keys()),
                    value=list(SCENARIOS.keys())[0],
                    label="",
                    show_label=False
                )
                
                gr.HTML('</div>')
                
                with gr.Row():
                    step1_next = gr.Button("下一步 →", elem_classes="next-btn")
                    gr.HTML('<div style="flex:1"></div>')
            
            # ===== 步骤2：选择风格 =====
            with gr.Group(visible=False) as step2:
                gr.HTML('''
                <div class="step-card">
                    <div class="step-header">
                        <div class="step-num">2</div>
                        <div>
                            <div class="step-title">选择文案风格</div>
                            <div class="step-desc">选择你想要的文案调性</div>
                        </div>
                    </div>
                ''')
                
                style = gr.Dropdown(
                    choices=list(STYLES.keys()),
                    value=list(STYLES.keys())[2],
                    label="",
                    show_label=False
                )
                
                gr.HTML('''
                <div style="margin-top: 15px;">
                    <div class="step-desc" style="margin-bottom: 10px;">💡 点击话题可查看相关案例</div>
                    <div id="topics-area"></div>
                </div>
                ''')
                
                gr.HTML('</div>')
                
                with gr.Row():
                    step2_next = gr.Button("下一步 →", elem_classes="next-btn")
                    step2_back = gr.Button("← 上一步", elem_classes="action-btn")
            
            # ===== 步骤3：输入主题 =====
            with gr.Group(visible=False) as step3:
                gr.HTML('''
                <div class="step-card">
                    <div class="step-header">
                        <div class="step-num">3</div>
                        <div>
                            <div class="step-title">输入视频主题</div>
                            <div class="step-desc">输入你想创作的主题关键词</div>
                        </div>
                    </div>
                ''')
                
                topic_input = gr.Textbox(
                    placeholder="例如：职场生存指南、极简生活、减肥逆袭...",
                    label="",
                    lines=2,
                    elem_id="topic-input"
                )
                
                gr.HTML('</div>')
                
                generate_btn = gr.Button("🚀 开始生成", elem_classes="next-btn", size="lg")
                
                with gr.Row():
                    step3_back = gr.Button("← 上一步", elem_classes="action-btn")
                    gr.HTML('<div style="flex:1"></div>')
            
            # ===== 步骤4：查看结果 =====
            with gr.Group(visible=False) as step4:
                gr.HTML('''
                <div class="result-card">
                    <div class="step-header">
                        <div class="step-num" style="background: linear-gradient(135deg, #52c41a, #73d13d);">✓</div>
                        <div>
                            <div class="step-title">生成结果</div>
                            <div class="step-desc">你可以直接修改下方文案</div>
                        </div>
                    </div>
                ''')
                
                result_output = gr.Textbox(placeholder="生成的文案将显示在这里...", label="", lines=12)
                hint_output = gr.Textbox(label="", lines=1, interactive=False)
                warning_output = gr.Textbox(label="", lines=2, interactive=False)
                messages_state = gr.Textbox(visible=False)
                
                gr.HTML('''
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <button class="action-btn" onclick="copyResult()">📋 复制</button>
                    <button class="action-btn" onclick="clearAll()">🗑️ 清空重来</button>
                </div>
                </div>
                ''')
                
                gr.HTML('''
                <script>
                function copyResult() {
                    var text = document.querySelector('#result-output textarea').value;
                    navigator.clipboard.writeText(text);
                    alert('已复制到剪贴板！');
                }
                function clearAll() { location.reload(); }
                </script>
                ''')
            
            # ===== 步骤5：修改反馈 =====
            with gr.Group(visible=False) as step5:
                gr.HTML('''
                <div class="modify-card">
                    <div class="step-header">
                        <div class="step-num" style="background: linear-gradient(135deg, #fa8c16, #ffc53d);">🔧</div>
                        <div>
                            <div class="step-title">修改反馈</div>
                            <div class="step-desc">输入修改意见，让AI调整文案</div>
                        </div>
                    </div>
                ''')
                
                feedback_input = gr.Textbox(placeholder="例如：开头更有吸引力一些，增加更多细节...", label="", lines=3)
                
                gr.HTML('''
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <button class="next-btn" onclick="applyModify()">✨ 应用修改</button>
                    <button class="action-btn" onclick="regenerate()">🔄 重新生成</button>
                </div>
                <div id="modify-status" style="margin-top: 10px;"></div>
                </div>
                ''')
                
                gr.HTML('''
                <script>
                function applyModify() {
                    var feedback = document.querySelector('#feedback-input textarea').value;
                    if (!feedback.trim()) { alert('请输入修改意见'); return; }
                    document.getElementById('modify-status').innerHTML = '⏳ AI正在修改...';
                }
                function regenerate() {
                    if (confirm('确定要重新生成吗？当前文案将被替换。')) {
                        location.reload();
                    }
                }
                </script>
                ''')
        
        # ===== 事件绑定 =====
        # 步骤1 → 步骤2
        step1_next.click(
            fn=go_to_step2,
            inputs=[],
            outputs=[step1, step2]
        )
        
        # 步骤2 → 步骤1 (返回)
        step2_back.click(
            fn=go_to_step1_from2,
            inputs=[],
            outputs=[step1, step2]
        )
        
        # 步骤2 → 步骤3
        step2_next.click(
            fn=go_to_step3,
            inputs=[],
            outputs=[step2, step3]
        )
        
        # 步骤3 → 步骤2 (返回)
        step3_back.click(
            fn=go_to_step2_from3,
            inputs=[],
            outputs=[step2, step3]
        )
        
        # 点击生成 → 显示步骤4结果
        generate_btn.click(
            fn=generate_script,
            inputs=[scenario, style, topic_input],
            outputs=[result_output, hint_output, warning_output, messages_state]
        ).then(
            fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
            inputs=[],
            outputs=[step3, step4]
        )
        
        # 步骤4 → 步骤5 (进入修改)
        gr.Button("进入修改 →", elem_classes="next-btn").click(
            fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
            inputs=[],
            outputs=[step4, step5]
        )

    return app


# ===== 启动 =====
if __name__ == "__main__":
    print("=" * 50)
    print("短视频AI文案生成器 v11.0")
    print("分步向导式界面")
    print("访问地址：http://localhost:7860")
    print("=" * 50)
    
    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)
