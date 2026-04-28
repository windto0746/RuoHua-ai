# -*- coding: utf-8 -*-
"""
短视频AI文案生成器 v8.0 修复版
- API Key通过环境变量保护
- 修复Gradio 6.x兼容性
- 修复API响应格式
"""

import os
import json
from datetime import datetime
import gradio as gr
import dashscope
from dashscope import Generation
from dotenv import load_dotenv

# ============================================
# 加载环境变量保护API Key
# ============================================
import sys

# 支持多种环境变量名称
ENV_KEYS = ['DASHSCOPE_API_KEY', 'API_KEY', 'DASHSCOPE_KEY']

# 1. 尝试从.env文件加载（本地环境）
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path, override=False)

# 2. 尝试从环境变量读取
API_KEY = ''
for key in ENV_KEYS:
    API_KEY = os.environ.get(key, '')
    if API_KEY:
        print(f"[配置] 使用环境变量: {key}")
        break

# 3. 如果都读取不到，尝试fallback（仅用于调试）
if not API_KEY:
    # 最后的fallback：使用直接赋值的变量（仅本地调试用）
    try:
        from config import DASHSCOPE_API_KEY as fallback_key
        API_KEY = fallback_key
        print("[配置] 使用config.py中的API Key")
    except ImportError:
        pass

if not API_KEY:
    print("\n" + "=" * 50)
    print("❌ API Key 未设置!")
    print("=" * 50)
    print("\n【本地运行】请在项目根目录创建 .env 文件：")
    print("   DASHSCOPE_API_KEY=你的API密钥")
    print("\n【GitHub云端】请在 Settings > Secrets 中添加：")
    print("   Name: DASHSCOPE_API_KEY")
    print("   Value: 你的API密钥")
    print("\n【或者】在终端运行前设置环境变量：")
    print("   Windows: set DASHSCOPE_API_KEY=你的密钥")
    print("   Linux/Mac: export DASHSCOPE_API_KEY=你的密钥")
    print("=" * 50)
    sys.exit(1)

dashscope.api_key = API_KEY

HISTORY_FILE = "history.json"

# ============================================
# 敏感词库
# ============================================
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
    """内容审核"""
    warnings = []
    filtered_text = text
    
    for category, words in SENSITIVE_WORDS.items():
        for word in words:
            if word in filtered_text:
                filtered_text = filtered_text.replace(word, '*' * len(word))
                warnings.append(f"[{category}] 已替换敏感词: {word}")
    
    for word in PLATFORM_WARNING_WORDS:
        if word in text:
            count = text.count(word)
            warnings.append(f"[平台规则] 建议减少使用 '{word}' (出现{count}次)")
    
    return filtered_text, warnings

