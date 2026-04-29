# -*- coding: utf-8 -*-
"""修复app_final.py的launch调用"""
file_path = r'C:\Users\zjw\Documents\GitHub\RuoHua-ai\app_final.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 替换最后几行
lines[503] = '    app = build_ui()\n'
lines[504] = '    app.launch(server_name="0.0.0.0", server_port=7860)\n'
# 删除多余的css行 (505-507)
del lines[505:508]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('已修复，共', len(lines), '行')
