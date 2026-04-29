"""短视频AI文案生成器 - 简化版"""
import gradio as gr
import random

def generate_script(scenario, style, topic):
    if not topic:
        return "请输入视频主题"
    
    templates = [
        f"""【{topic}】

开头（3秒抓人）：
你有没有想过，{topic}到底意味着什么？

发展：
今天我想和大家聊聊这个话题...

结尾：
你们觉得呢？欢迎在评论区聊聊~

#{topic} #情感 #共鸣""",
        f"""【{topic}】这个话题，我憋了很久了

各位好，今天聊个心里话。

说实话，关于{topic}这件事，我纠结了很久要不要说...

{topic}可能是很多人都在经历的事情。

不管你现在处于什么阶段，我想告诉你：你并不孤单。

觉得有收获的点个赞，我们下期见！

#{topic} #生活 #成长"""
    ]
    return random.choice(templates)

# 创建界面
with gr.Blocks(title="短视频AI文案生成器") as app:
    gr.Markdown("# 🎬 短视频AI文案生成器\n### ✨ v5.0 Web版 ✨")
    
    with gr.Row():
        with gr.Column():
            scenario = gr.Radio(
                choices=["重叙述型", "重总结型", "长篇故事型"],
                value="重叙述型",
                label="📌 选择场景"
            )
            style = gr.Radio(
                choices=["情绪渲染型", "搞笑幽默型", "正能量激励型", "种草带货型"],
                value="正能量激励型",
                label="💫 选择风格"
            )
            topic = gr.Textbox(label="📝 输入主题", placeholder="例如：职场生存指南...")
            btn = gr.Button("🚀 开始生成", variant="primary")
        
        with gr.Column():
            result = gr.Textbox(label="📋 生成结果", lines=15)
            copy_btn = gr.Button("📋 复制文案")
    
    btn.click(fn=generate_script, inputs=[scenario, style, topic], outputs=result)

if __name__ == "__main__":
    print("🚀 启动短视频AI文案生成器...")
    print("📍 访问地址：http://localhost:7860")
    app.launch(server_name="0.0.0.0", server_port=7860)
