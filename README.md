# 🌸 若花 - AI文案生成器

> 一款面向小红书内容创作者的AI文案生成工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

## 📖 项目简介

若花是一款基于**通义千问API**开发的AI文案生成工具，专为小红书内容创作者设计。用户只需输入主题关键词，即可快速生成适配平台的优质文案。

**核心特点**：
- 🏷️ **多场景支持**：重叙述型 / 重总结型 / 长篇故事型
- 🎨 **四风格体系**：感情系 / 抽象系 / 启发系 / 种草系
- 🔢 **场景×风格矩阵**：12种组合满足不同创作需求
- 🔒 **API Key安全保护**：使用环境变量管理敏感信息
- ⚡ **敏感词过滤**：内置内容审核机制

## 🚀 快速开始

### 环境要求
- Python 3.8+
- DashScope API Key（通义千问）

### 安装依赖

```bash
pip install gradio dashscope python-dotenv
```

### 运行项目

**第一步：配置API Key**

在项目根目录创建 `.env` 文件：

```bash
DASHSCOPE_API_KEY=你的API密钥
```

**第二步：启动应用**

```bash
python app_final.py
```

然后在浏览器中打开显示的地址（默认 `http://localhost:7860`）

### 一键分享

运行时会生成一个临时分享链接（有效期约7天），可以分享给他人体验。

## 📂 项目结构

```
RuoHua-ai/
├── app_final.py          # 主程序（修复版）
├── app_final_backup.py   # 原版备份
├── app_fixed.py          # 修复测试版
├── test_app_fixed.py     # 功能测试脚本
├── .env                  # API Key配置文件（不提交）
├── .env.example          # 环境变量模板
├── history.json          # 对话历史存储
├── requirements.txt      # Python依赖
└── README.md
```

## 📊 功能演示

### 使用流程

```
1. 选择场景类型（重叙述型/重总结型/长篇故事型）
2. 选择文案风格（感情系/抽象系/启发系/种草系）
3. 输入视频主题
4. 点击"开始生成"
5. AI智能生成专业文案
6. 可直接复制或保存
```

### 场景×风格矩阵

| | 感情系 | 抽象系 | 启发系 | 种草系 |
|---|:---:|:---:|:---:|:---:|
| **重叙述型** | 情感故事 | 搞笑叙事 | 治愈故事 | 种草推荐 |
| **重总结型** | 情感金句 | 抽象文案 | 治愈金句 | 种草安利 |
| **长篇故事型** | 情感故事文 | 抽象故事 | 治愈故事 | 探店种草 |

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 编程语言 | Python |
| AI模型 | 通义千问 (DashScope API) |
| 前端框架 | Gradio |
| 环境配置 | python-dotenv |

## 🔒 安全说明

本项目采用**环境变量**方式管理API Key，保护敏感信息：
- API Key 存储在 `.env` 文件中（已加入 .gitignore）
- 代码从环境变量读取，不在代码中硬编码
- 支持本地 .env 文件和 GitHub Secrets 多种配置方式

## 📈 版本历程

| 版本 | 日期 | 更新内容 |
|:---:|:---:|----------|
| v1.0 | 4月9日 | 命令行基础版本，API调用 |
| v8.0 | 4月28日 | Gradio界面 + API Key安全保护 + 兼容修复 |

## 👤 作者

- **GitHub**: [@windto0746](https://github.com/windto0746)

## 📄 License

本项目基于 MIT License 开源。
