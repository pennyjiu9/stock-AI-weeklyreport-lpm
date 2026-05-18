import subprocess
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cmd = ["quarto", "render", "report_template.qmd", "--to", "html,pdf"]

# 使用 utf-8 编码捕获输出，避免 Windows 下 gbk 解码错误
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

if result.returncode == 0:
    print("✅ 报告生成成功，请查看 output/ 文件夹")
    if result.stdout:
        print("输出信息：", result.stdout)
else:
    print("❌ 渲染失败：")
    print(result.stderr)