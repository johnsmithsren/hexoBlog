---
title: React Hook Form 在复杂表单场景下的应用实践
date: 2026-01-04 
tags: 
  - React
  - Form
  - react-hook-form
  - 前端开发
categories:
  - 前端技术
---

## 前言

在平台级应用开发中，表单组件是最常见的功能需求之一。虽然对于简单的表单需求，使用常规的表单组件已经足够，但在面对复杂的表单操作场景时，比如：

- 大量的表单操作
- 复杂的表单逻辑
- 表单的复用（如同一个 item 的创建和编辑）
- 多个页签中需要编辑相同的 item

这些场景就需要我们考虑更优雅的解决方案。

## 问题分析

当我们需要把表单的创建和编辑功能抽离出来，方便在不同地方独立引用时，会产生一个关键问题：**如何优雅地获取这些独立组件中的表单数据？**

## 解决方案：react-hook-form + yup

推荐使用 `react-hook-form` 配合 `yup` 进行参数校验，这个组合提供了强大的表单管理能力。

### 基本用法

```typescript
// 定义复杂表单数据的 TypeScript 接口
interface ComplexFormData {
  name: string;
  value: number;
  email: string;
  startDate: Date;
  endDate: Date;
  status: 'active' | 'inactive' | 'pending';
  tags: string[];
  config: {
    theme: string;
    timeout: number;
    retryCount: number;
  };
  permissions: Array<{
    id: string;
    name: string;
    actions: ('read' | 'write' | 'delete')[];
    resources: Array<{
      type: string;
      path: string;
      metadata?: {
        description?: string;
        priority?: number;
      };
    }>;
  }>;
  enableNotifications: boolean;
  notificationConfig?: {
    email: string;
    frequency: 'immediate' | 'daily' | 'weekly';
    channels: ('email' | 'sms' | 'push')[];
  } | null;
  password: string;
  confirmPassword: string;
  // 新增的可选字段
  description?: string;
  priority?: number;
  optionalTags?: string[];
  score?: number;
  trimmedName?: string;
  publishDate?: Date;
}
```

