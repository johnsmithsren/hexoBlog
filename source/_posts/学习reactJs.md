---
layout: post
title: React Hooks 学习笔记
date: 2024-12-12 16:07:42
categories:
  - 前端开发
tags:
  - React
  - JavaScript
  - Hooks
cover: /images/react.png
---

## 引言

React Hooks 是 React 16.8 引入的特性,让我们可以在函数组件中使用状态和其他 React 特性。本文将记录学习 React Hooks 的心得体会。

## 基础 Hooks

### useState

状态管理的基础 Hook:

1. 最常用的就是 setState,日常代码书写中，特别容易出现魔术字。虽然符合直觉，但需要时刻准备重构。在工程化中，应尽可能通过常量来替代魔术字，方便代码阅读，尤其是多人协作时。一个规范的变量命名和统一的常量管理，能极大提升代码的可维护性、可读性和可扩展性。

2. 这是最简单的应用了。这里需要注意的是对象和数组的更新，如果需要修改，需要使用函数式更新，否则可能会出现数据残留的问题。

```typescript
const USER_FUNCTION_MAP = {
  prohibit: "prohibit",
};
const [state, setState] = useState(USER_FUNCTION_MAP.prohibit);

setState((prev) => ({
  ...prev,
  layoutCollapsed: "true",
}));
```

3. 当功能变得复杂时，可能会出现大量的 useState。此时最好的做法是使用自定义 hook 来统一管理。实践证明这是很有必要的，特别是当一个页面有多个功能，或一个功能需要多个变量时。自定义 hook 可以让逻辑更集中，便于阅读和维护。

```typescript
const useUserFunction = () => {
  const [modifyData, setModifyData] = useState<IGameUser>({} as IGameUser);
  const [forceChangeNameVisible, setForceChangeNameVisible] = useState(false);
  const [gameUserOrderVisible, setGameUserOrderVisible] = useState(false);
  const [gameUserDetailVisible, setGameUserDetailVisible] = useState(false);
  const [prohibitVisible, setProhibitVisible] = useState(false);
  const [emailModalVisible, setEmailModalVisible] = useState(false);
  const [userActionVisible, setUserActionVisible] = useState(false);
  const [gameUserChatVisible, setGameUserChatVisible] = useState(false);
  const [detailVisible, setDetailVisible] = useState(false);
  const [gameUuidList, setGameUuidList] = useState([] as string[]);
  const [gameUuid, setGameUuid] = useState("");

  const processFunction = (
    functionName: string,
    row: IGameUser,
    gameUuidList?: string[]
  ) => {
    if (functionName === USER_FUNCTION_MAP.document) {
      setGameUserDetailVisible(true);
      setGameUuid(String(row.GameUUID));
    }
    if (functionName === USER_FUNCTION_MAP.prohibit) {
      setGameUuid(String(row.GameUUID));
      setGameUuidList([String(row.GameUUID)]);
      setProhibitVisible(true);
    }
  };

  return {
    modalStates: {
      modifyData,
      forceChangeNameVisible,
      gameUserOrderVisible,
      gameUserDetailVisible,
      prohibitVisible,
      emailModalVisible,
      userActionVisible,
      detailVisible,
      gameUuidList,
      gameUuid,
      gameUserChatVisible,
    },
    setDetailVisible,
    setEmailModalVisible,
    setUserActionVisible,
    setGameUserDetailVisible,
    setGameUuidList,
    setProhibitVisible,
    setForceChangeNameVisible,
    setGameUserOrderVisible,
    setGameUuid,
    setModifyData,
    processFunction,
    setGameUserChatVisible,
  };
};
```

4. 这个例子更加直观，展示了如何将页面的多个功能（如上传、部署、版本管理）进行逻辑封装：

