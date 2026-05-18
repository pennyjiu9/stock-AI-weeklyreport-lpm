import akshare as ak
import yfinance as yf
import json
import pandas as pd
import time
import os

# ========== 代理配置：仅在本地环境启用 ==========
# GitHub Actions 等 CI 环境不需要代理，直接直连
if not os.getenv('CI'):   # CI 环境变量在 GitHub Actions 中会被自动设为 'true'
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10808'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10808'
    print("✅ 本地模式：已启用代理 127.0.0.1:10808")
else:
    print("✅ CI 模式：直连，不设置代理")
# =============================================

def get_with_retry(func, retries=3, delay=2):
    """简单的重试装饰器"""
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"尝试 {i+1}/{retries} 失败: {e}")
            if i < retries - 1:
                time.sleep(delay)
            else:
                raise

def get_weekly_data():
    data = {}

    # ---------- A股指数 ----------
    def fetch_sh():
        sh = ak.stock_zh_index_daily(symbol="sh000001")
        sh = sh.tail(10)
        weekly_return = (sh['close'].iloc[-1] / sh['close'].iloc[-6] - 1) * 100
        return {
            'close': float(sh['close'].iloc[-1]),
            'change_pct': float(weekly_return)
        }
    try:
        data['上证指数'] = get_with_retry(fetch_sh)
        print("✅ 上证指数获取成功")
    except Exception as e:
        print(f"❌ 上证指数最终失败: {e}")
        data['上证指数'] = {'close': 0, 'change_pct': 0}

    def fetch_sz():
        sz = ak.stock_zh_index_daily(symbol="sz399001")
        sz = sz.tail(10)
        weekly_return = (sz['close'].iloc[-1] / sz['close'].iloc[-6] - 1) * 100
        return {
            'close': float(sz['close'].iloc[-1]),
            'change_pct': float(weekly_return)
        }
    try:
        data['深证成指'] = get_with_retry(fetch_sz)
        print("✅ 深证成指获取成功")
    except Exception as e:
        print(f"❌ 深证成指最终失败: {e}")
        data['深证成指'] = {'close': 0, 'change_pct': 0}

    def fetch_cy():
        cy = ak.stock_zh_index_daily(symbol="sz399006")
        cy = cy.tail(10)
        weekly_return = (cy['close'].iloc[-1] / cy['close'].iloc[-6] - 1) * 100
        return {
            'close': float(cy['close'].iloc[-1]),
            'change_pct': float(weekly_return)
        }
    try:
        data['创业板指'] = get_with_retry(fetch_cy)
        print("✅ 创业板指获取成功")
    except Exception as e:
        print(f"❌ 创业板指最终失败: {e}")
        data['创业板指'] = {'close': 0, 'change_pct': 0}

    # ---------- 美股指数（使用环境变量中的代理，不传 proxies 参数）----------
    def fetch_sp500():
        end = pd.Timestamp.now()
        start = end - pd.Timedelta(days=20)
        # 注意：这里不再传递 proxies 参数，因为代理已通过环境变量设置
        df = yf.download('^GSPC', start=start, end=end, progress=False, timeout=30)
        if df.empty or len(df) < 2:
            raise ValueError("数据不足")
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        close_val = last_close.item() if hasattr(last_close, 'item') else float(last_close)
        prev_val = prev_close.item() if hasattr(prev_close, 'item') else float(prev_close)
        change_pct = (close_val / prev_val - 1) * 100
        return {'close': close_val, 'change_pct': change_pct}
    try:
        data['标普500'] = get_with_retry(fetch_sp500, retries=3, delay=5)
        print("✅ 标普500获取成功")
    except Exception as e:
        print(f"❌ 标普500最终失败: {e}")
        data['标普500'] = {'close': 0, 'change_pct': 0}

    def fetch_nasdaq():
        end = pd.Timestamp.now()
        start = end - pd.Timedelta(days=20)
        df = yf.download('^IXIC', start=start, end=end, progress=False, timeout=30)
        if df.empty or len(df) < 2:
            raise ValueError("数据不足")
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        close_val = last_close.item() if hasattr(last_close, 'item') else float(last_close)
        prev_val = prev_close.item() if hasattr(prev_close, 'item') else float(prev_close)
        change_pct = (close_val / prev_val - 1) * 100
        return {'close': close_val, 'change_pct': change_pct}
    try:
        data['纳斯达克'] = get_with_retry(fetch_nasdaq, retries=3, delay=5)
        print("✅ 纳斯达克获取成功")
    except Exception as e:
        print(f"❌ 纳斯达克最终失败: {e}")
        data['纳斯达克'] = {'close': 0, 'change_pct': 0}

    # ---------- 行业数据（静态示例，确保非空）----------
    sectors_sample = {
        '通信': 4.5, '电子': 3.2, '计算机': 2.8,
        '汽车': 1.5, '医药': 0.3, '银行': -0.5,
        '地产': -1.2, '食品饮料': -2.1
    }
    data['sectors'] = [{'name': k, 'change_pct': v} for k, v in sectors_sample.items()]

    # 保存
    os.makedirs('data', exist_ok=True)
    with open('data/weekly_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ 数据已保存到 data/weekly_data.json")
    return data

if __name__ == '__main__':
    get_weekly_data()