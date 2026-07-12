# PocketWorld API 代理 (Vercel Serverless)

本目录包含部署到 Vercel 的 Python Serverless Functions，用于代理 Movebank 和 ACLED API。

## 为什么需要这个？

`地球online.html` 中的以下功能需要后端代理（涉及私密凭证，不能放在前端）：
- **Movebank 动物迁徙** - 需要 Basic Auth + 许可协议处理
- **ACLED 冲突事件** - 需要 API Key

网易云音乐已通过前端 WeAPI 加密实现，**不需要**后端代理。

## 部署步骤 (5分钟)

### 方法1: 通过 GitHub 自动部署 (推荐)

1. 将 `vercel-deploy` 目录的内容上传到你的 GitHub 仓库
2. 访问 [vercel.com](https://vercel.com)，用 GitHub 账号登录
3. 点击 "New Project" → 选择你的仓库 → "Import"
4. 保持默认配置，点击 "Deploy"
5. 等待部署完成，获得 URL，例如: `https://pocketworld-api.vercel.app`
6. 在 `地球online.html` 中将 `localhost:8767` 替换为你的 Vercel URL

### 方法2: 通过 Vercel CLI 手动部署

```bash
# 安装 Vercel CLI
npm i -g vercel

# 进入部署目录
cd vercel-deploy

# 登录并部署
vercel

# 首次部署后，设置为生产环境
vercel --prod
```

## 配置

部署前，请修改 `api/movebank.py` 和 `api/acled.py` 中的凭证为你的账号。
也可以在 Vercel 项目设置中添加环境变量，避免硬编码。

## 替换 HTML 中的地址

部署成功后，在 `地球online.html` 中搜索 `localhost:8767`，替换为你的 Vercel URL：
```
https://你的项目名.vercel.app
```

## 免费额度

Vercel 免费版每月包含:
- 100,000 次 Serverless Function 调用
- 100GB 带宽
对个人使用完全够用。
