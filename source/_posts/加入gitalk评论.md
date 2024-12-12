---
title: 为 Hexo 博客添加 Gitalk 评论系统
date: 2020-05-25 09:31:48
categories:
  - 博客搭建
tags:
  - Hexo
  - Gitalk
  - GitHub
  - 评论系统
---

## 配置步骤

### 1. 注册 GitHub OAuth Application

1. 进入 GitHub Settings -> Developer settings -> OAuth Apps
2. 点击 "New OAuth App"
3. 填写相关信息:
   - Application name: 随意填写
   - Homepage URL: 博客地址
   - Authorization callback URL: 博客地址

### 2. 安装 Gitalk

```bash
npm install --save gitalk
```

### 3. 修改主题配置

在主题的 _config.yml 中添加:

```yaml
gitalk:
  enable: true
  clientID: 'GitHub Application Client ID'
  clientSecret: 'GitHub Application Client Secret'
  repo: 'GitHub repo name'
  owner: 'GitHub repo owner'
  admin: ['GitHub repo owner and collaborators']
  distractionFreeMode: false
```

### 4. 添加评论组件

在 themes/your-theme/layout/_partial/article.ejs 中添加:

```html
<% if (theme.gitalk.enable && page.comments) { %>
  <div id="gitalk-container"></div>
  <script>
    const gitalk = new Gitalk({
      clientID: '<%= theme.gitalk.clientID %>',
      clientSecret: '<%= theme.gitalk.clientSecret %>',
      repo: '<%= theme.gitalk.repo %>',
      owner: '<%= theme.gitalk.owner %>',
      admin: ['<%= theme.gitalk.admin %>'],
      id: location.pathname,
      distractionFreeMode: false
    })
    gitalk.render('gitalk-container')
  </script>
<% } %>
```

## 注意事项

1. **安全性**
   - 不要泄露 Client Secret
   - 谨慎设置 admin 权限

2. **评论初始化**
   - 首次需要管理员登录初始化
   - 每篇文章都需要单独初始化

3. **常见问题**
   - Error: Not Found
   - Error: Validation Failed
   - 评论无法加载

## 参考资料
- [Gitalk 文档](https://github.com/gitalk/gitalk/blob/master/readme-cn.md)
- [GitHub OAuth 文档](https://docs.github.com/en/developers/apps/building-oauth-apps)
