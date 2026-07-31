import os
import subprocess
import sys

scripts_dir = 'e:/trae_work/autoProject/backend/config/ui_scripts'
files = [f for f in os.listdir(scripts_dir) if f.endswith('.py') and f.startswith('recorder_')]
print('Recorder scripts:', files)

# 运行最新的 recorder 脚本查看错误
if files:
    latest = sorted(files)[-1]
    script_path = os.path.join(scripts_dir, latest)
    print(f'\nTesting: {latest}')
    
    # 用超时方式运行，避免长时间阻塞
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    try:
        # 等待3秒看是否有输出
        import time
        time.sleep(3)
        
        # 检查是否有错误输出
        import signal
        try:
            stdout, _ = process.communicate(timeout=2)
            print('Output:', stdout[:1000] if stdout else '(no output)')
        except subprocess.TimeoutExpired:
            print('Process still running after 5s (expected)')
            process.terminate()
            print('Process terminated')
            
    except Exception as e:
        print(f'Error: {e}')
        process.terminate()
