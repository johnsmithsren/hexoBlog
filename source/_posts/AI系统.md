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

## 4. BOSS多阶段战斗实现

### 4.1 BOSS阶段管理
```typescript
// BOSS阶段枚举
enum BossPhase {
    PHASE_1,    // 第一阶段 (100% - 70%)
    PHASE_2,    // 第二阶段 (70% - 40%)
    PHASE_3     // 第三阶段 (40% - 0%)
}

// 扩展Blackboard以支持阶段管理
class BossBlackboard extends Blackboard {
    currentPhase: BossPhase = BossPhase.PHASE_1;
    maxHealth: number;
    minions: Enemy[] = [];
    lastSummonTime: number = 0;
    summonCooldown: number = 10; // 10秒召唤冷却

    constructor(boss: Enemy, target: Player) {
        super(boss, target);
        this.maxHealth = boss.health;
    }

    // 更新BOSS阶段
    updatePhase(): void {
        const healthPercent = (this.enemy.health / this.maxHealth) * 100;
        
        if (healthPercent <= 40) {
            this.currentPhase = BossPhase.PHASE_3;
        } else if (healthPercent <= 70) {
            this.currentPhase = BossPhase.PHASE_2;
        }
    }

    // 获取当前阶段的技能增强倍率
    getDamageMultiplier(): number {
        switch (this.currentPhase) {
            case BossPhase.PHASE_1: return 1.0;
            case BossPhase.PHASE_2: return 1.5;
            case BossPhase.PHASE_3: return 2.0;
            default: return 1.0;
        }
    }
}

// 检查阶段转换条件
class CheckPhaseTransition extends BTNode {
    private targetPhase: BossPhase;

    constructor(blackboard: BossBlackboard, targetPhase: BossPhase) {
        super(blackboard);
        this.targetPhase = targetPhase;
    }

    tick(): NodeStatus {
        return (this.blackboard as BossBlackboard).currentPhase === this.targetPhase
            ? NodeStatus.SUCCESS
            : NodeStatus.FAILURE;
    }
}

// 召唤小怪行为
class SummonMinions extends BTNode {
    private minionCount: number;
    private minionType: string;

    constructor(blackboard: BossBlackboard, count: number, type: string) {
        super(blackboard);
        this.minionCount = count;
        this.minionType = type;
    }

    tick(): NodeStatus {
        const bb = this.blackboard as BossBlackboard;
        const currentTime = performance.now() / 1000;

        // 检查召唤冷却
        if (currentTime - bb.lastSummonTime < bb.summonCooldown) {
            return NodeStatus.FAILURE;
        }

        // 清理已死亡的小怪
        bb.minions = bb.minions.filter(minion => minion.health > 0);

        // 如果小怪数量未达到上限，则召唤新的小怪
        if (bb.minions.length < this.minionCount) {
            const boss = bb.enemy;
            const angle = (Math.PI * 2) / this.minionCount;
            
            for (let i = bb.minions.length; i < this.minionCount; i++) {
                const x = boss.x + Math.cos(angle * i) * 100;
                const y = boss.y + Math.sin(angle * i) * 100;
                
                const minion = new Enemy(x, y);
                minion.health = 50;
                minion.damage = 10;
                minion.type = this.minionType;
                
                bb.minions.push(minion);
            }
            
            bb.lastSummonTime = currentTime;
            return NodeStatus.SUCCESS;
        }

        return NodeStatus.FAILURE;
    }
}

// 狂暴化行为（第三阶段特有）
class Enrage extends BTNode {
    tick(): NodeStatus {
        const bb = this.blackboard as BossBlackboard;
        const boss = bb.enemy;
        
        // 增加移动速度和攻击力
        boss.speed *= 1.5;
        boss.damage *= bb.getDamageMultiplier();
        
        return NodeStatus.SUCCESS;
    }
}

// 扩展BOSS行为树
class BossBehaviorTree extends EnemyBehaviorTree {
    constructor(boss: Enemy, target: Player) {
        super(boss, target);
    }

    protected buildTree(): BTNode {
        const bb = this.blackboard as BossBlackboard;
        const root = new Selector(bb);

        // 第一阶段行为
        const phase1Sequence = new Sequence(bb);
        phase1Sequence.addChild(new CheckPhaseTransition(bb, BossPhase.PHASE_1));
        phase1Sequence.addChild(new Selector(bb, [
            new Sequence(bb, [
                new CheckHealthCondition(bb, 90),
                new RangedAttack(bb, 15, 2)
            ]),
            new ChaseTarget(bb, 80)
        ]));

        // 第二阶段行为
        const phase2Sequence = new Sequence(bb);
        phase2Sequence.addChild(new CheckPhaseTransition(bb, BossPhase.PHASE_2));
        phase2Sequence.addChild(new Selector(bb, [
            new SummonMinions(bb, 3, "skeleton"),
            new Sequence(bb, [
                new CheckDistanceCondition(bb, 150),
                new RangedAttack(bb, 25, 1.5)
            ]),
            new ChaseTarget(bb, 100)
        ]));

        // 第三阶段行为
        const phase3Sequence = new Sequence(bb);
        phase3Sequence.addChild(new CheckPhaseTransition(bb, BossPhase.PHASE_3));
        phase3Sequence.addChild(new Enrage(bb));
        phase3Sequence.addChild(new Selector(bb, [
            new SummonMinions(bb, 5, "demon"),
            new Sequence(bb, [
                new CheckDistanceCondition(bb, 100),
                new RangedAttack(bb, 40, 1)
            ]),
            new ChaseTarget(bb, 120)
        ]));

        // 将所有阶段添加到根节点
        root.addChild(phase1Sequence);
        root.addChild(phase2Sequence);
        root.addChild(phase3Sequence);

        return root;
    }

    update(deltaTime: number): void {
        (this.blackboard as BossBlackboard).updatePhase();
        super.update(deltaTime);
    }
}
```

### 4.2 使用示例
```typescript
// 创建BOSS战斗
const boss = new Enemy(400, 300);
boss.health = 1000;  // BOSS有1000血量
boss.damage = 30;    // 基础伤害
boss.speed = 60;     // 基础速度

const player = new Player(100, 100);
const bossAI = new BossBehaviorTree(boss, player);

// 游戏循环
function gameLoop(deltaTime: number) {
    bossAI.update(deltaTime);
    
    // 更新小怪AI
    const bb = bossAI.blackboard as BossBlackboard;
    for (const minion of bb.minions) {
        // 可以给小怪也配置简单的行为树
        updateMinionBehavior(minion, player);
    }
}
```

这个多阶段BOSS战斗系统的特点：

1. **分阶段行为**
   - 第一阶段 (100%-70%): 基础攻击模式
   - 第二阶段 (70%-40%): 召唤骷髅小怪，伤害提升50%
   - 第三阶段 (40%-0%): 进入狂暴状态，召唤恶魔，伤害翻倍

2. **动态难度**
   - 血量越低，攻击越强
   - 不同阶段召唤不同类型和数量的小怪
   - 最后阶段会进入狂暴状态

3. **小怪管理**
   - 自动清理已死亡的小怪
   - 控制召唤冷却时间
   - 小怪围绕BOSS呈环形分布

4. **可扩展性**
   - 易于添加新的阶段
   - 可以为每个阶段定制独特的技能组合
   - 可以调整各种参数来平衡难度