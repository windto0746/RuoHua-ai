"""
短视频AI文案生成器 v7.0
- 淡蓝色清新界面
- 圆角卡片设计
- 场景字数严格控制
"""

import gradio as gr
import json
import os
from datetime import datetime
from openai import OpenAI

# ============================================
# 配置
# ============================================

DASHSCOPE_API_KEY = "sk-15d8a880bb6a41e7900e9e8c44bfa398"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=BASE_URL
)

HISTORY_FILE = "history.json"

# ============================================
# 场景定义（严格字数控制）
# ============================================

SCENARIOS = {
    "📖 重叙述型": {
        "desc": "视频配文型",
        "words": "80-150",
        "prompt": """你是一位专业的短视频文案创作者。

请创作一个【视频配文型】短视频文案，严格要求：
- 字数：80-150字
- 结构：开头抓眼球 → 中间叙述铺垫 → 结尾留悬念/引导互动
- 风格：叙事性强，画面感强，适合配合视频画面
- 语言：口语化、有节奏感
- 标签：2-3个热门话题标签

直接输出文案，不要解释。"""
    },
    "✨ 重总结型": {
        "desc": "金句升华型",
        "words": "10-20",
        "prompt": """你是一位金句大师。

请创作一个【金句升华型】短视频文案，严格要求：
- 字数：10-20字（越短越有力！）
- 特点：一句话戳中人心，引发共鸣
- 风格：精炼、有洞察、直击灵魂
- 用途：适合知识类、观点类视频的结尾升华
- 不需要标签

直接输出金句，不要解释。"""
    },
    "📚 长篇故事型": {
        "desc": "故事主线型",
        "words": "500-2000",
        "prompt": """你是一位故事叙述大师。

请创作一个【故事主线型】短视频文案，严格要求：
- 字数：500-2000字
- 结构：起（开头钩子）→ 承（发展铺垫）→ 转（冲突高潮）→ 合（结尾升华）
- 风格：完整的故事线，有人物、有冲突、有转折、有结局
- 情感：能让观众产生情感共鸣
- 标签：3-5个热门话题标签
- 节奏：前3秒必须有强烈吸引力

直接输出故事文案，不要解释。"""
    }
}

STYLES = {
    "情绪渲染型": "情感充沛，引发共鸣，让人感同身受",
    "搞笑幽默型": "幽默风趣，金句频出，让人笑着看完",
    "正能量激励型": "激励人心，给人与力量和勇气",
    "种草带货型": "种草推荐，突出卖点，引导购买决策"
}

# 热门话题
HOT_TOPICS = {
    "职场": ["职场PUA", "裸辞", "打工人", "职场生存法则", "薪资谈判", "职场焦虑", "加班", "同事关系"],
    "情感": ["原生家庭", "分手治愈", "婚姻焦虑", "恋爱技巧", "独居生活", "相亲", "异地恋", "复合"],
    "生活": ["极简生活", "独居女孩", "自律打卡", "断舍离", "收纳整理", "生活习惯", "时间管理", "独居男孩"],
    "颜值": ["早C晚A", "精简护肤", "减肥逆袭", "穿搭分享", "变美日记", "护肤心得", "发型推荐", "美妆教程"]
}

