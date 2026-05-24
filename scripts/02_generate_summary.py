# scripts/02_generate_summary.py
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_market_summary(weekly_data: dict) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")

    # DeepSeek API 使用 OpenAI 兼容接口
    url = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
你是一位专业的金融分析师，请根据以下本周市场数据，
撰写一段 300-400 字的市场周报摘要，风格专业、客观、简洁。

本周数据：
{json.dumps(weekly_data, ensure_ascii=False, indent=2)}

要求：
1. 概括主要指数涨跌情况
2. 点评 2-3 个表现突出的行业及可能原因
3. 简要展望下周需要关注的因素
4. 不要使用「根据数据」「如上所示」等套话
5. 直接输出正文，不需要标题
"""

    payload = {
        "model": "deepseek-chat",       # DeepSeek V4 Flash（OpenAI 兼容）
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    print("状态码:", response.status_code)
    if response.status_code != 200:
        print("返回内容:", response.text)
        raise Exception(f"API 调用失败，状态码 {response.status_code}: {response.text}")

    result = response.json()
    # OpenAI 兼容接口的响应解析方式
    summary = result["choices"][0]["message"]["content"]
    return summary

if __name__ == "__main__":
    # 读取真实数据文件（路径相对于项目根目录）
    data_file = "data/weekly_data.json"
    if not os.path.exists(data_file):
        print(f"错误：找不到 {data_file}，请先运行 01_fetch_data.py")
        exit(1)

    with open(data_file, "r", encoding="utf-8") as f:
        weekly_data = json.load(f)

    summary = generate_market_summary(weekly_data)
    print("\n生成的摘要：\n", summary)

    # 保存到 data/ai_summary.txt（注意：脚本在根目录运行，所以相对路径直接写 data/）
    os.makedirs("data", exist_ok=True)
    with open("data/ai_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    print("✅ 摘要已保存到 data/ai_summary.txt")