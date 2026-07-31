import os
import json

scripts_dir = 'e:/trae_work/autoProject/backend/config/ui_scripts'
files = [f for f in os.listdir(scripts_dir) if f.endswith('.json') and f.startswith('record_')]
print('Record files:', files)

for f in files[:3]:
    filepath = os.path.join(scripts_dir, f)
    try:
        with open(filepath, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            print(f'\n{f}:')
            print(f'  Status: {data.get("status")}')
            print(f'  Actions count: {data.get("count", len(data.get("actions", [])))}')
    except Exception as e:
        print(f'\n{f}: Error reading - {e}')
