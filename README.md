# 📰 AI Daily Digest

每天 8:00 自动推送 AI、Startup、新应用的精华资讯到你的邮箱 📱

> **零成本运行** — 基于 GitHub Actions 免费计划，无需服务器。

---

## ✨ 功能亮点

- **精选信源** — 9 个高质量中英文信息源（TechCrunch、机器之心、Product Hunt 等）
- **智能筛选** — 每天从数百篇文章中精选 2-3 篇最值得读的
- **移动优化** — 手机优先的 HTML 邮件排版
- **自动运行** — 设定一次，每天 8:00 准时送达
- **可扩展** — 轻松添加更多 RSS 信源，还可接入 LLM 获得智能摘要

---

## 🗺️ 部署指南（约 10 分钟）

### 前置准备

1. 一个 **GitHub 账号** → 在 [github.com](https://github.com) 免费注册
2. 一个 **QQ 邮箱** → 有 QQ 号就有 QQ 邮箱

---

### Step 1：在 GitHub 创建仓库

1. 登录 GitHub，点击右上角 **+** → **New repository**
2. 仓库名填 `ai-daily-digest`，选择 **Private**（私有仓库）
3. 不要勾选任何初始化选项，直接点击 **Create repository**
4. 创建后会看到快速设置页面，**暂时保留这个页面**，后面会用到

---

### Step 2：开启 QQ 邮箱 SMTP 服务

这是为了让程序能用你的 QQ 邮箱发送邮件。

1. 登录 [mail.qq.com](https://mail.qq.com)
2. 点击顶部 **设置** → **账户**
3. 往下翻到 **POP3/IMAP/SMTP 服务** 这一栏
4. 点击 **POP3/SMTP 服务** 右边的 **开启** 按钮
   - 会弹出一个手机验证窗口
   - 按提示用绑定的手机号发送短信
5. 验证通过后，会生成一个 **16 位授权码**（示例：`abcdefghijklmnop`）
   - ⚠️ **复制并保存好这个授权码！** 它只会显示这一次
   - 这就是后面要用到的 `SMTP_PASS`，**不是你的 QQ 密码**

---

### Step 3：配置 GitHub Secrets

Secrets 是 GitHub 的加密变量，用来安全存储你的邮箱凭证。

1. 在刚才创建的仓库页面，点击 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**，添加以下 3 个 Secret：

| Secret 名称 | 值 |
|-------------|-----|
| `SMTP_USER` | 你的 QQ 邮箱地址，如 `123456789@qq.com` |
| `SMTP_PASS` | 上一步获取的 **16 位授权码** |
| `EMAIL_TO` | 接收简报的邮箱（可以是同一个 QQ 邮箱，也可以是其他邮箱） |

添加方法：填写 Name 和 Secret，点 **Add secret** 即可。

> 最终应该有 3 个 Secrets：`SMTP_USER`、`SMTP_PASS`、`EMAIL_TO`。

---

### Step 4：推送代码到 GitHub

现在需要把项目代码上传到你刚创建的仓库。

打开终端（Cmd / PowerShell / Git Bash），执行：

```bash
# 进入项目目录
cd D:/CC-desktop/ai-daily-digest

# 初始化 git
git init

# 添加所有文件
git add .
git commit -m "🎉 Initial commit: AI Daily Digest"

# 关联你的 GitHub 仓库（换成你自己的用户名）
git remote add origin https://github.com/你的用户名/ai-daily-digest.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

> 💡 如果 GitHub 要求登录，输入你的 GitHub 用户名和个人访问令牌（Personal Access Token）。如果还没有 Token：
> 1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
> 2. Generate new token，勾选 `repo` 权限
> 3. 复制生成的 token，在终端登录时当密码使用

---

### Step 5：验证！手动触发一次

1. 打开你的 GitHub 仓库页面
2. 点击顶部 **Actions** 标签
3. 在左侧列表找到 **Daily AI Digest**
4. 点击右侧 **Run workflow** → **Run workflow** 按钮
5. 等待一两分钟，绿色 ✓ 表示成功！
6. 检查你的邮箱，应该已经收到今天的简报邮件了 📧

如果看到红色 ✗，点击进去查看日志，常见问题：
- `SMTP authentication failed` → 授权码填错了，重新在 QQ 邮箱生成一个
- 其他错误 → 把日志发给我，我来帮你排查

---

### 🎉 大功告成！

从明天开始，每天 **北京时间 8:00** 你的邮箱会自动收到 AI Daily Digest。

---

## 📧 邮件示例

你会在每天早上 8 点左右收到这样一封邮件：

```
📰 AI Daily Digest | 06/27 (3 篇)

早上好！👋 以下是今日精选的 3 篇科技资讯。

🤖 AI
[TechCrunch AI] OpenAI 发布 GPT-5…
  文章摘要内容…

🚀 创业
[Product Hunt] 某个新应用上线…
  文章摘要内容…

📱 应用
[少数派] 某个效率工具推荐…
  文章摘要内容…
```

---

## 🔧 可选功能：LLM 智能摘要

如果想获得更高质量的 AI 摘要（目前是提取原文前几句话），可以接入 ChatGPT 或 Claude。

1. 获取 OpenAI API Key（需付费）或 Anthropic API Key
2. 在 GitHub Secrets 中添加：
   - `LLM_API_KEY` → 你的 API Key
   - `LLM_PROVIDER` → `openai` 或 `claude`
3. 下次运行时，摘要就会由 AI 重写

> 注意：LLM 调用会产生 API 费用（每天约几分钱），默认是不开启的。

---

## 📂 项目结构

```
ai-daily-digest/
├── .github/workflows/
│   └── daily_digest.yml      # GitHub Actions 定时任务
├── src/
│   ├── config.py             # 信源配置（加源改这里！）
│   ├── fetcher.py            # 抓取文章
│   ├── curator.py            # 精选 + 摘要
│   ├── email_builder.py      # 构建邮件
│   ├── sender.py             # 发送邮件
│   └── main.py               # 主入口
├── templates/
│   └── email.html            # 邮件 HTML 模板
├── requirements.txt
├── .env.example
└── README.md
```

---

## ➕ 如何添加更多信源

编辑 `src/config.py` 中的 `SOURCES` 列表，按格式添加即可：

```python
Source(
    name="你的信源名称",
    feed_url="https://example.com/feed.xml",
    category="ai",           # "ai" | "startups" | "apps"
    language="zh",           # "zh" | "en"
)
```

推送到 GitHub 后自动生效，无需其他操作。

---

## 📝 技术说明

- **语言**：Python 3.11
- **运行环境**：GitHub Actions（Ubuntu）
- **邮件发送**：QQ邮箱 SMTP（SSL 465 端口）
- **RSS 解析**：feedparser
- **依赖**：requirements.txt 中声明，Actions 自动安装

---

## ❓ 常见问题

**Q：收不到邮件怎么办？**
A：先检查垃圾箱。如果还是没有，在 GitHub Actions 页面手动触发一次，看日志中的错误信息。

**Q：可以换其他邮箱发送吗？**
A：可以。修改 GitHub Secrets 中的 `SMTP_HOST`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASS` 为你所用邮箱的 SMTP 配置即可。163 邮箱、Gmail 等均支持。

**Q：每天只能收到 2-3 篇？我想看更多。**
A：修改 `src/config.py` 中的 `curation.target_count` 数值即可。但不推荐太多，手机上读太多文章反而压力大。
