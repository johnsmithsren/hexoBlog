---
layout: post
title: elasticSearch使用笔记
date: 2025-05-22 09:55:09
tags:
  - ElasticSearch
  - Docker
  - NestJS
  - 数据库
  - 搜索引擎
categories:
  - 技术笔记
cover: https://johnsmithsren.github.io/renjmBlog.github.io/images/es.png
---

## ElasticSearch 简介

- 核心特性和优势

1.  数据统计快，查询快
2.  算法优秀，倒排索引，列存储机制，对于聚合分析有较大优势

## Docker 部署 ElasticSearch

### 单容器部署

ElasticSearch 可以通过 Docker 快速部署，这是开发环境或小规模应用的理想选择。

#### docker-compose 配置示例

对于更复杂的配置，推荐使用 docker-compose：

1. 我这里因为是内部日志分析需求，所以就是单节点部署，实测下来，每月大概 50g 左右的存储量，日志根据不同的日志 ID 分类存储，查询分析性能符合要求，基本都是秒级返回
2. 这里比较关键的就是配置密码登陆了，我这里没有使用 ssl。经验之谈就是要切记能使用密码就使用密码，不能偷懒，不使用默认端口部署，之前使用 kafka 的默认端口部署，就莫名出现异常的数据，互联网环境复杂，各种爬虫，扫描。必须要小心
3. 就是这个 jvm 内存了，我用的 1g，如果是大型集群，可以提高，根据设备的内存大小决定，不过实际使用下来，1g 也够用。

```yaml
version: "3.5"

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:9.0.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - ELASTIC_PASSWORD=xxxxxxxxxxx
      - xpack.security.enabled=true
      - xpack.security.http.ssl.enabled=false
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
    ports:
      - "10001:9200" # ES API 端口（避开默认）
      - "10002:9300"
    volumes:
      - /work/esdata:/usr/share/elasticsearch/data
    networks:
      - es-net
networks:
  es-net:
```

#### 常用环境变量设置

ES 容器可通过环境变量进行配置：

| 环境变量               | 作用             | 示例值            |
| ---------------------- | ---------------- | ----------------- |
| discovery.type         | 节点发现类型     | single-node       |
| ES_JAVA_OPTS           | JVM 参数设置     | -Xms512m -Xmx512m |
| xpack.security.enabled | 是否启用安全功能 | false/true        |

1. 对于 es 中数据创建，则是需要提前规划，我这边的需求是大概一百多个 ID，我这边的做法是将数据，按照日志 id，年月存储，这样的话，大概可以存储四个月的索引，超过的话，就会出现索引超限，无法继续创建索引的情况，对于的实际使用场景已经足够了

## EggJs 集成 ElasticSearch

1. 这边主要是提供一些 js 使用 es 的代码
2. 我是使用 eggJs 的，首先是对这个 es 进行封装，不过后期发现，gpt 一般都直接使用 es 的原生方法，倒是很少直接使用这个类的内部方法，直接调用 client 更加方便

