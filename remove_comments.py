import re
import os

# 读取main.py文件内容
file_path = os.path.join("d:\p\Hacker Srumble-Cpp", "main.py")
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# 删除Python多行注释（三引号）
multi_line_pattern = re.compile(r'("""[\s\S]*?""")|(\'\'\'[\s\S]*?\'\'\')', re.DOTALL)
content = multi_line_pattern.sub('', content)

# 删除Python单行注释
lines = content.split('\n')
cleaned_lines = []
for line in lines:
    # 保留代码部分，去掉注释部分，但要注意处理字符串中的#符号
    code_part = ''
    in_string = False
    quote_char = None
    i = 0
    while i < len(line):
        # 处理字符串开始/结束
        if line[i] in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
            if not in_string:
                in_string = True
                quote_char = line[i]
            elif line[i] == quote_char:
                in_string = False
        # 如果不是在字符串中，且遇到#，则停止处理该行
        elif not in_string and line[i] == '#':
            break
        # 否则保留字符
        code_part += line[i]
        i += 1
    # 添加清理后的行，如果不为空
    cleaned_line = code_part.rstrip()
    if cleaned_line:
        cleaned_lines.append(cleaned_line)

# 重新组合内容
cleaned_content = '\n'.join(cleaned_lines)

# 保存清理后的内容回文件
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(cleaned_content)

print("所有注释已成功删除！")