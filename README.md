# Zotero Research Radar

本地优先的 Zotero 文献雷达：根据 Zotero 文献库检索、重排并输出最近论文。它将推荐流程与投递方式解耦，默认生成本地 JSON 或 Markdown 报告，不发送邮件。

本项目是 [TideDra/zotero-arxiv-daily](https://github.com/TideDra/zotero-arxiv-daily) 的衍生项目，保留其 AGPL-3.0 许可和原作者归属。

公开源码仓库：`https://github.com/sky09101230/zotero-research-radar`

## v0.1 能做什么

- 复用 Zotero 语料、arXiv/bioRxiv/medRxiv 检索与 embedding 重排。
- 提供稳定的 `radar` CLI，供脚本或 Agent 调用。
- 输出 JSON 或 Markdown；邮件不再是主流程的一部分。
- 使用本地 SQLite 记录已推荐论文，默认不重复推荐。
- 内置 Codex skill 与 Windows Task Scheduler 模板。

## 本地运行

安装 [uv](https://docs.astral.sh/uv/)，然后配置环境变量：

```powershell
$env:ZOTERO_ID = "你的 Zotero 用户 ID"
$env:ZOTERO_KEY = "只读 Zotero API key"
$env:OPENAI_API_KEY = "可选，仅 --summarize 时需要"
$env:OPENAI_API_BASE = "可选，OpenAI 兼容端点"
```

在 `config/custom.yaml` 中设置检索来源与学科分类。首次执行前检查配置：

```powershell
uv run radar doctor
```

生成给 Agent 使用的 JSON：

```powershell
uv run radar recommend --format json --output reports/radar.json
```

生成人工阅读的报告：

```powershell
uv run radar recommend --format markdown --output reports/daily.md
```

启用 LLM TL;DR 与作者机构提取：

```powershell
uv run radar recommend --summarize --format markdown --output reports/daily.md
```

传递 Hydra 覆盖项，例如限定检索源：

```powershell
uv run radar recommend --set executor.source=[arxiv] --top-k 20
```

记录阅读反馈：

```powershell
uv run radar feedback accept "arxiv:https://arxiv.org/abs/2608.01234"
```

当前版本保存反馈以便后续实现反馈重排；它尚不改变分数。

## Codex Skill

仓库内的 [skills/zotero-research-radar/SKILL.md](skills/zotero-research-radar/SKILL.md) 将自然语言请求转换为 CLI 调用，并只读取 JSON 结果。将该目录安装到 Codex skills 目录后，可用于“根据我的 Zotero 推荐今天的论文”“生成本周文献简报”等请求。

## 定时运行

Windows 每天 08:00 生成 Markdown：

```powershell
.\workflows\windows\install-task.ps1 -WorkingDirectory $PWD
```

该脚本创建名为 `ZoteroResearchRadar` 的当前用户计划任务。它不会配置邮件，也不会上传 Zotero 数据。

## 开发

```powershell
uv run pytest
uv run radar --help
```

原有邮件入口仍可用：

```powershell
uv run src/zotero_arxiv_daily/main.py
```

## 许可与归属

本项目依据 GNU Affero General Public License v3.0 发布。详见 [LICENSE](LICENSE)。

```text
This project is based on Zotero-arXiv-Daily by TideDra
and contains substantial modifications.

Original project: TideDra/zotero-arxiv-daily
```
