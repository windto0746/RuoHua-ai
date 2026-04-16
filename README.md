# 若花 - AI文案生成器

一款面向小红书内容创作者的AI文案生成工具。

## 功能特点

- **多场景支持**：重叙述型、重总结型、长篇故事型
- **四风格体系**：感情系、抽象系、启发系、种草系
- **场景×风格矩阵**：12种组合满足不同创作需求
- **多轮交互**：支持用户反馈迭代优化
- **版本管理**：保留历史版本，随时回溯

## 技术栈

- Python + DashScope API (通义千问)
- HTML/CSS/JavaScript
- Gradio Web框架

## 快速开始

1. 克隆项目
```bash
git clone <your-repo-url>
cd ruohua-ai
```

2. 安装依赖
```bash
pip install gradio dashscope
```

3. 运行
```bash
python app.py
```

## 项目结构

```
├── app.py              # Web界面主程序
├── index.html          # 前端界面
├── app_simple.py       # 基础版本
├── app_complete.py     # 完整版本
├── app_ruohua.py       # 若花定制版
└── README.md
```

## 版本历程

| 版本 | 更新内容 |
|:---:|----------|
| v1.0 | 命令行基础版本 |
| v2.0 | 场景×风格矩阵 |
| v3.0 | 多轮交互机制 |
| v4.0 | 长篇故事场景 |
| v5.0 | Web界面 |
| v6.0 | 若花界面重塑 |
| v7.0 | 对话系统重构 |

## License

MIT
