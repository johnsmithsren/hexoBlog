---
title: react感想
date: 2022-04-23 13:31:48
---

关于react的感想 .就我现在的做的这个对内使用的管理平台的内容来说，单纯的使用 usestate, useeffect,再辅助以少量的useref也就差不多了。

用的antd的组件，只需要针对部分做样式简单的调整 .比较关键的问题，就是组件的状态传递，也就是增加组件的复用程度，对于一些组件进行拆分，重组。

以达到复用的情况时候，就碰到了状态传递的问题，对我现在这个简单的项目而言，性能方面的考虑暂时涉及不到。

最近碰到的问题主要就是关于状态传递的，父组件如何传递状态给子组件，子组件中再嵌套子组件的情况下，内容传递的一致性，同时还要考虑代码的简洁。

我发现，useref这些对于一层父子组件来说，还是比较直观，可靠的。

```javascript
import React,
  {
  forwardRef,
  useImperativeHandle,
  useState 
}
from "react";
import {
  Button,
  DatePicker,
  Divider 
}
from "antd";
import {
  useObserver 
}
from "mobx-react";
import ComponentStore from "store/ComponentStore";
const {
  RangePicker 
}
= DatePicker;
import moment from "moment";
const _ = require("lodash");
export const RangePickCondition = forwardRef((props,
  ref) => {
  const [startTime,
  setStartTime] = useState();
const [endTime,
  setEndTime] = useState();
const [regTime,
  setRegTime] = useState();
const type = _.get(props,
  "type");
useImperativeHandle(ref,
  () => ({
  startTime: _.toNumber(moment(startTime).format("X")),
  endTime: _.toNumber(moment(endTime).format("X")),
  regTime: _.toNumber(moment(regTime).format("X")),
  }
));
return useObserver(() => ( <> {
  type == "needReg" ? ( <div> <Button type="primary">注册时间</Button> <Divider type="vertical" /> <DatePicker showTime format="YYYY-MM-DD HH:mm:ss" onChange={
  (dates: any,
  dateStrings: any[]) => {
  setRegTime(dates.valueOf());
ComponentStore.rangePickRegtime = _.toNumber( moment(regTime).format("X") );
}

}
/> </div> ) : ( [] )
}
<Button type="primary">时间范围</Button> <Divider type="vertical" /> <RangePicker format="YYYY-MM-DD HH:mm:ss" placeholder={
  ["开始时间",
  "结束时间"]
}
onChange={
  (dates: any,
  dateStrings: any[]) => {
  setStartTime(dates[].valueOf());
setEndTime(dates[].valueOf());
ComponentStore.rangePickStartTime = _.toNumber( moment(dates[].valueOf()).format("X") );
ComponentStore.rangePickEndTime = _.toNumber( moment(dates[].valueOf()).format("X") );
}

}
/> </> ));
}
);
export default RangePickCondition;
但是我尝试在这个子组件中再加上一个小的子组件时候，用ref就会发现初始值出现延迟的问题，连续点击按钮两次，才能够获得正确数值，第一次只会获取这个useref定义的初始默认值。

期间考虑了使用usecontext，然而效果依然不佳 最终想了想，这种传值还是只限于两层的父子组件中可以尝试，如果涉及多层，我还是决定引入mobx来作为统一的存储。

这样就能够自如的进行组件的组合拼接，而不再去通过props，ref这些去做深层次的数值传递。

因为看到大家一般使用也是作为控件的简单操作会引入。
