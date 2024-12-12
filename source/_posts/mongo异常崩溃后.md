---
title: Docker MongoDB 异常崩溃处理指南
date: 2022-04-23 12:31:48
categories:
  - 数据库
tags:
  - MongoDB
  - Docker
  - 故障处理
  - 运维
---

## 问题背景

测试环境的平台突然无法访问,经排查发现是 MongoDB 数据库连接异常。通过日志发现是磁盘空间不足导致的崩溃。

## 问题排查

### 1. 检查磁盘空间
```bash
df -h
```
输出显示存放 MongoDB 数据的根目录空间已满:
```
Filesystem    Size  Used  Avail  Use%  Mounted on
/dev/sda1     20G   19G   1G    95%   /
/dev/sdb1     100G  30G   70G   30%   /data
```

### 2. 分析原因
- MongoDB 数据默认存储在系统盘
- 之前的数据备份占用大量空间
- 日志文件未及时清理
- 缺乏磁盘监控预警

## 解决步骤

### 1. 迁移数据目录
```bash
# 移动数据到数据盘
mv /db/* /w/db
```

### 2. 修复数据库
由于非正常关闭,需要删除锁文件并修复:
```bash
# 删除锁文件
rm -rf mongo.lock

# Docker 环境下修复数据库
sudo docker run -d \
  -v /x/db:/data/db \
  -p x:27017 \
  mongo:latest \
  --wiredTigerCacheSizeGB 1.5 \
  --auth \
  --repair
```

### 3. 调整配置
- 限制缓存大小
- 配置日志轮转
- 设置监控告警

## 经验总结

1. **预防措施**
   - 合理规划存储空间
   - 配置磁盘监控
   - 定期清理日志
   - 使用数据盘存储数据

2. **应急预案**
   - 准备数据备份
   - 制定恢复流程
   - 记录问题处理步骤

3. **改进建议**
   - 完善监控系统
   - 优化存储策略
   - 规范运维流程

## 参考资料
- [MongoDB 数据修复文档](https://docs.mongodb.com/manual/tutorial/recover-data-following-unexpected-shutdown/)
- [Docker MongoDB 文档](https://hub.docker.com/_/mongo)
