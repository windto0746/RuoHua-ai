# -*- coding: utf-8 -*-
"""
小红书AI文案生成器 v5.0 - 若花界面版
基于豆包风格的聊天式交互界面
"""

from dashscope import Generation
import dashscope
import logging
import os
from datetime import datetime

# ===== 初始化日志系统 =====
def setup_logging():
    """配置日志系统"""
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(log_dir, f'xiaohongshu_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ===== 配置 =====
# API Key 从环境变量读取，保护密钥安全
dashscope.api_key = os.environ.get('DASHSCOPE_API_KEY', '')
if not dashscope.api_key:
    raise ValueError('请先设置环境变量：set DASHSCOPE_API_KEY=你的API密钥')
logger.info("程序启动，API配置完成")

# ===== 敏感词库 =====
SENSITIVE_WORDS = {
    '政治': ['领导', '国家主席', '总理', '总统', '抗议', '示威', '反动', '颠覆'],
    '医疗': ['根治', '治愈', '药到病除', '保证治愈', '无效退款', '神医'],
    '投资': ['稳赚', '保本', '高收益', '天天涨', '翻倍', '内幕消息'],
    '夸大': ['第一', '最好', '最强', '顶级', '独家', '全网最低'],
    '低俗': ['约', '泡', '撩', '上床', '做爱', '性感', '诱惑'],
    '平台': ['加我', '微信', 'QQ群', '购买链接', '私信', '加群']
}

PLATFORM_WARNING_WORDS = ['最', '绝对', '彻底', '完美', '一定', '保证', '必须']


def filter_sensitive_words(text):
    """敏感词过滤"""
    warnings = []
    filtered_text = text
    
    for category, words in SENSITIVE_WORDS.items():
        for word in words:
            if word in filtered_text:
                filtered_text = filtered_text.replace(word, '*' * len(word))
                warnings.append(f"[{category}敏感词] 已替换: {word}")
    
    return filtered_text, warnings


def check_platform_rules(text):
    """检查平台规则"""
    warnings = []
    for word in PLATFORM_WARNING_WORDS:
        if word in text:
            count = text.count(word)
            warnings.append(f"[平台规则] 建议减少使用 '{word}' (出现{count}次)")
    return warnings


def content_audit(text):
    """内容审核主函数"""
    all_warnings = []
    filtered_text, sensitive_warnings = filter_sensitive_words(text)
    all_warnings.extend(sensitive_warnings)
    platform_warnings = check_platform_rules(text)
    all_warnings.extend(platform_warnings)
    
    if all_warnings:
        logger.warning(f"内容审核发现问题: {all_warnings}")
    
    return filtered_text, all_warnings


# ===== Prompt模板库 =====
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
✓ 必须有具体细节

请根据用户给的主题，写一篇符合上述要求的文案。""",

    ('narrative', '抽象系'): """你是一个深谙互联网"抽象文化"的年轻创作者，擅长写让人"笑死"的无厘头叙事文案。

【字数要求】60-100字，要有完整的"抽象叙事"
【风格要求】无厘头、反转、出人意料、打破常规
【结构要求】制造反差感，结局要出人意料

请根据用户给的主题，写一篇符合上述要求的文案。""",

    ('narrative', '启发系'): """你是一个小红书头部治愈系博主，擅长写让人感到"被理解"的温柔叙事。

【字数要求】80-120字，要有"娓娓道来"的感觉
【风格要求】温柔治愈、文艺清新、有力量但不说教
【格式要求】适合小红书的"分段+emoji"风格

请根据用户给的主题，写一篇符合上述要求的文案。""",

    ('narrative', '种草系'): """你是一个小红书头部种草博主，擅长写让人"忍不住想点进去"的种草型叙事文案。

【字数要求】100-150字，要有完整的推荐逻辑
【风格要求】真实感、场景化、有记忆点
【结构要求】制造好奇心 → 场景描述 → 独特卖点 → 行动引导

请根据用户给的主题，写一篇符合上述要求的文案。""",

    ('summary', '感情系'): """你是一个资深的小红书情感博主，擅长写精炼的情感金句。

【字数要求】10-20字，越精炼越有力量
【风格要求】文艺伤感、一针见血、引发共鸣
【格式要求】单句或对仗短句，末尾可加emoji

请根据用户给的主题，写一句符合上述要求的金句。""",

    ('summary', '抽象系'): """你是一个深谙互联网"抽象文化"的年轻创作者，擅长写让人"笑喷"的一句话抽象文案。

【字数要求】10-20字，要"短小精悍出乎意料"
【风格要求】无厘头、反转、一句话让人笑出声

请根据用户给的主题，写一句符合上述要求的抽象文案。""",

    ('summary', '启发系'): """你是一个小红书治愈成长类博主，擅长写让人感到"被理解"的金句。

【字数要求】10-20字，要有"一语点醒梦中人"的感觉
【风格要求】温柔治愈、文艺清新、让人感到被理解

请根据用户给的主题，写一句符合上述要求的治愈金句。""",

    ('summary', '种草系'): """你是一个小红书头部种草博主，擅长写让人"立刻想下单"的一句话安利。

【字数要求】10-20字，要有"冲动感"
【风格要求】真实感、冲击力、一句话说清楚"为什么值得"

请根据用户给的主题，写一句符合上述要求的种草文案。""",

    ('story', '感情系'): """你是一个专业的小红书故事类内容创作者，擅长写能引发深度情感共鸣的完整故事。

【字数要求】500-2000字，要讲述一个完整的、有起伏的故事
【风格要求】文艺伤感、有血有肉、让人产生强烈的代入感
【结构要求】
1. 开场：用具体场景或细节吸引注意力
2. 发展：铺垫背景，引出核心冲突或转折点
3. 高潮：情感最强烈的部分，要有"戳心"的细节
4. 结尾：升华主题，留有余韵

请根据用户给的主题，写一篇符合上述要求的完整故事。""",

    ('story', '抽象系'): """你是一个专业的小红书"抽象文学"创作者，擅长写让人"脑洞大开"的荒诞故事。

【字数要求】300-1500字，要有完整的"抽象叙事"
【风格要求】荒诞搞笑 + 出人意料的反转 + 细思极恐的结尾
【结构要求】
1. 开场：制造一种正常的假象
2. 发展：逐渐加入离谱的设定
3. 高潮：彻底放飞自我的抽象情节
4. 结尾：出人意料的收尾

请根据用户给的主题，写一篇符合上述要求的抽象故事。""",

    ('story', '启发系'): """你是一个专业的小红书治愈成长类内容创作者，擅长写温暖人心的故事。

【字数要求】500-2000字，要有"娓娓道来"的叙事感
【风格要求】温柔治愈、真实可信、让人感到被理解、被治愈
【结构要求】
1. 开场：设置一个真实的生活场景或困境
2. 发展：描述内心的挣扎和转变过程
3. 高潮：找到答案或实现突破的时刻
4. 结尾：升华感悟，用温暖有力的结语收尾

请根据用户给的主题，写一篇符合上述要求的治愈故事。""",

    ('story', '种草系'): """你是一个专业的小红书探店/测评类内容创作者，擅长写让人"身临其境"的推荐文案。

【字数要求】500-2000字，要有完整的"体验叙事"
【风格要求】场景化、细节丰富、有代入感
【结构要求】
1. 开场：制造好奇心或共鸣感
2. 发展：详细的体验过程，场景描写丰富
3. 高潮：最惊艳/最值得的部分
4. 结尾：总结推荐理由，有明确的行动引导

请根据用户给的主题，写一篇符合上述要求的种草故事。""",
}


# ===== 风格定义 =====
STYLES = {
    'narrative': {
        '1': {'name': '感情系', 'emoji': '💔'},
        '2': {'name': '抽象系', 'emoji': '🤪'},
        '3': {'name': '启发系', 'emoji': '✨'},
        '4': {'name': '种草系', 'emoji': '🛒'},
    },
    'summary': {
        '1': {'name': '感情系', 'emoji': '💔'},
        '2': {'name': '抽象系', 'emoji': '🤪'},
        '3': {'name': '启发系', 'emoji': '✨'},
        '4': {'name': '种草系', 'emoji': '🛒'},
    },
    'story': {
        '1': {'name': '感情系', 'emoji': '💔'},
        '2': {'name': '抽象系', 'emoji': '🤪'},
        '3': {'name': '启发系', 'emoji': '✨'},
        '4': {'name': '种草系', 'emoji': '🛒'},
    }
}


# ===== API调用函数 =====
def call_llm(messages, model='qwen-plus'):
    """调用通义千问API"""
    try:
        logger.info(f"开始调用API，模型: {model}")
        response = Generation.call(model=model, messages=messages)
        
        status_code = response.get('status_code', None)
        
        if status_code == 200:
            output = response.get('output', {})
            text = output.get('text', '')
            if text:
                logger.info(f"API调用成功，内容长度: {len(text)}")
                return text
            return '生成结果为空，请重试'
        else:
            error_msg = response.get('message', '未知错误')
            logger.error(f"API调用失败: {error_msg}")
            return f'调用失败: {error_msg}'
            
    except Exception as e:
        logger.error(f"API调用异常: {type(e).__name__}: {str(e)}")
        return f'系统异常: {type(e).__name__}: {str(e)}'


def build_system_prompt(scene, style_name):
    """构建系统提示词"""
    return PROMPTS.get((scene, style_name), "")


# ===== 主程序 =====
def main():
    logger.info("=" * 50)
    logger.info("小红书AI文案生成器 v5.0 若花界面版 启动")
    logger.info("=" * 50)
    
    print("=" * 60)
    print("     小红书AI文案生成器 v5.0 [若花界面版]")
    print("=" * 60)
    
    while True:
        print("\n📌 请选择文案场景：")
        print("-" * 50)
        print("1. 📖 重叙述型 - 80-150字，视频配文型")
        print("2. ✨ 重总结型 - 10-20字，金句升华型")
        print("3. 📚 长篇故事型 - 500-2000字，故事主线型")
        print("4. 🚪 退出程序")
        
        scene_choice = input("\n请输入选项(1-4)：").strip()
        
        if scene_choice == '4':
            print("\n感谢使用！再见~")
            logger.info("用户退出程序")
            break
        
        if scene_choice not in ['1', '2', '3']:
            print("无效选项，请重新选择！")
            continue
        
        scene_map = {'1': 'narrative', '2': 'summary', '3': 'story'}
        scene_name_map = {'1': '重叙述型', '2': '重总结型', '3': '长篇故事型'}
        
        scene_key = scene_map[scene_choice]
        scene_name = scene_name_map[scene_choice]
        
        print(f"\n📌 已选择【{scene_name}】场景，请选择风格：")
        print("-" * 50)
        for key, style in STYLES[scene_key].items():
            print(f"{key}. {style['emoji']} {style['name']}")
        
        style_choice = input("\n请输入选项(1-4)：").strip()
        
        if style_choice not in STYLES[scene_key]:
            print("无效选项，请重新选择！")
            continue
        
        style_name = STYLES[scene_key][style_choice]['name']
        logger.info(f"用户选择: {scene_key} - {style_name}")
        
        topic = input("\n请输入主题关键词：").strip()
        
        if not topic:
            print("主题不能为空！")
            continue
        
        logger.info(f"用户输入主题: {topic}")
        
        system_prompt = build_system_prompt(scene_key, style_name)
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'请根据主题"{topic}"和风格"{style_name}"，生成文案。'}
        ]
        
        print("\n📝 正在生成初稿...")
        logger.info("开始生成初稿")
        
        result = call_llm(messages)
        round_count = 1
        
        filtered_result, warnings = content_audit(result)
        
        print(f"\n【第{round_count}版】")
        print(filtered_result)
        
        if warnings:
            print("\n⚠️ 内容审核建议：")
            for w in warnings:
                print(f"   • {w}")
        
        while True:
            print("\n" + "=" * 60)
            print("🔄 请选择下一步操作：")
            print("-" * 50)
            print("1. ✅ 满意，保存结果")
            print("2. 🔧 补充修改意见，让AI重新生成")
            print("3. 🔄 随机重新生成")
            print("4. 🚪 取消，返回主菜单")
            
            action = input("\n请输入选项(1-4)：").strip()
            
            if action == '1':
                print("\n" + "=" * 60)
                print("🎉 已保存！最终文案如下：")
                print("=" * 60)
                print(filtered_result)
                print("=" * 60)
                logger.info(f"用户保存结果，长度: {len(filtered_result)}")
                break
            
            elif action == '2':
                feedback = input("\n💬 请输入你的修改意见：\n>>> ").strip()
                
                if not feedback:
                    print("修改意见不能为空！")
                    continue
                
                messages.append({'role': 'assistant', 'content': result})
                messages.append({'role': 'user', 'content': f'根据以下修改意见优化文案："{feedback}"'})
                
                print("\n📝 正在根据你的意见重新生成...")
                logger.info(f"用户反馈: {feedback}")
                
                result = call_llm(messages)
                filtered_result, warnings = content_audit(result)
                round_count += 1
                print(f"\n【第{round_count}版】")
                print(filtered_result)
                
                if warnings:
                    print("\n⚠️ 内容审核建议：")
                    for w in warnings:
                        print(f"   • {w}")
            
            elif action == '3':
                messages = [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': f'请根据主题"{topic}"和风格"{style_name}"，生成一版不同的文案。'}
                ]
                
                print("\n📝 正在重新生成...")
                logger.info("用户请求重新生成")
                
                result = call_llm(messages)
                filtered_result, warnings = content_audit(result)
                round_count = 1
                print(f"\n【第{round_count}版】")
                print(filtered_result)
                
                if warnings:
                    print("\n⚠️ 内容审核建议：")
                    for w in warnings:
                        print(f"   • {w}")
            
            elif action == '4':
                print("\n已取消，返回主菜单。")
                logger.info("用户返回主菜单")
                break
            
            else:
                print("无效选项，请重新选择！")


if __name__ == "__main__":
    main()
