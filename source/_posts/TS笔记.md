---
title: TypeScript 入门笔记
date: 2024-12-27 11:15:42
tags:
  - TypeScript
  - JavaScript
  - 前端开发
categories:
  - 编程语言
cover: https://johnsmithsren.github.io/renjmBlog.github.io/images/typescript.png
---

## TypeScript 简介

TypeScript 是 JavaScript 的超集，它添加了可选的静态类型和基于类的面向对象编程。TypeScript 由微软开发和维护，设计目标是开发大型应用。

### 常用点

1. 类型判断
2. as 断言
3. interface
4. record 用法
5. keyof typeof 
6. 类，class，type，enum 枚举



### 1. 基本类型
```typescript
// 布尔值
let isDone: boolean = false;

// 数字
let decimal: number = 6;
let hex: number = 0xf00d;

// 字符串
let color: string = "blue";
let sentence: string = `The color is ${color}`;

// 数组
let list: number[] = [1, 2, 3];
let list2: Array<number> = [1, 2, 3];

// 元组
let x: [string, number] = ["hello", 10];
```

### 2. 特殊类型
```typescript
// any - 任意类型
let notSure: any = 4;
notSure = "maybe a string";

// void - 没有任何类型
function warnUser(): void {
    console.log("This is a warning message");
}

// null 和 undefined
let u: undefined = undefined;
let n: null = null;
```

## 接口（Interfaces）

接口是 TypeScript 的一个核心概念，它定义了对象的结构：

```typescript
interface User {
    name: string;
    age: number;
    email?: string; // 可选属性
    readonly id: number; // 只读属性
}

let user: User = {
    name: "Tom",
    age: 25,
    id: 1
};
```

## 类（Classes）

TypeScript 提供了完整的面向对象编程特性：

```typescript
class Animal {
    private name: string;
    
    constructor(name: string) {
        this.name = name;
    }
    
    move(distance: number = 0) {
        console.log(`${this.name} moved ${distance}m.`);
    }
}

class Dog extends Animal {
    bark() {
        console.log('Woof! Woof!');
    }
}
```

## 泛型（Generics）

泛型允许我们编写可重用的代码：

```typescript
function identity<T>(arg: T): T {
    return arg;
}

let output = identity<string>("myString");
```

## Type 与 Interface 的比较

TypeScript 中的 `type` 和 `interface` 都可以用来定义类型，但它们有一些重要的区别：

### Interface

1. **扩展性**
```typescript
interface Animal {
    name: string
}

interface Bear extends Animal {
    honey: boolean
}
```

2. **自动合并**
```typescript
interface User {
    name: string
}

interface User {
    age: number
}

// 自动合并为：
// interface User {
//     name: string
//     age: number
// }
```

### Type

1. **类型别名**
```typescript
type Point = {
    x: number;
    y: number;
};

// 可以使用联合类型
type ID = number | string;

// 可以使用工具类型
type Partial<T> = {
    [P in keyof T]?: T[P];
};
```

2. **无法重复声明**
```typescript
type User = {
    name: string
}

// 错误：不能重复声明
type User = {
    age: number
}
```

### 主要区别

1. **扩展方式**
   - interface 使用 extends
   - type 使用 & 交叉类型

2. **合并声明**
   - interface 支持自动合并
   - type 不支持重复声明

3. **使用场景**
   - interface：定义对象结构
   - type：需要使用联合类型、交叉类型时

## Record 工具类型

Record 是 TypeScript 中一个非常实用的工具类型，用于创建一个对象类型，其属性键为 K，属性值为 T。

### 1. 基本用法

```typescript
// Record<Keys, Type>
type PageInfo = Record<string, string>;

// 等同于
type PageInfo = {
    [key: string]: string;
}

// 实际使用示例
const page: PageInfo = {
    title: "Home",
    description: "Welcome to our site"
};
```

### 2. 限定键名

```typescript
// 使用字面量类型限定键名
type Roles = "admin" | "user" | "guest";
type UserRoles = Record<Roles, boolean>;

// 使用示例
const userAccess: UserRoles = {
    admin: true,
    user: true,
    guest: false
};
```

### 3. 复杂类型

```typescript
// 配合接口使用
interface UserInfo {
    name: string;
    age: number;
}

type UsersDatabase = Record<string, UserInfo>;

// 使用示例
const users: UsersDatabase = {
    "user1": { name: "John", age: 30 },
    "user2": { name: "Jane", age: 25 }
};
```

### 4. 实践应用

1. **状态管理**
```typescript
type LoadingState = Record<string, boolean>;

const pageLoadingState: LoadingState = {
    userProfile: true,
    settings: false,
    notifications: true
};
```

2. **API 响应处理**
```typescript
type ApiResponse<T> = Record<string, {
    data: T;
    loading: boolean;
    error: Error | null;
}>;

interface User {
    id: number;
    name: string;
}

const apiState: ApiResponse<User> = {
    userProfile: {
        data: { id: 1, name: "John" },
        loading: false,
        error: null
    }
};
```

