---
title: LeetCode 每日一题 - 两数之和
date: 2020-07-01 19:31:48
categories:
  - 算法
tags:
  - LeetCode
  - JavaScript
  - 算法
  - 哈希表
---

## 题目描述

给定一个整数数组 nums 和一个目标值 target，请你在该数组中找出和为目标值的那两个整数，并返回他们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素不能使用两遍。

## 解题思路

### 方法一: 暴力循环
最初采用双重循环的方式,但在大数据量时会超时。

### 方法二: Map优化
使用 Map 数据结构可以避免多次遍历:

```javascript
var twoSum = function(nums, target) {
    let map = new Map();
    let result;
    
    for(let key in nums) {
        let value = nums[key];
        result = target - value;
        
        if(map.has(result)) {
            return [map.get(result), key];
        }
        map.set(value, key);
    }
};
```

### 代码分析
1. 使用 Map 存储遍历过的数字及其索引
2. 每次遍历时检查 target - 当前值 是否存在于 Map 中
3. 如果存在,说明找到了答案
4. 如果不存在,将当前值和索引存入 Map

## 学习心得

1. Map 数据结构在查找场景中的优势
2. 时间复杂度从 O(n²) 优化到 O(n)
3. 空间换时间的经典应用

## 后续计划
- 继续学习二叉树相关题目
- 研究其他人的解题思路
- 加强算法训练

## 参考资料
- [LeetCode 两数之和](https://leetcode.cn/problems/two-sum/)
- [JavaScript Map 对象](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Map)
