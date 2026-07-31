import os
import re

# 读取 main.py 文件内容
main_py = os.path.join(os.path.dirname(__file__), "app", "main.py")
with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找 RECORD_INJECT_SCRIPT 定义
match = re.search(r"RECORD_INJECT_SCRIPT = '''(.*?)'''", content, re.DOTALL)
if match:
    script_content = match.group(1)
    print(f"RECORD_INJECT_SCRIPT length: {len(script_content)}")
    
    # 检查是否有双花括号
    if '{{' in script_content:
        print("WARNING: '{{' found in RECORD_INJECT_SCRIPT!")
        idx = script_content.find('{{')
        print(f"  At position {idx}: {repr(script_content[max(0,idx-20):idx+30])}")
    if '}}' in script_content:
        print("WARNING: '}}' found in RECORD_INJECT_SCRIPT!")
        idx = script_content.find('}}')
        print(f"  At position {idx}: {repr(script_content[max(0,idx-20):idx+30])}")
else:
    print("Could not find RECORD_INJECT_SCRIPT")

# 查找 template 定义
template_matches = list(re.finditer(r"template = '''(.*?)'''", content, re.DOTALL))
print(f"\nFound {len(template_matches)} template definitions")

for i, m in enumerate(template_matches):
    template_content = m.group(1)
    print(f"\nTemplate {i+1} length: {len(template_content)}")
    print(f"  Contains '{{': {'{{' in template_content}")
    print(f"  Contains '}}': {'}}' in template_content}")
    
    # 查找具体的双花括号位置
    for mm in re.finditer(r'\{\{', template_content):
        pos = mm.start()
        context = template_content[max(0,pos-20):pos+40]
        print(f"  Double '{{' at {pos}: ...{repr(context)}...")
    
    for mm in re.finditer(r'\}\}', template_content):
        pos = mm.start()
        context = template_content[max(0,pos-20):pos+40]
        print(f"  Double '}}' at {pos}: ...{repr(context)}...")

# 检查关键代码行
print("\n\nChecking key lines around template generation...")
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'template.replace' in line or 'inject_script_repr' in line or 'script_content = template' in line:
        print(f"  Line {i+1}: {line}")

# 检查 f-string 定义
print("\n\nChecking for f-strings with double braces...")
for i, line in enumerate(lines):
    if ('f"' in line or "f'" in line) and ('{{' in line or '}}' in line):
        print(f"  Line {i+1}: {line}")