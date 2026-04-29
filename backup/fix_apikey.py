# -*- coding: utf-8 -*-
file_path = r'C:\Users\zjw\Documents\GitHub\RuoHua-ai\app_final.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old = "API_KEY = 'sk-15d8a880bb6a41e7900e9e8c44bfa398'"
new = "API_KEY = 'sk-99e79fdfec30402299e3a5a6a3ed3000'"

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('已更新 API Key')
