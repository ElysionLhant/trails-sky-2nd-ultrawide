# 空之轨迹 the 2nd 32:9 补丁（静态字节补丁）
# 思路移植自 Lyall 的 Sky1stChapterFix（https://codeberg.org/Lyall/Sky1stChapterFix）
#   1. 分辨率解钳制：游戏原逻辑在 画面宽高比 > 上限 时把渲染宽度钳制回上限（产生 32:9 黑边），
#      把两处 jbe 改为 jmp 后，钳制分支永远跳过，渲染分辨率=全屏分辨率，居中偏移=0。
#   2. 过场黑条（Letterbox Top/Bottom）：黑条矩形的宽度原本取自渲染宽度，改为恒 0（xor ecx,ecx），
#      黑条不再绘制。
# 用法：python apply_32x9_patch.py        # 打补丁（自动备份 .bak）
#       python apply_32x9_patch.py restore  # 还原
import shutil, sys, os

EXE = 'sora_2nd.exe'
BAK = EXE + '.bak'

# (文件偏移, 期望原字节, 补丁字节, 说明)
PATCHES = [
    (0x5abb2b, bytes.fromhex('76'),             bytes.fromhex('eb'),             '分辨率宽度钳制 jbe->jmp'),
    (0x5abb57, bytes.fromhex('76'),             bytes.fromhex('eb'),             '分辨率高度钳制 jbe->jmp'),
    (0x513727, bytes.fromhex('8b88b0000000'),   bytes.fromhex('31c990909090'),   '过场上黑条 宽度=0'),
    (0x513857, bytes.fromhex('8b88b0000000'),   bytes.fromhex('31c990909090'),   '过场下黑条 宽度=0'),
]

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        if not os.path.exists(BAK):
            sys.exit('没有找到备份 ' + BAK)
        shutil.copy2(BAK, EXE)
        print('已还原原版 ' + EXE)
        return

    data = bytearray(open(EXE, 'rb').read())
    applied = all(bytes(data[o:o+len(p)]) == p for o, _, p, _ in PATCHES)
    if applied:
        sys.exit('补丁已处于应用状态，无需重复打。')
    for off, expect, _, desc in PATCHES:
        if bytes(data[off:off+len(expect)]) != expect:
            sys.exit(f'校验失败 @ {off:#x}（{desc}）：期望 {expect.hex()}，实际 {bytes(data[off:off+len(expect)]).hex()}。\n'
                     '游戏可能已更新，补丁偏移需要重新适配。')
    if not os.path.exists(BAK):
        shutil.copy2(EXE, BAK)
        print('已备份原版 -> ' + BAK)
    for off, _, patch, desc in PATCHES:
        data[off:off+len(patch)] = patch
        print(f'已补丁 @ {off:#x}  {desc}')
    open(EXE, 'wb').write(bytes(data))
    print('完成。')

main()
