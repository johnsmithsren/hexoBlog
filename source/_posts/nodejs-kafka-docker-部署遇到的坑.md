---
title: Node.js + Kafka Docker部署实践
date: 2022-04-23 05:31:48
categories:
  - 后端开发
tags:
  - Node.js
  - Kafka
  - Docker
  - 微服务
---

## 部署经验

在使用 Docker 部署 Kafka 时,主要使用了 bitnami/kafka 镜像。这个镜像在 DockerHub 上口碑较好,功能完善。

### 关键配置点

最重要的配置是 `KAFKA_CFG_ADVERTISED_LISTENERS` 参数:

```bash
KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://xxx.xxx.xxx.xxx:9092
```

- 需要配置内网 IP(有些场景也可以使用外网 IP)
- 这个配置对客户端连接至关重要

### Docker Compose 配置

1. 这个版本是 kraft 的，没有 zookeeper，使用起来感觉比较方便。

2. 另一个关键点是端口映射。多次经验表明，不能使用默认端口，例如 Redis 和 Kafka 的 9092。网络上存在各种扫描，对于常用端口都有可能遭受攻击。

3. 因此，在生产环境中，建议将服务映射到一个不常用的端口，并且该端口不对外开放。生产环境对于端口开放的管理非常严格，通常只开放几个端口供外部访问。

4. 剩下的端口仅用于内部消费。一般情况下，内网端口是开放的，数据库访问和内部消息请求都可以使用内网端口，这样既能避免攻击，又能节省流量，同时提高速度。

5. 对于安全性要求较高的应用，例如游戏，通常需要独立的网关服务。暴露给玩家的地址都是网关地址，而游戏服务器的地址则是转发过来的。

6. 这样可以随时更换网关地址，避免重要的 IP 地址被玩家直接知晓。

7. 总之，使用 kraft 版本的 Kafka 没有 zookeeper，确实让部署和管理变得更加方便。

```yaml
version: "3.5"
services:
  kafka:
    image: "bitnami/kafka:3.9.0"
    container_name: kafka
    ports:
      - "6092:9092"
    volumes:
      - "./kafka_data:/bitnami"
    networks:
      - kafka_network
    environment:
      - KAFKA_ADVERTISED_HOST_NAME=xxxx
      - KAFKA_ENABLE_KRAFT=yes
      - KAFKA_NUM_PARTITIONS=4
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
      - KAFKA_CFG_PROCESS_ROLES=broker,controller
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_KRAFT_CLUSTER_ID=LelM2dIFQkiUFvXCEcqRWA
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=true
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://xxxx:6092
volumes:
  kafka_data:
    driver: local

networks:
  kafka_network:
    driver: bridge
```

## 注意事项

说实话，在国内，现在不怎么推荐 docker 了，封锁太厉害，镜像都基本挂了，只能说等吧，等解封了，再看看

1. 仔细阅读 DockerHub 上的官方文档
2. 关注 KAFKA_CFG_ADVERTISED_LISTENERS 参数的配置说 ���
3. 确保网络配置正确
4. 合理设置 JVM 参数

## 参考资料

- [Bitnami Kafka Docker Hub](https://hub.docker.com/r/bitnami/kafka)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