# 优秀案例
CASES = [
    {
        "type": "重叙述型",
        "preview": "凌晨三点，我第8次加班到崩溃边缘...",
        "content": """【凌晨三点的崩溃】

凌晨三点，我第8次加班到崩溃边缘。

手机屏幕亮起，是妈妈的消息："睡了吗？"

那一刻，眼泪真的忍不住了。

我们已经多久没有好好陪过家人？
多久没有准时吃过一顿饭？
多久没有12点前睡过觉了？

如果有一天我不在了，这些加班又有什么意义？

#凌晨三点的崩溃 #职场焦虑 #打工人"""
    },
    {
        "type": "重总结型",
        "preview": "允许自己慢一点，也是一种成长",
        "content": """允许自己慢一点，也是一种成长。"""
    },
    {
        "type": "长篇故事型",
        "preview": "我辞掉了月薪3万的工作...",
        "content": """【我辞职的那一天】

"你疯了吗？月薪3万说不要就不要了？"

那天，我爸妈的眼神我这辈子都忘不了。

我叫小林，今年28岁，在互联网大厂工作了5年。

从月薪8000拼到月薪3万，所有人都说我成功了。

但只有我知道，每天凌晨2点才到家，早上6点又要爬起来的日子，我已经撑不住了。

第108次加班到崩溃的那个晚上，我终于递上了辞职信。

爸妈骂了我整整一个星期。

但现在，我想告诉你：

工资可以再赚，但生活只有一次。

如果你也在996里迷失了自己，听我说：

你不必等到身体垮掉才学会停下。

#辞职 #职场 #成长 #裸辞"""
    }
]

# ============================================
# 核心功能
# ============================================

def generate_script_ai(scenario, style, topic):
    """调用通义千问API生成文案"""
    if not topic or not topic.strip():
        return "请输入视频主题", ""

    try:
        scenario_info = SCENARIOS.get(scenario, SCENARIOS["📖 重叙述型"])
        
        system_prompt = scenario_info["prompt"]
        # 添加风格要求
        system_prompt += f"\n\n风格要求：{STYLES.get(style, '')}"

        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"帮我创作一个关于「{topic}」的短视频文案"}
            ],
            temperature=0.8,
            max_tokens=2500
        )

        script = response.choices[0].message.content
        save_history(topic, script, scenario, style)
        
        # 生成提示信息
        hint = f"📝 {scenario} | 字数要求：{scenario_info['words']}字"
        
        return script, hint

    except Exception as e:
        return f"生成失败：{str(e)}", ""


