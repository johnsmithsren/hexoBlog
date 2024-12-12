---
title: egg-mongoose 多数据库配置实践
date: 2022-04-23 03:44:43
categories:
  - 后端开发
tags:
  - Egg.js
  - MongoDB
  - Mongoose
  - Node.js
---

## 背景

在开发运维平台时,需要支持多分支环境,每个分支连接不同的数据库。为了实现数据库的动态切换,对 egg-mongoose 进行了多数据库配置。由于网上相关资料较少,特此记录实现方案。

## 实现步骤

### 1. 配置多数据库连接

在 `config.default.js` 中配置多个数据库连接:

```javascript
config.mongoose = {
  clients: {
    // clientId, 通过 app.mongooseDB.get('clientId') 访问实例
    local: {
      url: 'mongodb://xxx:xxx@xxx:/xxx-s?authSource=admin',
      options: {
       
      },
    },
    master: {
      url: 'mongodb://xxxx:xxx@xxxxx:/xxxx?authSource=admin&authMechanism=SCRAM-SHA-1',
      options: {
      
      }
    },
    // ... 其他数据库配置
  },
}
```

### 2. Model 定义

需要为每个数据库连接创建对应的 Model:

```javascript
// 自动生成的 Model 代码
import { Application } from "egg";

module.exports = (app: Application) => {
  const mongoose = app.mongoose;
  const Schema = mongoose.Schema;
  const GameUserSchema = new Schema({});
  
  // 指定使用的数据库连接
  const conn = app.mongooseDB.get('v');
  const GameUserModel = conn.model('nnnn', GameUserSchema);
  
  return GameUserModel;
};
```

### 3. 统一的 Model 获取方法

在 Service 层实现统一的 Model 获取方法:

```javascript
getModel(dbName: string) {
  // 根据当前用户选择的 NAT 服务器获取对应配置
  let config = NATENDPOINT.find(nat => nat.port == this.ctx.natServer);
  if (!config) {
    throw new Error('内部异常');
  }
  
  // 获取数据库配置
  let mongooseConfig = config.mongoose.find((_mongo) => _mongo.dbName == dbName);
  if (!mongooseConfig) {
    throw new Error('内部异常');
  }
  
  return this.ctx.model[mongooseConfig.fileName];
}
```

## 自动生成 Model 文件

为了提高开发效率,实现了自动生成 Model 文件的脚本:

```javascript
import { dddd } from "./app/utils/constants";
const fs = require("fs");
const path = require("path");

// 遍历配置生成 Model 文件
for (let server of dddd) {
  if (!server.mongodb) continue;
  
  for (let mongooseConfig of server.mongoose) {
    let savePath = path.join(__dirname, `./app/model/${mongooseConfig.fileName}.ts`);
    
    // Model 文件模板
    let inputData = `// Code AutoGenerate. DO NOT EDIT.\n
      import { Application } from "egg";\n
      module.exports = (app: Application) => {
        const mongoose = app.mongoose;
        const Schema = mongoose.Schema;
        const ${mongooseConfig.schemaName}Schema = new Schema({});
        const conn = app.mongooseDB.get('${server.mongodb}');
        const ${mongooseConfig.schemaName}Model = conn.model('${mongooseConfig.dbName}', ${mongooseConfig.schemaName}Schema);
        return ${mongooseConfig.schemaName}Model;
      };`;
      
    fs.writeFile(savePath, inputData, (err) => {
      if (err) throw err;
      console.log("autoGenerate modal success");
    });
  }
}
```

## 注意事项

1. Schema 定义虽然可以为空,但建议根据实际需求定义字段
2. Model 命名需要注意,egg 会自动处理大小写
3. 建议将常用数据同步到本地数据库,添加索引提升查询性能

## 总结

通过合理配置 egg-mongoose 多数据库连接,可以实现灵活的数据库切换。配合自动生成 Model 文件的脚本,可以显著提升开发效率。
