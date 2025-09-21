---
title: Hexo博客自动化部署：GitHub Actions实践指南
date: 2024-12-13 16:26:14
tags: 
  - GitHub Actions
  - Hexo
  - CI/CD
categories: 技术分享
---

## 背景介绍

### 为什么选择 GitHub Actions

- 持续集成与部署的必要性
- 自动化工作流的价值
- Hexo 博客部署的痛点

### 所需工具

- Node.js
- npm
- GitHub Personal Access Token

## GitHub Actions 工作流配置

#### 触发条件
- 推送到主分支
- 手动触发部署

#### 权限配置
- 最小权限原则
- `contents: write` 的作用

## 部署步骤

### 1. 生成 Personal Access Token

在 GitHub 中生成 Personal Access Token 的步骤如下：
1. 进入 GitHub Settings
2. 点击 "Developer settings"
3. 选择 "Personal access tokens"
4. 点击 "Generate new token (classic)"
5. 选择必要的权限，至少包括 `repo` 和 `workflow`
6. 生成并复制 Token

### 2. 配置 GitHub Actions Token

Hexo 博客通常涉及两个 GitHub 仓库：
- 博客源码仓库（用于管理 Hexo 配置和文章）
- 博客展示仓库（GitHub Pages 仓库）

配置 Token 的详细步骤：
1. 进入博客源码仓库的 Settings
2. 点击 "Secrets and variables"
3. 选择 "Actions"
4. 点击 "New repository secret"
5. 名称设置为 `BLOG`（全大写），这一步是无所谓的，我用的BLOG，其实名称随意配置，只要yml中的匹配就行
6. 将之前生成的 Token 粘贴为 Value

![Secrets and variables](/images/hexoSecret.png)

### 工作流配置关键点

在早期实践中，我遇到了一些常见问题：
- 最初使用 `bash deploy.sh` 执行部署
- 在 shell 脚本中管理 npm 指令
- 频繁遇到部署错误，估计可能是没安装hexo-cli 和 hexo-deployer-git

最终的解决方案是：
- 直接在 GitHub Actions 工作流 (`deploy.yml`) 中管理部署流程，这样更加直观
- 确保安装必要的 Hexo 部署依赖
  ```bash
fatal: could not read Username for 'https://github.com': No such device or address
FATAL Something's wrong. Maybe you can find the solution here: https://hexo.io/docs/troubleshooting.html
Error: Spawn failed
    at ChildProcess.<anonymous> (/home/runner/work/hexoBlog/hexoBlog/node_modules/hexo-deployer-git/node_modules/hexo-util/lib/spawn.js:51:21)
    at ChildProcess.emit (node:events:518:28)
    at ChildProcess._handle.onexit (node:internal/child_process:293:12)
Error: Process completed with exit code 2.
```


### 工作流文件详解

```yaml
name: Deploy Hexo Blog

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.BLOG }}

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install Dependencies
        run: |
          npm ci
          npm install hexo-cli hexo-deployer-git

      - name: Configure Git
        env:
          GITHUB_TOKEN: ${{ secrets.BLOG }}
        run: |
          git config --global user.name 'xxxx'
          git config --global user.email 'xxxx'
          git config --global url."https://oauth2:${GITHUB_TOKEN}@github.com".insteadOf "https://github.com"

      - name: Build Hexo Site
        run: |
          npx hexo clean
          npx hexo generate

      - name: Deploy to GitHub Pages
        env:
          GITHUB_TOKEN: ${{ secrets.BLOG }}
        run: |
          npx hexo deploy || {
            echo "Deployment failed"
            exit 1
          }

      - name: Notify Deployment Status
        if: success()
        run: echo "🚀 Deployment successful!"

      - name: Error Logging
        if: failure()
        run: |
          echo "❌ Deployment failed"
          echo "Git Configuration:"
          git config --list
          echo "Repository Remote:"
          git remote -v

```

### 部署错误示例

典型的部署错误信息：
```bash
fatal: could not read Username for 'https://github.com': No such device or address
FATAL Something's wrong...
Error: Spawn failed
Error: Process completed with exit code 2.
```

这类错误通常源于：
- Token 权限不足
- 认证配置不正确
- 依赖管理问题


### 总结

- 现在，只需要写好文章，push即可，就可以自动部署啦，ci赞