"""
短视频AI文案生成器 v6.0 完整版
- 接入通义千问AI API
- 历史记录功能
- 文案编辑修改功能
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
# 数据定义
# ============================================

SCENARIOS = {
    "重叙述型": "讲述故事型：通过真实故事引发共鸣，情节跌宕起伏，结尾反转或升华",
    "重总结型": "观点输出型：开篇提出核心观点，分点论述，干货满满，适合知识分享",
    "长篇故事型": "完整叙事型：有完整的故事线，包括起承转合，吸引人从头看到尾"
}

STYLES = {
    "情绪渲染型": "情感充沛，引发共鸣，让人感同身受",
    "搞笑幽默型": "幽默风趣，金句频出，让人笑着看完",
    "正能量激励型": "激励人心，给人与力量和勇气",
    "种草带货型": "种草推荐，突出卖点，引导购买决策"
}

HOT_TOPICS = {
    "职场": ["职场PUA", "裸辞", "打工人", "职场生存法则", "薪资谈判"],
    "情感": ["原生家庭", "分手治愈", "婚姻焦虑", "恋爱技巧", "独居生活"],
    "生活": ["极简生活", "独居女孩", "自律打卡", "断舍离", "时间管理"],
    "颜值": ["早C晚A", "精简护肤", "减肥逆袭", "穿搭分享", "变美日记"]
}

CASES = [
    {
        "style": "情绪渲染型",
        "preview": "凌晨三点，我第8次加班到崩溃边缘...",
        "full": """【凌晨三点的崩溃】

凌晨三点，我第8次加班到崩溃边缘。

手机屏幕亮起，是妈妈的消息："睡了吗？"

那一刻，眼泪真的忍不住了。

我已经记不清，这是第几次错过家里的电话；
第几次推掉朋友的聚会；
第几次忘记自己曾经也是个会做梦的人。

我们都在拼命奔跑，却忘了问自己：
这样的生活，真的是我们想要的吗？

如果你也累了，就停下来歇一歇吧。
允许自己慢一点，也是一种勇气。

#凌晨三点的崩溃 #职场焦虑 #共鸣"""
    },
    {
        "style": "正能量激励型",
        "preview": "允许自己慢一点，也是一种成长...",
        "full": """【允许自己慢一点】

允许自己慢一点，也是一种成长。

25岁那年，我辞掉了月薪3万的工作，选择从零开始学习画画。

所有人都说我疯了，但只有我知道，这是我内心最真实的声音。

现在的我，每天画8个小时，虽然收入只有以前的十分之一，但我找到了真正的快乐。

人生不是赛跑，不必每一步都赢。找到属于自己的节奏，才是最重要的。

#成长 #自律 #生活方式"""
    },
    {
        "style": "种草带货型",
        "preview": "用了三个月，我的皮肤状态直接开挂...",
        "full": """【这个精华真的绝了】

姐妹们，这个精华我真的按头安利！

用了三个月，我的皮肤状态直接开挂！

质地超级清爽，一抹就化开，上脸完全不油腻，吸收超快~

坚持用了一个月：
毛孔肉眼可见变小了
皮肤光泽度提升了
熬夜后的暗沉也改善了很多

而且性价比超高，学生党也能冲！

现在下单还有专属优惠~

#精华推荐 #护肤 #好物分享"""
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
        system_prompt = f"""你是一位专业的短视频文案创作者。

场景类型：{scenario}
风格要求：{STYLES.get(style, '')}

请创作一个引人入胜的短视频文案，要求：
1. 开头3秒要有吸引力，能抓住观众
2. 中间内容有信息量或情感共鸣
3. 结尾引导互动
4. 包含适当的标签话题
5. 总时长控制在60-90秒
6. 语言要口语化、自然

直接输出文案内容。"""

        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"帮我创作一个关于「{topic}」的短视频文案"}
            ],
            temperature=0.8,
            max_tokens=800
        )

        script = response.choices[0].message.content
        save_history(topic, script, scenario, style)
        return script, ""

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
    custom_css = """
    .main-header {text-align: center; padding: 20px; background: linear-gradient(135deg, #FF6B6B 0%, #ee5a5a 100%); border-radius: 16px; margin-bottom: 20px;}
    .topic-tag {display: inline-block; background: #FF6B6B; color: white; padding: 6px 14px; border-radius: 20px; margin: 4px; cursor: pointer; font-size: 14px;}
    .topic-tag:hover {transform: scale(1.05); box-shadow: 0 4px 15px rgba(255,107,107,0.4);}
    .result-box {background: #fffbf0; border-radius: 12px; padding: 20px; border: 2px solid #FF6B6B;}
    """

    with gr.Blocks(title="短视频AI文案生成器 v6.0") as app:
        gr.HTML("""
        <div class="main-header">
            <h1 style="color: white; margin: 0;">短视频AI文案生成器</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">v6.0 完整版 | 通义千问AI驱动</p>
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 第一步：选择场景")
                scenario = gr.Dropdown(choices=list(SCENARIOS.keys()), value=list(SCENARIOS.keys())[0], label="场景类型")

                gr.Markdown("### 第二步：选择风格")
                style = gr.Dropdown(choices=list(STYLES.keys()), value=list(STYLES.keys())[2], label="文案风格")

                gr.Markdown("### 第三步：输入主题")
                topic_input = gr.Textbox(placeholder="例如：职场生存指南、极简生活...", label="视频主题", lines=2)

                generate_btn = gr.Button("开始生成", variant="primary", size="lg")

                gr.Markdown("### 生成结果（可直接编辑）")
                result_output = gr.Textbox(placeholder="生成的文案将显示在这里，你可以直接修改...", label="AI生成的文案", lines=15)

                with gr.Row():
                    copy_btn = gr.Button("复制文案", size="sm")
                    save_btn = gr.Button("保存修改", size="sm")
                    clear_btn = gr.Button("清空", size="sm")

                status_msg = gr.Textbox(label="状态", visible=False)

            with gr.Column(scale=1):
                gr.Markdown("### 热门话题")
                for category, topics in HOT_TOPICS.items():
                    gr.HTML(f"<b>{category}：</b>")
                    tags = " ".join([f"<span class='topic-tag' onclick='setTopic(\"{t}\")'>{t}</span>" for t in topics])
                    gr.HTML(f"<div style='margin-bottom:10px'>{tags}</div>")

                gr.HTML("<hr>")

                gr.Markdown("### 历史记录")
                history_list = gr.JSON(value=load_history(), label="最近生成")
                refresh_btn = gr.Button("刷新历史", size="sm")

                gr.HTML("<hr>")

                gr.Markdown("### 优秀案例")
                for case in CASES:
                    gr.Markdown(f"**{case['style']}**：{case['preview']}")

        # 事件绑定
        generate_btn.click(
            fn=generate_script_ai,
            inputs=[scenario, style, topic_input],
            outputs=[result_output, status_msg]
        )

        refresh_btn.click(fn=load_history, outputs=[history_list])

        copy_btn.click(
            fn=lambda x: "已复制到剪贴板！" if x else "文案为空",
            inputs=[result_output],
            outputs=[status_msg]
        )

        clear_btn.click(fn=lambda: ("", ""), outputs=[result_output, status_msg])

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
    print("短视频AI文案生成器 v6.0")
    print("访问地址：http://localhost:7860")
    print("=" * 50)

    app = build_ui()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, css=custom_css)