3. **配置对象**
```typescript
type Config = Record<string, {
    enabled: boolean;
    value: string | number;
}>;

const appConfig: Config = {
    theme: { enabled: true, value: "dark" },
    language: { enabled: true, value: "en" },
    notifications: { enabled: false, value: 0 }
};
```

## Omit 工具类型

Omit 是 TypeScript 中的一个实用工具类型，用于从一个类型中剔除指定的属性，创建一个新的类型。

### 1. 基本用法

```typescript
interface User {
    id: number;
    name: string;
    email: string;
    password: string;
}

// 创建一个不包含密码的用户类型
type PublicUser = Omit<User, 'password'>;

// 等同于
// type PublicUser = {
//     id: number;
//     name: string;
//     email: string;
// }
```

### 2. 剔除多个属性

```typescript
interface Product {
    id: number;
    name: string;
    price: number;
    stock: number;
    createTime: Date;
    updateTime: Date;
}

// 剔除多个属性
type ProductBasicInfo = Omit<Product, 'createTime' | 'updateTime'>;

const product: ProductBasicInfo = {
    id: 1,
    name: "iPhone",
    price: 999,
    stock: 100
};
```

### 3. 实践应用

1. **API 请求参数处理**
```typescript
interface UserCreateParams {
    name: string;
    email: string;
    password: string;
    id: number;        // 自动生成的
    createTime: Date;  // 自动生成的
}

// 创建用户时只需要这些字段
type UserCreate = Omit<UserCreateParams, 'id' | 'createTime'>;

function createUser(user: UserCreate) {
    // 处理用户创建
}
```

2. **表单数据处理**
```typescript
interface FormData {
    username: string;
    password: string;
    confirmPassword: string;
    token: string;     // 内部使用
}

// 提交到服务器时不需要 confirmPassword 和 token
type SubmitData = Omit<FormData, 'confirmPassword' | 'token'>;

function submitForm(data: FormData) {
    const submitData: SubmitData = {
        username: data.username,
        password: data.password
    };
    // 发送到服务器
}
```

3. **与其他工具类型组合**
```typescript
interface User {
    id: number;
    name: string;
    email: string;
    password: string;
}

// 组合使用 Omit 和 Partial
type UpdateUserParams = Partial<Omit<User, 'id'>>;

function updateUser(userId: number, data: UpdateUserParams) {
    // 可以部分更新用户信息，但不能更新 id
}
```

## 类型断言

类型断言用于告诉编译器"相信我，我知道自己在做什么"。

### 1. 基本语法
```typescript
// 尖括号语法
let someValue: any = "this is a string";
let strLength: number = (<string>someValue).length;

// as 语法（推荐，在 JSX 中只能使用这种）
let someValue: any = "this is a string";
let strLength: number = (someValue as string).length;
```

### 2. 常见用途

1. **断言具体类型**
```typescript
interface Cat {
    name: string;
    run(): void;
}

interface Fish {
    name: string;
    swim(): void;
}

function isFish(animal: Cat | Fish) {
    if (typeof (animal as Fish).swim === 'function') {
        return true;
    }
    return false;
}
```

2. **断言为 unknown**
```typescript
let foo = 'hello';
(foo as unknown as number).toFixed(2); // 不推荐这样做
```

3. **非空断言**
```typescript
function processName(name?: string) {
    // 使用 ! 断言 name 一定不为空
    console.log(name!.toUpperCase());
}
```

4. **使用枚举来表示固定选项**
   ```typescript
   enum Direction {
       Up = "UP",
       Down = "DOWN",
       Left = "LEFT",
       Right = "RIGHT"
   }
   ```

## 注意事项

1. **类型断言不是类型转换**
   - 断言只会影响 TypeScript 编译时的类型检查
   - 不会真的改变变量的类型

2. **断言限制**
   - 只能断言为更具体或更不具体的类型
   - 不能随意断言不相关的类型

3. **最佳实践**
   - 尽量避免使用类型断言
   - 优先使用类型声明和类型推断
   - 必要时才使用类型断言

## 实践建议

1. **始终启用严格模式**
   ```json
   {
     "compilerOptions": {
       "strict": true
     }
   }
   ```

2. **善用类型推断**
   - 不要过度注解类型
   - 让 TypeScript 自动推断简单类型

3. **接口优于类型别名**
   - 接口可以被扩展和实现
   - 错误信息更清晰

4. **使用枚举来表示固定选项**
   ```typescript
   enum Direction {
       Up = "UP",
       Down = "DOWN",
       Left = "LEFT",
       Right = "RIGHT"
   }
   ```

## 总结

TypeScript 通过添加类型系统，极大地提升了 JavaScript 开发的体验和代码质量。它不仅提供了更好的开发工具支持，还能帮助我们在开发阶段就发现潜在的问题。合理使用 interface、type、类型断言和工具类型（如 Record、Omit），可以让我们的代码更加健壮和可维护。对于大型项目来说，TypeScript 是一个非常值得考虑的选择。