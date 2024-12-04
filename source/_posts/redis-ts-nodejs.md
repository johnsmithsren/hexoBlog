---
title: redis,ts,nodejs
date: 2022-04-23 08:31:48
---

最近碰到一个技术问题，就是现在做的平台需要提供日志分析 最初的想法就是简单的mongo查询，然后恶补了一下聚合查询的方式，基本解决了最初的需求，然后发现一旦采用lookup会特别慢，感觉和索引有啥关系之类，得设置一下，才能够联表查询。

所以改写了原先的写法，非常蠢的先查询一个表，找到符合的例如uuid之类，然后通$in查询，速度提升了一些，但是这个方法其实还是蛮致命的，如果用户级数上升到十万百万级别，到时候单纯的数据存储查询uuid估计是不行的，所以后续还得改进，应该还是得走lookup那条路。

然后现在遇到了另一个问题，就算现在的测试用户数量只有可怜的万人级别，日活跃用户千人的级别，生成的日志数量依然达到了千万条的级别，一旦跨日期查询，还是需要等待几十秒，这个实在是不能忍，于是乎产生了另外一个想法，就是采用redis的缓存机制来减少和数据库的交互，想法也很简单，就是数据库交互时间总归要大于内存查询时间。

平台使用的技术栈就是react，koa。

然后语言是typescript，node版本用的吧，现在node都是async，await了嘛，有时候都有点感觉不到异步了。

。

。

习惯性await了，这个时候才发现redis那边暂时还不支持async，await。

也不是完全不支持，我的意思是stream方式。

因为我想要缓存日志信息，就是根据日期，玩家id，还有指定条目，去缓存玩家的使用数值，大概这样流程，然后就涉及到遍历key，谷歌一番，首先解决方法不多，大多是采用额外插件来做这个redis。

幸好看到一个人说可以采用node新特性解决，然后我就是试了下，是可以打出key，就是下面这个，不过不知道还有没有坑，后续会进行数据校验，看看是否真的可以 let uuidList = [];var stream = RedisStore.redis.scanStream({ // only returns keys following the pattern of `user:*` match: `*${currentDay}:${this.radioValue}`, // returns approximately  elements per call count: ,});for await (let x of stream) { console.log(x);} 希望这次采用promise.all + redis 缓存辅助的方式能够让日志分析突破一下，为后续平台处理更大规模日志做准备。

当然还得继续学习mongo看看聚合查询针对数组数据处理的方法，这样要是能够大部分运算都在mongo引擎内处理掉，也能够接受。

```javascript
const allTask = [];
await cursor.eachAsync((actionInfo) => {
  allTask.push(this.xxxx(xxx,
  xxx));
}
);
await Promise.all(allTask);
如果这些路都走不通，依然扛不住大规模推广产生的用户日志数据分析的话，也许就得采用elk啥的，把日志搞到kibana上面去，不过我还是觉得能够在平台查看自然是最方便的，接到kibana就属于下策了
```
