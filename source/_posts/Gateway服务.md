---
layout: post
title: Gateway服务
date: 2025-01-13 11:06:52
categories:
  - 后端开发
tags:
  - Gateway
---

在现代分布式系统架构中，Gateway（网关）服务扮演着至关重要的角色。本文将探讨 Gateway 服务的核心价值和主要应用场景。

## 服务路由与负载均衡

在大型项目中，Gateway 服务几乎是不可或缺的组件。虽然在简单的开发环境中可能并不必要，但在实际项目中，我们经常需要处理多服务的场景。例如：

- 支付系统需要对接多个支付服务
- 推送系统需要集成多个推送渠道

这种多服务架构能够提升系统的健壮性和负载均衡能力。Gateway 的核心职责之一就是解决服务路由问题：当客户端发起连接时，如何将请求精确地分发到相应的后端服务。

## 后端服务封装

Gateway 的另一个重要价值是实现后端服务的封装。通过 Gateway：

- 客户端只需要知道单一的 Gateway 服务地址
- 后端的支付服务、推送服务等实现细节都被很好地隐藏
- 在分布式架构中，可以通过增加后端服务实例并更新 Gateway 的服务列表来实现服务扩展和分流

## 通用功能集中化

Gateway 还可以集中处理多个关键的横切关注点，包括：

- 统一鉴权
- 日志记录
- 系统监控
- 限流控制
- 熔断机制

将这些基础功能集中在 Gateway 层，可以让后端微服务更专注于核心业务逻辑的实现，同时显著降低了各个微服务的复杂度。

### 使用 http-proxy-middleware 的实现

这是一个使用 http-proxy-middleware 的替代实现方案，可以更简单地处理代理转发。

```bash
# 安装额外依赖
npm install http-proxy-middleware
```

```typescript
// proxy/proxy.middleware.ts
import { Injectable, NestMiddleware } from "@nestjs/common";
import { Request, Response, NextFunction } from "express";
import { createProxyMiddleware } from "http-proxy-middleware";

@Injectable()
export class ProxyMiddleware implements NestMiddleware {
  private proxy = createProxyMiddleware({
    target: "http://localhost:3001",
    changeOrigin: true,
    pathRewrite: {
      "^/api": "",
    },
    router: {
      "/payment": "http://payment-service:3002",
      "/notification": "http://notification-service:3003",
    },
    onProxyReq: (proxyReq, req, res) => {
      // 添加自定义请求头
      proxyReq.setHeader("x-forwarded-by", "nest-gateway");
    },
    onProxyRes: (proxyRes, req, res) => {
      // 处理响应
      proxyRes.headers["x-powered-by"] = "nest-gateway";
    },
    onError: (err, req, res) => {
      res.writeHead(500, {
        "Content-Type": "text/plain",
      });
      res.end("Gateway Error");
    },
  });

  use(req: Request, res: Response, next: NextFunction) {
    this.proxy(req, res, next);
  }
}

// app.module.ts
import { Module, NestModule, MiddlewareConsumer } from "@nestjs/common";
import { ProxyMiddleware } from "./proxy/proxy.middleware";

@Module({
  imports: [],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(ProxyMiddleware).forRoutes("*");
  }
}

// 如果需要在代理之前添加认证
// auth.middleware.ts
import {
  Injectable,
  NestMiddleware,
  UnauthorizedException,
} from "@nestjs/common";
import { Request, Response, NextFunction } from "express";

@Injectable()
export class AuthMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    const token = req.headers["authorization"];

    if (!token) {
      throw new UnauthorizedException("No token provided");
    }

    try {
      // 验证 token
      // verify(token, 'secret');
      next();
    } catch (error) {
      throw new UnauthorizedException("Invalid token");
    }
  }
}

// app.module.ts 中配置中间件顺序
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(AuthMiddleware, ProxyMiddleware).forRoutes("*");
  }
}
```

这个实现相比之前的版本有以下优势：

1. 使用 http-proxy-middleware 提供的成熟功能
2. 更简单的路由配置
3. 内置的错误处理
4. 更灵活的请求/响应拦截
5. 支持 WebSocket 代理
6. 更好的性能表现

你可以根据需求配置更多 http-proxy-middleware 的选项：

```typescript
const proxyOptions = {
  // 负载均衡配置
  router: {
    "/api": ["http://service1:3001", "http://service2:3001"],
  },

  // 请求路径重写
  pathRewrite: {
    "^/api/old-path": "/api/new-path",
    "^/api/remove/path": "/path",
  },

  // 自定义请求头
  headers: {
    "x-powered-by": "nest-gateway",
  },

  // WebSocket 支持
  ws: true,

  // 请求超时设置
  proxyTimeout: 3000,

  // 自定义日志
  logLevel: "debug",

  // 忽略特定请求头
  ignorePath: false,

  // 本地化SSL证书
  secure: false,
};
```

这两种实现方式（直接使用 HttpService 和使用 http-proxy-middleware）各有优势：

1. HttpService 方式：

   - 更好的类型支持
   - 更细粒度的控制
   - 更容易进行单元测试
   - 适合简单的代理需求

2. http-proxy-middleware 方式：
   - 更成熟的代理功能
   - 更好的性能
   - 内置的 WebSocket 支持
   - 更适合复杂的代理场景
