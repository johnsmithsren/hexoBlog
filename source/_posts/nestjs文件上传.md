---

title: nestjs文件上传
date: 2024-12-09 15:31:25
categories:
  - 后端开发
tags:
  - Node.js
  - Nest.js
  - TypeScript
---

## 引言

在开发 Web 应用时，文件上传是一个非常常见的需求。本文将详细介绍如何在 NestJS 框架中实现文件上传功能，包括普通上传和大文件分片上传两种实现方式。

## 文件上传实现方案

### 1. 分片上传实现

对于小型文件的分片上传，我们可以直接将文件存储在内存中。通过 `FileInterceptor` 拦截器，我们可以轻松获取到包含文件 buffer 的文件流：

```typescript:src/controllers/file.controller.ts
@Post('file/uploadFile')
@UseInterceptors(FileInterceptor('file'))
async uploadCommonChunk(
    @UploadedFile() file: Express.Multer.File,
    @Body('index') index: number,
    @Body('hash') hash: string,
    @Body('dir') dir: string,
) {
    return await this.fileService.uploadCommonChunk(file, index, hash, dir);
}
```

### 2. 大文件上传实现

对于大文件上传，建议使用磁盘存储方式。我们可以通过配置 `diskStorage` 来指定存储目录：

```typescript:src/controllers/file.controller.ts
@Post('file/uploadHotpatch/:filePath')
@UseInterceptors(
    FileInterceptor('file', {
        storage: diskStorage({
            destination: './temp',
            filename: (req, file, cb) => {
                cb(null, file.originalname);
            },
        }),
    }),
)
async uploadHotPatch(
    @UploadedFile() file: Express.Multer.File,
    @Param('filePath') filePath: string,
    @Body('dir') dir: string,
) {
    return this.fileService.uploadHotPatch(file, filePath, dir);
}
```

## 分片上传实现细节

### 工作原理

分片上传的核心思路是：

1. 前端将文件切分成固定大小的块
2. 为每个文件生成唯一的 hash 值
3. 将分片和 hash 值传送到服务端
4. 服务端接收并存储分片
5. 所有分片上传完成后进行合并

### 优势

- 支持多核并行上传，显著提升上传速度
- 可实现断点续传功能
- 降低上传失败风险

### 前端实现示例

关键代码展示了如何进行文件分片和并发上传：

```typescript:src/utils/upload.ts
const chunkSize = 20 * 1024 * 1024; // 设置分片大小为20MB
const blobSlice = File.prototype.slice;
const blockCount = Math.ceil(file.size / chunkSize);

// 生成文件hash
const sparkMd5 = new SparkMD5();
sparkMd5.append(file.name);
const hash = sparkMd5.end();

// 并发控制
const batchLength = 6;
let batchArray = [];

// 分片上传实现
for (let i = 0; i < blockCount; i++) {
    const start = i * chunkSize;
    const end = Math.min(file.size, start + chunkSize);
    // ... 分片上传逻辑 ...
}
```

### 服务端合并实现

使用 Node.js 的流式处理来合并文件分片：

```typescript:src/services/file.service.ts
import * as fs from 'fs-extra';

async function mergeChunks(chunksPath: string, filePath: string, total: number, hash: string) {
    try {
        // 验证分片完整性
        const chunkPaths = Array.from({ length: total },
            (_, index) => path.join(chunksPath, `${hash}-${index}`));

        // 创建写入流并按序合并
        const writeStream = fsNormal.createWriteStream(filePath);
        for (let i = 0; i < total; i++) {
            await new Promise((resolve, reject) => {
                const chunkStream = fsNormal.createReadStream(chunkPaths[i]);
                chunkStream.pipe(writeStream, { end: false });
                chunkStream.on('end', resolve);
                chunkStream.on('error', reject);
            });
        }

        // 清理临时文件
        await fs.remove(chunksPath);
        return true;
    } catch (error) {
        await fs.remove(filePath).catch(() => {});
        throw error;
    }
}
```

## 总结

本文详细介绍了在 NestJS 中实现文件上传的两种方案：普通上传和分片上传。分片上传虽然实现较为复杂，但能够有效处理大文件上传的场景，并提供更好的用户体验。通过合理使用 Node.js 的流式处理，我们可以高效地处理文件合并操作。
