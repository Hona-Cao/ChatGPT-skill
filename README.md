# ChatGPT Skills

一个用于集中管理个人 **ChatGPT / Codex Skills** 的公开仓库。每个 Skill 保存在 `skills/<skill-name>/` 下，独立维护说明、参考资料、脚本、测试和版本。

## 已收录的 Skills

| Skill | 版本 | 用途 | 入口 |
| --- | --- | --- | --- |
| Clinical Manuscript Writing & Scientific Audit | **v1.1.0** | 临床医学、公共卫生与流行病学论文写作；统计报告核查；Major Revision；Response to Reviewers；投稿前质量检查 | [clinical-manuscript-audit](skills/clinical-manuscript-audit/SKILL.md) |

## 目录约定

```text
ChatGPT-skill/
├── .codex-plugin/plugin.json       # 当前合集的 ChatGPT 插件清单
├── skills/
│   └── clinical-manuscript-audit/
│       ├── SKILL.md                # Skill 入口与核心规则
│       ├── agents/openai.yaml      # 展示信息
│       ├── references/            # 科研规范与返修指南
│       ├── scripts/               # 统计与返修一致性检查
│       ├── tests/                 # 自动测试
│       └── assets/                # 空白项目模板（无患者信息）
└── docs/ADD_A_SKILL.md            # 后续新增 Skill 的方法
```

新增 Skill 请使用 `skills/<new-skill-name>/`，**不要覆盖其他 Skill**。详见 [新增 Skill 指南](docs/ADD_A_SKILL.md)。

## 使用方法

- **阅读 / 复制 Skill**：打开 [SKILL.md](skills/clinical-manuscript-audit/SKILL.md)。
- **ChatGPT 的 Skills 上传**：将单个 `skills/clinical-manuscript-audit/` 文件夹打包为 ZIP 后上传到支持自定义 Skills 的入口。
- **作为 ChatGPT Plugin 使用**：仓库根目录提供 `.codex-plugin/plugin.json`，其 `skills` 字段指向 `./skills/`。打包和上传前，应根据目标平台的插件要求检查清单、文件布局与版本。
- **使用当前已发布的私人插件**：[Clinical Manuscript Writing & Audit](https://chatgpt.com/plugins/Plugin_2b84b819b2c881919a3f4e0a6cb025e3)（仅对有相应权限的用户可见）。

在 GitHub 推送新版本 **不会自动同步/更新** ChatGPT 中已安装的插件；更新插件仍需通过 ChatGPT 插件发布流程完成。

## 运行测试

无需安装第三方 Python 包：

```bash
python -m unittest discover -s skills/clinical-manuscript-audit/tests -v
```

## 医学研究的使用边界

此 Skill 对论文内容和统计结果进行**一致性、可溯源性及报告规范检查**，不能仅凭统计汇总表重新验证原始数据分析，也不能替代真实医学/统计学专家审核。仓库仅保存代码、指南和**空白模板**；请勿提交患者数据、未公开的投稿材料、编辑来信或任何未经授权共享的信息。

## 许可证

本仓库尚未指定开源许可证。公开可见不等于授予再利用或再发布的许可；如计划允许他人复用，请由仓库所有者明确选择许可证。