def save_history(topic, script, scenario, style):
    """保存历史记录"""
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
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "preview": script[:50] + "..." if len(script) > 50 else script
    })

    history = history[:20]

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_history():
    """加载历史记录"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []


# ============================================
# 构建界面
# ============================================

def build_ui():
    """构建清新蓝色主题界面"""
    
    custom_css = """
    /* 全局样式 */
    :root {
        --primary: #4A90E2;
        --primary-light: #5BA3F5;
        --primary-dark: #3A7BC8;
        --bg-gradient: linear-gradient(135deg, #E8F4FD 0%, #D6EBFF 100%);
        --card-bg: #FFFFFF;
        --text-primary: #2C3E50;
        --text-secondary: #7F8C8D;
        --border-radius: 16px;
        --shadow: 0 4px 20px rgba(74, 144, 226, 0.15);
        --shadow-hover: 0 8px 30px rgba(74, 144, 226, 0.25);
    }
    
    body {
        background: var(--bg-gradient) !important;
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }
    
    /* 标题区域 */
    .header-section {
        background: linear-gradient(135deg, #4A90E2 0%, #67B8F5 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(74, 144, 226, 0.3);
    }
    
    .header-section h1 {
        color: white !important;
        font-size: 28px !important;
        font-weight: 600 !important;
        margin: 0 0 8px 0 !important;
    }
    
    .header-section p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 15px !important;
        margin: 0 !important;
    }
    
    /* 主卡片 */
    .main-card {
        background: var(--card-bg);
        border-radius: var(--border-radius);
        padding: 28px;
        box-shadow: var(--shadow);
        border: 1px solid rgba(74, 144, 226, 0.1);
    }
    
    /* 侧边栏卡片 */
    .sidebar-card {
        background: var(--card-bg);
        border-radius: var(--border-radius);
        padding: 22px;
        box-shadow: var(--shadow);
        margin-bottom: 18px;
        border: 1px solid rgba(74, 144, 226, 0.1);
    }
    
    /* 场景选择卡片 */
    .scenario-card {
        background: linear-gradient(135deg, #F0F7FF 0%, #E3F0FF 100%);
        border-radius: 14px;
        padding: 18px;
        margin: 12px 0;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .scenario-card:hover {
        border-color: var(--primary);
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    .scenario-card.selected {
        border-color: var(--primary);
        background: linear-gradient(135deg, #E8F4FD 0%, #D6EBFF 100%);
    }
    
    .scenario-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 6px;
    }
    
    .scenario-desc {
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 4px;
    }
    
    .scenario-words {
        font-size: 12px;
        color: var(--primary);
        font-weight: 500;
    }
    
    /* 话题标签 */
    .topic-tag {
        display: inline-block;
        background: linear-gradient(135deg, #4A90E2, #67B8F5);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        cursor: pointer;
        font-size: 13px;
        transition: all 0.3s ease;
        border: none;
    }
    
    .topic-tag:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.4);
    }
    
    /* 历史记录项 */
    .history-item {
        background: linear-gradient(135deg, #F8FBFF 0%, #F0F7FF 100%);
        border-radius: 12px;
        padding: 14px 16px;
        margin: 10px 0;
        border-left: 4px solid var(--primary);
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        background: linear-gradient(135deg, #E8F4FD 0%, #D6EBFF 100%);
        transform: translateX(4px);
    }
    
    .history-topic {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 14px;
        margin-bottom: 6px;
    }
    
    .history-meta {
        font-size: 12px;
        color: var(--text-secondary);
    }
    
    /* 案例卡片 */
    .case-card {
        background: linear-gradient(135deg, #FFFAF0 0%, #FFF5E6 100%);
        border-radius: 14px;
        padding: 16px;
        margin: 10px 0;
        border: 1px solid #FFE4C4;
    }
    
    .case-type {
        font-size: 12px;
        color: #E67E22;
        font-weight: 600;
        margin-bottom: 6px;
    }
    
    .case-preview {
        font-size: 13px;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    /* 结果区域 */
    .result-section {
        background: linear-gradient(135deg, #F0FFF4 0%, #E6FFE6 100%);
        border-radius: 14px;
        padding: 20px;
        margin-top: 20px;
        border: 2px solid #90EE90;
    }
    
    /* 生成按钮 */
    .generate-btn {
        background: linear-gradient(135deg, #4A90E2 0%, #67B8F5 100%) !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 14px 35px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .generate-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.5) !important;
    }
    
    /* 操作按钮 */
    .action-btn {
        border-radius: 20px !important;
        font-size: 13px !important;
    }
    
    /* 分类标题 */
    .section-title {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 15px !important;
        padding-bottom: 10px !important;
        border-bottom: 2px solid var(--primary) !important;
        display: inline-block !important;
    }
    
    /* 分割线 */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
        margin: 20px 0;
    }
    
    /* 输入框 */
    input[type="text"], textarea {
        border-radius: 12px !important;
        border: 2px solid #E8F4FD !important;
        padding: 14px !important;
        font-size: 15px !important;
    }
    
    input[type="text"]:focus, textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2) !important;
    }
    """

    with gr.Blocks(title="短视频AI文案生成器 v7.0") as app:
        
        # ========== 标题 ==========
        gr.HTML("""
        <div class="header-section">
            <h1>🎬 短视频AI文案生成器</h1>
            <p>✨ v7.0 清新版 | 通义千问AI驱动 | 智能场景匹配</p>
        </div>
        """)

        # ========== 主布局 ==========
        with gr.Row():
            # ---------- 左侧：生成功能 ----------
            with gr.Column(scale=2):
                with gr.Group():
                    gr.HTML('<div class="section-title">📌 第一步：选择场景类型</div>')
                    
                    # 场景选择卡片
                    for name, info in SCENARIOS.items():
                        emoji = name.split()[0]
                        with gr.Group():
                            scenario_card = gr.HTML(f"""
                            <div class="scenario-card" id="card-{name}">
                                <div class="scenario-title">{name}</div>
                                <div class="scenario-desc">{info['desc']}</div>
                                <div class="scenario-words">📏 字数要求：{info['words']}字</div>
                            </div>
                            """)
                    
                    # 场景下拉选择（与卡片联动）
                    scenario = gr.Dropdown(
                        choices=list(SCENARIOS.keys()),
                        value=list(SCENARIOS.keys())[0],
                        label="",
                        visible=True
                    )

                with gr.Group():
                    gr.HTML('<div class="section-title">💫 第二步：选择文案风格</div>')
                    style = gr.Dropdown(
                        choices=list(STYLES.keys()),
                        value=list(STYLES.keys())[2],
                        label=""
                    )

                with gr.Group():
                    gr.HTML('<div class="section-title">📝 第三步：输入视频主题</div>')
                    topic_input = gr.Textbox(
                        placeholder="输入你想创作的主题，如：职场生存指南、极简生活...",
                        label="",
                        lines=2
                    )

                # 生成按钮
                generate_btn = gr.Button("🚀 开始生成", elem_classes="generate-btn")

                # ========== 结果展示 ==========
                gr.HTML('<div class="result-section"><div class="section-title">✏️ 生成结果（可直接编辑）</div></div>')
                
                result_output = gr.Textbox(
                    placeholder="生成的文案将显示在这里，你可以直接修改...",
                    label="",
                    lines=12
                )
                
                hint_output = gr.Textbox(label="", lines=1, interactive=False)

                # 操作按钮
                with gr.Row():
                    copy_btn = gr.Button("📋 复制", elem_classes="action-btn")
                    save_btn = gr.Button("💾 保存", elem_classes="action-btn")
                    clear_btn = gr.Button("🗑️ 清空", elem_classes="action-btn")

                status_msg = gr.Textbox(label="", visible=False, lines=1)

            # ---------- 右侧：辅助模块 ----------
            with gr.Column(scale=1):
                
                # 热门话题
                gr.HTML('<div class="sidebar-card"><div class="section-title">🔥 热门话题</div>')
                
                for category, topics in HOT_TOPICS.items():
                    gr.HTML(f'<div style="margin: 12px 0 8px 0; font-weight: 600; color: #4A90E2;">{category}</div>')
                    tags_html = " ".join([f'<button class="topic-tag" onclick="document.querySelector(\'#{topic_input_id}\').value=\'{t}\'">{t}</button>' 
                                         for t in topics])
                    gr.HTML(f'<div>{tags_html}</div>')
                
                gr.HTML('</div>')

                # 历史记录
                gr.HTML('<div class="sidebar-card"><div class="section-title">📜 历史记录</div>')
                
                history_list = gr.JSON(value=load_history(), label="")
                refresh_btn = gr.Button("🔄 刷新", elem_classes="action-btn")
                
                gr.HTML('</div>')

                # 优秀案例
                gr.HTML('<div class="sidebar-card"><div class="section-title">📚 优秀案例</div>')
                
                for case in CASES:
                    gr.HTML(f"""
                    <div class="case-card">
                        <div class="case-type">{case['type']}</div>
                        <div class="case-preview">{case['preview']}</div>
                    </div>
                    """)
                
                gr.HTML('</div>')

        # 隐藏的topic_input的ID
        topic_input_id = "c5"

        # ========== 事件绑定 ==========
        generate_btn.click(
            fn=generate_script_ai,
            inputs=[scenario, style, topic_input],
            outputs=[result_output, hint_output]
        )

        refresh_btn.click(fn=load_history, outputs=[history_list])

        copy_btn.click(
            fn=lambda x: "✅ 已复制到剪贴板！" if x else "⚠️ 文案为空",
            inputs=[result_output],
            outputs=[status_msg]
        )

        clear_btn.click(
            fn=lambda: ("", "", ""),
            outputs=[result_output, hint_output, status_msg]
        )

        status_msg.change(
            fn=lambda x: gr.update(visible=bool(x)),
            inputs=[status_msg],
            outputs=[status_msg]
        )

    return app


# ============================================
# 启动
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("短视频AI文案生成器 v7.0")
    print("清新蓝色主题 | 严格字数控制")
    print("访问地址：http://localhost:7860")
    print("=" * 50)

    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, css=custom_css)
