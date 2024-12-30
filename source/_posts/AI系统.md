---
layout: post
title: AI系统：行为树vs状态机
date: 2024-12-30 17:15:31
tags: [游戏开发, AI]
---

# 游戏AI系统
## 1. 行为树核心系统

### 1.1 基础节点类型
```typescript
// 节点状态枚举
enum NodeStatus {
    SUCCESS,    // 执行成功
    FAILURE,    // 执行失败
    RUNNING     // 正在执行
}

// 抽象节点基类
abstract class BTNode {
    protected blackboard: Blackboard;  // 共享数据

    constructor(blackboard: Blackboard) {
        this.blackboard = blackboard;
    }

    abstract tick(): NodeStatus;
}

// 组合节点基类
abstract class CompositeNode extends BTNode {
    protected children: BTNode[] = [];

    addChild(child: BTNode): void {
        this.children.push(child);
    }
}

// 装饰器节点基类
abstract class DecoratorNode extends BTNode {
    protected child: BTNode;

    constructor(blackboard: Blackboard, child: BTNode) {
        super(blackboard);
        this.child = child;
    }
}
```

### 1.2 组合节点实现
```typescript
// 选择节点：执行直到一个子节点成功
class Selector extends CompositeNode {
    tick(): NodeStatus {
        for (const child of this.children) {
            const status = child.tick();
            if (status !== NodeStatus.FAILURE) {
                return status;
            }
        }
        return NodeStatus.FAILURE;
    }
}

// 序列节点：执行直到所有子节点成功
class Sequence extends CompositeNode {
    tick(): NodeStatus {
        for (const child of this.children) {
            const status = child.tick();
            if (status !== NodeStatus.SUCCESS) {
                return status;
            }
        }
        return NodeStatus.SUCCESS;
    }
}

// 并行节点：同时执行所有子节点
class Parallel extends CompositeNode {
    private requiredSuccesses: number;

    constructor(blackboard: Blackboard, requiredSuccesses: number) {
        super(blackboard);
        this.requiredSuccesses = requiredSuccesses;
    }

    tick(): NodeStatus {
        let successes = 0;
        let failures = 0;

        for (const child of this.children) {
            const status = child.tick();
            
            if (status === NodeStatus.SUCCESS) {
                successes++;
            } else if (status === NodeStatus.FAILURE) {
                failures++;
            }
        }

        if (successes >= this.requiredSuccesses) {
            return NodeStatus.SUCCESS;
        }
        if (failures > this.children.length - this.requiredSuccesses) {
            return NodeStatus.FAILURE;
        }
        return NodeStatus.RUNNING;
    }
}
```

### 1.3 装饰器节点实现
```typescript
// 取反装饰器
class Inverter extends DecoratorNode {
    tick(): NodeStatus {
        const status = this.child.tick();
        if (status === NodeStatus.SUCCESS) {
            return NodeStatus.FAILURE;
        }
        if (status === NodeStatus.FAILURE) {
            return NodeStatus.SUCCESS;
        }
        return status;
    }
}

// 重复执行装饰器
class Repeater extends DecoratorNode {
    private maxRepeats: number;
    private currentRepeats: number = 0;

    constructor(blackboard: Blackboard, child: BTNode, maxRepeats: number) {
        super(blackboard, child);
        this.maxRepeats = maxRepeats;
    }

    tick(): NodeStatus {
        if (this.currentRepeats >= this.maxRepeats) {
            return NodeStatus.SUCCESS;
        }

        const status = this.child.tick();
        if (status === NodeStatus.SUCCESS) {
            this.currentRepeats++;
        }
        return NodeStatus.RUNNING;
    }
}

// 条件装饰器
class ConditionalDecorator extends DecoratorNode {
    private condition: () => boolean;

    constructor(blackboard: Blackboard, child: BTNode, condition: () => boolean) {
        super(blackboard, child);
        this.condition = condition;
    }

    tick(): NodeStatus {
        if (!this.condition()) {
            return NodeStatus.FAILURE;
        }
        return this.child.tick();
    }
}
```

## 2. 具体行为节点实现

### 2.1 条件检查节点
```typescript
// 检查生命值
class CheckHealthCondition extends BTNode {
    private threshold: number;

    constructor(blackboard: Blackboard, threshold: number) {
        super(blackboard);
        this.threshold = threshold;
    }

    tick(): NodeStatus {
        return this.blackboard.enemy.health <= this.threshold 
            ? NodeStatus.SUCCESS 
            : NodeStatus.FAILURE;
    }
}

// 检查距离
class CheckDistanceCondition extends BTNode {
    private range: number;

    constructor(blackboard: Blackboard, range: number) {
        super(blackboard);
        this.range = range;
    }

    tick(): NodeStatus {
        const distance = this.blackboard.getDistanceToTarget();
        return distance <= this.range 
            ? NodeStatus.SUCCESS 
            : NodeStatus.FAILURE;
    }
}

// 检查掩体
class CheckCoverAvailable extends BTNode {
    tick(): NodeStatus {
        const cover = this.blackboard.findNearestCover();
        return cover ? NodeStatus.SUCCESS : NodeStatus.FAILURE;
    }
}
```

