# -*- coding: utf-8 -*-
"""修复云端环境API Key读取问题"""
file_path = r'C:\Users\zjw\Documents\GitHub\RuoHua-ai\app_final.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 新的环境变量加载逻辑
old_config = '''# ============================================
# 加载环境变量保护API Key
# ============================================
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

API_KEY = os.environ.get('DASHSCOPE_API_KEY', '')
if not API_KEY:
    raise ValueError('请在.env文件中设置DASHSCOPE_API_KEY')'''

new_config = '''# ============================================
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
    print("\\n" + "=" * 50)
    print("❌ API Key 未设置!")
    print("=" * 50)
    print("\\n【本地运行】请在项目根目录创建 .env 文件：")
    print("   DASHSCOPE_API_KEY=你的API密钥")
    print("\\n【GitHub云端】请在 Settings > Secrets 中添加：")
    print("   Name: DASHSCOPE_API_KEY")
    print("   Value: 你的API密钥")
    print("\\n【或者】在终端运行前设置环境变量：")
    print("   Windows: set DASHSCOPE_API_KEY=你的密钥")
    print("   Linux/Mac: export DASHSCOPE_API_KEY=你的密钥")
    print("=" * 50)
    sys.exit(1)'''

content = content.replace(old_config, new_config)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('已修复云端环境支持')
