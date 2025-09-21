---
layout: post
title: pokemonInterview
date: 2025-04-14 14:27:12
tags: [JavaScript, 算法, 面试, 数据结构, 编程]
---

# JavaScript 算法面试题精选

本文整理了常见的 JavaScript 编程面试题型，包含详细的代码示例与解析，帮助你应对技术面试中的编程挑战。

## 1. 字符串处理

### 1.1 判断回文字符串

判断一个字符串是否为回文字符串（正读和反读都一样）。

```javascript
/**
 * 判断字符串是否为回文
 * @param {string} s - 输入字符串
 * @return {boolean} - 是否为回文
 */
function isPalindrome(s) {
  // 1. 预处理：转小写并移除非字母数字字符
  const cleanStr = s.toLowerCase().replace(/[^a-z0-9]/g, "");

  // 2. 双指针法判断是否回文
  let left = 0,
    right = cleanStr.length - 1;
  while (left < right) {
    if (cleanStr[left] !== cleanStr[right]) {
      return false;
    }
    left++;
    right--;
  }

  return true;
}

// 测试
console.log(isPalindrome("A man, a plan, a canal: Panama")); // true
console.log(isPalindrome("race a car")); // false
```

### 1.2 最长不重复子串

找出字符串中最长的不包含重复字符的子串长度。

```javascript
/**
 * 找出最长不含重复字符的子串长度
 * @param {string} s - 输入字符串
 * @return {number} - 最长子串长度
 */
function lengthOfLongestSubstring(s) {
  // 滑动窗口 + 哈希表
  const charMap = new Map();
  let maxLength = 0;
  let left = 0;

  for (let right = 0; right < s.length; right++) {
    const currentChar = s[right];

    // 如果字符已存在于当前窗口中，移动左指针
    if (charMap.has(currentChar) && charMap.get(currentChar) >= left) {
      left = charMap.get(currentChar) + 1;
    }
    // 更新最大长度
    maxLength = Math.max(maxLength, right - left + 1);

    // 记录字符位置
    charMap.set(currentChar, right);
  }

  return maxLength;
}

// 测试
console.log(lengthOfLongestSubstring("abcabcbb")); // 3 ("abc")
console.log(lengthOfLongestSubstring("bbbbb")); // 1 ("b")
```

## 2. 数组处理

### 2.1 查找数组中的重复数字

找出数组中任意一个重复的数字。

```javascript
/**
 * 查找数组中的重复数字
 * @param {number[]} nums - 输入数组
 * @return {number} - 重复的数字，若无则返回-1
 */
function findDuplicate(nums) {
  // 使用哈希表记录出现过的数字
  const seen = new Set();

  for (const num of nums) {
    if (seen.has(num)) {
      return num;
    }
    seen.add(num);
  }

  return -1; // 无重复数字
}

// 测试
console.log(findDuplicate([1, 2, 3, 4, 2])); // 2
console.log(findDuplicate([1, 2, 3, 4])); // -1
```

### 2.2 旋转数组

将数组向右旋转 k 步。

```javascript
/**
 * 旋转数组 k 步
 * @param {number[]} nums - 输入数组
 * @param {number} k - 旋转步数
 * @return {number[]} - 旋转后的数组
 */
function rotateArray(nums, k) {
  // 处理 k 大于数组长度的情况
  k = k % nums.length;

  // 三次翻转法
  // 1. 翻转整个数组
  reverse(nums, 0, nums.length - 1);
  // 2. 翻转前k个元素
  reverse(nums, 0, k - 1);
  // 3. 翻转剩余元素
  reverse(nums, k, nums.length - 1);

  return nums;

  // 辅助函数：翻转数组指定区间
  function reverse(arr, start, end) {
    while (start < end) {
      [arr[start], arr[end]] = [arr[end], arr[start]];
      start++;
      end--;
    }
  }
}

// 测试
console.log(rotateArray([1, 2, 3, 4, 5, 6, 7], 3)); // [5, 6, 7, 1, 2, 3, 4]
```

## 3. 栈/队列

### 3.1 有效括号

判断括号是否有效闭合。

```javascript
/**
 * 判断括号是否有效闭合
 * @param {string} s - 包含括号的字符串
 * @return {boolean} - 是否有效闭合
 */
function isValidParentheses(s) {
  const stack = [];
  const pairs = {
    ")": "(",
    "}": "{",
    "]": "[",
  };

  for (const char of s) {
    // 如果是左括号，入栈
    if (!pairs[char]) {
      stack.push(char);
    }
    // 如果是右括号，检查栈顶是否匹配
    else if (stack.pop() !== pairs[char]) {
      return false;
    }
  }

  // 栈为空则全部匹配成功
  return stack.length === 0;
}

// 测试
console.log(isValidParentheses("()[]{}")); // true
console.log(isValidParentheses("([)]")); // false
```

### 3.2 逆波兰表达式求值

计算逆波兰表达式（后缀表达式）的值。

