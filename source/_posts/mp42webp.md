---
layout: post
title: 使用 FFmpeg 将 MP4 转换为 WebP
date: 2024-12-12 18:26:18
tags:
  - FFmpeg
  - 视频处理
  - WebP
  - MP4
---

## 引言

在现代 Web 开发中，WebP 格式因其高效的压缩率和良好的图像质量而受到广泛欢迎。本文将介绍如何使用 FFmpeg 将 MP4 视频转换为 WebP 格式。

## 转换步骤

### 基本命令

1. 仅仅是记录一下，对于 ffmpeg 也是试水，这个软件过于强大，摸个毛
2. H.264(AVC) 和 H.265(HEVC) 是两种视频编码标准，主要差异如下：

- 压缩效率：H.265 比 H.264 更高效，能够在相同质量下提供更小的文件大小
- 视频质量：H.265 通常提供更好的视频质量，尤其是在高分辨率视频上
- 计算复杂度：H.265 的编码和解码过程更复杂，需要更多的计算资源
- 兼容性：H.264 是更广泛支持的编码标准，许多设备和平台都支持 H.264

3. 一般的 mp4 都是 h264 格式，可以通过查看视频的详情：

```bash
ffmpeg -i input.mp4
```

输出：

```bash
Stream #0:0[0x1](und): Video: h264 (High) (avc1 / 0x31637661), yuv420p(progressive), 1920x1080 [SAR 1:1 DAR 16:9], 2693 kb/s, 24 fps, 24 tbr, 12288 tbn
```

这意味：

- 编码格式: h264 (High)，确实是 H.264 编码
- 分辨率: 1920x1080，即 1080p
- 帧率: 24 fps
- 比特率: 2693 kb/s
- 色彩空间: yuv420p
- 视频时长: Duration: 00:00:16.00

4. 转换为 webp 格式

代码就没什么了，都是基础操作，现在 AI 时代，无需多言：

```javascript
const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");

/**
 * 检查 FFmpeg 是否已安装
 * @returns {Promise<boolean>}
 */
function checkFFmpeg() {
  return new Promise((resolve) => {
    exec("ffmpeg -version", (error) => {
      resolve(!error);
    });
  });
}

/**
 * 将单个视频文件转换为 WebP 动图
 * @param {string} inputVideoPath - 输入视频文件路径
 * @param {string} outputWebPPath - 输出 WebP 文件路径
 * @param {Object} options - 转换选项
 * @returns {Promise} 转换结果的 Promise
 */
async function generateWebPFromVideo(
  inputVideoPath,
  outputWebPPath,
  options = {}
) {
  // 检查 FFmpeg 是否安装
  const isFFmpegInstalled = await checkFFmpeg();
  if (!isFFmpegInstalled) {
    throw new Error(
      "FFmpeg 未安装或未添加到环境变量。请安装 FFmpeg 并将其添加到系统环境变量中。"
    );
  }

  // 解构配置参数，设置默认值
  const {
    width = -1, // 输出宽度，设为-1表示按比例缩放
    quality = 75, // 质量参数(0-100)：越高质量越好，文件越大
    fps = 24, // 每秒帧数：越高越流畅，文件越大
    compression = 4, // 压缩级别(0-6)：越高压缩率越大，但处理更慢
    threads = 4, // CPU线程数：建议设置为CPU核心数
  } = options;

  console.log(`开始转换: ${path.basename(inputVideoPath)}`);

  // 构建 FFmpeg 命令
  const command = `ffmpeg -threads ${threads} -i "${inputVideoPath}" -c:v libwebp -vf "fps=${fps},scale=${width}:-1:flags=lanczos" -loop 0 -compression_level ${compression} -q:v ${quality} -lossless 0 -preset picture -an -y "${outputWebPPath}"`;

  // 返回 Promise 用于异步处理
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`转换错误: ${stderr}`);
        reject(error);
        return;
      }
      console.log(`成功转换: ${path.basename(outputWebPPath)}`);
      resolve(stdout);
    });
  });
}

/**
 * 批量转换文件夹中的视频文件
 * @param {string} inputFolder - 输入文件夹路径
 * @param {string} outputFolder - 输出文件夹路径
 * @param {Object} options - 转换选项
 */
async function convertVideosInFolder(inputFolder, outputFolder, options = {}) {
  try {
    // 检查 FFmpeg 是否安装
    const isFFmpegInstalled = await checkFFmpeg();
    if (!isFFmpegInstalled) {
      console.error("错误：FFmpeg 未安装或未添加到环境变量。");
      console.error("请按照以下步骤安装 FFmpeg：");
      console.error(
        "1. 下载 FFmpeg: https://ffmpeg.org/download.html  或者 winget install ffmpeg"
      );
      console.error("2. 解压下载的文件");
      console.error("3. 将 ffmpeg/bin 目录添加到系统环境变量");
      console.error("4. 重新启动命令提示符或终端");
      return;
    }

    // 确保输出文件夹存在
    if (!fs.existsSync(outputFolder)) {
      fs.mkdirSync(outputFolder);
    }

    // 获取所有 MP4 文件
    const inputFiles = fs
      .readdirSync(inputFolder)
      .filter((file) => file.endsWith(".mp4"));

    // 遍历处理每个文件
    for (const inputFile of inputFiles) {
      try {
        const inputFilePath = path.join(__dirname, inputFolder, inputFile);
        const outputFileName =
          path.basename(inputFile, path.extname(inputFile)) + ".webp";
        const outputFilePath = path.join(
          __dirname,
          outputFolder,
          outputFileName
        );

        console.log(`\n开始处理 ${inputFile}`);
        await generateWebPFromVideo(inputFilePath, outputFilePath, options);
      } catch (err) {
        console.error(`处理 ${inputFile} 时发生错误:`, err);
      }
    }
  } catch (err) {
    console.error("发生错误:", err);
  }
}

// 定义输入输出路径
const inputVideoPath = "./mp4"; // MP4文件所在文件夹
const outputWebPPath = "./webp"; // WebP输出文件夹

// 转换参数配置
const conversionOptions = {
  width: 360, // 输出宽度（像素）
  quality: 75, // 质量参数（推荐65-80之间）
  fps: 24, // 帧率（标准帧率，可根据需求调整）
  compression: 4, // 压缩级别（推荐4-6之间）
  threads: 4, // CPU线程数（建议设置为CPU核心数）
};

// 执行批量转换
convertVideosInFolder(inputVideoPath, outputWebPPath, conversionOptions).catch(
  console.error
);
```
