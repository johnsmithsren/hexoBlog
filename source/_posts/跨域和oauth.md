---
layout: post
title: 跨域和OAuth详解
date: 2025-01-07 15:34:09
tags: 
  - OAUTH
  - 跨域
  - 网络安全
  - Web开发
---

## 跨域（CORS）详解

### 什么是跨域？
跨域（Cross-Origin Resource Sharing，CORS）是一种浏览器的安全机制，用于限制网页中的脚本只能访问同源（相同协议、域名和端口）的资源。当网页需要请求不同源的资源时，就需要进行跨域处理。

### CORS 关键响应头
跨域主要通过以下HTTP响应头来控制：

1. `Access-Control-Allow-Origin`：指定允许跨域访问的域名
   - 可以设置具体域名：`http://example.com`
   - 使用`*`允许所有域名（不推荐用于生产环境）

2. `Access-Control-Allow-Methods`：允许的HTTP方法
   - 常见值：GET, POST, PUT, DELETE, OPTIONS等

3. `Access-Control-Allow-Headers`：允许的请求头
   - 可以指定自定义请求头
   - 常见值：Content-Type, Authorization等

4. `Access-Control-Allow-Credentials`：是否允许携带认证信息（cookies）
   - 设置为`true`时必须指定具体的`Allow-Origin`，不能使用`*`

### 跨域解决方案

#### 1. 静态配置（Nginx方案）
适用于前后端分离架构，且访问域名固定的场景：
```nginx
location /api {
    add_header Access-Control-Allow-Origin http://your-frontend-domain.com;
    add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
    add_header Access-Control-Allow-Headers 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization';
}
```
#### 2. 动态配置（后端方案）
适用于多客户端、多域名访问的场景：
- 在后端中间件中动态设置CORS头
- 可以根据请求来源动态判断是否允许跨域
- 支持更灵活的访问控制策略

各个框架都有不同的解决方案，暂且抛砖引玉，用的是eggjs
```
import { HttpStatusCode } from "axios";

export default () => {
    return async function cors(ctx, next) {
        const { allowedOrigins } = ctx.app.config.cors;
        const origin = ctx.request.origin
        ctx.app.logger.info(`origin: ${origin}`, `allowedOrigins: ${JSON.stringify(allowedOrigins)}`);
        // 验证来源
        if (allowedOrigins.includes(origin) || allowedOrigins.includes('*')) {
            ctx.set('Access-Control-Allow-Origin', origin);
            ctx.set('Access-Control-Allow-Credentials', 'true');
            ctx.set('Access-Control-Allow-Methods', ctx.app.config.cors.allowMethods);
            ctx.set('Access-Control-Allow-Headers', ctx.app.config.cors.allowHeaders.join(','));
            ctx.set('Access-Control-Expose-Headers', ctx.app.config.cors.exposeHeaders.join(','));
            ctx.set('Access-Control-Max-Age', ctx.app.config.cors.maxAge);

            // 添加安全相关头   
            ctx.set('X-Content-Type-Options', 'nosniff');
            ctx.set('X-Frame-Options', 'DENY');
            ctx.set('X-XSS-Protection', '1; mode=block');
        } else {
            ctx.status = HttpStatusCode.Forbidden;
            ctx.body = {
                code: HttpStatusCode.Forbidden,
                msg: 'orgin not allowed',
                data: null,
            };
            return
        }

        // 处理预检请求
        if (ctx.method === 'OPTIONS') {
            ctx.status = 204;
            return;
        }

        await next();
    };
};

```

## OAuth 2.0 授权详解

### OAuth 2.0 基本概念
OAuth 2.0 是一个授权框架，允许第三方应用获取用户在其他服务（如GitHub、Google等）上的资源访问权限。

### 主要角色
1. Resource Owner（资源所有者）：即用户
2. Client（客户端）：第三方应用
3. Authorization Server（授权服务器）：如GitHub的授权服务器
4. Resource Server（资源服务器）：存储用户资源的服务器

### OAuth 2.0 授权流程

#### 1. 授权码模式（Authorization Code Flow）
最常用且最安全的流程：

1. 用户访问第三方应用
2. 应用重定向到授权服务器
3. 用户在授权服务器登录并授权
4. 授权服务器返回授权码（code）
5. 应用使用授权码换取访问令牌（access token）
6. 使用访问令牌获取用户资源

### 回调URL配置策略

#### 1. 后端回调方案（推荐）
优点：
- 更安全，授权码直接在后端处理
- 可以立即进行token交换
- 减少授权码泄露风险

实现流程：
1. 配置后端API地址作为回调URL
2. 后端接收授权码后直接与授权服务器交换token
3. 处理完成后重定向到前端，携带必要的信息

#### 2. 前端回调方案
优点：
- 实现较简单
- 流程直观

注意事项：
- 需要注意授权码的安全传输
- 建议使用state参数防止CSRF攻击
- 授权码仅使用一次后立即销毁

### 安全性考虑

1. 令牌管理
- Access Token应妥善保存
- 建议使用HTTPOnly Cookie存储敏感信息
- 实现令牌刷新机制

2. 跨域配置
- OAuth流程中需要特别注意跨域配置
- 授权服务器的回调请求需要在CORS白名单中
- 建议使用环境变量管理允许的域名列表

3. 最佳实践
- 使用HTTPS保护所有通信
- 实现合适的错误处理机制
- 记录关键操作日志
- 定期轮换密钥和令牌