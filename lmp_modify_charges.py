import re
# import os
def modify_charge_only(input_file, output_file):
    # 1. 定义各区间电荷规则（仅更新elem_charge_map的数值，其他完全不变）
    charge_group1 = [-0.6750957486, 0.2383586420, 0.2383586420, 0.4638739783,
                     -0.0090754506, -0.0090754506, -0.5834434289, 0.3360988165]
    charge_group2 = [0.0770263515, 0.0392325988, 0.0392325988, 0.3063565794,
                     0.0043122093, 0.0043122093, -0.4704725470]
    charge_group3 = [-0.0326139987, 0.0103821741, 0.0103821741, 0.0103821741,
                     0.2583968995, -0.0283060923, -0.0283060923, -0.2003172383]
    # -------------------------- 仅更新此处的元素-电荷映射数值 --------------------------
    elem_charge_map = {
        'n': -0.98945714,    # 新数值
        'o': -0.553871429,   # 新数值
        'f': -0.132714286,   # 新数值
        'c': 0.393142857,    # 新数值
        's': 1.107471429     # 新数值
    }
    # --------------------------------------------------------------------------------

    # 2. 处理状态标记：是否进入Atoms段（格式保留逻辑完全不变）
    in_atom_section = False
    with open(input_file, 'r', encoding='utf-8') as in_f, \
         open(output_file, 'w', encoding='utf-8') as out_f:
        
        for line in in_f:
            # 2.1 检测Atoms段开始：只在"Atoms # full"后开始处理
            if 'Atoms # full' in line:
                in_atom_section = True
                out_f.write(line)
                continue
            
            # 2.2 检测Atoms段结束：遇到Bonds则停止，后续内容原样输出
            if in_atom_section and 'Bonds' in line:
                in_atom_section = False
                out_f.write(line)
                for remaining_line in in_f:
                    out_f.write(remaining_line)
                break
            
            # 2.3 处理Atoms段内的行（只改电荷列，不动格式）
            if in_atom_section:
                if not line.strip():
                    out_f.write(line)
                    continue
                
                # 精准定位各列的字符位置，不破坏原始空格
                col_matches = list(re.finditer(r'\S+', line))
                if len(col_matches) < 4:
                    out_f.write(line)
                    continue
                
                try:
                    # 提取原子索引，计算目标电荷（规则完全不变）
                    atom_index = int(col_matches[0].group())
                    new_charge = 0.0
                    if 1 <= atom_index <= 29670:
                        pos_in_cycle = (atom_index - 1) % 989 + 1
                        if 1 <= pos_in_cycle <= 8:
                            new_charge = charge_group1[pos_in_cycle - 1]
                        elif 9 <= pos_in_cycle <= 981:
                            new_charge = charge_group2[(pos_in_cycle - 9) % len(charge_group2)]
                        elif 982 <= pos_in_cycle <= 989:
                            new_charge = charge_group3[pos_in_cycle - 982]
                    elif 29671 <= atom_index <= 29860:
                        new_charge = 1.0
                    elif 29861 <= atom_index <= 32710:
                        # 按新的elem_charge_map赋值（仅数值变化，逻辑不变）
                        if '#' in line:
                            comment_part = line[line.index('#')+1:]
                            for char in comment_part:
                                if char.isalpha():
                                    new_charge = elem_charge_map.get(char.lower(), 0.0)
                                    break
                
                    # 仅替换电荷列字符，保留所有格式（逻辑完全不变）
                    new_charge_str = f"{new_charge:.10f}"
                    modified_line = (
                        line[:col_matches[3].start()]
                        + new_charge_str
                        + line[col_matches[3].end():]
                    )
                    out_f.write(modified_line)

                except (ValueError, IndexError):
                    out_f.write(line)
                    continue
            
            # 2.4 非Atoms段：所有内容原样输出
            else:
                out_f.write(line)

# 调用函数（替换为你的实际文件路径）
if __name__ == "__main__":
    input_path = "initial_PEO_Li_TFSI.data"
    output_path = "modified_PEO_Li_TFSI.data"
    modify_charge_only(input_path, output_path)
    print(f"已按新元素电荷值修改！\n原始文件：{input_path}\n修改后文件：{output_path}")
