---
title: eggjs+umi 总结
date: 2022-04-23 07:31:48
---

开头先聊一些废话吧，从年月入职，接手koa项目的前后台，后台koa+rpc 前台是react使用下来有一些累，比如日志的统一，定时类的添加这些，才感觉到框架的一些好处，就是一些通用的业务处理方法如果能够规范化，对于开发效率的提高是显著的，比如日志，和定时，都是一个业务开发中必不可少的部分，还有应用的稳定性处理，任何业务都无法避免。

所以在项目伊始，就开始考虑使用框架，按照之前长期使用antd的惯性，这次就采用了eggjs来作为后台，然后 umijs来作为前台，通信方式变成了 http+nats，nats主要负责和后端各个应用间通讯，http负责前后台通讯。

不过有点调查不严的地方在于，当umi用完的时候才看到大家说umi在年已经被阿里放弃维护了。

。

。

瞬间黑线，感觉又给自己埋下了一个坑。

不过umi这边也只是对react做了一些外部封装，感觉弃用也还好。

后台这边其实eggjs还是学习了一些的，首先，官方文档还不错，但是没到好的地步，给我一种官方文档有点老的感觉，egg的配置和官网给出的代码配置已经不大一样了。

不过好在有万能的github 可以借鉴，还是很好的。

岔开一下，百度真的是不争气，不是一般的废，谷歌一个国外的搜索引擎，搜中文居然比百度还方便，基本上想搜啥，绝大部分时候不需要翻页的。

你让我怎么能忍，真就地主家的儿子，靠着国内人口流量，百度能成为巨头，但是就技术能力，真就没用，中文搜索都比不过谷歌，何谈出去竞争呢。

日常开发还是推荐谷歌+github，很省事，github的搜索更加有效，但是也有些难度，毕竟浏览器的搜索属于文字类，还能加入一些理解，github 的搜索更加注重 关键字和对于代码的理解了，当然好处是相当直接，大家的代码是不会欺骗你的，基本上传上去的代码都是可以解决问题和提供思路的，也没人传压根不能运行的上去，关键就在于能不能理解运用了。

回到eggjs开发，好的思路就是直接抄插件了，egg本身就是提倡插件化的，所以当我想要把项目中通用的代码抽出来，比如nats的通信解码部分，鉴权，这块抽出来，就是直接打开node_modules找到egg_xxx 这些插件看看，基本就知道插件应该怎样布局了，毕竟egg也是强调约定的框架，换言之，不照着他的路，你走不通。

所以顺利解决了插件，然后就豁然开朗，感觉插件真的非常好，能够省略很多的代码。

当然如果只有一个项目，也没啥感觉了，不过我这边后续可能有多个项目，这个时候，抽出通用部分就相当的重要了，首先代码复用，其次维护的便利性，修bug的便利性，开发的便利性都提升了，只要改一个地方的幸福感，想必大家都是深有体会的。

