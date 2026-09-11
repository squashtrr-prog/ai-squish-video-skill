![AI 捏捏 Skill 大公开](docs/images/cover.png)

# AI Squish Video Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-111111.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-84ff5a.svg)](scripts/ai_squish.py)

一个面向 Agent 的 AI 捏捏短视频工作流：从随机食物选题开始，依次完成 9:16 首帧、15 秒 MiniMax H3 中英双语提示词、小红书标题文案和可追溯归档。

它不是一条万能 Prompt，而是一条不会跳步骤的制作流水线。

## 能做什么

- 从内置主题池随机抽取 8 个不重复的食物主题。
- 生成适合后续形变的 9:16 微距产品摄影首帧。
- 依据已确认首帧编排 15 秒连续动作，而不是让画面凭空换物。
- 输出结构完整的 MiniMax H3 英文提示词及逐段等义中文版提示词。
- 为关键阶段设置确认闸门：首帧、H3 和标题未经确认就不会继续。
- 自动建立时间戳目录，并归档图片、提示词、文案、标签和制作记录。
- 首次使用先询问输出目录；配置保存在用户目录，不把个人路径写进 Skill。

![AI 捏捏工作流](docs/images/workflow.png)

## 示例

下图是这套 Skill 生成的两种首帧方向。一个强调半透明、弹性的豆荚结构，一个强调蓬松外壳与软糯夹心。后续动作和声音会根据画面里的真实材质分别编排。

<p align="center">
  <img src="docs/images/example-pea.png" width="47%" alt="半透明豌豆拟态首帧">
  <img src="docs/images/example-puff.png" width="31.3%" alt="软糯泡芙拟态首帧">
</p>

## 安装

### Skills CLI

```bash
npx skills add squashtrr-prog/ai-squish-video-skill
```

### Codex 手动安装

```bash
git clone https://github.com/squashtrr-prog/ai-squish-video-skill.git ~/.codex/skills/ai-squish-video
```

Windows PowerShell：

```powershell
git clone https://github.com/squashtrr-prog/ai-squish-video-skill.git "$env:USERPROFILE\.codex\skills\ai-squish-video"
```

安装后重启或重新加载 Agent，让它重新发现 `SKILL.md`。

## 第一次使用

在支持 Agent Skills 的客户端中说：

```text
使用 ai-squish-video 帮我做一条 AI 捏捏视频。
```

第一次调用时，Skill 会先询问内容包的保存位置，并说明将创建哪些文件。只有在你明确确认后，它才会保存配置并进入选题流程。

配置文件默认位置：

- Windows：`%APPDATA%\ai-squish-video\config.json`
- macOS / Linux：`$XDG_CONFIG_HOME/ai-squish-video/config.json` 或 `~/.config/ai-squish-video/config.json`

如需自定义配置文件位置，可设置环境变量 `AI_SQUISH_CONFIG`。

## 工作流

1. **首次配置**：询问、复述并确认输出根目录。
2. **随机选题**：给出 8 个不重复的食物主题，等待用户选择。
3. **锁定首帧**：生成首帧及提示词，确认画面后才继续。
4. **编排 H3**：依据首帧写满 15 秒动作、物理反馈和 ASMR 声景。
5. **确认标题**：从 5 个候选标题里选择最终版本。
6. **归档发布包**：保存文案、标签、确认版本和制作记录。

每一个“等待确认”都是硬闸门。否定当前结果时只重做当前阶段，新版本按 `v02`、`v03` 递增，不覆盖旧文件。

## 输出结构

```text
<你确认的输出目录>/
└── 20260911-153000-草莓/
    ├── run.json
    ├── 00-制作记录.txt
    ├── 01-首帧图片提示词-v01.txt
    ├── 02-首帧-v01.png
    ├── 03-H3视频提示词-英文-v01.txt
    ├── 03-H3视频提示词-中文-v01.txt
    └── 04-小红书发布文案.txt
```

## 运行时工具

`scripts/ai_squish.py` 只使用 Python 标准库，可独立检查：

```bash
python scripts/ai_squish.py doctor
python scripts/ai_squish.py config show
python scripts/ai_squish.py topics --count 8
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

## 兼容性

- Agent：Codex、Claude Code，以及其他兼容 `SKILL.md` 的 Agent 客户端
- Python：3.10+
- 图像模型：需要客户端提供可调用的图像生成能力
- 视频提示词：按 MiniMax H3 的 15 秒视频结构编排

Skill 生成提示词和内容包，不会替你绕过所使用模型或平台的权限、额度与内容政策。

## 隐私

- 输出目录只保存在本机用户配置中，不提交到仓库。
- Skill 不要求 API Key，也不会读取浏览器 Cookie、账号凭据或无关文件。
- 运行目录只记录任务主题、阶段状态和已确认文件名。
- 发布前请自行检查素材版权、人物授权和平台规则。

## 参与贡献

欢迎扩充主题池、材质规则和动作链。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，并确保状态机的确认闸门不被绕过。

## License

[MIT](LICENSE) © 2026 [squashtrr-prog](https://github.com/squashtrr-prog)
