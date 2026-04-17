# 🌸 若花 - AI文案生成器

> 一款面向小红书内容创作者的AI文案生成工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

## 📖 项目简介

若花是一款基于通义千问API开发的AI文案生成工具，专为小红书内容创作者设计。用户只需输入主题关键词，即可快速生成适配平台的优质文案。

**核心特点**：
- 🏷️ 多场景支持：重叙述型 / 重总结型 / 长篇故事型
- 🎨 四风格体系：感情系 / 抽象系 / 启发系 / 种草系
- 🔢 场景×风格矩阵：12种组合满足不同创作需求
- 🔄 多轮交互：支持用户反馈迭代优化
- 📜 版本管理：保留历史版本，随时回溯

## 🚀 快速开始

### 环境要求
- Python 3.8+
- DashScope API Key（通义千问）

### 安装依赖

```bash
pip install gradio dashcope
```

### 运行项目

```bash
python app.py
```

然后在浏览器中打开 `http://localhost:7860`

## 📂 项目结构

```
├── index.html          # 若花Web界面（主界面）
├── app.py              # Gradio Web框架入口
├── app_simple.py       # 基础版本
├── app_complete.py     # 完整功能版本
├── app_ruohua.py       # 若花定制版
├── history.json        # 对话历史存储
├── deploy/             # 部署相关文件
└── README.md
```

## 📈 版本历程

| 版本 | 日期 | 更新内容 |
|:---:|:---:|----------|
| v1.0 | 4月9日 | 命令行基础版本，API调用 |
| v2.0 | 4月11日 | 场景×风格矩阵设计 |
| v3.0 | 4月11日 | 多轮交互机制 |
| v4.0 | 4月12日 | 长篇故事场景 |
| v5.0 | 4月12日 | Gradio Web界面 |
| v6.0 | 4月14日 | 若花界面重塑（豆包风格） |
| v7.0 | 4月15日 | 对话系统重构（版本管理） |

## 🎯 产品设计亮点

### 1. 场景细分思维
将用户「生成文案」的需求，细分为：
- **重叙述型**：80-150字，适合叙事类视频
- **重总结型**：10-20字，适合干货类视频
- **长篇故事型**：500-2000字，适合故事类内容

### 2. 迭代优化机制
采用「生成 → 反馈 → 优化」的交互模式，解决AI一次性生成不完美的问题。

### 3. 版本管理系统
保留所有历史版本，支持用户随时回溯和对比。

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 编程语言 | Python |
| AI模型 | 通义千问 (DashScope API) |
| 前端框架 | HTML / CSS / JavaScript |
| UI组件 | Gradio |
| 部署平台 | MiniMax Spaces |

## 👤 作者

- **GitHub**: [@windto0746](https://github.com/windto0746)
- **在线演示**: [若花AI文案生成器](https://67fe5cm79wb4.space.minimaxi.com)

## 📄 License

本项目基于 MIT License 开源。
