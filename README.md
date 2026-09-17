# trails-sky-2nd-ultrawide

A 32:9 / ultrawide fix for **The Legend of Heroes: Trails in the Sky 2nd Chapter** (Falcom, 2026, PC/Steam).

Removes the engine's aspect-ratio clamp (full-width rendering, no pillarboxing) and skips the cutscene letterbox bars.
Shipped as two equivalent implementations: a **SUWSF runtime patch** (modifies nothing on disk) or a **static byte patcher**.

> **Unofficial patch** — an independent third-party mod.
>
> 中文说明见文末（Chinese notes at the bottom of this page）。

---

## What it does

The engine clamps the render aspect ratio to a maximum, which causes pillar/letterboxing on ultrawide displays; cutscenes additionally draw top/bottom bars. This patch changes 4 instructions:

| # | File offset | Original | Patched | Effect |
|---|-------------|----------|---------|--------|
| 1 | `0x5abb2b` | `76 1A` (jbe) | `EB 1A` (jmp) | Skip the render **width** clamp branch |
| 2 | `0x5abb57` | `76 24` (jbe) | `EB 24` (jmp) | Skip the render **height** clamp branch |
| 3 | `0x513727` | `8B 88 B0 00 00 00` | `31 C9 90 90 90 90` | Cutscene bar (top) size = 0 |
| 4 | `0x513857` | `8B 88 B0 00 00 00` | `31 C9 90 90 90 90` | Cutscene bar (bottom) size = 0 |

- With both clamps skipped, the render resolution equals the full screen resolution (e.g. 5120x1440 edge to edge, no black borders).
- The bar size is read from a render-size field; forcing it to 0 stops the bars from being drawn.

**Tested environment**

- Steam buildid `25340742` (release day 2026-09-17), `sora_2nd.exe` size 13,463,552 bytes
- Vanilla exe SHA-256: `485EFF96B37B11860F39C2D1A7390D6C91F4046E79519A85076E1CA4CDB6B616`
- Steam AppID: `4225980`

> No game assets are included in this repository. Pick either installation method below — they have the same effect.

---

## Installation — Option A: SUWSF runtime patch (recommended)

[SUWSF](https://github.com/PhantomGamers/SUWSF) scans the process memory at launch for the byte patterns from an INI file and rewrites them — **the exe is never modified**, and the patch usually keeps working after game updates.

1. Make sure the **VC++ x64 runtime** is installed. Download `SUWSF-x64.zip` from [SUWSF Releases](https://github.com/PhantomGamers/SUWSF/releases) and extract it (`SUWSF.asi`, `SUWSF.ini`, `dsound.dll`).
2. Replace the sample INI with **this repo's `SUWSF.ini`**.
3. **Rename `dsound.dll` to `d3d11.dll`.**
   ⚠️ Important: this game does not import `dsound.dll` — it imports `D3D11CreateDevice` from `d3d11.dll`, so the loader must use that exact filename to be loaded by Windows.
4. Put `SUWSF.asi`, `SUWSF.ini` and `d3d11.dll` next to `sora_2nd.exe` (game root folder).
5. If you previously used the static patch, restore the exe first: `python apply_32x9_patch.py restore`.
6. Launch the game. A `SUWSF.log` file appears in the folder; it should contain:

   ```
   Found patch Patch:UW_ResWidthUnclamp
   ...
   Found 1 matches        <- width clamp
   Found 1 matches        <- height clamp
   Found 2 matches        <- cutscene bars (top + bottom)
   ```

   (`Found 0 matches` means the patterns no longer match: either the exe is already statically patched, or the game updated.)

**Uninstall**: delete `d3d11.dll`, `SUWSF.asi`, `SUWSF.ini` (and `SUWSF.log`) — the game itself is untouched.

> `d3d11.dll` is a new file added by this patch; game updates won't overwrite it. If a future game update breaks the patterns, open an issue with the new `SUWSF.log`.

---

## Installation — Option B: Static byte patcher

1. Patches the exe directly; the original is backed up automatically as `sora_2nd.exe.bak` on first run.

   ```
   python apply_32x9_patch.py            # apply
   python apply_32x9_patch.py restore    # restore the vanilla exe
   ```

2. Every game update overwrites the exe, so the patch must be re-applied. If the script reports a check failure, the offsets changed and need re-deriving.

**Pattern check** (works for both options — verifies that the current exe still matches `SUWSF.ini`):

```
python check_patterns.py                  # checks ./sora_2nd.exe + ./SUWSF.ini by default
python check_patterns.py sora_2nd.exe.bak # check the vanilla backup
```

---

## Known limitations

- Black borders drawn by the `black_belt` vfx during story scenes are not covered (they need runtime logic; neither the static patch nor SUWSF can do it).
- Some HUD anchor positions are likewise runtime logic and are not covered.

## Credits

- [SUWSF](https://github.com/PhantomGamers/SUWSF) by PhantomGamers — the runtime byte-patcher used here
- [Ultimate ASI Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader) by ThirteenAG — ASI loading
- Thanks to Lyall — the approach was inspired by his [Sky1stChapterFix](https://codeberg.org/Lyall/Sky1stChapterFix)
- The game is © Nihon Falcom — please support the official release.

## License

MIT

---

## 中文说明（Chinese）

《空之轨迹 the 2nd》32:9 / 超宽屏补丁（独立第三方作品；思路受 Lyall 的 *Sky1stChapterFix* 启发，详见 Credits）。

- **方式 A（推荐，不改游戏文件）**：下载 [SUWSF x64](https://github.com/PhantomGamers/SUWSF/releases)，用本仓库的 `SUWSF.ini` 替换示例配置，并把 `dsound.dll` **改名为 `d3d11.dll`**（本游戏只导入 `d3d11.dll`，必须用该文件名才会被加载）；三个文件放入游戏根目录。启动后检查 `SUWSF.log`，应显示 `Found 1 / 1 / 2 matches`。卸载＝删除这三个文件。
- **方式 B（静态）**：`python apply_32x9_patch.py` 打补丁 / `python apply_32x9_patch.py restore` 还原；游戏更新后需重打补丁。
- **自检**：`python check_patterns.py`（游戏更新后确认特征码是否仍匹配）。
- **已知限制**：vfx `black_belt` 演出黑边、部分 HUD 锚点需 ASI 插件级处理，暂未包含。

测试环境：Steam buildid `25340742`（2026-09-17）；原版 exe SHA-256 `485EFF96B37B11860F39C2D1A7390D6C91F4046E79519A85076E1CA4CDB6B616`。
