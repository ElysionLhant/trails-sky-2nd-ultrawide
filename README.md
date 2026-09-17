# trails-sky-2nd-ultrawide

**空之轨迹 the 2nd / Trails in the Sky 2nd Chapter —— 32:9 / 超宽屏补丁**

*无黑边全幅渲染（解锁宽高比钳制）+ 去除过场黑条。两种等价实现：SUWSF 运行时补丁（不改游戏文件）或静态字节补丁。*

A 32:9 (and general ultrawide) fix for *The Legend of Heroes: Trails in the Sky 2nd Chapter* (Falcom, 2026 PC/Steam).

> ⚠️ **非官方、临时性补丁（stop-gap）**：若 Lyall 发布正式的 *Sky2ndChapterFix*，请优先使用官方修复；本仓库届时会更新指引（见文末「共存说明」）。

---

## 补丁内容

游戏原版会把渲染宽高比钳制在某个上限，超宽屏下出现两侧黑边；过场演出还会绘制上下黑条。本补丁共修改 4 处机器码：

| # | 文件偏移 | 原始 | 修改后 | 作用 |
|---|----------|------|--------|------|
| 1 | `0x5abb2b` | `76 1A`（jbe） | `EB 1A`（jmp） | 跳过「渲染宽度钳制」分支 |
| 2 | `0x5abb57` | `76 24`（jbe） | `EB 24`（jmp） | 跳过「渲染高度钳制」分支 |
| 3 | `0x513727` | `8B 88 B0 00 00 00` | `31 C9 90 90 90 90` | 过场黑条（上）尺寸=0 |
| 4 | `0x513857` | `8B 88 B0 00 00 00` | `31 C9 90 90 90 90` | 过场黑条（下）尺寸=0 |

- 宽度/高度钳制改为无条件跳过后，渲染分辨率 = 全屏分辨率（例如 5120x1440 全幅渲染、无黑边）。
- 黑条尺寸取自渲染尺寸字段，置 0 后不再绘制。

**测试环境**

- Steam buildid `25340742`（发售日 2026-09-17），`sora_2nd.exe` 大小 13,463,552 字节
- 原版 exe SHA-256：`485EFF96B37B11860F39C2D1A7390D6C91F4046E79519A85076E1CA4CDB6B616`
- Steam AppID：`4225980`

> 本仓库不包含任何游戏资源。两种安装方式任选其一，效果完全相同。

---

## 安装方式 A：SUWSF 运行时补丁（推荐）

