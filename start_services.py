import subprocess
import sys
import os

# 启动后端服务
backend_dir = 'e:/trae_work/autoProject/backend'
backend_cmd = [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload']
backend_proc = subprocess.Popen(backend_cmd, cwd=backend_dir, 
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                               env=os.environ.copy())
print(f'Backend service started with PID: {backend_proc.pid}')

# 启动前端服务
frontend_dir = 'e:/trae_work/autoProject/frontend'
npm_cmd = 'npm run dev'
frontend_proc = subprocess.Popen(npm_cmd, cwd=frontend_dir, shell=True,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
print(f'Frontend service started with PID: {frontend_proc.pid}')

print('Both services are starting...')
print('Backend API: http://localhost:8000')
print('Frontend UI: http://localhost:5173')
