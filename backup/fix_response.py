# -*- coding: utf-8 -*-
file_path = r'C:\Users\zjw\Documents\GitHub\RuoHua-ai\app_final.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复新版dashscope响应格式
old = "result = response['output']['text']"
new = "result = response.output.text"

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('已修复响应格式')