```typescript
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// 定义复杂的校验规则
const validationSchema = yup.object({
  // 基础字符串校验
  name: yup.string()
    .required('名称不能为空')
    .min(2, '名称至少2个字符')
    .max(50, '名称不能超过50个字符')
    .matches(/^[a-zA-Z\u4e00-\u9fa5]+$/, '名称只能包含中文和英文字母'),
  
  // 数值校验
  value: yup.number()
    .required('值不能为空')
    .min(0, '值不能小于0')
    .max(100, '值不能大于100')
    .integer('值必须为整数'),
  
  // 邮箱校验
  email: yup.string()
    .email('邮箱格式不正确')
    .required('邮箱不能为空'),
  
  // 日期校验
  startDate: yup.date()
    .required('开始日期不能为空')
    .min(new Date(), '开始日期不能早于今天'),
  
  endDate: yup.date()
    .required('结束日期不能为空')
    .min(yup.ref('startDate'), '结束日期不能早于开始日期'),
  
  // 枚举值校验
  status: yup.string()
    .oneOf(['active', 'inactive', 'pending'], '状态值无效')
    .required('状态不能为空'),
  
  // 字符串数组校验
  tags: yup.array()
    .of(yup.string().min(1, '标签不能为空').max(20, '标签长度不能超过20'))
    .min(1, '至少需要一个标签')
    .max(5, '标签数量不能超过5个')
    .required('标签不能为空'),
  
  // 对象校验
  config: yup.object({
    theme: yup.string().required('主题不能为空'),
    timeout: yup.number().min(1000, '超时时间至少1000ms').required('超时时间不能为空'),
    retryCount: yup.number().min(0).max(5).integer().required('重试次数不能为空'),
  }).required('配置对象不能为空'),
  
  // 对象数组嵌套校验
  permissions: yup.array()
    .of(
      yup.object({
        id: yup.string().required('权限ID不能为空'),
        name: yup.string()
          .required('权限名称不能为空')
          .min(2, '权限名称至少2个字符'),
        actions: yup.array()
          .of(yup.string().oneOf(['read', 'write', 'delete'], '操作类型无效'))
          .min(1, '至少需要一个操作权限')
          .required('操作权限不能为空'),
        resources: yup.array()
          .of(
            yup.object({
              type: yup.string().required('资源类型不能为空'),
              path: yup.string()
                .required('资源路径不能为空')
                .matches(/^\/[a-zA-Z0-9\/\-_]*$/, '资源路径格式不正确'),
              metadata: yup.object({
                description: yup.string().max(200, '描述不能超过200字符'),
                priority: yup.number().min(1).max(10).integer(),
              }).nullable(),
            })
          )
          .min(1, '至少需要一个资源')
          .required('资源列表不能为空'),
      })
    )
    .min(1, '至少需要一个权限配置')
    .required('权限配置不能为空'),
  
  // 条件校验
  enableNotifications: yup.boolean(),
  notificationConfig: yup.object().when('enableNotifications', {
    is: true,
    then: (schema) => schema.shape({
      email: yup.string().email('邮箱格式不正确').required('通知邮箱不能为空'),
      frequency: yup.string()
        .oneOf(['immediate', 'daily', 'weekly'], '通知频率无效')
        .required('通知频率不能为空'),
      channels: yup.array()
        .of(yup.string().oneOf(['email', 'sms', 'push']))
        .min(1, '至少选择一个通知渠道')
        .required('通知渠道不能为空'),
    }),
    otherwise: (schema) => schema.nullable(),
  }),
  
  // 自定义校验
  password: yup.string()
    .required('密码不能为空')
    .min(8, '密码至少8位')
    .test('complexity', '密码必须包含大小写字母、数字和特殊字符', (value) => {
      if (!value) return false;
      const hasUpper = /[A-Z]/.test(value);
      const hasLower = /[a-z]/.test(value);
      const hasNumber = /[0-9]/.test(value);
      const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);
      return hasUpper && hasLower && hasNumber && hasSpecial;
    }),
  
  confirmPassword: yup.string()
    .required('确认密码不能为空')
    .oneOf([yup.ref('password')], '两次输入的密码不一致'),
  
  // 可选字段校验 - 使用 optional() 和 transform()
  description: yup.string()
    .optional()
    .transform(val => val || undefined)
    .max(500, '描述不能超过500字符'),
  
  // 可选数字字段，空值转换为 undefined
  priority: yup.number()
    .optional()
    .transform((val, originalVal) => originalVal === '' ? undefined : val)
    .min(1, '优先级不能小于1')
    .max(10, '优先级不能大于10'),
  
  // 可选数组，空数组转换为 undefined
  optionalTags: yup.array()
    .optional()
    .transform(val => val && val.length > 0 ? val : undefined)
    .of(yup.string().min(1, '标签不能为空')),
  
  // 字符串转数字，并处理空值
  score: yup.number()
    .transform((val, originalVal) => {
      // 如果原始值是空字符串或 null/undefined，返回 undefined
      if (originalVal === '' || originalVal == null) return undefined;
      // 尝试转换为数字
      const parsed = Number(originalVal);
      return isNaN(parsed) ? undefined : parsed;
    })
    .optional()
    .min(0, '分数不能小于0')
    .max(100, '分数不能大于100'),
  
  // 去除空白字符的字符串校验
  trimmedName: yup.string()
    .transform(val => val?.trim())
    .optional()
    .min(2, '名称至少2个字符'),
  
  // 处理日期字符串转换
  publishDate: yup.date()
    .transform((val, originalVal) => {
      // 如果是空字符串，返回 undefined
      if (originalVal === '') return undefined;
      // 如果已经是 Date 对象，直接返回
      if (val instanceof Date) return val;
      // 尝试解析日期字符串
      const parsed = new Date(originalVal);
      return isNaN(parsed.getTime()) ? undefined : parsed;
    })
    .optional()
    .min(new Date('2020-01-01'), '发布日期不能早于2020年'),
});

export const FeatureFlagsDrawer: React.FC<IProps> = observer(
  ({ isOpen, onCancel, startDate, endDate, onSubmit }) => {
    const {
      items: { selected },
      buildFeatureFlags,
      filteredFeatureFlags,
    } = useStore();

    // 设置默认值（对应复杂的数据结构）
    const defaultValues: Partial<ComplexFormData> = {
      name: '',
      value: 0,
      email: '',
      startDate: undefined,
      endDate: undefined,
      status: 'pending',
      tags: [],
      config: {
        theme: 'default',
        timeout: 5000,
        retryCount: 3,
      },
      permissions: [{
        id: '',
        name: '',
        actions: ['read'],
        resources: [{
          type: 'api',
          path: '/',
          metadata: {
            description: '',
            priority: 5,
          },
        }],
      }],
      enableNotifications: false,
      notificationConfig: null,
      password: '',
      confirmPassword: '',
    };

    // 初始化表单
    const methods = useForm<ComplexFormData>({
      mode: 'onTouched',
      resolver: yupResolver(validationSchema),
      defaultValues,
    });

    const { reset, setValue, handleSubmit: formSubmit, control, watch } = methods;
    
    // ... 其他逻辑
  }
);
```

