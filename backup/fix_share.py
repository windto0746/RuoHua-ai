# -*- coding: utf-8 -*-
file_path = r'C:\Users\zjw\Documents\GitHub\RuoHua-ai\app_final.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old = 'app.launch(server_name="0.0.0.0", server_port=7860)'
new = 'app.launch(server_name="0.0.0.0", server_port=7860, share=True)'

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('已添加 share=True')
