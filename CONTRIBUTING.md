# Contributing

感谢你愿意改进 AI Squish Video Skill。

## 开始之前

1. Fork 仓库并从 `main` 创建分支。
2. 保持 `SKILL.md` 简短，只放触发条件、状态机、关键流程和硬约束。
3. 将阶段性细则放入 `references/`，将稳定、可重复的机械逻辑放入 `scripts/`。
4. 不要提交个人绝对路径、生成账号凭据、Cookie、API Key 或未经授权的素材。

## 修改主题池

编辑 `scripts/topics.json` 时，请确保：

- 每个主题名称唯一；
- `category`、`topic` 和 `emoji` 字段完整；
- 主题的外形与材质适合连续捏压、拉伸或折叠；
- JSON 使用 UTF-8 编码。

## 修改工作流

以下确认闸门不能被自动跳过：

- 首次输出目录确认；
- 首帧确认；
- H3 提示词确认；
- 最终标题选择。

重做当前阶段时必须递增版本号，不能覆盖已有文件。

## 验证

提交 Pull Request 前运行：

```bash
python -m unittest discover -s tests -v
```

并确认仓库中没有个人路径：

```bash
rg -n 'H:\\|C:\\|/Users/|/home/' .
```

请在 PR 描述里写明改动目的、用户可见变化和验证结果。