### 复杂校验场景说明

上面的校验示例涵盖了多种常见的复杂校验场景：

#### 1. 字符串数组校验
```typescript
tags: yup.array()
  .of(yup.string().min(1).max(20))
  .min(1, '至少需要一个标签')
  .max(5, '标签数量不能超过5个')
```

#### 2. 嵌套对象数组校验
```typescript
permissions: yup.array()
  .of(
    yup.object({
      resources: yup.array()
        .of(yup.object({
          metadata: yup.object({
            description: yup.string().max(200),
            priority: yup.number().min(1).max(10),
          }).nullable(),
        }))
    })
  )
```

#### 3. 条件校验（when）
```typescript
notificationConfig: yup.object().when('enableNotifications', {
  is: true,
  then: (schema) => schema.shape({...}),
  otherwise: (schema) => schema.nullable(),
})
```

#### 4. 跨字段引用校验
```typescript
endDate: yup.date()
  .min(yup.ref('startDate'), '结束日期不能早于开始日期'),
confirmPassword: yup.string()
  .oneOf([yup.ref('password')], '两次输入的密码不一致')
```

#### 5. 自定义校验函数
```typescript
password: yup.string()
  .test('complexity', '密码必须包含大小写字母、数字和特殊字符', (value) => {
    // 自定义校验逻辑
    return hasUpper && hasLower && hasNumber && hasSpecial;
  })
```

#### 6. 可选字段与值转换
```typescript
// 基础可选字段
description: yup.string()
  .optional()
  .transform(val => val || undefined)
  .max(500, '描述不能超过500字符')

// 数字字段空值处理
priority: yup.number()
  .optional()
  .transform((val, originalVal) => originalVal === '' ? undefined : val)
  .min(1).max(10)

// 字符串去空格处理
trimmedName: yup.string()
  .transform(val => val?.trim())
  .optional()
  .min(2, '名称至少2个字符')

// 日期字符串转换
publishDate: yup.date()
  .transform((val, originalVal) => {
    if (originalVal === '') return undefined;
    const parsed = new Date(originalVal);
    return isNaN(parsed.getTime()) ? undefined : parsed;
  })
  .optional()
```

**transform 方法的常见用法：**
- 处理空字符串转 undefined
- 字符串去除首尾空格
- 数据类型转换
- 格式化处理
- 空数组/空对象的处理
```

### 嵌入式表单组件

对于需要嵌入到其他组件中的表单，可以使用 `useFormContext` 来获取父级表单的控制权：

```typescript
import { useFormContext, Controller } from 'react-hook-form';

const FormSelectComponent = ({ fieldName, label, children, onChange, extra }) => {
  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <Form.Item label={label}>
      <>
        <Flex>
          <Controller
            name={fieldName}
            control={control}
            render={({ field }) => (
              <Select
                value={field.value || undefined}
                showSearch={!disableSearch}
                showAction={['click', 'focus']}
                key={fieldName}
                onChange={(value: unknown | undefined) => {
                  field.onChange(setCorrectValue(value));
                  if (onChange) onChange(value as T);
                }}
                filterOption={searchLabel && !rest.filterOption ? filterOption : rest.filterOption}
              >
                {children}
              </Select>
            )}
          />
         
        </Flex>
      </>
    </Form.Item>
  );
};
```

## 实时监听表单值变化

`react-hook-form` 的一个强大特性是能够实时监听表单字段的变化：

```typescript
import { useFormContext } from 'react-hook-form';

