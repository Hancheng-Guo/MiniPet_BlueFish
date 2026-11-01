# MiniPet_BlueFish

蓝色大肥鱼的 ChatGPT Mini Pet 素材项目，包含常服、冬装两套独立造型。两套使用相同的目录结构和 ChatGPT Pets v2 精灵图布局。

## 从哪里开始

| 用途 | 常服 | 冬装 |
| --- | --- | --- |
| 最终精灵图 | [spritesheet.png](常服/spritesheet.png) | [spritesheet.png](冬装/spritesheet.png) |
| 名称、描述、帧位置与校验值 | [素材清单.json](常服/素材清单.json) | [素材清单.json](冬装/素材清单.json) |
| 全动作预览 | [all-states.gif](常服/预览/all-states.gif) | [all-states.gif](冬装/预览/all-states.gif) |
| 造型说明 | [README](常服/README.md) | [README](冬装/README.md) |

创建宠物所用的图像文件是所选造型的 `spritesheet.png`；名称和描述可参考该目录的 `素材清单.json`。逐帧图用于后续编辑、重新组装，预览和创作素材用于检查与维护，不需要合入上传图。素材清单是本项目的管理文件，并非 ChatGPT 官方导入配置。

## 统一目录

```text
常服/ 或 冬装/
├── README.md
├── spritesheet.png       # 最终上传图像
├── 素材清单.json          # 名称、描述、历史宠物 ID、帧路径与 SHA-256
├── contact-sheet.png     # 动作总览
├── directions.png        # 方向总览
├── 逐帧PNG/              # 73 张透明单帧，按标准状态命名
├── 预览/                 # 统一的 12 个动作、方向及过渡 GIF
├── 创作素材/             # 当前可用源图、生成记录或素材说明
└── 验证/                 # 已有报告、当前素材完整性记录和验证范围说明
```

目录职责保持一致；创作素材和预览文件名统一，验证报告按实际已有资料保留，缺失报告不补造。以根目录的最终精灵图及逐帧图为编辑起点。旧版本、修复前后对照和历史素材包交由 Git 保存，不在当前目录重复归档。

### 必要预览

常服、冬装的 `预览/` 均保留以下 12 个 GIF：

- 九个独立动作：`idle.gif`、`running-right.gif`、`running-left.gif`、`waving.gif`、`jumping.gif`、`failed.gif`、`waiting.gif`、`running.gif`、`review.gif`。
- `all-states.gif`：依次播放九个标准动作，便于快速检查整体表现；方向单独检查。
- `look-loop.gif`：16 个看向方向的完整循环。
- `idle-hover-idle.gif`：待机 → 悬停吃饭 → 待机，用于检查交互切换。

这些预览用于本地检查，不是上传文件。单张静态截图与 `逐帧PNG/` 重复，已从预览目录移除；动作、方向静态总览仍保留在各造型根目录的 `contact-sheet.png` 和 `directions.png`。常服新增过渡 GIF 由当前逐帧 PNG 直接编码，没有重绘角色。

## 精灵图布局

最终图为透明 PNG，1536 × 2288 像素；8 列 × 11 行，每格 192 × 208 像素。共 73 个有效帧，剩余 15 格保持透明。文件需不超过 20 MiB。

| 行（从 0 开始） | 状态 | 帧数 |
| --- | --- | ---: |
| 0 | idle | 6 |
| 1 | running-right | 8 |
| 2 | running-left | 8 |
| 3 | waving | 4 |
| 4 | jumping | 5 |
| 5 | failed | 8 |
| 6 | waiting | 6 |
| 7 | running | 6 |
| 8 | review | 6 |
| 9–10 | look | 16 |

单帧文件名从 `00.png` 开始。`look` 按顺时针从正上方开始，每帧间隔 22.5°，第 8 帧起放在第 10 行。`running` 表示工作处理状态；左右移动分别使用 `running-right`、`running-left`。

本项目保留原有吃白米饭的悬停动作，占用 `jumping` 行。常服旧名称 `jumping-hover-eating` 已统一为 `jumping`，仅更名，未修改画面；它不等同于已满足当前规范所要求的离地跳跃。

## 修改与创建流程

1. 选择造型，查看 `预览/all-states.gif`、动作总览和方向总览。
2. 需要修改时，从对应的 `逐帧PNG/` 或 `创作素材/` 开始；重新组装时保持上表布局、透明留白和各帧定位。
3. 更新最终精灵图后，同步更新单帧、预览和素材清单中的 SHA-256。
4. 使用 ChatGPT Pets 创建技能的正式流程重新运行精灵图与画面质量检查，并检查动作、方向及悬停过渡，再对最终上传文件执行平台预检。
5. 在支持自定义 Pets 的环境中，使用最终精灵图及名称、描述完成上传和创建。素材清单中的 `pet_id` 仅用于记录既有宠物，不能作为新建时的上传会话 ID。

本次整理保留原始图像字节，执行了文件完整性和单帧对应关系检查；不表示两套素材已通过当前版本的完整创建验收。历史报告的适用范围见各造型的 `验证/README.md`。
