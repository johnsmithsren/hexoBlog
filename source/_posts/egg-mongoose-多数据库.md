---
title: egg-mongoose 多数据库
date: 2022-04-23 03:44:43
---

因为业务中涉及到多分支运维平台开发。

因为多分支链接的数据库也会有所不同，所以，平台链接的数据库也需要进行相应切换，才能配合数据的查看，这里，做了一些匹配工作，记录一下，方便有需要的人可以借鉴。

感觉网络上相关的记录不是很多。

第一步eggjs config 配置config.mongoose = { clients: { // clientId, access the client instance by app.mongooseDB.get('clientId') local: { url: 'mongodb://xxx:xxx@xxx:/xxx-s?authSource=admin', options: { useUnifiedTopology: true, useNewUrlParser: true, poolSize: , serverSelectionTimeoutMS: , connectTimeoutMS:  }, }, master: { url: 'mongodb://xxxx:xxx@xxxxx:/xxxx?authSource=admin&authMechanism=SCRAM-SHA-', options: { useUnifiedTopology: true, useNewUrlParser: true, serverSelectionTimeoutMS: , connectTimeoutMS:  } }, v: { url: 'mongodb://xxx:xxx@xxxx:/xxxx?authSource=admin&authMechanism=SCRAM-SHA-', options: { useUnifiedTopology: true, useNewUrlParser: true, serverSelectionTimeoutMS: , connectTimeoutMS:  } }, }, } 第二步生成model这里就和单例有差异，需要指定链接的数据库，切记，这里一定需要生成这个schema，schema中的字段可以为空，感觉为空只是对于具体增删改查操作有影响，但是对于单纯查询没啥差异，但是如果不使用model，直接操作的话，会无法使用mongoose加载的一些插件方法，比如lean之类的，而这些方法还是很方便的。

所以需要生成，可以看到，我这里是自动生成的，因为我的业务中，对于远程数据库的数据只有查询，没有其余操作，所以我这边只生成了空schema。

// Code AutoGenerate. DO NOT EDIT. import { Application } from "egg"; module.exports = (app: Application) => { const mongoose = app.mongoose; const Schema = mongoose.Schema; const GameUserSchema = new Schema({}); const conn = app.mongooseDB.get('v'); const GameUserModel = conn.model('nnnn', GameUserSchema); return GameUserModel;}; 数据查询使用业务这边使用了统一的getmodel方法来查询.这里是统一的处理方法，展示的是个简单的分页查询操作。

其实如果真正的业务使用的话，感觉还是可以同步到平台的本地表中，增加各种索引来的实际，我这个是初期版本，并且还只是内网开发中，所以没有存储本地哈。

只是个最基础的查询 import BaseService from "../base";export default class GameUser extends BaseService { public async index(pageSize, skipSize) { let data = await this.getModel('dddd').find({}, { dddd: , ddee: , }).find({}) .sort({ _id: - }) .skip(skipSize) .limit(pageSize).lean(); let total = await this.getModel('dddd').find({}).countDocuments(); return { total, data } }} 这个就是那个统一处理model 的地方，有点设计模式那个味道了。

。

。

我这里是和登陆者选择的nat服务器逻辑关联了，不过读者应该可以大概了解思路，进行改造。

getModel(dbName: string) { let config = NATENDPOINT.find(nat => nat.port == this.ctx.natServer); if (!config) { throw new Error( '内部异常' ) } let mongooseConfig = config.mongoose.find((_mongo) => _mongo.dbName == dbName); if (!mongooseConfig) { throw new Error( '内部异常' ) } return this.ctx.model[mongooseConfig.fileName] } 附加自动生成model 的代码非常简单，只是为了文章的完整性，班门弄斧了. egg这边的model获取方式依赖命名，好像自动大写了。

所以需要注意下 import { dddd } from "./app/utils/constants";const fs = require("fs");const path = require("path");for (let server of dddd) { if (!server.mongodb) { continue; } for (let mongooseConfig of server.mongoose) { let savePath = path.join( __dirname, `./app/model/${mongooseConfig.fileName}.ts` ); let inputData = `// Code AutoGenerate. DO NOT EDIT.\n \import { Application } from "egg"; \n \module.exports = (app: Application) => { \n \ const mongoose = app.mongoose; \n \ const Schema = mongoose.Schema; \n \ const ${mongooseConfig.schemaName}Schema = new Schema({}); \n \ const conn = app.mongooseDB.get('${server.mongodb}'); \n \ const ${mongooseConfig.schemaName}Model = conn.model('${mongooseConfig.dbName}', ${mongooseConfig.schemaName}Schema); return ${mongooseConfig.schemaName}Model;};`; fs.writeFile(savePath, inputData, (err) => { if (err) { throw err; } console.log("autoGenerate modal success"); }); }} 这个自动生成代码也还是偶然看到项目组的其他项目有这么搞，发现其实还真的蛮有用的，拼接组合，是程序员的必备技能，极为实用，能够自动生成的，一定要去做，否则，手动去增加超级累哈 参考资料
