---
title: Git 常用命令记录
date: 2020-05-25 08:31:48
categories:
  - 开发工具
tags:
  - Git
  - 版本控制
  - 命令行
---

## 引言

今天在掘金上看到关于 `git log` 的详细用法,才发现自己对 Git 的了解还很肤浅。这里记录一些实用的 Git 命令,方便日后查阅。

## Git Log 常用命令

### 基础查看命令
```bash
# 在一行显示提交信息
git log --oneline

# 根据日期查询
git log --since="2020-01-01" --until="2020-12-31"

# 根据提交人汇总
git shortlog
```

### 高级显示格式
```bash
# 图形化显示分支合并历史
git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative
```

### 设置命令别名
```bash
# 为复杂命令设置别名
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative"
```

### 搜索提交历史
```bash
# 搜索包含特定关键词的提交
git log --grep='测试' --oneline

# 显示指定长度的提交哈希值
git log --abbrev=4 --oneline
```

## 格式说明

常用的格式化参数含义:
- `%h`: 提交的简短哈希值
- `%d`: 引用名称(分支、标签等)
- `%s`: 提交信息
- `%cr`: 相对时间
- `%an`: 作者名字
- `%Cred`/`%Creset`: 颜色控制

## 实用技巧

1. 使用 `--oneline` 可以获得简洁的输出格式
2. `--graph` 选项可以可视化显示分支合并历史
3. `--pretty=format` 支持自定义输出格式
4. 合理使用别名可以简化常用命令

## 后续学习计划

计划深入学习以下开源项目:
- [Crawlab](https://github.com/crawlab-team/crawlab): 分布式爬虫管理平台
- [Apify](https://github.com/apify/apify-js): Node.js 爬虫框架

这些项目涉及 Go、Node.js 和 Docker 部署等技术,值得学习。

## 参考资料
- [Git 官方文档](https://git-scm.com/docs)
- [Git 命令速查](https://github.github.com/training-kit/downloads/github-git-cheat-sheet/)