```
import { Client } from "@elastic/elasticsearch";
import BaseService from "../base";

export default class EsService extends BaseService {
    client: Client;

    constructor(ctx) {
        super(ctx);
        // 从配置中获取ES连接信息
        const { elasticsearch } = this.config;
        this.client = new Client({
            node: elasticsearch?.node || 'http://localhost:9200',
            auth: {
                password: elasticsearch?.password || 'password',
                username: elasticsearch?.username || 'elastic',
            }
        });
    }

    /**
     * 添加或更新文档
     * @param index 索引名称
     * @param doc 文档内容
     * @param id 可选文档ID，不提供则自动生成
     */
    async index(index: string, doc: any, id?: string) {
        try {
            return await this.client.index({
                index,
                id,
                body: doc,
            });
        } catch (error) {
            this.ctx.logger.error(`[ES Index Error] index: ${index}, error: ${error.message}`);
            throw error;
        }
    }

    /**
     * 删除文档
     * @param index 索引名称
     * @param id 文档ID
     */
    async delete(index: string, id: string) {
        try {
            return await this.client.delete({
                index,
                id,
            });
        } catch (error) {
            this.ctx.logger.error(`[ES Delete Error] index: ${index}, id: ${id}, error: ${error.message}`);
            throw error;
        }
    }

    /**
     * 执行批量操作
     * @param operations 批量操作数组
     */
    async bulk(operations: any[]) {
        try {
            const result = await this.client.bulk({ body: operations });

            // 检查是否有操作失败
            if (result.errors) {
                const failedItems = result.items.filter(item => item.index?.error || item.create?.error || item.update?.error || item.delete?.error);
                this.ctx.logger.error(`[ES Bulk Error] ${failedItems.length} operations failed: ${JSON.stringify(failedItems)}`);
            }

            return result;
        } catch (error) {
            this.ctx.logger.error(`[ES Bulk Error] error: ${error.message}`, error.stack);
            this.ctx.logger.error(`[ES Bulk Error] operations sample: ${JSON.stringify(operations.slice(0, 2))}`);
            throw error;
        }
    }

    /**
     * 执行聚合查询
     * @param index 索引名称(支持模式匹配如 index-*)
     * @param aggs 聚合定义
     * @param query 查询条件(可选)
     * @returns 聚合结果
     */
    async aggregate(index: string, aggs: Record<string, any>, query?: any) {
        try {
            const body: any = {
                size: 0, // 默认不返回文档，只返回聚合结果
                aggs
            };

            // 如果提供了查询条件，则加入查询
            if (query) {
                body.query = query;
            }

            const result = await this.client.search({
                index,
                body
            });

            // 返回聚合结果
            return result.aggregations || {};
        } catch (error) {
            this.ctx.logger.error(`[ES Aggregation Error] index: ${index}, error: ${error.message}`);
            this.ctx.logger.error(`[ES Aggregation Error] aggs: ${JSON.stringify(aggs)}`);
            if (query) {
                this.ctx.logger.error(`[ES Aggregation Error] query: ${JSON.stringify(query)}`);
            }
            throw error;
        }
    }

    /**
     * 检查索引是否存在
     * @param index 索引名称
     * @returns 是否存在
     */
    async indexExists(index: string): Promise<boolean> {
        try {
            const result = await this.client.indices.exists({
                index
            });
            return !!result;
        } catch (error) {
            this.ctx.logger.error(`[ES Index Exists Error] index: ${index}, error: ${error.message}`);
            return false;
        }
    }

    /**
     * 创建索引
     * @param index 索引名称
     * @param options 索引选项(映射和设置)
     */
    async createIndex(index: string, options?: { mappings?: any, settings?: any }) {
        try {
            const body: any = {};

            if (options?.mappings) {
                body.mappings = options.mappings;
            }

            if (options?.settings) {
                body.settings = options.settings;
            }

            await this.client.indices.create({
                index,
                body
            });

            return true;
        } catch (error) {
            this.ctx.logger.error(`[ES Create Index Error] index: ${index}, error: ${error.message}`);
            throw error;
        }
    }
}

```

3. 然后就是 日志插入部分

```
async saveActionLogs() {
        if (this.actionLogs.length > 0) {
            this.app.customLogger.info('[SaveActionLogs] Inserting ' + this.actionLogs.length + ' logs into MongoDB');
            await this.ctx.model.UserAction.insertMany(this.actionLogs, { ordered: false });
            await this.ctx.model.UserActionToday.insertMany(this.actionLogs, { ordered: false });
            try {
                const groupedLogs = this.groupLogsByActionAndDate();
                for (const [indexKey, logs] of Object.entries(groupedLogs)) {
                    await this.ctx.service.elasticsearch.bulkInsert(indexKey, logs);
                }
            } catch (error) {
                this.app.customLogger.error("Error inserting logs into Elasticsearch", error);
            }
            this.app.customLogger.info('[SaveActionLogs success] Inserted ' + this.actionLogs.length + ' logs into MongoDB');
            this.actionLogs = [];
        }
    }

    private groupLogsByActionAndDate(): Record<string, any[]> {
        const grouped: Record<string, any[]> = {};
        this.actionLogs.forEach(log => {
            const actionId = log.ActionId || 'unknown';
            const date = dayjs().format('YYYY-MM');
            const indexName = `user_action_log_${actionId}_${date}`;
            if (!grouped[indexName]) {
                grouped[indexName] = [];
            }
            grouped[indexName].push(log);
        });

        return grouped;
    }
```

4. 一般来说日志索引模版的写入，数据字段的确认，在最开始定好肯定是最佳的，但是我这边就因为初始时候考虑不到位，导致最初的日志数据无法聚合使用，后续就得通过定时任务去改写数据，满足我的数据分析的需求。下面就是我常用的一个方式，通过定时任务，一般是 15 分钟一次，去改写 es 中的数据, es 查询连个重要的点，一个是 字段偏平化，这和他的存储方式有关，k-v 存储适合列存储，对于设置 keyword 也友好，我这边因为初始的时候关键的数据字段是个名为 paramList 的字段，导致需要去将字段扁平化。