const FormComponent = ({ fieldName }) => {
  const { setValue, trigger, watch } = useFormContext();

  // 监听特定字段的值变化
  const selectedEventId = watch(fieldName);

  useEffect(() => {
    // 当 selectedEventId 变化时执行相应的逻辑
    console.log('字段值发生变化：', selectedEventId);
  }, [selectedEventId]);

  return (
    // 组件渲染内容
  );
};
```

这种方式让我们能够：

- 实时响应表单值的变动
- 实现表单字段间的联动
- 优化用户体验

## 核心 API 介绍

### Controller

`Controller` 是 react-hook-form 提供的受控组件包装器，用于集成第三方 UI 组件库：

- **作用**：将非受控组件转换为受控组件
- **使用场景**：集成 Ant Design、Material-UI 等组件库
- **优势**：提供统一的表单控制接口

### useFormContext

`useFormContext` 用于在组件树中共享表单状态：

- **作用**：在子组件中访问父级表单的方法和状态
- **使用场景**：复杂表单的组件化拆分
- **优势**：避免 props 层层传递，简化组件通信

## Controller vs useFormContext 使用场景详解

虽然 `Controller` 不是在所有情况下都必需的，但了解何时使用哪种方式可以让你的代码更优雅和高效。

### 何时不需要 Controller

当你的表单组件已经支持 `value` 和 `onChange` props（即已经是受控组件）时，你可以直接使用 `useFormContext`：

```typescript
import { useFormContext } from 'react-hook-form';

const SimpleInputComponent = ({ fieldName, label }) => {
  const { 
    register, 
    formState: { errors },
    setValue,
    watch
  } = useFormContext();

  // 方式1: 使用 register（推荐用于原生 HTML 元素）
  return (
    <div>
      <label>{label}</label>
      <input {...register(fieldName)} />
      {errors[fieldName] && <span>{errors[fieldName].message}</span>}
    </div>
  );
};

// 方式2: 手动控制值和变更
const ManualControlComponent = ({ fieldName, label }) => {
  const { setValue, watch, formState: { errors } } = useFormContext();
  
  const value = watch(fieldName);

  return (
    <div>
      <label>{label}</label>
      <input 
        value={value || ''} 
        onChange={(e) => setValue(fieldName, e.target.value)}
      />
      {errors[fieldName] && <span>{errors[fieldName].message}</span>}
    </div>
  );
};
```

### 何时必须使用 Controller

`Controller` 主要用于以下场景：

#### 1. 第三方组件库（如 Ant Design）

```typescript
import { Controller, useFormContext } from 'react-hook-form';
import { Select, DatePicker } from 'antd';

// 需要 Controller，因为 Ant Design 组件的 API 与原生不同
const AntSelectComponent = ({ fieldName, options }) => {
  const { control, formState: { errors } } = useFormContext();

  return (
    <Controller
      name={fieldName}
      control={control}
      render={({ field }) => (
        <Select
          {...field}
          options={options}
          onChange={(value) => field.onChange(value)} // Ant Design 的 onChange 参数不同
        />
      )}
    />
  );
};
```

#### 2. 需要自定义值转换的组件

```typescript
const NumberInputComponent = ({ fieldName }) => {
  const { control } = useFormContext();

  return (
    <Controller
      name={fieldName}
      control={control}
      render={({ field }) => (
        <input
          type="number"
          value={field.value || ''}
          onChange={(e) => {
            // 自定义转换逻辑：字符串转数字
            const numValue = e.target.value ? Number(e.target.value) : undefined;
            field.onChange(numValue);
          }}
        />
      )}
    />
  );
};
```

### 实际项目示例：DatePickerInput 组件

下面是一个完整的日期选择器组件示例，展示了如何正确使用 Controller：

```typescript
import { DatePicker as dp, Form } from 'antd';
import React from 'react';
import { Controller, useFormContext } from 'react-hook-form';
import dateFnsGenerateConfig from 'rc-picker/es/generate/dateFns';