```javascript
/**
 * 计算逆波兰表达式的值
 * @param {string[]} tokens - 逆波兰表达式数组
 * @return {number} - 计算结果
 */
function evalRPN(tokens) {
  const stack = [];
  const operators = {
    "+": (a, b) => a + b,
    "-": (a, b) => a - b,
    "*": (a, b) => a * b,
    "/": (a, b) => Math.trunc(a / b), // 整数除法，向零取整
  };

  for (const token of tokens) {
    if (operators[token]) {
      // 是运算符，取出两个操作数进行计算
      const b = stack.pop();
      const a = stack.pop();
      stack.push(operators[token](a, b));
    } else {
      // 是操作数，转为数字并入栈
      stack.push(Number(token));
    }
  }

  return stack[0];
}

// 测试
console.log(evalRPN(["2", "1", "+", "3", "*"])); // 9
console.log(evalRPN(["4", "13", "5", "/", "+"])); // 6
```

## 4. 哈希表

### 4.1 两数之和

找出数组中和为目标值的两个数的下标。

```javascript
/**
 * 两数之和
 * @param {number[]} nums - 数字数组
 * @param {number} target - 目标和
 * @return {number[]} - 满足条件的两数下标
 */
function twoSum(nums, target) {
  // 哈希表存储已遍历的数及其下标
  const numMap = new Map();

  for (let i = 0; i < nums.length; i++) {
    const complement = target - nums[i];

    // 如果找到互补的数，返回结果
    if (numMap.has(complement)) {
      return [numMap.get(complement), i];
    }

    // 存储当前数字及其下标
    numMap.set(nums[i], i);
  }

  return []; // 未找到符合条件的结果
}

// 测试
console.log(twoSum([2, 7, 11, 15], 9)); // [0, 1]
```

### 4.2 找众数

找出数组中出现次数超过一半的元素。

```javascript
/**
 * 找出数组中的众数（出现次数超过一半的元素）
 * @param {number[]} nums - 输入数组
 * @return {number} - 众数
 */
function majorityElement(nums) {
  // 使用哈希表统计频次
  const countMap = new Map();
  const threshold = nums.length / 2;

  for (const num of nums) {
    const count = (countMap.get(num) || 0) + 1;
    countMap.set(num, count);

    if (count > threshold) {
      return num;
    }
  }

  // 也可以使用Boyer-Moore投票算法优化空间复杂度
}

// 测试
console.log(majorityElement([3, 2, 3])); // 3
console.log(majorityElement([2, 2, 1, 1, 1, 2, 2])); // 2
```

## 5. 排序/查找

### 5.1 合并重叠区间

合并所有重叠的区间。

```javascript
/**
 * 合并重叠区间
 * @param {number[][]} intervals - 区间数组
 * @return {number[][]} - 合并后的区间数组
 */
function mergeIntervals(intervals) {
  if (intervals.length <= 1) return intervals;

  // 按区间起始点排序
  intervals.sort((a, b) => a[0] - b[0]);

  const result = [intervals[0]];

  for (let i = 1; i < intervals.length; i++) {
    const currentInterval = intervals[i];
    const lastMerged = result[result.length - 1];

    // 如果当前区间与上一个合并结果重叠，则合并
    if (currentInterval[0] <= lastMerged[1]) {
      lastMerged[1] = Math.max(lastMerged[1], currentInterval[1]);
    } else {
      // 不重叠，添加到结果中
      result.push(currentInterval);
    }
  }

  return result;
}

// 测试
console.log(
  mergeIntervals([
    [1, 3],
    [2, 6],
    [8, 10],
    [15, 18],
  ])
); // [[1,6],[8,10],[15,18]]
```

### 5.2 手写快速排序

实现快速排序算法。

```javascript
/**
 * 快速排序实现
 * @param {number[]} arr - 待排序数组
 * @return {number[]} - 排序后的数组
 */
function quickSort(arr) {
  if (arr.length <= 1) return arr;

  const pivot = arr[Math.floor(arr.length / 2)]; // 选择中间元素作为基准
  const left = [];
  const right = [];
  const equal = [];

  // 分区
  for (const num of arr) {
    if (num < pivot) {
      left.push(num);
    } else if (num > pivot) {
      right.push(num);
    } else {
      equal.push(num);
    }
  }

  // 递归排序并合并结果
  return [...quickSort(left), ...equal, ...quickSort(right)];
}

// 测试
console.log(quickSort([3, 1, 4, 1, 5, 9, 2, 6])); // [1, 1, 2, 3, 4, 5, 6, 9]
```

## 6. 模拟类题

### 6.1 简易购物车系统

实现一个简单的购物车系统，支持添加、删除商品和计算总价。

