---
title: NODEJS笔记
date: 2024-12-24 17:11:50
tags:
  - Node.js
categories:
  - 后端开发
cover: https://johnsmithsren.github.io/renjmBlog.github.io/images/nodejs.webp
---

## Node.js 事件循环机制

Node.js 存在事件循环，主要分为 task 和 microtask 两种任务队列：
- **microtask**：一般涉及业务逻辑的 await 后面的逻辑都会在 microtask 中执行，执行优先级很高
- **task**：在每次清理完 microtask 中的任务后执行

### Task 的六个阶段
1. timers：定时器回调阶段
2. I/O callbacks：处理网络、流、TCP的错误回调
3. idle, prepare：仅系统内部使用
4. poll：检索新的 I/O 事件
5. check：setImmediate() 回调
6. close callbacks：关闭回调

### 示例代码
```javascript
setTimeout(() => console.log('setTimeout'), 0);
setImmediate(() => console.log('setImmediate'));

(async () => {
  console.log('async start');
  await Promise.resolve();
  console.log('async end');
})();

console.log('sync end');
```

输出结果：
```
async start
sync end
async end
setTimeout  
setImmediate
```

执行顺序说明：
1. 同步代码优先执行：输出 `async start` 和 `sync end`
2. 清空微任务队列：输出 `async end`
3. timer 阶段执行：输出 `setTimeout`
4. check 阶段执行：输出 `setImmediate`

## Redis 缓存问题及解决方案

### 1. 缓存穿透
- **问题**：请求的值既不在数据库中也不在缓存中
- **解决**：缓存空值，避免重复访问数据库

### 2. 缓存雪崩
- **问题**：大量的 key 同时失效
- **解决**：设置随机过期时间

### 3. 缓存击穿
- **问题**：大量请求同时访问一个 key
- **解决**：设置阻塞锁

## 错误处理

### 全局错误捕获
```javascript
process.on('uncaughtException', (err) => console.error('Uncaught Exception:', err));
process.on('unhandledRejection', (reason) => console.error('Unhandled Rejection:', reason));
```

### 延迟函数
主要通过promise和定时器的方式来实现延迟函数，阻塞函数，感觉还是挺有用的，比如解决缓存击穿的情况，应对热点数据的高并发读取
感觉一般来说js服务中不出现while吧，主要是用promise+定时器，主要while作为同步，还是风险太大了
```javascript
function delay(time) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve();
        }, time);
    });
}
function waitForResponse(func){
    return new Promise((resolve, reject) => {
       let timeoutFlag = setTimeout(() => {
        resolve();
       }, 5000);
       let intervalFlag = setInterval(() => {
        func().then(() => {
            clearTimeout(timeoutFlag);
            clearInterval(intervalFlag);
            resolve();
        }).catch((error) => {
            reject(error);
        })
       }, 3000);
    })
}

```
### 异步错误处理
对于复杂逻辑，特别是涉及异步流程时，必须使用 try-catch 确保代码健壮性。

## Node.js 集群

```javascript
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  // Fork workers
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.log(`worker ${worker.process.pid} died`);
  });
} else {
  // Workers share HTTP server
  http.createServer((req, res) => {
    res.writeHead(200);
    res.end('hello world\n');
  }).listen(8000);
}
```

## 文件操作

```javascript
const fs = require('fs');

async function readFile() {
    const files = await fs.readdir(__dirname);
    for (const file of files) {
        if (file.isDirectory()) {
            await readFile(file);
        } else {
            const fullPath = path.join(__dirname, file.name);
            console.log(fullPath);
        }
    }
}
```

## Kafka 相关

### 消息积压问题
**原因**：消费者处理速度慢于生产者生产速度

**影响**：
1. 消息处理延迟增加
2. 服务器资源可能耗尽

**解决方案**：
- 增加分区数量
- 扩容消费者服务
- 提高并发处理能力

### 消息可靠性保证
1. **持久化机制**
   - 使用零拷贝技术
   - 实现副本机制
   - 采用 ack 确认机制

2. **分区策略**
   - 根据消息 key 选择合适分区
   - 确保消息均匀分散

### 消费者偏移量管理
- 每个消费者组维护独立偏移量
- 支持自动或手动提交偏移量

## Redis 部署模式

1. 单机模式
2. 集群模式
3. 哨兵模式