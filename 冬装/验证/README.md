# 验证记录 · 冬装

本目录原有 JSON 均为历史生成时保留的原始报告，未修改其中的绝对路径和检查结果。原机器路径用于追溯，当前素材路径以 `../素材清单.json` 为准。

- `validation-extended.json`：原精灵图检查。
- `review.json`：原动作帧检查。
- `chroma-despill-extended.json`：原色键边缘处理记录。
- `direction-semantics.json`、`look-continuity.json`：原方向语义与连续性检查。
- `pet-quality.json`：原质量汇总，包含最终图 SHA-256 和告警。
- `素材完整性.json`：本次整理后的本地文件与单帧对应检查，不是正式质量验收。

原 `pet-quality.json` 虽记录 `ok: true`，但同时记录 `airborne_lift_pixels: 0` 及方向孔洞、首尾连续性告警。保留这些事实；不将历史通过结果等同于当前技能的完整验收。重新创建或替换时，应对最终字节重新执行正式检查和平台预检。