```typescript
const useVersion = () => {
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [deployModalVisible, setDeployModalVisible] = useState(false);
  const [versionId, setVersionId] = useState("");
  const [type, setType] = useState("");

  const showDeployModal = (uuid: string, type: string) => {
    setDeployModalVisible(true);
    setVersionId(uuid);
    setType(type);
  };

  return {
    modalStates: {
      uploadModalVisible,
      deployModalVisible,
      versionId,
      type,
    },
    setUploadModalVisible,
    setDeployModalVisible,
    showDeployModal,
  };
};
```

### useEffect

1. 这是第二个最常用的 hook。主要有两种使用场景：初始化和依赖变化时的处理。

```typescript
useEffect(() => {}, []); // 初始化
useEffect(() => {
  ref.current?.reload();
}, [menuType]); // 依赖变化
```

### useMemo

1. 这个 hook 使用相对较少，可能是因为项目逻辑不够复杂，没有明显的性能瓶颈。

```typescript
// 使用 useMemo 缓存计算结果
const sysStatus = useMemo(() => {
  if (!actionStore.gameServerStatus.sysStatus) return null;

  return SYS_STATUS_CONFIG.map(({ key, label }) => (
    <ProDescriptions.Item label={label} key={label}>
      {actionStore.gameServerStatus.sysStatus?.[key as keyof SysStatus]}
    </ProDescriptions.Item>
  ));
}, [actionStore.gameServerStatus.sysStatus]);
```

### useRef

1. 这个 hook 使用频率很高，主要用于获取 DOM 元素引用或保存可变值，特别是在处理表格和表单时：

```typescript
const channelRef = useRef<ProCoreActionType>();
<CommonProTable
  ghost={true}
  actionRef={channelRef}
  request={(params) => actionStore.getChannelList(params)}
  search={false}
  columns={useChannelColumns(
    access,
    (row) => {
      setModifyData(row);
      setModifyModalVisible(true);
    },
    async (id) => {
      await actionStore.deleteChannel(id);
      channelRef.current?.reload();
    }
  )}
  toolBarRender={() => [
    <Button
      key="create"
      icon={<PlusOutlined />}
      type="primary"
      onClick={() => {
        if (access.channelCreate) {
          setModifyModalVisible(true);
        } else {
          message.warning("权限不足");
        }
      }}
    >
      <FormattedMessage id="CREATE" />
    </Button>,
    <Button key="download" type="primary" onClick={downloadChannelExcel}>
      下载
    </Button>,
  ]}
/>;
```

## 实践总结

总的来说，React Hooks 的使用需要因地制宜。当功能开始变得复杂时，可以考虑重构为自定义 hook。但对于简单功能，没有必要过度封装。另外，TypeScript 的类型系统在现代前端开发中优势明显，配合 AI 辅助开发，可以极大提升开发效率和代码质量。

### 注意事项

#### 1. Hook 调用规则

- 只能在函数组件或自定义 Hook 的顶层调用 Hooks
- 不要在循环、条件或嵌套函数中调用 Hooks

```typescript
// ❌ 错误示例
if (condition) {
  const [count, setCount] = useState(0);
}

// ✅ 正确示例
const [count, setCount] = useState(0);
if (condition) {
  // 使用 count
}
```

#### 2. 依赖项管理

- useEffect 的依赖数组要完整
- 避免依赖项过多导致频繁更新

```typescript
// ❌ 错误示例 - 缺少依赖项
useEffect(() => {
  console.log(count);
}, []); // count 应该加入依赖数组

// ✅ 正确示例
useEffect(() => {
  console.log(count);
}, [count]);
```

#### 3. 闭包陷阱

- 注意异步操作中的状态获取
- 使用 useRef 或 useCallback 解决闭包问题

```typescript
// ❌ 可能出现问题的代码
const [count, setCount] = useState(0);
useEffect(() => {
  const timer = setInterval(() => {
    setCount(count + 1); // 这里的 count 是闭包中的旧值
  }, 1000);
  return () => clearInterval(timer);
}, []);

// ✅ 正确处理
useEffect(() => {
  const timer = setInterval(() => {
    setCount((prev) => prev + 1); // 使用函数式更新
  }, 1000);
  return () => clearInterval(timer);
}, []);
```