# ============================================
# 专业Prompt模板库
# ============================================
PROMPTS = {
    ('narrative', '感情系'): """你是一个资深的小红书情感博主，3年创作经验，擅长写能引发深度情感共鸣的叙事型文案。

【场景定义】这是"重叙述"场景，文案作为视频中作者故事与价值观阐述的主要载体。
【字数要求】80-150字，要有完整的叙事弧度
【风格要求】文艺伤感、有深度、引发共鸣、让人看完想说"太真实了"
【结构要求】采用"场景描写 → 情感铺陈 → 升华感悟"三段式
【格式要求】每句话单独成段，末尾可加emoji，制造"画面感"

【禁止事项】
✗ 避免空泛的情感语录
✗ 避免流水账叙述
✗ 避免过度煽情显得做作
✓ 必须有具体细节（时间、地点、人物、对话）

请根据用户给的主题，写一篇符合上述要求的文案。""",

    ('narrative', '抽象系'): """你是一个深谙互联网"抽象文化"的年轻创作者，擅长写让人"笑死"的无厘头叙事文案。

【场景定义】这是"重叙述"场景，文案作为搞笑/猎奇内容的故事载体。
【字数要求】60-100字，要有完整的"抽象叙事"
【风格要求】无厘头、反转、出人意料、制造"意想不到"的效果
【结构要求】制造反差感，结局要出人意料

请根据用户给的主题，写一篇符合上述要求的文案。""",

    ('narrative', '启发系'): """你是一个小红书头部治愈系博主，擅长写让人感到"被理解"的温柔叙事。

【场景定义】这是"重叙述"场景，文案作为治愈/励志内容的故事载体。
【字数要求】80-120字，要有"娓娓道来"的感觉
【风格要求】温柔治愈、文艺清新、有力量但不说教

请根据用户给的主题，写一篇符合上述要求的文案。""",

    ('narrative', '种草系'): """你是一个小红书头部种草博主，擅长写让人"忍不住想点进去"的种草型叙事文案。

【场景定义】这是"重叙述"场景，文案作为产品/景点/服务推荐的详细推荐词。
【字数要求】100-150字，要有完整的推荐逻辑
【风格要求】真实感、场景化、有记忆点
【结构要求】制造好奇心 → 场景描述 → 独特卖点 → 行动引导

请根据用户给的主题，写一篇符合上述要求的文案。""",

    ('summary', '感情系'): """你是一个资深的小红书情感博主，擅长写精炼的情感金句，让人看完就想点赞收藏。

【场景定义】这是"重总结"场景，文案是视频内容的主旨升华/金句点睛。
【字数要求】10-20字，越精炼越有力量
【风格要求】文艺伤感、一针见血、引发共鸣

【正面示例】
"不是不想恋爱，是不想随便恋爱后更孤独。"
"后来才明白，没人能救赎谁，只能自己放过自己。"
"懂事的人，连崩溃都要挑时间。"

请根据用户给的主题，写一句符合上述要求的金句。""",

    ('summary', '抽象系'): """你是一个深谙互联网"抽象文化"的年轻创作者，擅长写让人"笑喷"的一句话抽象文案。

【场景定义】这是"重总结"场景，文案是视频内容的"抽象升华"。
【字数要求】10-20字，要"短小精悍出乎意料"
【风格要求】无厘头、反转、制造"反差萌"

【正面示例】
"生活不止眼前的苟且，还有读不懂的诗和去不了的远方。"
"上帝给你关上一扇门，顺便把窗户焊死了。"

请根据用户给的主题，写一句符合上述要求的抽象文案。""",

    ('summary', '启发系'): """你是一个小红书治愈成长类博主，擅长写让人感到"被理解"的金句。

【场景定义】这是"重总结"场景，文案是视频内容的立意升华/心灵金句。
【字数要求】10-20字，要有"一语点醒梦中人"的感觉
【风格要求】温柔治愈、文艺清新

【正面示例】
"允许自己偶尔脆弱，也是一种坚强。"
"慢一点也没关系，你已经在路上了。"

请根据用户给的主题，写一句符合上述要求的治愈金句。""",

    ('summary', '种草系'): """你是一个小红书头部种草博主，擅长写让人"立刻想下单"的一句话安利。

【场景定义】这是"重总结"场景，文案是视频/内容的"一句话安利"。
【字数要求】10-20字，要有"冲动感"
【风格要求】真实感、冲击力

【正面示例】
"用了三年了，离不开了。"
"这个价格这个品质，老板是不是傻？"

请根据用户给的主题，写一句符合上述要求的种草文案。""",

    ('story', '感情系'): """你是一个专业的小红书故事类内容创作者，擅长写能引发深度情感共鸣的完整故事。

【场景定义】这是"长篇故事"场景，文案是视频的主要内容载体，以完整故事叙述为核心。
【字数要求】500-2000字，要讲述一个完整的、有起伏的故事
【风格要求】文艺伤感、有血有肉、让人产生强烈的代入感

请根据用户给的主题，写一篇符合上述要求的完整故事。""",

    ('story', '抽象系'): """你是一个专业的小红书"抽象文学"创作者，擅长写让人"脑洞大开"的荒诞故事。

【场景定义】这是"长篇故事"场景，以"无厘头+反转"为核心。
【字数要求】300-1500字，要有完整的"抽象叙事"
【风格要求】荒诞搞笑 + 出人意料的反转

请根据用户给的主题，写一篇符合上述要求的抽象故事。""",

    ('story', '启发系'): """你是一个专业的小红书治愈成长类内容创作者，擅长写温暖人心的故事。

【场景定义】这是"长篇故事"场景，以真实感人的故事传递力量和希望。
【字数要求】500-2000字，要有"娓娓道来"的叙事感
【风格要求】温柔治愈、真实可信、让人感到被理解、被治愈

请根据用户给的主题，写一篇符合上述要求的治愈故事。""",

    ('story', '种草系'): """你是一个专业的小红书探店/测评类内容创作者，擅长写让人"身临其境"的推荐文案。

【场景定义】这是"长篇故事"场景，以故事化的方式讲述体验过程。
【字数要求】500-2000字，要有完整的"体验叙事"
【风格要求】场景化、细节丰富、有代入感

请根据用户给的主题，写一篇符合上述要求的种草故事。""",
}

# ============================================
# 场景和风格定义
# ============================================
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

