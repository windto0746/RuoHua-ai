"""
短视频AI文案生成器 v5.0 Web版
基于Gradio构建的现代化界面
"""

import gradio as gr
import json
import random
from datetime import datetime

# ============================================
# 数据定义
# ============================================

# 场景类型
SCENARIOS = [
    "重叙述型 - 讲述故事，引发共鸣",
    "重总结型 - 观点输出，干货满满",
    "长篇故事型 - 完整叙事，吸引关注"
]

# 风格选项（带emoji）
STYLES = [
    ("情绪渲染型", "💔"),
    ("搞笑幽默型", "🤪"),
    ("正能量激励型", "✨"),
    ("种草带货型", "🛒")
]

# 热门话题
HOT_TOPICS = {
    "职场": ["#职场PUA", "#裸辞", "#打工人的一天", "#职场生存法则", "#薪资谈判"],
    "情感": ["#原生家庭", "#分手治愈", "#婚姻焦虑", "#恋爱技巧", "#独居生活"],
    "生活": ["#极简生活", "#独居女孩", "#自律打卡", "#极简主义", "#断舍离"],
    "颜值": ["#早C晚A", "#精简护肤", "#减肥逆袭", "#穿搭分享", "#变美日记"]
}

# 示例文案案例
CASES = [
    {
        "type": "💔 情感系",
        "title": "凌晨三点的崩溃",
        "preview": "凌晨三点，我第8次加班到崩溃边缘...",
        "full": """凌晨三点，我第8次加班到崩溃边缘。

手机屏幕亮起，是妈妈的消息："睡了吗？"

那一刻，眼泪真的忍不住了。

我已经记不清，这是第几次错过家里的电话；
第几次推掉朋友的聚会；
第几次忘记自己曾经也是个会做梦的人。

我们都在拼命奔跑，却忘了问自己：
这样的生活，真的是我们想要的吗？

如果你也累了，就停下来歇一歇吧。
允许自己慢一点，也是一种勇气。"""
    },
    {
        "type": "✨ 启发系",
        "title": "允许自己慢一点",
        "preview": "允许自己慢一点，也是一种成长...",
        "full": """允许自己慢一点，也是一种成长。

25岁那年，我辞掉了月薪3万的工作，
选择从零开始学习画画。

所有人都说我疯了，
但只有我知道，这是我内心最真实的声音。

现在的我，每天画8个小时，
虽然收入只有以前的十分之一，
但我找到了真正的快乐。

人生不是赛跑，不必每一步都赢。
找到属于自己的节奏，才是最重要的。"""
    },
    {
        "type": "🛒 种草系",
        "title": "这瓶精华真的绝了",
        "preview": "用了三个月，我的皮肤状态直接开挂...",
        "full": """用了三个月，我的皮肤状态直接开挂！

姐妹们，这个精华我真的按头安利！

质地超级清爽，一抹就化开
上脸完全不油腻，吸收超快

坚持用了一个月：
✅ 毛孔肉眼可见变小了
✅ 皮肤光泽度提升了
✅ 熬夜后的暗沉也改善了很多

而且性价比超高，学生党也能冲！

现在下单还有专属优惠，点击下方链接领取~
"""
    }
]

# ============================================
# 核心功能函数
# ============================================

def generate_script(scenario, style, topic):
    """生成短视频文案"""
    if not topic:
        return "请输入视频主题", ""

    # 模拟AI生成
    templates = [
        f"""【{topic}】

开头（3秒抓人）：
你有没有想过，{topic}到底意味着什么？

发展（30秒）：
今天我想和大家聊聊这个话题...

当你第一次面对{topic}的时候，
那种感觉是不是既陌生又熟悉？

其实啊，{topic}并没有想象中那么难。
重要的是，你要相信自己。

结尾（引导互动）：
你们觉得呢？欢迎在评论区聊聊~

#{topic} #情感 #共鸣""",

        f"""【{topic}】这个话题，我憋了很久了

各位好，今天聊个心里话。

说实话，关于{topic}这件事，
我纠结了很久要不要说...

但是今天，
我觉得不能再等了。

{topic}，
可能是很多人都在经历的事情。

不管你现在处于什么阶段，
我想告诉你：

你并不孤单。

觉得有收获的点个赞，
我们下期见！

#{topic} #生活 #成长""",

        f"""救命！{topic}真的太绝了！

姐妹们听我说！

我之前一直被{topic}困扰，
直到我发现了这个方法...

第一步，先调整心态
第二步，制定小目标
第三步，坚持执行

一周后，你就会看到变化！

还有什么想问的，评论区见~
#{topic} #干货 #分享"""
    ]

    script = random.choice(templates)

    # 添加审核提示（示例）
    review_note = ""
    if any(word in topic for word in ["裸辞", "辞职", "分手", "离婚"]):
        review_note = "⚠️ 建议内容客观中立，避免过度情绪化表达"

    return script, review_note


def copy_to_clipboard(text):
    """复制到剪贴板"""
    return gr.Textbox.update(value=text)


