---
title: git 记录
date: 2020-05-25 08:31:48
---

git 学习 惊呆了，今天偶然掘金上看到有人写到关于 git log 的命令，才恍然觉得自己和文盲差不多，git 只会一些皮毛，一直没有深入去了解过，这次看到 git log 这么详细的参数命令，感觉很有用，赶紧记录一下 在一行显示提交信息 git log --oneline 根据日期查询 git log --since=".." --until=".." 根据提交人汇总 git short log 掘金那位提供的一个炫酷使用版本 git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative 对应的别名设置，感觉蛮实用 git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative" 搜索 git log --grep='测试' --oneline –abbrev= 显示 hash 值的前几位，具体 不过这个感觉得配合–oneline 使用，一般的 git log –abbrev= 不起效果git-log掘金文章 之后几篇应该都会去学习 crawlab 这个开源项目，有我感兴趣的 go，ks 还有 docker 部署的流程，满满的干货样子先贴上链接crawlab 还有一个 nodejs 版本的 craw，也会一并学习。

apify
