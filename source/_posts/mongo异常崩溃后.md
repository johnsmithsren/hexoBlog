---
title: docker mongo 异常崩溃后
date: 2022-04-23 12:31:48
---

前言不得不说被吓到了，测试告诉我平台挂了，我看了下 docker 日志，好像没啥问题，然后看到数据库好像链接不了了，顿感疑惑，docker mongo 服务一直很正常，没出过啥问题，换言之，我也没处理过异常。

查看 mongo 日志，看到一堆报错，关键报错就是 disk out 的感觉，估计是存储空间不够了 df -h 果然，存放 mongo 数据的盘满了 Filesystem Size Used Avail Use% Mounted onudev .G  .G % /atmpfs M M M % /b/e G G  % /tmpfs .G  .G % /xtmpfs .M  .M % /ytmpfs .G  .G % /z/f G .G G % /wtmpfs M  M % /z （都是化名） 也就是 这里的根目录 我错了，因为一开始挂载的时候，就是用的默认路径，一般来说，这个盘应该类似 windows 的 C 盘，不放项目的，谁让我菜鸡呢。

。

应该正常放在 w 那边 解决首先 移动所有的数据内容 到 w 目录下 mv /db/* /w/db 然后我就开心的重启，一堆报错，继续挂，这我就开始冷汗了。

照例谷歌，发现 如果是正常关闭的，这个时候重启是没问题，感觉像是废话，没事我正常关闭数据库做什么？

当然，缺乏运维知识的我哪有资格吐槽 然后就是非正常关闭 . rm -rf mongo.lock // 删除mongod.lock文件. ./mongod --dbpath=/opt/rh/mongodbData --repair //对数据库进行修复 大概说法就是 这个文件会记录异常状态，不删除会导致重启失效。

第二步不适合我，因为我是 docker 启动的，所以 sudo docker run -d -v /x/db:/data/db -p x: mongo:latest --wiredTigerCacheSizeGB . --auth --repair 因为我启动 mongo 一般是这样的，所以就直接在后面加了–repair 即可，这样就会正常开始修复数据，等待这个过程结束，然后再次启动，就不会报错。

然后我还对 cachesize 做了限制，结果触发了另外一个问题，内存不够。

因为曾经我在这个测试环境的数据库里面备份了一次线上的日志数据，大概  千万条，导致这个时候恢复数据的时候内存不够了，然后我就修改了原先的限制，扩大到了 .，就好了。

总结如果是线上出现这个问题，首先避免出现，测试环境出现后我第一时间去看了线上的剩余磁盘空间，然后发现其实还有非常多，暂时没问题。

然后如果出现异常关闭，我感觉应该还是以恢复备份为最佳，直接修复数据感觉消耗的时间也是非常慢的。
