---
title: A*寻路算法的JavaScript实现
date: 2025-01-10 14:15:40
tags:
  - Node.js
  - 算法
categories:
  - 游戏
---

## A\*算法简介

A\*（A-Star）算法是一种启发式搜索算法，广泛应用于游戏开发中的寻路系统。

## 核心概念

A\*算法的核心在于其评估函数:<span style="color: red; font-weight: bold;">f(n) = g(n) + h(n)</span>,其中：

- g(n)：从起点到当前节点的实际代价，g(b)+(b,c)
- h(n)：从当前节点到目标节点的估计代价（启发函数）
- f(n)：总估计代价

算法通过维护一个开放列表（openList）来存储待评估的节点，每次从中选择 f 值最小的节点进行扩展。这种方式既能避免遍历大量远离目标的节点，又能有效规避障碍物，从而找到最优路径。

1. 记住 f(n) = g(n) + h(n)
2. 每次轮询 openList，都是找 f 值最小的节点
3. 将当前节点从 openList 移到 closedList
4. 评估所有相邻节点，此时会更新各个相邻节点的 f 值，g 值
5. 如果是新节点，添加到 openList
6. 如果找到更优路径，更新节点信息
7. 直到找到目标节点，返回路径

## 代码实现

下面是一个完整的 JavaScript 实现，包含了详细的注释：

```javascript
class AStar {
  constructor(grid) {
    this.grid = grid;
    this.openList = new Map(); // 存储待评估的节点
    this.closedList = new Set(); // 存储已评估的节点
    this.cameFrom = new Map(); // 记录路径
  }

  // 计算两点间的曼哈顿距离作为启发函数
  distance(nodeA, nodeB) {
    return Math.abs(nodeA.x - nodeB.x) + Math.abs(nodeA.y - nodeB.y);
  }

  // 生成节点的唯一键
  getNodeKey(node) {
    return `${node.x},${node.y}`;
  }

  findPath(start, end) {
    // 初始化起点
    start.g = 0;
    start.f = this.distance(start, end);
    this.openList.set(this.getNodeKey(start), start);

    while (this.openList.size > 0) {
      // 获取f值最小的节点
      const current = Array.from(this.openList.values()).reduce((min, node) =>
        !min || node.f < min.f ? node : min
      );

      // 到达终点，返回路径
      if (current.x === end.x && current.y === end.y) {
        return this.reconstructPath(start, end);
      }

      // 将当前节点从openList移到closedList
      const currentKey = this.getNodeKey(current);
      this.openList.delete(currentKey);
      this.closedList.add(currentKey);

      // 评估所有相邻节点
      for (const neighbor of this.grid.getNeighbors(current)) {
        const neighborKey = this.getNodeKey(neighbor);

        // 跳过已评估的节点
        if (this.closedList.has(neighborKey)) {
          continue;
        }

        // 计算经过当前节点到达邻居节点的代价
        const tentativeG = current.g + 1;
        neighbor.g = tentativeG;
        neighbor.f = neighbor.g + this.distance(neighbor, end);
        this.cameFrom.set(neighborKey, current);
        // 如果是新节点，添加到openList
        if (!this.openList.has(neighborKey)) {
          this.openList.set(neighborKey, neighbor);
        }
      }
    }

    return null; // 未找到可行路径
  }

  // 重建从起点到终点的路径
  reconstructPath(start, end) {
    const path = [];
    let current = end;

    while (current) {
      path.unshift(current);
      const currentKey = this.getNodeKey(current);
      current = this.cameFrom.get(currentKey);

      if (current && current.x === start.x && current.y === start.y) {
        path.unshift(start);
        break;
      }
    }

    return path;
  }
}

// 测试用例
function testAStar() {
  // 创建10x10网格
  const grid = new Grid(10, 10);

  // 设置障碍物
  [
    [2, 2],
    [2, 3],
    [2, 4],
    [5, 5],
    [5, 6],
    [5, 7],
    [7, 2],
    [7, 3],
    [7, 4],
  ].forEach(([x, y]) => grid.addObstacle(x, y));

  const start = { x: 0, y: 0 };
  const end = { x: 9, y: 9 };

  const astar = new AStar(grid);
  const path = astar.findPath(start, end);

  // 可视化网格和路径
  console.log("Grid with path:");
  for (let y = 0; y < grid.height; y++) {
    let line = "";
    for (let x = 0; x < grid.width; x++) {
      if (grid.obstacles.has(`${x},${y}`)) {
        line += "█ "; // 障碍物
      } else if (path && path.some((node) => node.x === x && node.y === y)) {
        line += "* "; // 路径
      } else {
        line += ". "; // 空地
      }
    }
    console.log(line);
  }

  if (path) {
    console.log(
      "\nPath found:",
      path.map((node) => `(${node.x},${node.y})`).join(" -> ")
    );
  } else {
    console.log("\nNo path found!");
  }
}

// 运行测试
testAStar();
```
