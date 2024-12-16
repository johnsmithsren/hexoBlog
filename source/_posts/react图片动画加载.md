---
layout: post
title: React 图片动画加载技术详解
date: 2024-12-16 11:25:14
tags:
  - React
  - 前端开发
  - 图片加载
  - 动画
categories:
  - 前端技术
---

### 图片加载动画的挑战

开发过程中，我遇到了一个常见的问题：页面初始加载时，多张图片未完成加载会导致动画效果丢失。这不仅影响了用户体验，也降低了页面的交互质感。

### 解决方案：动态监听与懒加载

我们的解决方案包含两个核心策略：
1. **图片加载监听**：确保所有图片加载完成后再触发动画
2. **滚动懒加载**：延迟加载动画，提高初始页面响应速度

### 代码实现

```typescript
useEffect(() => {
    const onLoad = () => {
      gsap.utils
        .toArray(".section-image-friends")
        .forEach((image: any, index) => {
          // 交替方向，创建更生动的视觉效果
          const direction = index % 2 === 0 ? "-10vw" : "10vw"; 
          
          gsap.fromTo(
            image,
            {
              x: direction,
              opacity: 0,
              rotationX: 90,
            },
            {
              x: 0,
              opacity: 1,
              rotationX: 0,
              duration: 1.2,
              scrollTrigger: {
                trigger: image,
                toggleActions: "play none none reverse",
                markers: false,
              },
            }
          );
        });
    };

    // 图片加载状态追踪
    const images = document.querySelectorAll<HTMLImageElement>(
      ".section-image-friends"
    );
    let loadedCount = 0;

    images.forEach((img) => {
      if (img.complete) {
        loadedCount++;
      } else {
        img.addEventListener("load", () => {
          loadedCount++;
          if (loadedCount === images.length) onLoad();
        });
      }
    });

    // 如果图片已全部加载，立即触发动画
    if (loadedCount === images.length) onLoad(); 
  }, []);
```

### 关键技术点

- **GSAP动画库**：提供流畅的过渡效果
- **ScrollTrigger**：实现滚动触发的动画
- **动态加载监听**：确保动画在所有图片就绪后执行

### 优化建议

1. 对于大量图片，考虑使用 Intersection Observer API 替代当前方案
2. 添加错误处理机制，防止个别图片加载失败阻塞整体动画
3. 根据网络环境动态调整动画持续时间

### 结语

通过精心设计的图片加载动画，我们不仅能提升视觉体验，还能优化性能和用户交互。持续关注细节，方能打造卓越的前端应用。