const DatePickerInput: React.FC = ({
  label, fieldName, tooltip, ...rest
}) => {
  const {
    control, 
    formState: { errors }, 
    setValue, 
    watch,
  } = useFormContext();

  const selectedDate = watch(fieldName);

  const handleDateChange = (date: string | undefined) => {
    setValue(fieldName, date);
  };

  return (
    <Form.Item label={label} tooltip={tooltip}>
      <Controller
        name={fieldName}
        control={control}
        render={({ field }) => (
          <DatePicker
            {...rest}
            {...field}
            value={selectedDate}
            onChange={handleDateChange}
          />
        )}
      />
    </Form.Item>
  );
};

export default DatePickerInput;
```

**这个示例的关键要点：**

1. **类型安全**：使用 TypeScript 接口定义严格的 props 类型
2. **错误处理**：集成了嵌套错误信息的显示逻辑
3. **灵活性**：支持传递额外的 props 到底层组件
4. **状态管理**：同时使用 `Controller` 和 `watch/setValue` 来处理复杂的日期逻辑
5. **样式定制**：支持自定义表单项样式

### 最佳实践建议

根据你的使用场景选择最合适的方式：

#### 1. 原生 HTML 元素 → 使用 register

```typescript
const NativeInputs = () => {
  const { register, formState: { errors } } = useFormContext();

  return (
    <>
      <input {...register('name')} placeholder="姓名" />
      <input {...register('email')} type="email" placeholder="邮箱" />
      <textarea {...register('description')} placeholder="描述" />
    </>
  );
};
```

#### 2. 第三方组件库 → 使用 Controller

```typescript
const ThirdPartyComponents = () => {
  const { control } = useFormContext();

  return (
    <>
      <Controller
        name="status"
        control={control}
        render={({ field }) => (
          <Select {...field} options={statusOptions} />
        )}
      />
      
      <Controller
        name="date"
        control={control}
        render={({ field }) => (
          <DatePicker {...field} />
        )}
      />
    </>
  );
};
```

#### 3. 需要实时监听或复杂逻辑 → 手动控制

```typescript
const ComplexComponent = ({ fieldName }) => {
  const { setValue, watch, trigger } = useFormContext();
  
  const value = watch(fieldName);
  
  const handleChange = async (newValue) => {
    setValue(fieldName, newValue);
    // 触发验证
    await trigger(fieldName);
    // 其他业务逻辑
  };

  return (
    <CustomComponent 
      value={value} 
      onChange={handleChange}
    />
  );
};
```

### 错误处理工具函数

在复杂表单中，处理嵌套字段的错误信息是常见需求。可以创建一个工具函数：

```typescript
// utils/FormHelpers.ts
export const errorMessageNested = (errors: any, fieldName: string) => {
  // 处理嵌套字段路径，如 'user.profile.name'
  const fieldParts = fieldName.split('.');
  let error = errors;
  
  for (const part of fieldParts) {
    if (error && error[part]) {
      error = error[part];
    } else {
      return null;
    }
  }
  
  return error?.message ? (
    <span style={{ color: 'red', fontSize: '12px' }}>
      {error.message}
    </span>
  ) : null;
};
```

## 组件封装模式

### 1. FormProvider 模式

```typescript
// 父组件
const ParentForm = () => {
  const methods = useForm();
  
  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        <DatePickerInput fieldName="startDate" label="开始日期" />
        <DatePickerInput fieldName="endDate" label="结束日期" />
        <SubmitButton />
      </form>
    </FormProvider>
  );
};
```

### 2. 组件组合模式

```typescript
// 复杂表单的组合
const ComplexForm = () => {
  return (
    <FormProvider {...methods}>
      <PersonalInfoSection />
      <AddressSection />
      <PermissionsSection />
      <NotificationSettings />
    </FormProvider>
  );
};
```

## 总结

**选择指南：**

- **FormProvider** 负责共享表单状态和方法
- **Controller** 只是一个适配器，用于处理与 react-hook-form 期望不同的组件 API
- 对于已经符合标准受控组件模式的组件，直接使用 `useFormContext` 就足够了
