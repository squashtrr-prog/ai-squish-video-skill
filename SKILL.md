---
name: ai-squish-video
description: 制作食物拟态史莱姆、AI 捏捏和解压 ASMR 短视频内容包。用于用户提出 AI 捏捏、食物解压、史莱姆首帧、15 秒 MiniMax H3 提示词或小红书发布包时；首次使用先确认并保存输出目录，再按选题、首帧、视频提示词、标题和发布包的硬确认流程推进。
metadata:
  version: 1.0.0
  author: squashtrr-prog
  license: MIT
---

# AI 捏捏视频

把一个食物主题推进为完整的 15 秒解压短视频内容包：随机选题、9:16 首帧、MiniMax H3 中英双语视频提示词、小红书标题文案和可追溯归档。

只读取当前阶段指定的 reference。不要一次加载全部规则、模板或历史输出。

## 首次运行配置

在选题或创建文件前，先运行：

```bash
python "<skill-dir>/scripts/ai_squish.py" config show
```

如果返回 `configured: false`，或者已保存的目录不可用：

1. 询问用户希望把每次生成的内容保存到哪个目录，并要求提供明确路径。
2. 告知用户每次任务会在该目录内新建 `yyyyMMdd-HHmmss-主题` 子目录，不会覆盖旧文件。
3. 说明内容包包含首帧提示词、首帧图片、H3 中英文提示词、标题文案、标签和制作记录。
4. 汇总配置并等待用户明确确认。未确认前不得生成选题、图片或任何内容文件。
5. 确认后运行：

```bash
python "<skill-dir>/scripts/ai_squish.py" config set --output-root "<用户确认的目录>"
```

后续调用若配置有效，简短告知当前输出根目录并直接继续。用户随时可以要求更换目录；更换前仍需确认新路径，再执行 `config set`。

配置默认保存在系统用户配置目录。可通过 `AI_SQUISH_CONFIG` 环境变量改写配置文件位置；不要把个人路径写回本仓库。

## 状态机与确认闸门

从对话识别当前状态，只推进尚未完成的阶段：

1. `AWAITING_SETUP_CONFIRMATION`：首次运行配置尚未确认。
2. `AWAITING_TOPIC`：提供 8 个随机主题，等待选择。
3. `AWAITING_IMAGE_APPROVAL`：生成并展示首帧，等待确认。
4. `AWAITING_H3_APPROVAL`：生成 H3 中英双语完整提示词，等待确认。
5. `AWAITING_TITLE_CHOICE`：提供 5 个标题，等待选择。
6. `COMPLETE`：生成文案、标签和制作记录，并核查归档。

所有“等待”都是硬闸门：到达后结束当前回复，不得替用户确认。用户否定时只重做当前阶段，所有新版本递增编号，不覆盖旧版本。

## 阶段 1：主题

如果用户尚未指定主题，只运行：

```bash
python "<skill-dir>/scripts/ai_squish.py" topics --count 8
```

将结果编号 1–8，保留类别和 emoji，只询问用户选择哪一个，然后停止。此阶段不读取任何 reference 或模板。

用户选定或直接指定主题后运行：

```bash
python "<skill-dir>/scripts/ai_squish.py" create-run --topic "<主题>"
```

将返回的绝对路径作为本次唯一输出目录。

## 阶段 2：首帧

只读取 [references/runtime-image.md](references/runtime-image.md) 并执行。生成、保存并展示首帧后等待确认。

## 阶段 3：H3 提示词

仅在首帧确认后读取 [references/runtime-h3.md](references/runtime-h3.md) 并执行。完整展示英文版与逐段等义中文版后等待确认。

## 阶段 4：标题

仅在 H3 提示词确认后读取 [references/runtime-titles.md](references/runtime-titles.md) 并执行。给出 5 个标题后等待用户选择。

## 阶段 5：发布包

用户选定标题后读取 [references/runtime-publish.md](references/runtime-publish.md) 并执行。完成后报告输出目录、最终标题和核心文件。

## 文件与隐私安全

- 只在用户确认的输出根目录及本次任务子目录中新增内容。
- 模板只读，不修改 `references/templates/` 内的源文件。
- 不把未经清理的用户输入直接拼入文件名；目录名由脚本清洗。
- 不记录用户隐私、模型密钥、内部工具信息或未公开素材来源。
- 图像工具不能直接落盘时，优先复制其本地输出；无法保存时如实说明，不虚报归档完成。
- 输出目录不可写、配置损坏或模板缺失时停止并说明具体问题，不自行改用其他目录。

## 低消耗规则

- 选题阶段不读 reference；后续每阶段只读一个对应的 runtime 文件。
- 不读取旧输出、历史图片或历史完整提示词，除非用户明确要求比较或复用。
- 不为节省 Token 压缩 H3 中英文正文；模板规定的字段、时间轴、动作和声景必须完整。
- 不无限重做图片；每次重做应来自用户反馈或可见硬失败。
