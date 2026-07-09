# Build Workflow

这是一个 `build` 类型项目。

## 关注重点

- 先把目标和边界说清
- 再定义阶段和交付节点
- 研究材料服务于构建，不反客为主
- 关键取舍进入 `memory/decisions.jsonl`
- 结构设计、规格说明、原型结果优先成为 artifact

## 默认顺序

1. 明确目标和成功标准
2. 定义输入、约束、依赖
3. 建立第一批 artifact 目标
4. 拆阶段和里程碑
5. 逐轮推进并更新 compact state / working summary / handoff
6. 沉淀可复用教训和 procedures

## 本类型项目最常见的错误

- 还没定义边界就开始做
- 把研究材料堆成主线
- 有很多动作，但没有显式决策记录
- 用聊天代替 artifact
