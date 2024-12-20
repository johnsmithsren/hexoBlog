---
title: bullMq在NestJs中的应用
date: 2024-12-20 21:33:29
tags: 
  - NestJS
  - BullMQ
  - Queue
  - Node.js
categories:
  - Backend
  - Message Queue
---

## 简介

BullMQ 是一个强大的基于 Redis 的队列管理库，它可以帮助我们在 NestJS 应用中处理后台任务、消息队列和作业调度。在实际项目开发中，消息队列是一个几乎不可或缺的组件，主要基于以下几个原因：

1. **延时队列需求**：在业务中经常需要处理延时执行的任务。

2. **事件触发处理**：比如玩家登录、升级等行为触发的后续操作，这些都需要可靠的消息处理机制。

3. **消息可靠性**：直接在消息监听器中处理业务逻辑风险较高，特别是对于一些关键操作（如支付）。消息队列提供了消息持久化能力，确保即使处理失败也可以重试。

4. **系统解耦**：通过消息队列，可以实现业务逻辑的解耦，提高系统的可维护性和扩展性。

5. **性能优化**：提供消息缓存机制，避免系统过载，实现更好的性能表现。

## 为什么选择 BullMQ？

BullMQ 具有以下优势：

- **高性能**：基于 Redis 实现，具有出色的性能表现
- **可靠性**：支持任务重试和错误处理机制
- **功能丰富**：提供作业进度追踪能力
- **并发处理**：支持多进程并发处理任务
- **灵活调度**：支持延迟任务和重复任务处理
- **事件系统**：完善的事件监听和处理机制
- **框架集成**：与 NestJS 框架完美集成

## 配置 BullMQ

在 NestJS 应用中配置 BullMQ 主要包含两个步骤：

1. **Redis 配置**：设置 Redis 连接参数，包括：
   - 服务器地址和端口
   - 访问密码
   - 数据库编号
   
2. **队列注册**：注册所需的消息队列。

> 注意：项目中通常会创建多个队列，这样做有两个主要好处：
> - 实现不同类型消息的隔离，使逻辑更清晰
> - 支持并发消费消息，提高处理效率
> 
> 但需要注意的是，使用多个队列可能会影响消息的处理顺序。

具体配置示例如下：

```typescript
// 导入必要的模块
import { Module } from '@nestjs/common';
// 使用 @nestjs/bullmq
import { BullModule } from "@nestjs/bullmq"
// 导入配置模块，用于读取环境变量
import { ConfigModule, ConfigService } from '@nestjs/config'

@Module({
  imports: [
     // 异步配置 BullMQ，使用 ConfigService 读取环境变量
     BullModule.forRootAsync({
            inject: [ConfigService],
            imports: [ConfigModule],
            useFactory: (configService: ConfigService) => ({
                connection: {
                    // 从环境变量中读取 Redis 配置
                    host: configService.get<string>('REDIS_HOST'),
                    port: configService.get<number>('REDIS_PORT'),
                    password: configService.get<string>('REDIS_PASSWORD'),
                    db: configService.get<number>('REDIS_DB'),
                },
            }),
        }),
        // 注册多个队列，每个队列处理不同类型的任务
        BullModule.registerQueue(
            {
                name: BULL_MQ_QUEUE,  // 通用队列
                defaultJobOptions: {
                    removeOnComplete: true,  // 任务完成后自动删除，避免占用 Redis 存储空间
                },
            },
            {
                name: BULL_MQ_PRE_OPEN_BOX,  // 开箱前置处理队列
                defaultJobOptions: {
                    removeOnComplete: true,
                },
            },
        ),
  ],
})
export class AppModule {}
```

## 创建生产者（Producer）

生产者的主要职责是接收消息并将其发送到相应的 BullMQ 队列中。以下是一个典型的生产者实现示例：

```typescript
import { Injectable } from '@nestjs/common';
import { InjectQueue } from '@nestjs/bull';
import { Queue } from 'bull';

@Injectable()
export class TaskProducer {
  constructor(
    // 注入预定义的队列，可以注入多个队列用于不同场景
    @InjectQueue(BULL_MQ_PRE_OPEN_BOX)
    private BullPreOpenBoxQueue: Queue,  // 处理开箱前置逻辑的队列
    @InjectQueue(BULL_MQ_SHIP)
    private BullShipQueue: Queue,  // 处理船只相关逻辑的队列
  ) {}

  async addTask(data: any) {
    // 添加任务到队列
    // 参数说明：
    // - 'processTask': 任务名称，消费者将通过这个名称识别要处理的任务类型
    // - data: 任务数据，可以包含任何需要传递给消费者的信息
    await this.BullPreOpenBoxQueue.add('processTask', data);
  }
}
```

## 创建消费者（Consumer）

消费者负责处理队列中的任务，通过继承 WorkerHost 类，我们可以获得更完善的任务管理机制。下面是一个实际的消费者示例：

```typescript
// 使用 @Processor 装饰器定义消费者，concurrency: 1 表示串行处理任务
@Processor(BULL_MQ_SHIP, { concurrency: 1 })
export class ShipProcessor extends WorkerHost {
    private readonly logger = new Logger(ShipProcessor.name);
    constructor( 
        // 注入所需的服务和依赖
        @InjectModel('History') private historyModel: Model<HistoryDocument>,  // MongoDB 模型
        private configService: ConfigService,  // 配置服务
        private utilityService: UtilityService,  // 工具服务
        @InjectRedis() private readonly redis: Redis,  // Redis 客户端
    ) {
        super()
    }

    // 处理队列中的任务
    async process(job: Job<any, any, string>): Promise<any> {
        try {
            // 开发环境跳过处理
            if (this.configService.get('IsDev') == 'true') {
                return
            }

            // 根据任务名称处理不同类型的任务
            if (job.name == 'shipClaimJob') {
                let { account } = job.data
                this.logger.log(`开始处理 ${job.name} ${transactionHash} 任务`)
                // 具体的业务处理逻辑
                xxxxxx
                this.logger.log(`结束处理 ${job.name} ${transactionHash} 任务`)
            }

            return {}
        } catch (error) {
            // 错误处理和日志记录
            this.logger.error('[job]任务处理失败', error)
            throw error  // 抛出错误以触发重试机制
        }
    }
}
```