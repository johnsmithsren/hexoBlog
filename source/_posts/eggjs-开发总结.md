---
title: Egg.js + UmiJS 开发总结
date: 2022-04-23 07:31:48
categories:
  - 后端开发
tags:
  - Egg.js
  - UmiJS
  - React
  - 项目实践
---

## 前言

从 Koa 到 Egg.js 的转变让我深刻体会到框架的重要性。框架不仅提供了规范化的开发方式,还解决了日志、定时任务等通用业务问题。本文记录使用 Egg.js + UmiJS 开发过程中的经验总结。

## 技术栈选择

### 后端框架
- Egg.js: 企业级 Node.js 框架
- NATS: 微服务通信
- HTTP: 前后端通信

### 前端框架
- UmiJS: 可插拔的企业级 React 应用框架
- Ant Design: UI 组件库

## 项目优化经验

### 1. 打包优化

UmiJS 配置示例:

```typescript
// .umirc.ts
export default defineConfig({
  nodeModulesTransform: { type: 'none' },
  hash: true,
  exportStatic: {},
  dynamicImport: {},
  antd: {},
  externals: {
    react: 'window.React',
    bizcharts: "BizCharts",
    '@antv/data-set': 'DataSet',
  },
  headScripts: [
    'https://unpkg.com/react@17/umd/react.production.min.js'
  ],
  scripts: [
    'https://g.alicdn.com/code/lib/bizcharts/4.1.11/BizCharts.js',
    "https://unpkg.com/@antv/data-set@1.2.8/build/data-set.js"
  ],
  chainWebpack(config) {
    if (process.env.NODE_ENV === 'production') {
      // 生产环境配置
      config.merge({
        optimization: {
          splitChunks: {
            chunks: 'async',
            minSize: 30000,
            minChunks: 2,
            automaticNameDelimiter: '.',
            cacheGroups: {
              vendor: {
                name: 'vendors',
                test: /[\\/]node_modules[\\/]/,
                priority: 10
              }
            }
          }
        }
      });
    }
  }
});
```

### 2. Nginx 配置

```nginx
server {
    listen 80;
    server_name _;
    
    # 静态资源配置
    location / {
        root /work/frontend;
        index index.html;
    }
    
    # API 代理配置
    location /api/v1 {
        proxy_pass http://backend:7001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Gzip 配置
    gzip on;
    gzip_min_length 1k;
    gzip_comp_level 6;
    gzip_types text/plain application/javascript application/x-javascript text/css application/json;
    gzip_static on;
    gzip_vary on;
    gzip_buffers 4 16k;
}
```

