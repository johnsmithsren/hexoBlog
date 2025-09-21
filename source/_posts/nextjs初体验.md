---
layout: resources
title: nextjs初体验
date: 2025-09-21 21:44:08
tags:
  - Next.js
  - JavaScript
  - React
  - 数据库
  - 项目实践
categories:
  - 前端开发
---
## Next.js 初体验总结

### 项目背景
最近在学习 Next.js 框架进行项目开发，这是一个非常强大的 React 全栈框架，它提供了服务端渲染（SSR）、静态站点生成（SSG）等现代 Web 开发所需的关键特性。

### 遇到的问题：数据库连接实例丢失
在开发环境（dev）中，我遇到了一个有趣的问题。具体表现为：

- 使用 MySQL 作为后端数据库
- 采用单例模式创建数据库连接
- 当应用发生热重载（Hot Reload）时，偶尔会出现数据库实例丢失的现象

### 问题分析
起初，我认为这可能是单例模式实现的问题。但在对比测试其他框架（如 NestJS）后发现，这个问题似乎是 Next.js 特有的。这让我开始思考框架本身的特性：

1. Next.js 是一个全栈框架，同时处理前端和后端逻辑
2. 开发模式下的热重载机制可能会影响到后端状态的维护
3. 传统的 Node.js 单例模式在这种环境下可能不够稳定

### 解决方案
通过深入研究，发现可以使用 `globalThis` 来解决这个单例重复加载的问题。示例代码如下：

```typescript
// lib/db.ts
import mysql from 'mysql2/promise';

export class Database {
  private static instance: Database;

  private constructor() {
    // 初始化数据库连接
  }

  public static getInstance(): Database {
    if (!(globalThis as any).databaseInstance) {
      (globalThis as any).databaseInstance = new Database();
    }
    return (globalThis as any).databaseInstance;
  }
}
```

### 技术要点解释
1. `globalThis` 是一个标准的全局对象，在所有环境中都可用
2. 将数据库实例存储在 `globalThis` 上，可以确保在热重载过程中保持实例的持久性
3. 这种方案特别适合 Next.js 这样的同构应用框架

### 最佳实践建议
1. 在 Next.js 项目中处理全局状态时，考虑使用 `globalThis`
2. 对于数据库连接等需要持久化的资源，确保proper cleanup和重连机制
3. 开发环境中要特别注意热重载对后端状态的影响


## 一些体会

- Next.js 虽然提供了全栈开发能力，但其核心优势仍然在前端领域。其后端功能主要通过 API Routes 和 Route Handlers 实现，这种方式相对简单化：

  1. 请求处理通过单一的 handler 函数
  2. 或者通过路由匹配来做接口区分
  3. HTTP 方法区分通过条件判断实现（GET、POST等）

- 与专业的后端框架（如 Express.js 或 NestJS）相比，Next.js 在后端能力上存在一些局限：

  - 中间件支持相对基础
  - 缺乏完整的依赖注入系统
  - 服务层抽象不够完善
  - 缺少内置的请求管道和拦截器

这种设计可能更适合前端开发者构建轻量级的后端服务，但对于复杂的后端业务场景，可能需要考虑配合专门的后端框架使用。

## CDN 和扩展性解决方案

主要是通过cdn来优化图片资源的获取，对于一些静态页面，也可以通过cdn来缓存。减少对于后端服务器的压力