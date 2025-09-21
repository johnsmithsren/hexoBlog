---
layout: post
title: nginx配置之CDN回源
date: 2025-02-08 16:55:38
tags:
  - nginx
  - cdn
---

## CDN 回源配置要点

1. cdn 回源是生产环境配置不可缺少的一部分，但是这其中又有一些细节，需要我们注意。

2. 首先，cdn 回源就是当用户请求资源时，cdn 节点没有命中，就会回源到源站获取资源。此时一般两种做法：

   - 直接 nginx 导向文件夹，也就是打包好的静态文件
   - 此时需要注意的是压缩方法。切记，线上环境打包时候可以同时提供 gz，br 这些压缩文件，当请求的 url 头部带有 accept-encoding: gzip, br 时，就可以优先返回压缩文件了，这样可以减少带宽的消耗，加快页面加载速度，此时静态文件夹中是可以只有 gz 或者 br 后缀的文件的，nginx 或者 http-server 会自动去匹配，然后返回给用户。

3. 此时就需要关注压缩方式了，gz 还比较好处理，但是 br 就需要我们注意了：

   - br 是 brotli 压缩，需要 nginx 安装 brotli 模块
   - 需要配置 brotli 的压缩参数，否则会导致压缩失败
   - 据说 nginx 高版本会提供 br，但是我的 nginx 是低版本，并没有提供 br
   - 我这边是 nginx 那边做 proxy，去到后端服务，我用的是 http-server 作为后端服务来解决这个 br 的压缩文件返回

4. 此时又涉及到另外一点了，也就是说，当指定了 header 是 br 或者 gz 之后，其实你的静态文件中是可以只有 gz 或者 br 后缀的文件，nginx 或者 http-server 会自动去匹配，然后返回给用户。比如 xxxx/aaa.js，此时 nginx 会自动去匹配去静态文件夹中匹配 aaa.js.gz 或者 aaa.js.br，然后返回给用户。静态文件夹中不需要存在 aaa.js，这本身没有问题，但是当你使用 cdn 回源的话，cdn 那边可能不会主动设置这个头部，此时你回源的文件夹中需要存在 aaa.js 文件，否则会报错，相当于 cdn 一直回源失败。我使用的谷歌云是不会主动设置的，所以需要关注，解决方法也简单，那就是在 cdn 那边主动添加自定义头部，这样 cdn 回源会带上你的自定义头部，也就可以正常命中了。

5. 另外就是关于 index.html 和其他的 js，png 这些的差别：

   - index.html 作为项目的入口文件，或者说一切的入口文件，都是不应该缓存的
   - 需要去设置 cache-control 为 no-cache，否则会导致 index.html 被缓存
   - 因为一般打包出来的那些 js 都会带 hash，方便版本的迭代，而 index 是不变的
   - 设置 no-cache 的话，就能每次都获取最新的版本，防止版本迭代的时候，用户获取到旧的版本，导致页面加载失败

6. 除此以外的 js 文件，则可以设置一天的缓存，甚至更久，因为那些文件变动很小，无需频繁更新。

7. 另外就是如果说 nginx 做了 proxy，而后端服务会去自行设置 header 的情况下，如何做覆盖呢？可以通过以下方式处理，来强制覆盖掉后端的 header 设置：

```nginx
location / {
        proxy_set_header HOST $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass xxxxxx;
        proxy_hide_header Cache-Control;

        # 然后由Nginx重新定义Cache-Control
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires 0 always;
}
```

8. 也就是说 cdn 回源需要关注几个点：
   - 静态文件的压缩方式
   - 静态文件的缓存策略
   - 后端服务的 header 设置
   - 强制覆盖后端服务的 header 设置
   - 关注 index 文件是否会被缓存