HOT_TOPICS = {
    "职场": ["职场PUA", "裸辞", "打工人", "职场生存法则", "薪资谈判"],
    "情感": ["原生家庭", "分手治愈", "婚姻焦虑", "恋爱技巧", "独居生活"],
    "生活": ["极简生活", "独居女孩", "自律打卡", "断舍离", "时间管理"],
    "颜值": ["早C晚A", "精简护肤", "减肥逆袭", "穿搭分享", "变美日记"]
}

# ============================================
# 核心功能
# ============================================
def generate_script(scenario, style, topic):
    """调用API生成文案"""
    if not topic or not topic.strip():
        return "请输入视频主题", ""

    try:
        scenario_info = SCENARIOS.get(scenario, SCENARIOS["📖 重叙述型"])
        scene_key = scenario_info["key"]
        style_name = STYLES.get(style, "启发系")
        
        system_prompt = PROMPTS.get((scene_key, style_name), PROMPTS[('narrative', '启发系')])

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'请根据主题"{topic}"和风格"{style_name}"，生成文案。'}
        ]

        response = Generation.call(model='qwen-plus', messages=messages)

        if response.status_code == 200:
            result = response.output.text
            filtered_result, warnings = content_audit(result)
            save_history(topic, filtered_result, scenario, style)
            
            hint = f"📝 {scenario} | {scenario_info['words']}"
            if warnings:
                warning_text = "\n".join([f"⚠️ {w}" for w in warnings])
                return filtered_result, f"{hint}\n{warning_text}"
            return filtered_result, hint
        else:
            error_msg = response.message if hasattr(response, 'message') else '未知错误'
            return f"生成失败: {error_msg}", ""

    except Exception as e:
        return f"生成失败: {str(e)}", ""


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
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
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
    with gr.Blocks(title="短视频AI文案生成器 v8.0") as app:
        gr.Markdown("""# 🎬 短视频AI文案生成器
## v8.0 清新版 | 通义千问AI | 专业Prompt驱动""")

        with gr.Row():
            with gr.Column(scale=2):
                scenario = gr.Dropdown(
                    choices=list(SCENARIOS.keys()),
                    value=list(SCENARIOS.keys())[0],
                    label="📌 第一步：选择场景类型"
                )
                
                style = gr.Dropdown(
                    choices=list(STYLES.keys()),
                    value=list(STYLES.keys())[2],
                    label="💫 第二步：选择文案风格"
                )
                
                topic_input = gr.Textbox(
                    placeholder="输入你想创作的主题，如：职场生存指南、极简生活...",
                    label="📝 第三步：输入视频主题",
                    lines=2
                )
                
                generate_btn = gr.Button("🚀 开始生成", variant="primary")
                
                result_output = gr.Textbox(
                    placeholder="生成的文案将显示在这里，你可以直接修改...",
                    label="✏️ 生成结果（可直接编辑）",
                    lines=12
                )
                hint_output = gr.Textbox(label="提示", lines=1, interactive=False)

                with gr.Row():
                    copy_btn = gr.Button("📋 复制")
                    save_btn = gr.Button("💾 保存")
                    clear_btn = gr.Button("🗑️ 清空")

                status_msg = gr.Textbox(label="", visible=False, lines=1)

            with gr.Column(scale=1):
                gr.Markdown("### 🔥 热门话题")
                for category, topics in HOT_TOPICS.items():
                    gr.Markdown(f"**{category}**")
                    for t in topics:
                        gr.Button(t, size="sm")
                
                gr.Markdown("### 📜 历史记录")
                history_list = gr.JSON(value=load_history())
                refresh_btn = gr.Button("🔄 刷新")

        generate_btn.click(fn=generate_script, inputs=[scenario, style, topic_input], outputs=[result_output, hint_output])
        refresh_btn.click(fn=load_history, outputs=[history_list])
        copy_btn.click(fn=lambda x: "✅ 已复制！" if x else "⚠️ 文案为空", inputs=[result_output], outputs=[status_msg])
        clear_btn.click(fn=lambda: ("", "", ""), outputs=[result_output, hint_output, status_msg])
        status_msg.change(fn=lambda x: gr.update(visible=bool(x)), inputs=[status_msg], outputs=[status_msg])

    return app


if __name__ == "__main__":
    print("=" * 50)
    print("短视频AI文案生成器 v8.0")
    print("清新蓝色主题 | 专业Prompt | 敏感词过滤")
    print("API Key保护: 已启用(.env)")
    print("访问地址：http://localhost:7860")
    print("=" * 50)

    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860, share=True)
