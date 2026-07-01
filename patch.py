import os
import struct
import sys

def patch_libsynocore_v3(file_path):
    print(f"[*] 开始分析文件: {file_path}")
    if not os.path.exists(file_path):
        print(f"[-] 错误: 找不到文件 {file_path}")
        return False
    
    with open(file_path, 'rb') as f:
        data = bytearray(f.read())
        
    # 1. 动态定位目标字符串 "string_join.c"
    old_str = b"string_join.c\x00"
    str_offset = data.find(old_str)
    if str_offset == -1:
        print("[-] 错误: 未能在文件中匹配到 'string_join.c' 特征字符串。")
        return False

    # 计算 "zh" 在文件中的绝对偏移位置 (.c 替换为 zh，z在索引11)
    zh_offset = str_offset + 11
    print(f"[+] 成功定位字符串基址: {hex(str_offset)}，'zh' 目标寻址位置: {hex(zh_offset)}")

    # 2. 动态搜索所有的 LEA RDI, [RIP + ...] 指令 (特征码: 48 8D 3D)
    lea_matches = []
    curr = 0
    while True:
        curr = data.find(b"\x48\x8D\x3D", curr)
        if curr == -1:
            break
        lea_matches.append(curr)
        curr += 1
        
    if not lea_matches:
        print("[-] 错误: 未能在文件中匹配到 LEA RDI 指令特征码。")
        return False
        
    target_lea_offset = None

    # 3. 跨版本模糊通用适配（算法匹配）
    print("[!] 启动跨版本动态跨度识别...")
    for lea_ptr in lea_matches:
        # 读取当前 LEA 指令的 4 字节小端序偏移
        old_offset = struct.unpack("<i", data[lea_ptr+3:lea_ptr+7])[0]
        next_instruction_addr = lea_ptr + 7
        
        # 算法核心：利用拓扑关系
        # 核心修补点的 LEA 指令下一条地址，距离 string_join.c 的固定距离通常是 0xCBF3
        # 我们在前后 0x1000 字节范围内寻找满足该控制流拓扑关系的唯一指令
        if abs((str_offset - next_instruction_addr) - 0xCBF3) < 0x1000:
            target_lea_offset = lea_ptr
            print(f"[+] 跨版本动态识别成功！锁定当前版本的 LEA 指令位置: {hex(target_lea_offset)}")
            break

    if target_lea_offset is None:
        print("[-] 错误: 无法在当前版本的文件中安全锁定修补点，请检查是否为正确的 libsynocore.so.7 文件。")
        return False

    # 4. 执行修改：将 string_join.c 修改为 string_joinzh
    data[str_offset+11] = 0x7A  # 'z'
    data[str_offset+12] = 0x68  # 'h'
    print("[+] 步骤 1/2: 字符资源层成功改写为 'string_joinzh'")

    # 5. 执行修改：计算全新的 RIP 相对寻址偏移量
    next_instr_addr = target_lea_offset + 7
    new_rip_offset = zh_offset - next_instr_addr

    # 打包为 4 字节小端序有符号整数 bytes
    new_offset_bytes = struct.pack("<i", new_rip_offset)

    # 覆写 LEA 指令内的偏移数据
    data[target_lea_offset+3:target_lea_offset+7] = new_offset_bytes
    print(f"[+] 步骤 2/2: 新相对寻址偏移量计算成功: {hex(new_rip_offset & 0xFFFFFFFF)}")
    print(f"[+] 修补后指令完整 HEX: {data[target_lea_offset:target_lea_offset+7].hex().upper()}")

    # 6. 自动备份并写入
    bak_path = file_path + ".bak"
    if not os.path.exists(bak_path):
        os.rename(file_path, bak_path)
        print(f"[+] 原始系统文件已备份至: {bak_path}")
    
    with open(file_path, 'wb') as f:
        f.write(data)
        
    print("[✔] 恭喜！libsynocore.so.7 拼音排序修补文件已成功生成！")
    return True

if __name__ == "__main__":
    # 支持拖拽文件到 exe 上运行，或者通过命令行传参
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_file = "libsynocore.so.7"
        print("提示：你可以直接把 libsynocore.so.7 拖拽到这个程序图标上运行！")
        
    patch_libsynocore_v3(target_file)
    input("\n按回车键退出...") # 防止 exe 运行完直接闪退