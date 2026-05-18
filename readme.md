# 📈 股市周报自动生成系统

每周自动生成 A 股 + 美股周报（HTML + PDF），通过 GitHub Pages 在线查看。

## 🌐 在线周报

- [📊 查看最新 HTML 报告](https://pennyjiu9.github.io/stock-AI-weeklyreport-lpm/output/report_template.html)

## ⏰ 更新时间

每周五 16:00（北京时间）自动更新，也可手动触发。

## 📁 项目结构

- `scripts/` – 数据获取、AI 摘要、渲染脚本
- `data/` – 临时数据文件
- `output/` – 生成的报告（HTML + PDF）
- `.github/workflows/` – 自动化流水线

## 🚀 本地运行

```bash
# 安装依赖
pip install akshare yfinance pandas matplotlib requests python-dotenv jupyter

# 获取数据
python scripts/01_fetch_data.py

# 生成 AI 摘要（需设置 MiniMax API 密钥）
python scripts/02_generate_summary.py

# 渲染报告
quarto render report_template.qmd --to html,pdf
```

## 📝 说明

数据来源：akshare（A股）、yfinance（美股）

AI 摘要：MiniMax API

报告渲染：Quarto + matplotlib

自动化：GitHub Actions