```javascript
/**
 * 购物车系统
 */
class ShoppingCart {
  constructor() {
    this.items = new Map(); // 商品ID -> {商品信息, 数量}
  }

  /**
   * 添加商品到购物车
   * @param {object} product - 商品信息对象
   * @param {number} quantity - 数量
   */
  addItem(product, quantity = 1) {
    const { id, name, price } = product;

    if (this.items.has(id)) {
      const item = this.items.get(id);
      item.quantity += quantity;
    } else {
      this.items.set(id, { product: { id, name, price }, quantity });
    }

    console.log(`已添加 ${quantity} 个 ${name} 到购物车`);
  }

  /**
   * 从购物车移除商品
   * @param {string} productId - 商品ID
   * @param {number} quantity - 移除数量，默认全部移除
   */
  removeItem(productId, quantity = null) {
    if (!this.items.has(productId)) {
      console.log("购物车中没有该商品");
      return;
    }

    const item = this.items.get(productId);

    if (quantity === null || quantity >= item.quantity) {
      this.items.delete(productId);
      console.log(`已从购物车移除所有 ${item.product.name}`);
    } else {
      item.quantity -= quantity;
      console.log(`已从购物车移除 ${quantity} 个 ${item.product.name}`);
    }
  }

  /**
   * 计算购物车总价
   * @return {number} - 总价
   */
  getTotalPrice() {
    let total = 0;

    for (const item of this.items.values()) {
      total += item.product.price * item.quantity;
    }

    return total;
  }

  /**
   * 显示购物车内容
   */
  viewCart() {
    if (this.items.size === 0) {
      console.log("购物车为空");
      return;
    }

    console.log("购物车内容：");
    for (const item of this.items.values()) {
      const { name, price } = item.product;
      console.log(
        `${name} - 单价: ¥${price} x ${item.quantity} = ¥${
          price * item.quantity
        }`
      );
    }
    console.log(`总价: ¥${this.getTotalPrice()}`);
  }
}

// 使用示例
const cart = new ShoppingCart();
cart.addItem({ id: "p1", name: "iPad", price: 3299 });
cart.addItem({ id: "p2", name: "AirPods", price: 1299 }, 2);
cart.viewCart();
cart.removeItem("p1");
cart.viewCart();
```

## 7. 简易算法

### 7.1 斐波那契数列

计算斐波那契数列的第 n 项。

```javascript
/**
 * 计算斐波那契数列的第n项（优化版）
 * @param {number} n - 第n项
 * @return {number} - 结果
 */
function fibonacci(n) {
  // 基础情况
  if (n <= 1) return n;

  // 动态规划优化，避免递归栈溢出
  let prev = 0;
  let curr = 1;

  for (let i = 2; i <= n; i++) {
    const next = prev + curr;
    prev = curr;
    curr = next;
  }

  return curr;
}

// 测试
console.log(fibonacci(10)); // 55
console.log(fibonacci(20)); // 6765
```

### 7.2 最大公约数

计算两个数的最大公约数。

```javascript
/**
 * 计算两个数的最大公约数（辗转相除法）
 * @param {number} a - 第一个数
 * @param {number} b - 第二个数
 * @return {number} - 最大公约数
 */
function gcd(a, b) {
  // 确保 a >= b
  if (a < b) [a, b] = [b, a];

  // 辗转相除法(欧几里得算法)
  while (b !== 0) {
    const temp = b;
    b = a % b;
    a = temp;
  }

  return a;
}

// 测试
console.log(gcd(54, 24)); // 6
console.log(gcd(105, 45)); // 15
```

## 8. 数据结构

### 8.1 LRU 缓存实现

实现一个 LRU (最近最少使用) 缓存结构，支持 get 和 put 操作。

```javascript
/**
 * LRU缓存实现
 * @param {number} capacity - 缓存容量
 */
class LRUCache {
  constructor(capacity) {
    this.capacity = capacity; // 缓存容量
    this.cache = new Map(); // 使用Map保持插入顺序
  }

  /**
   * 获取缓存中的值
   * @param {number} key - 键
   * @return {number} - 值，不存在则返回-1
   */
  get(key) {
    if (!this.cache.has(key)) {
      return -1;
    }

    // 访问过后，将该项移到最近使用（Map尾部）
    const value = this.cache.get(key);
    this.cache.delete(key);
    this.cache.set(key, value);

    return value;
  }

  /**
   * 添加或更新缓存
   * @param {number} key - 键
   * @param {number} value - 值
   */
  put(key, value) {
    // 如果键已存在，先删除
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    // 如果缓存已满，删除最久未使用的项（Map头部）
    else if (this.cache.size >= this.capacity) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    // 添加新项到Map尾部（最近使用）
    this.cache.set(key, value);
  }
}

// 测试
const lruCache = new LRUCache(2);
lruCache.put(1, 1); // 缓存是 {1=1}
lruCache.put(2, 2); // 缓存是 {1=1, 2=2}
console.log(lruCache.get(1)); // 返回 1，并将1移到最近使用
lruCache.put(3, 3); // 2被淘汰，缓存是 {1=1, 3=3}
console.log(lruCache.get(2)); // 返回 -1 (未找到)
```

以上就是常见的 JavaScript 面试编程题整理，希望这些例子和解析能够帮助你准备技术面试。每种类型的题目都涵盖了相关的知识点，包括算法思想和 JavaScript 的特性运用。

祝面试顺利！

---

参考资料：

1. LeetCode 题库: https://leetcode.com/
2. JavaScript 数据结构与算法: https://github.com/trekhleb/javascript-algorithms
