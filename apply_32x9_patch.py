# Trails in the Sky 2nd Chapter - 32:9 static byte patcher
# Approach inspired by Lyall's Sky1stChapterFix (https://codeberg.org/Lyall/Sky1stChapterFix)
#   1. Aspect-ratio unclamp: the engine clamps the render width/height to a maximum aspect
#      ratio (causing pillarboxing on 32:9). Turning the two JBE checks into JMP makes
#      the clamp branches unreachable; render resolution = full screen resolution.
#   2. Cutscene letterbox bars (top/bottom): the bar size is loaded from a render-size
#      field; force it to 0 (xor ecx, ecx) so the bars are not drawn.
# Usage: python apply_32x9_patch.py          # apply (auto-backup to .bak)
#        python apply_32x9_patch.py restore  # restore the vanilla exe
import shutil, sys, os

EXE = 'sora_2nd.exe'
BAK = EXE + '.bak'

# (file offset, expected bytes, patch bytes, description)
PATCHES = [
    (0x5abb2b, bytes.fromhex('76'),             bytes.fromhex('eb'),             'width clamp jbe->jmp'),
    (0x5abb57, bytes.fromhex('76'),             bytes.fromhex('eb'),             'height clamp jbe->jmp'),
    (0x513727, bytes.fromhex('8b88b0000000'),   bytes.fromhex('31c990909090'),   'letterbox top width=0'),
    (0x513857, bytes.fromhex('8b88b0000000'),   bytes.fromhex('31c990909090'),   'letterbox bottom width=0'),
]

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        if not os.path.exists(BAK):
            sys.exit('Backup not found: ' + BAK)
        shutil.copy2(BAK, EXE)
        print('Restored vanilla ' + EXE)
        return

    data = bytearray(open(EXE, 'rb').read())
    applied = all(bytes(data[o:o+len(p)]) == p for o, _, p, _ in PATCHES)
    if applied:
        sys.exit('Patch is already applied, nothing to do.')
    for off, expect, _, desc in PATCHES:
        if bytes(data[off:off+len(expect)]) != expect:
            sys.exit(f'Pattern check failed @ {off:#x} ({desc}): expected {expect.hex()}, got {bytes(data[off:off+len(expect)]).hex()}.\n'
                     'The game may have updated; the offsets need re-deriving.')
    if not os.path.exists(BAK):
        shutil.copy2(EXE, BAK)
        print('Backed up original -> ' + BAK)
    for off, _, patch, desc in PATCHES:
        data[off:off+len(patch)] = patch
        print(f'Patched @ {off:#x}  {desc}')
    open(EXE, 'wb').write(bytes(data))
    print('Done.')

main()