### 2.2 行为节点
```typescript
// 追击目标
class ChaseTarget extends BTNode {
    private speed: number;

    constructor(blackboard: Blackboard, speed: number) {
        super(blackboard);
        this.speed = speed;
    }

    tick(): NodeStatus {
        const target = this.blackboard.target;
        const enemy = this.blackboard.enemy;
        
        // 计算方向
        const dx = target.x - enemy.x;
        const dy = target.y - enemy.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 1) {
            return NodeStatus.SUCCESS;
        }

        // 移动
        const vx = (dx / distance) * this.speed;
        const vy = (dy / distance) * this.speed;
        
        enemy.x += vx * this.blackboard.deltaTime;
        enemy.y += vy * this.blackboard.deltaTime;
        
        return NodeStatus.RUNNING;
    }
}

// 远程攻击
class RangedAttack extends BTNode {
    private damage: number;
    private cooldown: number;
    private lastAttackTime: number = 0;

    constructor(blackboard: Blackboard, damage: number, cooldown: number) {
        super(blackboard);
        this.damage = damage;
        this.cooldown = cooldown;
    }

    tick(): NodeStatus {
        const currentTime = performance.now() / 1000;
        if (currentTime - this.lastAttackTime < this.cooldown) {
            return NodeStatus.RUNNING;
        }

        // 创建子弹
        const bullet = this.blackboard.createBullet(this.damage);
        this.lastAttackTime = currentTime;
        
        return NodeStatus.SUCCESS;
    }
}

// 寻找掩体
class SeekCover extends BTNode {
    tick(): NodeStatus {
        const cover = this.blackboard.findNearestCover();
        if (!cover) {
            return NodeStatus.FAILURE;
        }

        const enemy = this.blackboard.enemy;
        const dx = cover.x - enemy.x;
        const dy = cover.y - enemy.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 1) {
            return NodeStatus.SUCCESS;
        }

        // 移动到掩体
        enemy.x += (dx / distance) * enemy.speed * this.blackboard.deltaTime;
        enemy.y += (dy / distance) * enemy.speed * this.blackboard.deltaTime;

        return NodeStatus.RUNNING;
    }
}
```

### 2.3 行为树构建
```typescript
class EnemyBehaviorTree {
    private root: BTNode;
    private blackboard: Blackboard;

    constructor(enemy: Enemy, target: Player) {
        this.blackboard = new Blackboard(enemy, target);
        this.root = this.buildTree();
    }

    private buildTree(): BTNode {
        // 创建选择器作为根节点
        const root = new Selector(this.blackboard);

        // 撤退行为（低生命值时）
        const retreatSequence = new Sequence(this.blackboard);
        retreatSequence.addChild(new CheckHealthCondition(this.blackboard, 30));
        retreatSequence.addChild(new CheckCoverAvailable(this.blackboard));
        retreatSequence.addChild(new SeekCover(this.blackboard));

        // 远程攻击行为
        const attackSequence = new Sequence(this.blackboard);
        attackSequence.addChild(new CheckDistanceCondition(this.blackboard, 200));
        attackSequence.addChild(new RangedAttack(this.blackboard, 10, 1));

        // 追击行为
        const chaseSequence = new Sequence(this.blackboard);
        chaseSequence.addChild(new Inverter(this.blackboard, 
            new CheckDistanceCondition(this.blackboard, 200)));
        chaseSequence.addChild(new ChaseTarget(this.blackboard, 100));

        // 添加到根节点
        root.addChild(retreatSequence);
        root.addChild(attackSequence);
        root.addChild(chaseSequence);

        return root;
    }

    update(deltaTime: number): void {
        this.blackboard.deltaTime = deltaTime;
        this.root.tick();
    }
}

// 数据共享黑板
class Blackboard {
    enemy: Enemy;
    target: Player;
    deltaTime: number = 0;

    constructor(enemy: Enemy, target: Player) {
        this.enemy = enemy;
        this.target = target;
    }

    getDistanceToTarget(): number {
        const dx = this.target.x - this.enemy.x;
        const dy = this.target.y - this.enemy.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    findNearestCover(): Cover | null {
        // 实现查找最近掩体的逻辑
        return null;
    }

    createBullet(damage: number): Bullet {
        // 实现创建子弹的逻辑
        return new Bullet(this.enemy.x, this.enemy.y, damage);
    }
}
```

## 3. 使用示例

```typescript
// 创建并使用行为树
const enemy = new Enemy(100, 100);
const player = new Player(400, 300);
const behaviorTree = new EnemyBehaviorTree(enemy, player);

// 在游戏循环中更新
function gameLoop(deltaTime: number) {
    behaviorTree.update(deltaTime);
}
```