```
  async updateUserResourceAction(ctx) {
    const lockKey = `timeSchedule:updateUserResourceAction:${ctx.natServer}`;
    const locked = await this.app.redis.setnx(lockKey, "1");
    if (!locked) {
      return;
    }
    await this.app.redis.expire(lockKey, 60 * 60);

    try {
      const updateStartTime = dayjs().valueOf();
      this.app.logger.info('开始更新资源获取和消耗数据');

      // 定义资源相关行为ID
      const resourceActionIds = [9910003, 9910004]; // 9910003: 资源获取, 9910004: 资源消耗

      // 获取当前月份的索引
      const currentMonth = dayjs().format('YYYY-MM');
      const months = [currentMonth];

      for (const month of months) {
        for (const actionId of resourceActionIds) {
          const indexName = `user_action_log_${actionId}_${month}`;

          try {
            // 检查索引是否存在
            const indexExists = await ctx.service.fs.es.client.indices.exists({
              index: indexName
            });

            if (!indexExists) {
              this.app.logger.info(`索引 ${indexName} 不存在，跳过处理`);
              continue;
            }

            // 更新索引映射
            await this.updateResourceActionMapping(ctx, indexName, actionId);

            // 使用scroll API处理大量数据
            const batchSize = 1000;
            let scrollId = null;
            let processedCount = 0;
            let updatedCount = 0;

            // 初始查询 - 查找尚未拆分字段的记录
            const searchQuery = {
              bool: {
                must_not: []
              }
            };

            // 根据不同的actionId添加不同的查询条件
            if (actionId === 9910003) {
              searchQuery.bool.must_not.push({ exists: { field: "itemName" } });
            } else if (actionId === 9910004) {
              searchQuery.bool.must_not.push({ exists: { field: "consumeType" } });
            }

            const searchResponse = await ctx.service.fs.es.client.search({
              index: indexName,
              scroll: '1m',
              size: batchSize,
              body: {
                query: searchQuery,
                _source: ["_id", "ParamList"]
              }
            });

            // 安全地获取scrollId和hits
            scrollId = searchResponse._scroll_id || searchResponse?._scroll_id;
            let hits = searchResponse.hits?.hits || [];

            if (!scrollId) {
              this.app.logger.error(`无法获取索引 ${indexName} 的 _scroll_id，跳过处理`);
              continue;
            }

            while (hits && hits.length > 0) {
              const maxRecordsPerRun = 500000;
              if (processedCount >= maxRecordsPerRun) {
                this.app.logger.info(`达到单次处理上限 ${maxRecordsPerRun}，下次继续处理`);
                break;
              }
              const bulkOperations = [];

              for (const hit of hits) {
                processedCount++;

                if (hit._source.ParamList && Array.isArray(hit._source.ParamList)) {
                  // 根据不同的ActionId处理不同的字段
                  if (actionId === 9910003) {
                    // 资源获取行为 - 只处理第一个物品，方便后续统计
                    if (hit._source.ParamList.length >= 2) {
                      const paramFirst = hit._source.ParamList[0];

                      const rewardType = hit._source.ParamList[1];

                      // 分割为单个物品和数量
                      const itemParts = paramFirst.split(';').filter(Boolean);
                      const itemNameParts = itemParts[0]?.split(',') || [];

                      // 只取第一个物品
                      const itemName = itemNameParts[0] || '';
                      const itemValue = Number(itemNameParts[1] || 0);

                      bulkOperations.push({
                        update: { _index: indexName, _id: hit._id }
                      });

                      bulkOperations.push({
                        doc: {
                          itemName,
                          itemValue,
                          rewardType
                        }
                      });
                    }
                  } else if (actionId === 9910004) {
                    // 资源消耗行为
                    if (hit._source.ParamList.length >= 4) {
                      const itemName = hit._source.ParamList[0] || '';
                      const consumeAmount = Number(hit._source.ParamList[1] || 0);
                      const remainAmount = Number(hit._source.ParamList[2] || 0);
                      const consumeType = hit._source.ParamList[3] || '';

                      bulkOperations.push({
                        update: { _index: indexName, _id: hit._id }
                      });

                      bulkOperations.push({
                        doc: {
                          itemName,
                          consumeAmount,
                          remainAmount,
                          consumeType
                        }
                      });
                    }
                  }
                }
              }

              // 执行批量更新
              if (bulkOperations.length > 0) {
                const bulkResponse = await ctx.service.fs.es.client.bulk({
                  body: bulkOperations
                });

                if (bulkResponse.errors || bulkResponse?.errors) {
                  this.app.logger.error(`批量更新出错: ${JSON.stringify(
                    (bulkResponse.items || bulkResponse?.items || [])
                      .filter(item => item.update.status >= 400)
                  )}`);
                } else {
                  updatedCount += bulkOperations.length / 2;
                }
              }

              // 获取下一批数据
              const scrollResponse = await ctx.service.fs.es.client.scroll({
                scroll_id: scrollId,
                scroll: '1m'
              });

              // 安全地获取scrollId和hits
              scrollId = scrollResponse._scroll_id || scrollResponse?._scroll_id;
              if (!scrollId) {
                this.app.logger.warn(`无法获取索引 ${indexName} 的下一批数据的 _scroll_id，停止处理`);
                break;
              }

              hits = scrollResponse.hits?.hits || [];
            }

            // 清理scroll
            if (scrollId) {
              await ctx.service.fs.es.client.clearScroll({
                body: { scroll_id: scrollId }
              });
            }

            this.app.logger.info(`索引 ${indexName} 处理完成: 共处理 ${processedCount} 条数据，更新 ${updatedCount} 条数据`);
          } catch (error) {
            this.app.logger.error(`处理索引 ${indexName} 出错:`, error);
            continue;
          }
        }
      }

      const updateEndTime = dayjs().valueOf();
      this.app.logger.info(
        "资源获取和消耗数据更新完成",
        `耗时 ${(updateEndTime - updateStartTime) / 1000} s`
      );
    } catch (error) {
      this.app.logger.error("资源获取和消耗数据更新失败:", error);
    } finally {
      // 释放锁
      await this.app.redis.del(lockKey);
    }
  }

  // 更新资源行为索引映射方法
  async updateResourceActionMapping(ctx, indexName, actionId) {
    try {
      let mappingBody = {};

      if (actionId === 9910003) {
        // 资源获取行为映射 - 增加GameUuid字段映射和gameUserUuid字段
        mappingBody = {
          properties: {
            itemName: { type: "keyword" },    // 物品名称
            itemValue: { type: "integer" },   // 物品数量
            rewardType: { type: "keyword" },  // 奖励类型
            gameUserUuid: { type: "keyword" } // 添加专用于聚合的字段
          }
        };
      } else if (actionId === 9910004) {
        // 资源消耗行为的映射 - 增加GameUuid字段映射和gameUserUuid字段
        mappingBody = {
          properties: {
            itemName: { type: "keyword" },     // 物品名称
            consumeAmount: { type: "integer" }, // 消耗数量
            remainAmount: { type: "integer" },  // 剩余数量
            consumeType: { type: "keyword" },   // 消耗类型
            gameUserUuid: { type: "keyword" }   // 添加专用于聚合的字段
          }
        };
      }

      await ctx.service.fs.es.client.indices.putMapping({
        index: indexName,
        body: mappingBody
      });

      this.app.logger.info(`索引 ${indexName} 映射更新成功`);

      // 添加脚本更新已有文档，将GameUuid复制到gameUserUuid字段
      await ctx.service.fs.es.client.updateByQuery({
        index: indexName,
        body: {
          script: {
            source: "ctx._source.gameUserUuid = ctx._source.GameUuid",
            lang: "painless"
          },
          query: {
            bool: {
              must: [
                { exists: { field: "GameUuid" } },
                { bool: { must_not: [{ exists: { field: "gameUserUuid" } }] } }
              ]
            }
          }
        },
        wait_for_completion: false  // 异步执行，避免长时间阻塞
      });

      this.app.logger.info(`索引 ${indexName} 已启动 gameUserUuid 字段更新过程`);
    } catch (error) {
      this.app.logger.error(`更新索引 ${indexName} 映射失败:`, error);
      // 即使映射更新失败，我们仍然继续处理，因为可能已经有映射存在
    }
  }
```

