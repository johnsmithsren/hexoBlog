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

- 需要配置内网IP(有些场景也可以使用外网IP)
- 这个配置对客户端连接至关重要

### Docker Compose 配置

```yaml
version: "3"

networks:
  kafka-net:
    driver: bridge

services:
  zookeeper-server:
    image: "bitnami/zookeeper:latest"
    networks:
      - kafka-net
    ports:
      - "2181:2181"
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes

  kafdrop:
    image: obsidiandynamics/kafdrop
    networks:
      - kafka-net
    restart: "no"
    ports:
      - "9000:9000"
    environment:
      KAFKA_BROKERCONNECT: "PLAINTEXT://kafka-server:9092"
      JVM_OPTS: "-Xms128M -Xmx256M -Xss180K -XX:-TieredCompilation -XX:+UseStringDeduplication -noverify"
    depends_on:
      - "kafka-server"

  kafka-server:
    image: "bitnami/kafka:latest"
    networks:
      - kafka-net
    ports:
      - "9092:9092"
    environment:
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper-server:2181
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=true
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://xxx.xxx.xxx.xxx:9092
    depends_on:
      - zookeeper-server
```

## 注意事项

1. 仔细阅读 DockerHub 上的官方文档
2. 关注 KAFKA_CFG_ADVERTISED_LISTENERS 参数的配置说明
3. 确保网络配置正确
4. 合理设置 JVM 参数

## 参考资料
- [Bitnami Kafka Docker Hub](https://hub.docker.com/r/bitnami/kafka)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
