---
title: React 开发实践与组件设计思考
date: 2022-04-23 13:31:48
categories:
  - 前端开发
tags:
  - React
  - Hooks
  - 组件设计
  - 状态管理
---

## 项目实践

在开发内部管理平台时,主要使用了以下技术栈:
- React Hooks (useState, useEffect, useRef)
- Ant Design 组件库
- MobX 状态管理

## 组件设计经验

### 状态管理
对于简单的父子组件通信,使用 props 和 ref 就足够了。但在以下情况需要考虑使用状态管理工具:
- 组件层级过深
- 状态需要共享
- 状态变化复杂

### 组件拆分原则
1. 功能独立
2. 复用性高
3. 维护方便
4. 职责单一

### 实际案例

```jsx
// 日期范围选择组件
const RangePickCondition = ({ onChange }) => {
  const [dates, setDates] = useState([]);
  const pickerRef = useRef(null);

  useEffect(() => {
    // 初始化逻辑
  }, []);

  const handleChange = (values) => {
    setDates(values);
    onChange?.(values);
  };

  return (
    <DatePicker.RangePicker 
      ref={pickerRef}
      value={dates}
      onChange={handleChange}
    />
  );
};
```

## 遇到的问题

### Ref 使用问题
- 子组件中使用 ref 获取初始值存在延迟
- 需要多次点击才能获取正确值
- useRef 和 useState 配合使用需要注意时机

### 解决方案
1. 对于简单父子组件:
   - 使用 props 传递数据
   - ref 仅用于必要的 DOM 操作

2. 对于复杂状态管理:
   - 引入 MobX 统一管理状态
   - 避免过深的组件嵌套

## 最佳实践

1. **状态管理选择**
   - 简单场景: props + ref
   - 中等复杂度: Context
   - 复杂场景: MobX/Redux

2. **组件设计原则**
   - 保持组件纯粹性
   - 避免过度设计
   - 合理拆分组件

3. **性能优化**
   - 使用 useMemo 和 useCallback
   - 避免不必要的重渲染
   - 合理使用 React.memo

## 参考资料
- [React Hooks 文档](https://reactjs.org/docs/hooks-intro.html)
- [Ant Design 组件库](https://ant.design)
- [MobX 官方文档](https://mobx.js.org)