def save_history(topic, script, scenario, style):
    """保存历史记录"""
    history_file = "history.json"
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        history = []

    history.insert(0, {
        "topic": topic,
        "script": script,
        "scenario": scenario,
        "style": style,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    # 只保留最近10条
    history = history[:10]

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return history


def load_history():
    """加载历史记录"""
    history_file = "history.json"
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


# ============================================
# 构建界面
# ============================================

def build_ui():
    """构建Gradio界面"""

    # 自定义CSS样式
    custom_css = """
    /* 主容器样式 */
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 20px;
    }

    /* 标题样式 */
    .title-text {
        text-align: center;
        color: white;
        font-size: 32px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        margin-bottom: 10px;
    }

    .subtitle-text {
        text-align: center;
        color: rgba(255,255,255,0.9);
        font-size: 16px;
        margin-bottom: 20px;
    }

    /* 卡片样式 */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin: 10px 0;
    }

    /* 按钮样式 */
    .generate-btn {
        background: linear-gradient(135deg, #FF6B6B 0%, #ee5a5a 100%);
        color: white;
        border: none;
        padding: 15px 40px;
        border-radius: 30px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }

    .generate-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255,107,107,0.4);
    }

    /* 话题标签样式 */
    .topic-tag {
        display: inline-block;
        background: linear-gradient(135deg, #FF6B6B, #ee5a5a);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s;
    }

    .topic-tag:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(255,107,107,0.3);
    }

    /* 历史记录项样式 */
    .history-item {
        background: #f8f9fa;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* 结果区域样式 */
    .result-box {
        background: #fff9e6;
        border-left: 4px solid #FF6B6B;
        padding: 20px;
        border-radius: 8px;
        font-size: 16px;
        line-height: 1.8;
    }

    /* 审核提示样式 */
    .review-warning {
        background: #fff7e6;
        border: 1px solid #faad14;
        color: #d48806;
        padding: 10px 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    """

    with gr.Blocks(title="短视频AI文案生成器") as app:
        # ========================================
        # 标题区域
        # ========================================
        gr.Markdown("""
        # 🎬 短视频AI文案生成器
        ### ✨ v5.0 Web版 ✨
        """, elem_classes=["title-text"])

        # ========================================
        # 主布局：左侧功能区 + 右侧辅助区
        # ========================================
        with gr.Row():
            # ---------- 左侧：主要功能 ----------
            with gr.Column(scale=2):
                with gr.Group():
                    # 第一步：选择场景
                    gr.Markdown("### 📌 第一步：选择场景")
                    scenario = gr.Radio(
                        choices=SCENARIOS,
                        value=SCENARIOS[0],
                        label="场景类型"
                    )

                with gr.Group():
                    # 第二步：选择风格
                    gr.Markdown("### 💫 第二步：选择风格")
                    style = gr.Radio(
                        choices=[f"{emoji} {name}" for name, emoji in STYLES],
                        value=f"✨ {STYLES[0][0]}",
                        label="文案风格"
                    )

                with gr.Group():
                    # 第三步：输入主题
                    gr.Markdown("### 📝 第三步：输入主题")
                    topic_input = gr.Textbox(
                        placeholder="例如：职场生存指南、极简生活、减肥逆袭...",
                        label="视频主题",
                        lines=2
                    )

                # 生成按钮
                with gr.Row():
                    generate_btn = gr.Button(
                        "🚀 开始生成",
                        variant="primary",
                        size="lg"
                    )

                # 结果展示
                gr.Markdown("### 📋 生成结果")
                result_output = gr.Textbox(
                    placeholder="生成的文案将显示在这里...",
                    label="AI生成的短视频文案",
                    lines=12
                )

                # 操作按钮
                with gr.Row():
                    copy_btn = gr.Button("📋 复制文案", size="sm")
                    regen_btn = gr.Button("🔄 重新生成", size="sm")
                    use_btn = gr.Button("✨ 一键使用", size="sm", visible=False)

                # 内容审核提示
                review_output = gr.Textbox(
                    label="⚠️ 内容审核建议",
                    visible=False,
                    elem_classes=["review-warning"]
                )

            # ---------- 右侧：辅助模块 ----------
            with gr.Column(scale=1):
                # 热门话题推荐
                gr.Markdown("### 🔥 热门话题推荐")

                for category, topics in HOT_TOPICS.items():
                    gr.Markdown(f"**{category}**")
                    for topic in topics:
                        topic_btn = gr.Button(
                            topic,
                            size="sm",
                            variant="secondary"
                        )

                gr.Markdown("---")

                # 案例展示
                gr.Markdown("### 📚 案例展示")
                for case in CASES:
                    with gr.Group():
                        gr.Markdown(f"**{case['type']}**")
                        gr.Markdown(f"*{case['preview']}*")
                        case_btn = gr.Button("📖 查看全文", size="sm")
                        gr.Markdown("---")

                gr.Markdown("---")

                # 历史记录
                gr.Markdown("### 📜 历史记录")

                # 存储历史记录的隐藏组件
                history_state = gr.State(load_history())

                history_display = gr.JSON(
                    value=load_history(),
                    label="最近生成"
                )

                refresh_btn = gr.Button("🔄 刷新历史", size="sm")

        # ========================================
        # 事件绑定
        # ========================================

        # 点击话题标签 → 填入主题
        for category, topics in HOT_TOPICS.items():
            for topic in topics:
                topic_clean = topic.replace("#", "")
                # 注意：Gradio需要特殊处理按钮点击

        # 生成按钮事件
        generate_btn.click(
            fn=generate_script,
            inputs=[scenario, style, topic_input],
            outputs=[result_output, review_output]
        )

        # 复制按钮事件
        copy_btn.click(
            fn=copy_to_clipboard,
            inputs=[result_output],
            outputs=[topic_input]
        )
        gr.Info("已复制到剪贴板！")

        # 重新生成按钮
        regen_btn.click(
            fn=generate_script,
            inputs=[scenario, style, topic_input],
            outputs=[result_output, review_output]
        )

        # 刷新历史
        refresh_btn.click(
            fn=load_history,
            outputs=[history_display]
        )

    return app


# ============================================
# 启动应用
# ============================================

if __name__ == "__main__":
    print("🚀 启动短视频AI文案生成器 v5.0...")
    print("📍 访问地址：http://localhost:7860")

    app = build_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        css=custom_css
    )
