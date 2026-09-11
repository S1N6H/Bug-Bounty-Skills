---
name: asm-performance
description: >
  此技能适用于用户询问关于 "asm-performance"、"审计代码生成问题（边界检查、寄存器溢出、依赖链、未向量化、内存访问）" 等内容。汇编性能优化工作流程：收集编译器生成的汇编代码，审计代码生成问题（边界检查、寄存器溢出、依赖链、未向量化、内存访问、指令选择不当），每次只做一处修改并度量结果。在性能分析确认汇编是瓶颈后使用。
---

# asm-performance

编译器生成汇编代码的系统性审计与优化工作流程。

**前提条件**：先进行性能分析 (profiling)。在检查汇编代码之前，先确定热点函数。

---

## 阶段 1 — 收集汇编代码

### Rust（cargo-show-asm）

```bash
cargo install cargo-show-asm

# Full function — verbose
cargo asm --release --rust <crate> <module>::<function>

# LLVM IR + ASM side by side
cargo asm --release --llvm-ir <crate> <function>

# Filter to specific basic block
cargo asm --release <crate> <function> | grep -A30 '<label>:'
```

### C/C++（objdump）

```bash
gcc -O2 -g -c hot.c -o hot.o
objdump -d -S -M intel hot.o > hot.asm

# Named function only
objdump -d -M intel hot.o | awk '/^[0-9a-f]+ <your_fn>:/,/^$/'
```

### 共享库 / 二进制文件

```bash
objdump -d -M intel --demangle target/release/mybinary | grep -A200 '<hot_fn'
nm -S target/release/mybinary | grep hot_fn   # confirm symbol exists
```

---

## 阶段 2 — 审计

扫描收集到的汇编代码，检查以下 6 类问题。标记每个发现的实例。

| # | 类别 | 信号 |
|---|---|---|
| 1 | **Panic / 边界检查路径** | `call core::panicking` / `ud2` 可从热循环抵达 |
| 2 | **寄存器溢出 (Register spills)** | 循环体内有 `mov [rsp+N], reg`；栈深度非常量 |
| 3 | **依赖链 (Dependency chains)** | 连续指令读写同一寄存器，无指令级并行 (ILP) |
| 4 | **未向量化 (Missed SIMD)** | 对连续数据的标量循环；输出中无 `xmm`/`ymm` |
| 5 | **内存访问 (Memory traffic)** | 对同一地址的冗余加载/存储；无寄存器提升 |
| 6 | **指令选择不当 (Bad instruction selection)** | 对 2 的幂次使用 `idiv`/`div`；对 `lea` 友好的常数使用 `imul` |

> 加载 `references/codegen-issues.md` 查看每类问题的修改前后汇编对比。

### 审计清单

对每个发现的问题，记录：

```
CATEGORY: [1-6]
LOCATION: symbol + offset or line
SYMPTOM: what you see in the ASM
ROOT CAUSE: why the compiler made this choice
PLAN: specific change (source or inline asm constraint)
```

---

## 阶段 3 — 优化循环

每次只做一处修改，绝不批量操作。

```
1. Make ONE change (source, hint, attribute, or asm constraint)
2. Collect new ASM (Phase 1 command)
3. Diff old vs new ASM
4. Measure: perf stat / criterion / RDTSC
5. Accept or revert — see decision table
6. Repeat
```

### Diff 工作流程

```bash
# Save baseline
cargo asm --release <crate> <fn> > asm_before.s

# After change
cargo asm --release <crate> <fn> > asm_after.s

diff asm_before.s asm_after.s
```

### 决策表

| 观察结果 | 操作 |
|---|---|
| 问题消除，基准测试加速 | 接受 — 提交 |
| 问题消除，基准测试持平 | 接受（减少代码体积）；若预期周期数下降则进一步调查 |
| 问题消除，基准测试**变慢** | 回滚 — 编译器的判断优于你 |
| 问题依然存在 | 尝试下一种方法（attribute、手动提示、intrinsic） |
| 引入了新问题 | 回滚 — 引入另一个问题则净效果为负 |
| 可见 `ud2` / panic 路径 | 回滚或添加显式边界检查 |

---

## 阶段 4 — 度量

### Linux — perf stat

```bash
perf stat -e cycles,instructions,cache-misses,branch-misses ./bench
perf stat -r 5 ./bench          # 5 runs, aggregate
```

### Rust — criterion

```rust
// In benches/
use criterion::{black_box, criterion_group, criterion_main, Criterion};
fn bench_hot(c: &mut Criterion) {
  let input = black_box(/* build input */);
  c.bench_function("hot_fn", |b| b.iter(|| hot_fn(black_box(input))));
}
criterion_group!(benches, bench_hot);
criterion_main!(benches);
```

### 周期精确 — llvm-mca

```bash
llvm-mca -mcpu=znver3 -iterations=100 < snippet.s
# Reports: throughput, latency, port pressure
```

---

## 阶段 5 — 报告

```
== ASM Optimization Report ==
Function: <fully-qualified name>
Date:     YYYY-MM-DD

Baseline (cycles/iter): N
Final    (cycles/iter): N
Delta:                  -N%

Changes applied:
  1. [CATEGORY] Description of change — effect on ASM
  2. ...

Issues NOT fixed (and why):
  - [CATEGORY] Description — blocked by <reason>

Remaining hotspots: <next function to examine>
```

---

## 常见源码级提示

```rust
// Rust: disable bounds checks in hot loop
unsafe { *slice.get_unchecked(i) }

// Rust: hint for loop unroll
#[allow(clippy::all)]
let mut i = 0;
while i < n { /* body */ i += 1; }

// Rust: force inline
#[inline(always)]
fn hot_fn() { ... }

// C: restrict pointer aliasing
void process(float * restrict dst, const float * restrict src, int n);

// C: assume aligned
__builtin_assume_aligned(ptr, 32);
```

---

## 资源

- `references/codegen-issues.md` — 6 类问题的修改前后汇编模式对比
- `references/microarch.md` — ILP、执行单元、缓存行效应、分支预测规则
