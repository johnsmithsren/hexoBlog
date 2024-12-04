---
title: leetcode 每日一题
date: 2020-07-01 19:31:48
---

开始刷题 给定一个整数数组 nums 和一个目标值 target，请你在该数组中找出和为目标值的那 两个 整数，并返回他们的数组下标。

你可以假设每种输入只会对应一个答案。

但是，数组中同一个元素不能使用两遍。

var twoSum = function(nums, target) { let map=new Map() let result for(let key in nums){ let value = nums[key] result = target-value if(map.has(result)){ return [map.get(result),key] } map.set(value,key) }}; 这道题开始自然是 for 循环，然后超时。

。

。

愚蠢的我，一点新意都没有，然后就是采用 map 形式，避免多次遍历，然后就没有超时了。

这道题界解决信心爆棚，随机了一道二叉树的题目，然后崩溃。

。

。

明天会看下别人的题解，然后自行把二叉树用自己的语言写一遍，希望能够弥补自身算法逻辑缺少训练的弊端。