umi 的话，感觉没啥特别的，有个关键点，就是打包优化.umirc import { defineConfig } from 'umi';const CompressionPlugin = require('compression-webpack-plugin');export default defineConfig({ nodeModulesTransform: { type: 'none', }, hash: true, exportStatic: {}, dynamicImport: {}, antd: { }, externals: { react: 'window.React', bizcharts: "BizCharts", '@antv/data-set': 'DataSet', }, headScripts: ['https://unpkg.com/react@../umd/react.production.min.js'], scripts: ['https://g.alicdn.com/code/lib/bizcharts/../BizCharts.js', 'https://g.alicdn.com/code/lib/bizcharts/../BizCharts.min.js', "https://unpkg.com/@antv/data-set@../build/data-set.js"], chainWebpack(config) { if (process.env.NODE_ENV === 'production') { config.merge({ optimization: { minimize: true, splitChunks: { chunks: 'async', minSize: , minChunks: , automaticNameDelimiter: '.', cacheGroups: { vendor: { name: 'vendors', test: /^.*node_modules[\\/](?!ag-grid-|lodash|wangeditor|react-virtualized|rc-select|rc-drawer|rc-time-picker|rc-tree|rc-table|rc-calendar|antd).*$/, chunks: "all", priority: , }, virtualized: { name: "virtualized", test: /[\\/]node_modules[\\/]react-virtualized/, chunks: "all", priority:  }, rcselect: { name: "rc-select", test: /[\\/]node_modules[\\/]rc-select/, chunks: "all", priority:  }, rcdrawer: { name: "rcdrawer", test: /[\\/]node_modules[\\/]rc-drawer/, chunks: "all", priority:  }, rctimepicker: { name: "rctimepicker", test: /[\\/]node_modules[\\/]rc-time-picker/, chunks: "all", priority:  }, ag: { name: "ag", test: /[\\/]node_modules[\\/]ag-grid-/, chunks: "all", priority:  }, antd: { name: "antd", test: /[\\/]node_modules[\\/]antd[\\/]/, chunks: "all", priority:  }, rctree: { name: "rctree", test: /[\\/]node_modules[\\/]rc-tree/, chunks: "all", priority: - }, rccalendar: { name: "rccalendar", test: /[\\/]node_modules[\\/]rc-calendar[\\/]/, chunks: "all", priority: - }, rctable: { name: "rctable", test: /[\\/]node_modules[\\/]rc-table[\\/]es[\\/]/, chunks: "all", priority: - }, wang: { name: "wang", test: /[\\/]node_modules[\\/]wangeditor[\\/]/, chunks: "all", priority: - }, lodash: { name: "lodash", test: /[\\/]node_modules[\\/]lodash[\\/]/, chunks: "all", priority: - }, bizcharts: { name: "bizcharts", test: /[\\/]node_modules[\\/]bizcharts[\\/]/, chunks: "all", priority:  }, xlsx: { name: "xlsx", test: /[\\/]node_modules[\\/]xlsx[\\/]/, chunks: "async", priority:  } } } } }), config.plugin('compression-webpack-plugin').use(CompressionPlugin, [ { test: /\.js$|\.html$|\.css$/, //匹配文件名 threshold: , //对超过k的数据压缩 deleteOriginalAssets: false, //不删除源文件 algorithm: 'gzip', // 指定生成gzip格式 minRatio: . // 压缩比例，值为 ~  }, ]); } }, routes: [ { path: '/', component: '@/layouts/home', exact: true, redirect: '/home/introduce', }, { path: '/login', component: '@/pages/login' }, { path: '/home', component: '@/layouts/home', routes: [ { path: '/home/introduce', component: '@/pages/shortLinkIntroduce', }, { path: '/home/terms', component: '@/pages/terms', }, { path: '/home/privacy', component: '@/pages/privacy', }, { path: '/home/pricing', component: '@/pages/pricing', }, ], }, { path: '/dashboard', component: '@/layouts/index', wrappers: ['@/wrappers/auth'], routes: [ { path: '/dashboard/order', component: '@/pages/order', }, ], }, ], proxy: { '/api': { target: 'http://...:/', }, }, fastRefresh: {}, mfsu: {},}); external 是关键，虽然设置打包流程也很有用，但是实实在在的体积是没法减少的，只是把加载流程给换了。

但是外部external的话，一下子包体积就骤降了，不过这个有利有弊，引入外部会增加流量。

引入qiankun主应用：.umirc.ts qiankun: { master: { // 注册子应用信息 apps: [ { name: 'xxxx', // 唯一 id entry: process.env.NODE_ENV === 'production' ? '//xxxx:/' : '//...:/', }, ], }, }, 分应用 qiankun: { slave: {} }, 关于egg插件app.ts 'use strict';module.exports = app => { if (app.config.ops.app) { require('./lib/nats')(app) } if (app.config.ops.checkLogin) { app.config.coreMiddlewares.push('xxxxx'); }}; 这里就两个关键，一个是中间件的添加，一个是app的挂载，app启动应用的挂载直接参考egg-mongoose的写法。

中间件的挂载主要就是在这个app这边push进去才能启动，注意egg这边对于 文件名是很敏感的，文件名尽量保持统一，如果遇到一些启动不了，无法触发的问题，记得查看文件名。

umi 引入qiankun 之后 和后台的链接 主要依靠nginx server { listen ; index index.html index.htm index.nginx-debian.html; add_header 'Access-Control-Allow-Origin' '*'; add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type'; add_header 'Access-Control-Allow-Methods' 'PUT, POST, GET, DELETE, OPTIONS'; server_name _; location / { root /work/xxxx; index index.html; } gzip on; gzip_min_length k; gzip_comp_level ; gzip_types text/plain application/javascript application/x-javascript text/css application/xml text/xml text/javascript application/json; gzip_static on; gzip_vary on;}server { listen ; index index.html index.htm index.nginx-debian.html; add_header 'Access-Control-Allow-Origin' '*'; add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type'; add_header 'Access-Control-Allow-Methods' 'PUT, POST, GET, DELETE, OPTIONS'; server_name _; location / { root /work/xxxx; index index.html; } location /api/v { proxy_http_version .; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_set_header X-Real-IP $remote_addr; proxy_pass http://xxx:; } location /api/v { proxy_http_version .; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_set_header X-Real-IP $remote_addr; proxy_pass http://xxxxx:; } gzip on; gzip_min_length k; gzip_comp_level ; gzip_types text/plain application/javascript application/x-javascript text/css application/xml text/xml text/javascript application/json; gzip_static on; gzip_vary on; gzip_buffers  k;} 依靠监听端口的变化来处理 前端文件的映射，然后通过主应用的入口 通过 /api/v, /api/v 来分发主应用和分应用，这个处理挺挫的。

。

。

但是我查了一下，没有找到qiankun那边的处理方式，蛮奇怪的。

之后再看吧，暂时感觉也没啥问题。

感觉proto那边的文章也不多，就加一些nats消息的proto处理方式吧,记得初解除proto解析真的是折腾我好半天，这个protobuf 一种是这个直接读proto的，还有一种就是 解析protojson的。

其实这种nats感觉也就是定时器监听，通过消息号来判断信息一一对应的样子了。

protojson这条路，之前我也走过 import * as protobuf from "protobufjs";const dayjs = require('dayjs');const path = require('path');export default class NatClient { nc: any; logger: any; protobuf: protobuf.Root; topicList: Map<string, NatTopic>; constructor(instance, fileName, app) { this.nc = instance; this.topicList = new Map(); this.logger = app.logger; this.protobuf = new protobuf.Root().loadSync(path.join(path.join(app.baseDir, 'protos'), fileName), { keepCase: false, }); } getTopic(sub: string) { if (this.topicList.get(sub)) { return this.topicList.get(sub) } return null; } createTopic(sub, pub, messageName) { let topic = new NatTopic(this.nc, messageName, sub, pub, this.logger, this.protobuf) this.topicList.set(pub, topic); return topic }}class NatTopic { _subj: any; _instance: any; _topic: string; _reqSequence: number; _messageMap: Map<number, any>; _logger: any; _messageName: string; _protobufInfo: protobuf.Root; constructor(instance, messageName, subscribe, publish, logger, protoBuf) { this._subj = instance.subscribe(subscribe); this._instance = instance; this._topic = publish; this.subscription(); this._reqSequence = ; this._messageMap = new Map(); this._logger = logger; this._messageName = messageName; this._protobufInfo = protoBuf; } firsLowerCase(str: string) { return str.replace(/^\S/, (s) => { return s.toLowerCase(); }); }; // proto返回数据解析 deserializer(msg: any) { let request = this._protobufInfo.lookupType(this._messageName); let message = request.decode( msg ); // 接口名称 //@ts-ignore let apiName = message.body.bodyOneof; // 因为 long 型在js中表示不方便，然后就统一转为string型号显示 //@ts-ignore message = request.toObject(message, { enums: String, // 以字符串名称进行枚举 longs: String, // 将 longs 作为字符串 (需要 long.js) defaults: true, // 包含默认值 }) //@ts-ignore this._logger.info(`返回:${apiName}:rsp:${message.head.rspSequence}`) //@ts-ignore if (message.head.errorCode == ) { //@ts-ignore let info = Reflect.get(message.body, apiName) //@ts-ignore this._messageMap.set(message.head.rspSequence, info) } else { this._logger.error(JSON.stringify(message)) } } // proto 数据二进制化，方便传输 serializer<T>(opsMsg: T, reqSequence: number) { let info = { head: { token: "xxxx", timestamp: dayjs().valueOf(), errorCode: , reqSequence: reqSequence }, body: { [this.firsLowerCase(opsMsg.constructor.name)]: opsMsg }, }; let request = this._protobufInfo.lookupType(this._messageName); let result = request.create(info) let paramBuffer = request.encode(result).finish(); return paramBuffer } // 监听nats通道，解析返回数据，通过reqsequence来确保接口一一对应 async subscription() { for await (const m of this._subj) { this.deserializer(m.data) } this._logger.info("subscription closed"); } // 发送接口，然后通过定时器去获取返回数据 async publish(data?: any) { let reqSeq = this._reqSequence + ; this._reqSequence += ; //@ts-ignore this._logger.info(`发送:${data.constructor.name}:req:${reqSeq}`) this._instance.publish(this._topic, this.serializer(data, reqSeq)); const result: any = await new Promise((resolve, rejecet) => { let count = ; const interval = setInterval(() => { count++; if (this._messageMap.get(reqSeq)) { clearInterval(interval); resolve(this._messageMap.get(reqSeq)); } if (count > ) { clearInterval(interval); rejecet({ errorCode:  }); } }, ); }); this._messageMap.delete(reqSeq) return result; }} 从protojson解析的代码，不过是我另外一个项目的，和这个egg项目倒是没关系，egg那个是后端的解析。

这一套解析有局限性！

！

！

！

这个是前端的解析过程，用websocket通讯，其中有和服务端的特殊约定，比如buffer的前多少个字符是要截取出来的，作为方法号的方式，来单独解析，以此做到返回数据的一一对应，buffer的后面是通过proto的解码方式来的，所以，需要理解后改造！

！

！

！

PS: lodash 最好弃用 moment替换成dayjs 这两个包都太大，而且lodash 的方法，其实js本身已经实现的差不多了，而且lodash 的防报错能力太好，有种用多了之后 一般代码写不来的感觉了，还是不大好的。

我已经弃用了哈，看到网上蛮多人也是这么建议的，就拿来学习主义了。

```javascript
import {
  protoInfoMap 
}
from "./ProtoService";
import protoJson from "../proto/proto.json";
import xxxxlocalStorage from "./Localstorage";
import * as protobuf from "protobufjs/light";
import moment from "moment";
const _ = require("lodash");
const protobufInfo = protobuf.Root.fromJSON(protoJson);
class WebsocketProvider {
  retryCount: number;
provider: any;
ws: WebSocket | undefined;
loading: boolean;
messageMap: {
  
}
;
timeInterval: any;
messageInterval: any;
constructor() {
  this.retryCount = ;
this.ws = undefined;
this.loading = false;
this.connect();
this.messageMap = {
  
}
;
this.timeInterval = null;
this.messageInterval = null;
}
checkPing() {
  if (this.timeInterval > ) {
  clearInterval(this.timeInterval);
}
this.timeInterval = setInterval(() => {
  if (this.ws && this.ws.readyState === ) {
  this.send(xxxx,
  {
  
}
);
}
else {
  this.retryCount++;
if (this.retryCount > ) {
  clearInterval(this.timeInterval);
this.retryCount = ;
}

}

}
,
  );
}
connect() {
  const serverIp = xxxlocalStorage.getCookie("serverIp");
try {
  console.log("发起链接");
this.ws = new WebSocket(`ws://${
  serverIp
}
`);
// @ts-ignore this.ws.binaryType = "arraybuffer";
this.init();
}
catch (e) {
  console.log("无法连接，重连中");
}

}
init() {
  if (this.ws) {
  this.ws.onclose = (e) => {
  console.log( `${
  e.code
}
,
  ${
  e.reason
}
,
  ${
  e.wasClean
}
,
  onclose被调用,
  链接关闭` );
}
;
this.ws.onerror = () => {
  console.log("发生异常了");
}
;
}

}
async onOpen() {
  return new Promise((resolve) => {
  if (this.ws) {
  this.ws.onopen = (e) => {
  console.log("已经连接了");
if (this.ws?.readyState === ) {
  resolve({
  
}
);
}

}
;
}

}
);
}
get readyState() {
  if (this.ws) {
  return this.ws.readyState;
}
else {
  return ;
}

}
getMessage() {
  if (this.ws && this.ws.readyState === ) {
  if (_.keys(this.messageMap).length > ) {
  this.messageMap = {
  
}
;
}
this.ws.onmessage = (event) => {
  const num = event.data.slice(,
  );
const _apiNumber = new IntArray(num).toString();
const method = _.get(protoInfoMap,
  _apiNumber);
if (!method) {
  return;
}
const request: any = protobufInfo.lookupType(`xxxx.${
  method
}
`);
if (request) {
  const message = request.decode( new UintArray(event.data.slice(,
  event.data.byteLength)) );
_.set(this.messageMap,
  _apiNumber,
  message);
}

}
;
}

}
async closeWebsocket() {
  // console.log(`checkping：` + this.timeInterval);
return new Promise((resolve,
  rejecet) => {
  if (this.ws && (this.ws.readyState ===  || this.ws.readyState === )) {
  this.ws.close(,
  "normal-close");
console.log("连接关闭");
clearInterval(this.timeInterval);
resolve({
  
}
);
}
else {
  clearInterval(this.timeInterval);
resolve({
  
}
);
}

}
);
}
async send(apiNumber: number,
  param: any = {
  
}
) {
  const paramBuffer = await this.getParamBuffer(apiNumber,
  param);
_.unset(this.messageMap,
  `${
  apiNumber + 
}
`);
if (this.ws && this.ws.readyState ===  && paramBuffer) {
  const sendTime = moment().format("YYYY-MM-DD HH:mm:ss");
console.log(`${
  sendTime
}
-${
  apiNumber
}
`,
  param);
this.ws.send(paramBuffer);
this.getMessage();
const result: any = await new Promise((resolve,
  rejecet) => {
  let count = ;
const interval = setInterval(() => {
  count++;
if (_.get(this.messageMap,
  apiNumber + )) {
  clearInterval(interval);
resolve(_.get(this.messageMap,
  apiNumber + ));
}
if (count > ) {
  clearInterval(interval);
rejecet({
  errorCode:  
}
);
}

}
,
  );
}
);
return result;
}
return [];
}
async getParamBuffer(apiNumber: number,
  param: any) {
  const method = _.get(protoInfoMap,
  _.toString(apiNumber));
if (!method) {
  return "";
}
const request: any = protobufInfo.lookupType(`xxxx.${
  method
}
`);
if (request) {
  let header = new IntArray([apiNumber]).buffer;
const result = request.create(param);
let paramBuffer = request.encode(result).finish();
paramBuffer = Buffer.from(paramBuffer);
header = Buffer.from(header);
return Buffer.concat([header,
  paramBuffer]);
}
else {
  return;
}

}

}
const websocketProvider = new WebsocketProvider();
export default websocketProvider;
另外，拼凑出自己需要的代码，也是很重要的，很多时候一些数据格式不符合我们的要求，通过脚本形式来自动生成一个新的文件还是很有必要的,
  下面这个只是简单的拼凑出我要的proto json 的方法号对应文件，但其实，只要有这个思路，可以自动生成很多东西，希望抛砖引玉。

拼凑.sh #!/bin/bashdefultPath=$(pwd)projectPath=$(dirname "$PWD")cd $projectPath/xxx && git pull origin xxxcd $projectPath/xxxcp -r $projectPath/xxx/Proto/. $defultPath/proto/pbjs -t json ./proto/manager.proto -o ./src/proto/proto.jsonnode protoGen.js 拼凑.js "use strict";
const path = require("path");
const fs = require("fs");
let managetProtoPath = path.join(__dirname,
  "./manager.proto");
let savePath = path.join(__dirname,
  "./xxxx.tsx");
const data = fs.readFileSync(managetProtoPath,
  "utf-");
const lines = data.split(/\r?\n/);
let jsonMap = {
  
}
;
let key,
  value = "";
for (let line of lines) {
  if (line.startsWith("// ")) {
  key = line.split(" ")[];
}
if (line.startsWith("//")) {
  key = line.split("/")[];
}
if (line.startsWith("message")) {
  value = line.split(" ")[];
jsonMap[key] = value;
}

}
let inputData = `// Code AutoGenerate. DO NOT EDIT.\n export const protoInfoMap = ${
  JSON.stringify( jsonMap,
  null,
  "\t")
}
`;
fs.writeFile(savePath,
  inputData,
  (err) => {
  if (err) {
  throw err;
}
console.log("autoGenerate proto method map success");
}
);
