# -*- coding: utf-8 -*-
"""
短视频AI文案生成器 v10.0
全新界面设计：简洁步骤式 + 侧边栏滑出历史记录
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
    '医疗': ['根治', '治愈', '保证治愈', '无效退款', '神医'],
    '投资': ['稳赚', '保本', '高收益', '内幕消息'],
    '夸大': ['第一', '最好', '最强', '顶级', '独家'],
    '低俗': ['约', '泡', '上床', '做爱'],
    '平台': ['加我', '微信', 'QQ群', '购买链接', '私信']
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

# ===== Prompt模板库 =====
PROMPTS = {
    ('narrative', '感情系'): """你是一个资深情感博主。请写80-150字的情感叙事文案，要有具体细节和情感共鸣，格式：每句话单独成段。""",
    ('narrative', '抽象系'): """你是一个抽象文化创作者。请写60-100字的无厘头反转文案，制造反差和出人意料的效果。""",
    ('narrative', '启发系'): """你是一个治愈系博主。请写80-120字的温柔治愈文案，娓娓道来。""",
    ('narrative', '种草系'): """你是一个种草博主。请写100-150字的推荐文案，真实场景化。""",
    ('summary', '感情系'): """请写10-20字的情感金句，要文艺伤感、一针见血。""",
    ('summary', '抽象系'): """请写10-20字的抽象金句，要无厘头、反转、出人意料。""",
    ('summary', '启发系'): """请写10-20字的治愈金句，要温柔清新、让人有共鸣。""",
    ('summary', '种草系'): """请写10-20字的种草金句，要有冲击力、让人想立刻下单。""",
    ('story', '感情系'): """请写500-2000字的完整情感故事，要有起（开场钩子）→ 承（发展铺垫）→ 转（高潮冲突）→ 合（升华结尾）。""",
    ('story', '抽象系'): """请写300-1500字的抽象反转故事，荒诞搞笑，结局出人意料。""",
    ('story', '启发系'): """请写500-2000字的治愈成长故事，温暖人心、真实可信。""",
    ('story', '种草系'): """请写500-2000字的体验种草故事，场景化、细节丰富、有代入感。""",
}

# ===== 场景和风格定义 =====
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

# ===== 热门话题（按风格分类）=====
TOPICS_BY_STYLE = {
    "感情系": ["分手治愈", "原生家庭", "婚姻焦虑", "独居生活", "职场PUA"],
    "抽象系": ["打工人", "互联网嘴替", "发疯文学", "摆烂", "反内卷"],
    "启发系": ["极简生活", "自律打卡", "自我成长", "心态调整", "活在当下"],
    "种草系": ["护肤心得", "穿搭分享", "减肥逆袭", "好物推荐", "探店打卡"]
}

# ===== 案例库 =====
CASES = {
    "感情系": [
        {"preview": "凌晨三点，房东发来催租信息...", "full": "凌晨三点，房东发来催租信息。\n\n我盯着屏幕看了很久，想起老家打来电话问我攒了多少钱。\n\n那一刻突然明白，成年人的体面，是手机里有余额，卡里有存款，心里有底气。\n\n💔"},
        {"preview": "后来才明白，没人能救赎谁...", "full": "后来才明白，没人能救赎谁，只能自己放过自己。\n\n不是不想恋爱，是不想随便恋爱后更孤独。\n\n懂事的人，连崩溃都要挑时间。"}
    ],
    "抽象系": [
        {"preview": "我妈问我为什么天天加班还这么穷...", "full": "我妈问我为什么天天加班还这么穷。\n\n我说我在积累经验。\n\n她说她年轻时也这么骗自己。\n\n🤪那一刻我意识到，血统是真的会遗传的。"},
        {"preview": "上帝给你关上一扇门...", "full": "上帝给你关上一扇门，顺便把窗户焊死了。\n\n生活不止眼前的苟且，还有读不懂的诗和去不了的远方。\n\n我以为我很社恐，直到我遇到了我的手机。"}
    ],
    "启发系": [
        {"preview": "有时候觉得自己像个废物...", "full": "有时候觉得自己像个废物。\n\n一事无成，还挑三拣四。\n\n但转念一想，能在这个年纪意识到这些，本身就是一种清醒吧。\n\n✨允许自己偶尔低落，也是一种成长。"},
        {"preview": "慢一点也没关系...", "full": "慢一点也没关系，你已经在路上了。\n\n不是每件事都要有意义，活着本身就是意义。\n\n允许自己偶尔脆弱，也是一种坚强。"}
    ],
    "种草系": [
        {"preview": "被朋友拉去喝了一次，我承认后悔了...", "full": "被朋友拉去喝了一次，我承认我后悔了。\n\n后悔为什么没早点来！\n\n藏在老巷子里的小店，装修普通但味道绝了。\n\n排队排了40分钟，但是，值得！！\n\n🛒地址放评论区了~"},
        {"preview": "用了三年了，离不开了...", "full": "用了三年了，离不开了。\n\n这个价格这个品质，老板是不是傻？\n\n不夸张，这是我今年买过最值的东西。"}
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
        return "请输入视频主题", "", ""
    
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

def get_topics_for_style(style):
    """获取指定风格的热门话题"""
    style_name = STYLES.get(style, "启发系")
    topics = TOPICS_BY_STYLE.get(style_name, [])
    return "\n".join([f"• {t}" for t in topics])

def get_cases_for_style(style):
    """获取指定风格的案例"""
    style_name = STYLES.get(style, "启发系")
    cases = CASES.get(style_name, [])
    return cases

# ===== 构建界面 =====
def build_ui():
    custom_css = """
    /* 全局样式 */
    :root {
        --primary: #4A90E2;
        --primary-light: #7EB8F7;
        --primary-dark: #3A7BC8;
        --bg-color: #EEF6FC;
        --card-bg: #FFFFFF;
        --text-primary: #2C3E50;
        --text-secondary: #7F8C8D;
        --border-radius: 20px;
        --shadow: 0 4px 20px rgba(74, 144, 226, 0.12);
        --shadow-lg: 0 8px 40px rgba(74, 144, 226, 0.2);
    }
    
    body {
        background: var(--bg-color) !important;
        font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif !important;
    }
    
    /* 标题区域 */
    .header-section {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        border-radius: var(--border-radius);
        padding: 25px 30px;
        text-align: center;
        box-shadow: var(--shadow-lg);
        margin-bottom: 25px;
    }
    
    .header-section h1 {
        color: white !important;
        font-size: 26px !important;
        font-weight: 600 !important;
        margin: 0 0 8px 0 !important;
        letter-spacing: 1px;
    }
    
    .header-section p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 14px !important;
        margin: 0 !important;
    }
    
    /* 步骤卡片 */
    .step-card {
        background: var(--card-bg);
        border-radius: var(--border-radius);
        padding: 24px;
        margin-bottom: 18px;
        box-shadow: var(--shadow);
        border: 1px solid rgba(74, 144, 226, 0.08);
        transition: all 0.3s ease;
    }
    
    .step-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .step-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .step-number {
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 600;
    }
    
    /* 选择卡片样式 */
    .choice-card {
        background: linear-gradient(135deg, #F8FBFF 0%, #EEF6FC 100%);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 8px 0;
        border: 2px solid transparent;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .choice-card:hover {
        border-color: var(--primary-light);
        background: linear-gradient(135deg, #EEF6FC 0%, #E0F0FA 100%);
    }
    
    .choice-card.selected {
        border-color: var(--primary);
        background: linear-gradient(135deg, #E8F4FD 0%, #D6EBFF 100%);
    }
    
    .choice-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    
    .choice-desc {
        font-size: 13px;
        color: var(--text-secondary);
    }
    
    .choice-words {
        font-size: 12px;
        color: var(--primary);
        font-weight: 500;
        margin-top: 4px;
    }
    
    /* 话题标签 */
    .topic-btn {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 25px;
        margin: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
    }
    
    .topic-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.4);
    }
    
    /* 案例卡片 */
    .case-card {
        background: linear-gradient(135deg, #FFFBF5 0%, #FFF8EE 100%);
        border-radius: 18px;
        padding: 18px;
        margin: 10px 0;
        border: 1px solid #FFE4C4;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .case-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 15px rgba(255, 200, 100, 0.3);
    }
    
    .case-type {
        font-size: 12px;
        color: #E67E22;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .case-preview {
        font-size: 14px;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    /* 结果区域 */
    .result-section {
        background: linear-gradient(135deg, #F0FFF8 0%, #E6FFE6 100%);
        border-radius: var(--border-radius);
        padding: 24px;
        border: 2px solid #90EE90;
        margin-top: 20px;
    }
    
    /* 修改区域 */
    .modify-section {
        background: linear-gradient(135deg, #FFF5F5 0%, #FFE8E8 100%);
        border-radius: var(--border-radius);
        padding: 24px;
        margin-top: 18px;
        border: 2px solid #FFB4B4;
    }
    
    /* 侧边栏 */
    .sidebar-btn {
        position: fixed;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 15px 18px;
        border-radius: 0 20px 20px 0;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        box-shadow: var(--shadow-lg);
        z-index: 100;
        transition: all 0.3s ease;
        writing-mode: vertical-rl;
        text-orientation: mixed;
    }
    
    .sidebar-btn:hover {
        padding-left: 25px;
        box-shadow: 0 6px 25px rgba(74, 144, 226, 0.4);
    }
    
    /* 生成按钮 */
    .generate-btn {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 16px 50px !important;
        font-size: 17px !important;
        font-weight: 600 !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .generate-btn:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 25px rgba(74, 144, 226, 0.5) !important;
    }
    
    /* 操作按钮 */
    .action-btn {
        border-radius: 25px !important;
        font-size: 14px !important;
        padding: 10px 20px !important;
    }
    
    /* 对话框/Modal样式 */
    .modal-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    }
    
    .modal-container.show {
        opacity: 1;
        visibility: visible;
    }
    
    .modal-content {
        background: white;
        border-radius: 24px;
        padding: 30px;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        transform: scale(0.8) translateY(20px);
        transition: all 0.3s ease;
    }
    
    .modal-container.show .modal-content {
        transform: scale(1) translateY(0);
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .modal-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .modal-close {
        background: #f0f0f0;
        border: none;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    .modal-close:hover {
        background: #e0e0e0;
        transform: rotate(90deg);
    }
    
    /* 分割线 */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--primary-light), transparent);
        margin: 20px 0;
    }
    
    /* 提示文本 */
    .hint-text {
        font-size: 13px;
        color: var(--text-secondary);
        margin-top: 8px;
    }
    """

    with gr.Blocks(title="短视频AI文案生成器 v10.0") as app:
        # ===== 标题 =====
        gr.HTML("""
        <div class="header-section">
            <h1>🎬 短视频AI文案生成器</h1>
            <p>v10.0 简洁版 | 通义千问AI</p>
        </div>
        """)
        
        # ===== 侧边历史记录按钮 =====
        gr.HTML("""
        <div class="sidebar-btn" onclick="toggleSidebar()">
            📜 历史记录
        </div>
        """)
        
        # ===== 侧边历史记录栏 =====
        with gr.Column(visible=False) as sidebar:
            gr.HTML("""
            <div style="position: fixed; left: 0; top: 0; width: 350px; height: 100%; background: white; box-shadow: 4px 0 20px rgba(0,0,0,0.1); z-index: 99; padding: 20px; overflow-y: auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3 style="color: #2C3E50; margin: 0;">📜 生成历史</h3>
                    <button onclick="toggleSidebar()" style="background: #f0f0f0; border: none; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; font-size: 16px;">✕</button>
                </div>
            </div>
            """)
        
        # ===== 主内容区 =====
        with gr.Row():
            with gr.Column(scale=3):
                # 步骤1：选择场景
                gr.HTML("""
                <div class="step-card">
                    <div class="step-title">
                        <span class="step-number">1</span>
                        选择场景类型
                    </div>
                """)
                
                scenario = gr.Dropdown(
                    choices=list(SCENARIOS.keys()),
                    value=list(SCENARIOS.keys())[0],
                    label=""
                )
                
                gr.HTML("</div>")
                
                # 步骤2：选择风格
                gr.HTML("""
                <div class="step-card">
                    <div class="step-title">
                        <span class="step-number">2</span>
                        选择文案风格
                    </div>
                """)
                
                style = gr.Dropdown(
                    choices=list(STYLES.keys()),
                    value=list(STYLES.keys())[2],
                    label=""
                )
                
                # 风格对应话题提示
                gr.HTML("""
                <div class="hint-text">💡 点击下方话题可查看相关案例</div>
                """)
                
                topics_output = gr.HTML("")
                cases_output = gr.HTML("")
                
                gr.HTML("</div>")
                
                # 步骤3：输入主题
                gr.HTML("""
                <div class="step-card">
                    <div class="step-title">
                        <span class="step-number">3</span>
                        输入视频主题
                    </div>
                """)
                
                topic_input = gr.Textbox(
                    placeholder="输入你想创作的主题，如：职场生存指南、极简生活...",
                    label="",
                    lines=2
                )
                
                gr.HTML("</div>")
                
                # 生成按钮
                generate_btn = gr.Button("🚀 开始生成", elem_classes="generate-btn")
                
                # 结果区域
                gr.HTML('<div class="result-section"><div class="step-title">✏️ 生成结果</div></div>')
                
                result_output = gr.Textbox(
                    placeholder="生成的文案将显示在这里，你可以直接修改...",
                    label="",
                    lines=12
                )
                
                hint_output = gr.Textbox(label="", lines=1, interactive=False)
                warning_output = gr.Textbox(label="", lines=2, interactive=False)
                messages_state = gr.Textbox(visible=False)
                
                # 操作按钮
                with gr.Row():
                    copy_btn = gr.Button("📋 复制", elem_classes="action-btn")
                    clear_btn = gr.Button("🗑️ 清空", elem_classes="action-btn")
                
                # 修改区域
                gr.HTML('<div class="modify-section"><div class="step-title">🔧 修改反馈</div></div>')
                
                feedback_input = gr.Textbox(
                    placeholder="输入你的修改意见，让AI根据反馈调整文案...",
                    label="",
                    lines=2
                )
                
                with gr.Row():
                    modify_btn = gr.Button("✨ 应用修改", elem_classes="generate-btn")
                    regenerate_btn = gr.Button("🔄 重新生成", elem_classes="action-btn")
                
                modify_status = gr.Textbox(label="", lines=1, interactive=False)
            
            # ===== 右侧辅助区 =====
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="step-card" style="background: linear-gradient(135deg, #F8FBFF 0%, #E8F4FD 100%);">
                    <div class="step-title" style="color: #E67E22;">
                        📚 参考案例
                    </div>
                    <div class="hint-text" style="margin-bottom: 15px;">点击查看各风格的优秀文案</div>
                """)
                
                # 动态案例展示
                cases_display = gr.HTML("")
                
                gr.HTML("</div>")
                
                gr.HTML("""
                <div class="step-card">
                    <div class="step-title">
                        🔄 快捷操作
                    </div>
                    <button class="topic-btn" onclick="document.querySelector('#topic-input').querySelector('textarea').value='职场PUA'">💼 职场</button>
                    <button class="topic-btn" onclick="document.querySelector('#topic-input').querySelector('textarea').value='分手治愈'">💔 情感</button>
                    <button class="topic-btn" onclick="document.querySelector('#topic-input').querySelector('textarea').value='极简生活'">🏠 生活</button>
                    <button class="topic-btn" onclick="document.querySelector('#topic-input').querySelector('textarea').value='减肥逆袭'">💄 颜值</button>
                </div>
                """)

        # ===== 事件绑定 =====
        # 风格变化时更新话题和案例
        style.change(
            fn=get_cases_for_style,
            inputs=[style],
            outputs=[cases_display]
        )
        
        # 生成文案
        generate_btn.click(
            fn=generate_script,
            inputs=[scenario, style, topic_input, messages_state],
            outputs=[result_output, hint_output, warning_output, messages_state]
        )
        
        # 复制
        copy_btn.click(
            fn=lambda x: "✅ 已复制到剪贴板！" if x else "⚠️ 文案为空",
            inputs=[result_output],
            outputs=[modify_status]
        )
        
        # 清空
        clear_btn.click(
            fn=lambda: ("", "", "", "", ""),
            outputs=[result_output, hint_output, warning_output, messages_state, modify_status]
        )
        
        # 修改
        modify_btn.click(
            fn=modify_script,
            inputs=[feedback_input, result_output, messages_state, topic_input, scenario, style],
            outputs=[result_output, modify_status, warning_output, messages_state]
        )
        
        # 重新生成
        regenerate_btn.click(
            fn=generate_script,
            inputs=[scenario, style, topic_input, messages_state],
            outputs=[result_output, hint_output, warning_output, messages_state]
        )
        
        # 初始化案例显示
        app.load(
            fn=get_cases_for_style,
            inputs=[],
            outputs=[cases_display]
        )

    return app


# ===== 启动 =====
if __name__ == "__main__":
    print("=" * 50)
    print("短视频AI文案生成器 v10.0")
    print("简洁步骤式界面 | 清新淡蓝色主题")
    print("访问地址：http://localhost:7860")
    print("=" * 50)
    
    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