## ElasticSearch 查询方式

1. 我现在使用的 es 查询方式，主要就是 query 和 aggs

```
    async processCityLogWithES() {
        const dateKey = dayjs(this.queryTime).format('YYYY-MM-DD');
        const redisKeyPrefix = `${this.ctx.natServer}:ecology:cityLog:${dateKey}`;

        // 先尝试从缓存获取数据
        const cachedServers = [];
        for (const singleDayResult of this.ecologySingleDayResult) {
            const serverGameId = singleDayResult.serverGameId;
            const redisKey = `${redisKeyPrefix}:${serverGameId}`;
            const cachedData = await this.app.redis.get(redisKey);

            if (cachedData) {
                const data = JSON.parse(cachedData);
                singleDayResult.totalCityAttack = data.totalCityAttack || 0;
                singleDayResult.totalCityMove = data.totalCityMove || 0;
                cachedServers.push(serverGameId);
            }
        }

        // 如果所有服务器都有缓存数据，提前返回
        if (cachedServers.length === this.ecologySingleDayResult.length) {
            this.app.logger.info('使用缓存的城市日志数据');
            return;
        }

        // 对于没有缓存数据的服务器，查询 Elasticsearch
        const serverIdsToQuery = this.ecologySingleDayResult
            .filter(result => !cachedServers.includes(result.serverGameId))
            .map(result => result.serverGameId);

        if (serverIdsToQuery.length === 0) return;

        // 构建 ES 查询
        const query = {
            bool: {
                must: [
                    {
                        terms: {
                            ActionId: [9910216, 9910009] // 攻城和迁移城市
                        }
                    },
                    {
                        range: {
                            ActionTime: {
                                lte: dayjs(this.queryTime).endOf('d').valueOf()
                            }
                        }
                    },
                ]
            }
        };

        // 聚合定义
        const aggs = {
            by_server_action: {
                composite: {
                    size: 1000,
                    sources: [
                        { serverIdStr: { terms: { field: "ServerGameID" } } }, // Add this line
                        { ActionId: { terms: { field: "ActionId" } } }
                    ]
                },
                aggs: {
                    action_count: {
                        value_count: {
                            field: "ActionId"
                        }
                    }
                }
            }
        };

        try {
            // 执行 ES 聚合查询
            const startTime = Date.now();
            const result = await this.ctx.service.fs.es.aggregate("user_action_log_9910216_*,user_action_log_9910009_*", aggs, query);
            const queryTime = Date.now() - startTime;
            this.app.logger.info(`ES 城市日志查询耗时: ${queryTime}ms，服务器数: ${serverIdsToQuery.length}`);

            // 处理聚合结果
            if (result?.by_server_action?.buckets) {
                const cacheExpiry = 60 * 30;

                for (const bucket of result.by_server_action.buckets) {
                    const serverGameId = parseInt(bucket.key.serverIdStr);
                    const actionId = bucket.key.ActionId;
                    const count = bucket.action_count.value;

                    const singleDayResult = this.ecologySingleDayResult.find(
                        result => result.serverGameId === serverGameId
                    );

                    if (singleDayResult) {
                        const redisKey = `${redisKeyPrefix}:${serverGameId}`;
                        let cacheData = {
                            totalCityAttack: singleDayResult.totalCityAttack || 0,
                            totalCityMove: singleDayResult.totalCityMove || 0
                        };

                        if (actionId === 9910216) {
                            cacheData.totalCityAttack = Number(count.toFixed(2));
                            singleDayResult.totalCityAttack = cacheData.totalCityAttack;
                        }
                        if (actionId === 9910009) {
                            cacheData.totalCityMove = Number(count.toFixed(2));
                            singleDayResult.totalCityMove = cacheData.totalCityMove;
                        }

                        // 缓存这个服务器的结果
                        await this.app.redis.set(redisKey, JSON.stringify(cacheData), 'EX', cacheExpiry);
                    }
                }
            }
        } catch (error) {
            this.app.logger.error('从ES查询城市日志失败', error);
        }
    }

```

- 地理位置查询
- 高级查询技巧

## ElasticSearch 与 MongoDB 数据分析对比

1. mongo 虽然号称擅长大数据，同时提供丰富的查询语法，但是依然无法和 es 相比较，mongo 想要达到相同的查询性能，就必须使用数据清洗，尽可能的对数据进行预处理，另外，因为查询时候需要读取文档内容，导致单个文档的数量不能很大，而 es 可以只读取列，然后就是 mongo 作为一个正经的数据库，在数据库的存储，读写方面的优势和 es 是不同，es 就如果 docker 部署时候，开篇的 tag 所说，you know，for search. 在我看来，有点类似缓存的 redis，当然，两者决然是不同的，只是说两者的功能先对窄小。你是无法把 es 作为数据库的。
2. 切记不要使用 mongo 作为数据分析的核心，即便是简单的聚合累加，mongo 的速度都无法和 es 抗衡。但是 mongo 依然是合格的原始数据存储地方，我的做法是原始数据存储 mongo 中，一些字段提取，需要做数据分析的数据，存入 es 中，这样对于系统有好处，缺点是实时性差。
