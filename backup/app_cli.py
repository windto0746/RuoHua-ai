#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
短视频AI文案生成器 - 命令行版
API Key从.env文件读取，保证安全
使用方法：python app_cli.py
"""
import os
import sys
from dotenv import load_dotenv

# 加载.env配置
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

# 导入DashScope
import dashscope
from dashscope import Generation

# 设置API Key
dashscope.api_key = os.environ.get('DASHSCOPE_API_KEY', '')
if not dashscope.api_key:
    print("❌ 错误：请在 .env 文件中设置 DASHSCOPE_API_KEY")
    print("   创建一个 .env 文件，内容如下：")
    print("   DASHSCOPE_API_KEY=你的API密钥")
    sys.exit(1)

# 敏感词库
SENSITIVE_WORDS = {
    '政治': ['领导', '国家主席', '总理', '总统', '抗议', '示威'],
    '医疗': ['根治', '治愈', '保证治愈'],
    '夸大': ['第一', '最好', '最强', '顶级'],
    '低俗': ['上床', '做爱', '诱惑'],
    '平台': ['加我', '微信', 'QQ群']
}

def content_audit(text):
    """内容审核"""
    warnings = []
    filtered_text = text
    for category, words in SENSITIVE_WORDS.items():
        for word in words:
            if word in filtered_text:
                filtered_text = filtered_text.replace(word, '*' * len(word))
                warnings.append(f"[{category}] 已替换敏感词: {word}")
    return filtered_text, warnings

# Prompt模板
PROMPTS = {
    ('narrative', '感情系'): """你是一个资深的小红书情感博主，擅长写能引发共鸣的叙事型文案。
字数要求80-150字，要有完整的叙事弧度。
请根据用户给的主题，写一篇符合要求的文案。""",
    
    ('narrative', '启发系'): """你是一个小红书治愈系博主，擅长写温柔治愈的叙事。
字数要求80-120字。
请根据用户给的主题，写一篇符合要求的文案。""",
    
    ('summary', '感情系'): """你是一个情感博主，擅长写精炼的情感金句。
字数要求10-20字。
请根据用户给的主题，写一句符合要求的金句。""",
    
    ('summary', '启发系'): """你是一个治愈成长类博主，擅长写温暖的金句。
字数要求10-20字。
请根据用户给的主题，写一句符合要求的金句。""",
}

SCENARIOS = {
    "1": {"name": "重叙述型", "desc": "视频配文", "words": "80-150字", "key": "narrative"},
    "2": {"name": "重总结型", "desc": "金句升华", "words": "10-20字", "key": "summary"},
}

STYLES = {
    "1": "感情系",
    "2": "启发系",
}

def generate_script(scenario_key, style_key, topic):
    """生成文案"""
    if not topic or not topic.strip():
        return "请输入视频主题"

    try:
        scenario_info = SCENARIOS.get(scenario_key, SCENARIOS["1"])
        scene_key = scenario_info["key"]
        style = STYLES.get(style_key, "启发系")
        system_prompt = PROMPTS.get((scene_key, style), PROMPTS[('narrative', '启发系')])

        print(f"\n📝 场景：{scenario_info['name']} | 风格：{style}")
        print(f"⏳ 正在生成...\n")

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'请根据主题"{topic}"生成文案。'}
        ]

        response = Generation.call(model='qwen-plus', messages=messages)

        if response.get('status_code') == 200:
            result = response['output']['text']
            filtered_result, warnings = content_audit(result)
            
            print("=" * 50)
            print("✨ 生成结果：")
            print("=" * 50)
            print(filtered_result)
            print("=" * 50)
            
            if warnings:
                print("\n⚠️ 敏感词处理：")
                for w in warnings:
                    print(f"   {w}")
        else:
            print(f"❌ 生成失败: {response.get('message', '未知错误')}")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("  短视频AI文案生成器 - 命令行版")
    print("  通义千问AI | 专业Prompt | 敏感词过滤")
    print("=" * 50)
    
    while True:
        print("\n" + "-" * 40)
        print("请选择场景类型：")
        print("  1 - 重叙述型（视频配文，80-150字）")
        print("  2 - 重总结型（金句升华，10-20字）")
        print("  q - 退出程序")
        
        scenario = input("\n请输入选项 (1/2/q): ").strip()
        if scenario.lower() == 'q':
            print("\n👋 感谢使用，再见！")
            break
        
        if scenario not in SCENARIOS:
            print("❌ 无效选项，请重新选择")
            continue
        
        print("\n请选择文案风格：")
        print("  1 - 感情系")
        print("  2 - 启发系")
        
        style = input("请输入选项 (1/2): ").strip()
        if style not in STYLES:
            print("❌ 无效选项，请重新选择")
            continue
        
        print()
        topic = input("请输入视频主题: ").strip()
        if not topic:
            print("❌ 主题不能为空")
            continue
        
        generate_script(scenario, style, topic)
        
        print("\n" + "-" * 40)
        again = input("是否继续生成？ (y/n): ").strip().lower()
        if again != 'y':
            print("\n👋 感谢使用，再见！")
            break

if __name__ == "__main__":
    main()