原理：[SUWSF](https://github.com/PhantomGamers/SUWSF) 在游戏启动时按 INI 里的特征码扫描内存并改写字节——**不改动 exe**，游戏更新覆盖 exe 后通常仍自动生效。

1. 确保已安装 **VC++ x64 运行库**；从 [SUWSF Releases](https://github.com/PhantomGamers/SUWSF/releases) 下载 `SUWSF-x64.zip` 并解压（得到 `SUWSF.asi`、`SUWSF.ini`、`dsound.dll`）。
2. 用**本仓库的 `SUWSF.ini`** 替换解压出来的示例 INI。
3. **把 `dsound.dll` 改名为 `d3d11.dll`**。
   ⚠️ 关键步骤：本游戏不导入 `dsound.dll`，只从 `d3d11.dll` 导入 `D3D11CreateDevice`，因此加载器必须以 `d3d11.dll` 的文件名放在游戏目录才会被系统加载。
4. 把 `SUWSF.asi`、`SUWSF.ini`、`d3d11.dll` 一起放到游戏根目录（`sora_2nd.exe` 旁边）。
5. 若此前用过静态补丁，先还原 exe：`python apply_32x9_patch.py restore`。
6. 启动游戏。目录下会生成 `SUWSF.log`，正常应能看到：

   ```
   Found patch Patch:UW_ResWidthUnclamp
   ...
   Found 1 matches        <- 宽度钳制
   Found 1 matches        <- 高度钳制
   Found 2 matches        <- 过场黑条（上下两处）
   ```

   （`Found 0 matches` 表示特征码失配：要么 exe 已被静态补丁改过，要么游戏更新了。）

**卸载**：删除 `d3d11.dll`、`SUWSF.asi`、`SUWSF.ini`（和 `SUWSF.log`）即可，游戏本体零改动。

> `d3d11.dll` 是本补丁新增的文件，游戏更新不会覆盖它。若未来游戏改动导致失配，欢迎提 issue 附上新的 `SUWSF.log`。

---

## 安装方式 B：静态字节补丁

1. 直接改 exe；首次运行自动备份原版为 `sora_2nd.exe.bak`。

   ```
   python apply_32x9_patch.py            # 打补丁
   python apply_32x9_patch.py restore    # 还原原版
   ```

2. 游戏每次更新都会覆盖 exe，需要重新打补丁；若脚本提示「校验失败」，说明程序偏移变化，需要重新适配。

**特征码自检**（两种方式通用，用于确认当前 exe 是否仍可与 `SUWSF.ini` 匹配）：

```
python check_patterns.py                  # 默认检查同目录 sora_2nd.exe + SUWSF.ini
python check_patterns.py sora_2nd.exe.bak # 检查原版备份
```

---

## 已知限制

- 剧情演出中 vfx `black_belt` 绘制的黑边/黑框不在处理范围（需要 ASI 插件级别的运行时判断，静态补丁与 SUWSF 均做不了）。
- 部分 HUD 锚点位置同样属于运行时逻辑项，未处理。
- 若关于 Lyall 官方修复的共存说明

- 本补丁与 Lyall **无隶属关系**，也未使用其任何代码：4 处修改均为本仓库独立逆向得出，仅在思路上受到 *Sky1stChapterFix* 的启发（详见 Credits）。
- 这是一个**临时（stop-gap）方案**：截至 2026-09，作者尚未发布 2nd Chapter 版本（其 1st Chapter 版已修复同类核心问题，另含近距消抖等附加功能）。若其发布 2nd Chapter 版本，请优先使用官方修复。
- 当官方修复发布后，本仓库会更新 README 指引大家优先使用官方版本（并考虑归档）。
- 请勿与其他超宽屏补丁叠加使用，保留一种即可。

##  Lyall 发布正式的 *Sky2ndChapterFix*，建议平滑切换：<https://codeberg.org/Lyall>

## Credits

- [SUWSF](https://github.com/PhantomGamers/SUWSF) by PhantomGamers —— 通用运行时字节补丁器
- [Ultimate ASI Loader](https://github.com/ThirteenAG/Ultimate-ASI-Loader) by ThirteenAG
- 逆向思路参考 Lyall 的 [Sky1stChapterFix](https://codeberg.org/Lyall/Sky1stChapterFix)
- 游戏版权归 Nihon Falcom 所有；请支持正版

## License

MIT

---

## English (short)

32:9 / ultrawide fix for **Trails in the Sky 2nd Chapter** (Falcom 2026, Steam AppID 4225980). Removes the engine's aspect-ratio clamp (full-width rendering, no pillar/letterboxing) and skips the cutscene letterbox bars — 4 byte-level writes, shipped as two equivalent implementations:

- **A. Runtime (recommended):** drop `SUWSF.asi` + this repo's `SUWSF.ini` + the SUWSF loader **renamed to `d3d11.dll`** next to `sora_2nd.exe` (the game imports `D3D11CreateDevice` from `d3d11.dll` and does *not* import `dsound.dll`). Check `SUWSF.log` for `Found 1 / 1 / 2 matches`. No game files are modified; delete the 3 files to uninstall.
- **B. Static:** `python apply_32x9_patch.py` (auto-backup) / `python apply_32x9_patch.py restore`. Re-apply after every game update.

Tested on Steam buildid 25340742 (2026-09-17); vanilla exe SHA-256 `485EFF96B37B11860F39C2D1A7390D6C91F4046E79519A85076E1CA4CDB6B616`.

Known limitations: vfx `black_belt` cutscene borders and some HUD anchors need an ASI plugin and are not covered.

Credits: SUWSF (PhantomGamers), Ultimate ASI Loader (ThirteenAG); approach inspired by Lyall's Sky1stChapterFix. MIT license. No game assets are included.
