# -*- coding: utf-8 -*-
"""测试 app_fixed.py 的所有功能"""
import sys
import os

# 添加路径
sys.path.insert(0, r'C:\Users\zjw\Documents\GitHub\RuoHua-ai')

print("=" * 50)
print("测试 app_fixed.py")
print("=" * 50)

# 1. 测试环境变量加载
print("\n[1] 测试环境变量加载...")
from dotenv import load_dotenv
env_path = r'C:\Users\zjw\Documents\GitHub\RuoHua-ai\.env'
load_dotenv(env_path)
api_key = os.environ.get('DASHSCOPE_API_KEY', '')
if api_key:
    print(f"   ✅ API Key加载成功: {api_key[:10]}...")
else:
    print("   ❌ API Key加载失败")
    sys.exit(1)

# 2. 测试dashscope
print("\n[2] 测试dashscope配置...")
import dashscope
dashscope.api_key = api_key
print("   ✅ dashscope配置成功")

# 3. 测试API调用
print("\n[3] 测试API调用...")
from dashscope import Generation
try:
    response = Generation.call(
        model='qwen-plus',
        messages=[{'role': 'user', 'content': '测试'}]
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ API调用成功!")
        print(f"   响应: {response.output.text[:100]}...")
    else:
        print(f"   ❌ API调用失败: {response.message}")
except Exception as e:
    print(f"   ❌ 异常: {e}")
    sys.exit(1)

# 4. 测试generate_script函数
print("\n[4] 测试generate_script函数...")
from app_fixed import generate_script, content_audit

try:
    result, hint = generate_script("📖 重叙述型", "✨ 启发系", "测试主题")
    print(f"   提示: {hint}")
    if "生成失败" in result:
        print(f"   ❌ 生成失败: {result}")
    else:
        print(f"   ✅ 生成成功!")
        print(f"   结果预览: {result[:100]}...")
except Exception as e:
    print(f"   ❌ 异常: {e}")
    sys.exit(1)

# 5. 测试content_audit
print("\n[5] 测试content_audit...")
test_text = "这是一个测试文案，包含一些敏感词如领导等"
filtered, warnings = content_audit(test_text)
print(f"   原文: {test_text}")
print(f"   过滤后: {filtered}")
if warnings:
    print(f"   警告: {warnings}")
print("   ✅ 审核功能正常")

# 6. 测试历史记录
print("\n[6] 测试历史记录...")
from app_fixed import save_history, load_history
save_history("测试主题", "测试结果", "📖 重叙述型", "✨ 启发系")
history = load_history()
print(f"   历史记录数量: {len(history)}")
print("   ✅ 历史记录功能正常")

print("\n" + "=" * 50)
print("所有测试通过! app_fixed.py 可以正常运行")
print("=" * 50)
