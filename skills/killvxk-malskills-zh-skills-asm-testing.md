---
name: asm-testing
description: >
  此技能适用于用户询问关于 "asm-testing"、"验证新 .asm/.s/.S 文件的正确性"、"调试手写或手工优化汇编中的意外行为" 等内容。汇编代码测试与验证工作流程：用于单元测试手写函数的 C 测试驱动、GDB/LLDB 寄存器检查、objdump 结构分析、ABI 合规清单及周期精确度量。
---

# asm-testing

手写汇编代码的结构化测试与验证工作流程。

---

## 阶段 1 — ABI 合规清单

在编写任何测试之前先完成此清单。违反 ABI 的函数可能看似正常运行，直到它悄无声息地破坏调用者状态。

### x86-64 System V

- [ ] 每个 `call` 位置 `rsp` 保持 16 字节对齐（未对齐会导致 SSE 崩溃）
- [ ] `rbx`、`r12`–`r15` 在 `ret` 前已恢复为入口时的值
- [ ] 整型返回值在 `rax`；浮点/双精度在 `xmm0`
- [ ] 栈帧已正确释放（无净漂移）
- [ ] 除红区 (red zone)（仅限叶函数）外，`rsp` 以下无写入

### ARM64 AAPCS

- [ ] `sp` 始终保持 16 字节对齐（硬件强制执行）
- [ ] `ret` 前已恢复 `x19`–`x28` 和 `d8`–`d15`
- [ ] 如需向外调用，使用 `stp x29, x30, [sp, #-N]!` 保存 `x29`（fp）和 `x30`（lr）
- [ ] 整型返回值在 `x0`；浮点返回值在 `d0`

---

## 阶段 2 — 结构分析（运行前）

```bash
# Disassemble and check prologue/epilogue
objdump -d -M intel -S my.o | grep -A40 '<my_fn>:'

# Verify callee-saved registers are saved
objdump -d -M intel my.o | grep -E 'push|pop|mov \[rsp'

# Check section flags
objdump -h my.o

# Verify exported symbols
nm my.o | grep ' T '

# Show relocation targets (PIC / GOT usage)
objdump -r my.o
```

**需要确认的内容**：
- 序言 (Prologue) 保存了函数使用的寄存器
- 尾声 (Epilogue) 以相反顺序恢复了这些寄存器
- 栈分配/释放是对称的
- 无跳转到未定义符号

---

## 阶段 3 — C 驱动单元测试

编写一个精简的 C 驱动程序，调用汇编函数并断言结果。

```c
/* test_hot_fn.c */
#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <string.h>

/* Declare the ASM function */
extern int64_t hot_fn(int64_t a, int64_t b);

typedef struct { int64_t a; int64_t b; int64_t expected; } Case;

static const Case cases[] = {
    { 0,  0,  0 },
    { 1,  2,  3 },
    { -1, 1,  0 },
    { INT64_MAX, 0, INT64_MAX },
};

int main(void) {
    int failed = 0;
    for (size_t i = 0; i < sizeof cases / sizeof cases[0]; i++) {
        int64_t got = hot_fn(cases[i].a, cases[i].b);
        if (got != cases[i].expected) {
            fprintf(stderr, "FAIL case %zu: hot_fn(%ld, %ld) = %ld, want %ld\n",
                    i, cases[i].a, cases[i].b, got, cases[i].expected);
            failed++;
        }
    }
    if (!failed) puts("ALL PASS");
    return failed ? 1 : 0;
}
```

### 构建并运行

```bash
# NASM + C harness
nasm -f elf64 hot_fn.asm -o hot_fn.o
gcc -g -o test_hot_fn test_hot_fn.c hot_fn.o
./test_hot_fn

# GAS + C harness
as -g --gstabs+ hot_fn.s -o hot_fn.o
gcc -g -o test_hot_fn test_hot_fn.c hot_fn.o
./test_hot_fn
```

> 加载 `references/c-harness.md` 查看 Makefile 模式以及浮点、SIMD 输出和内存缓冲区的断言辅助工具。

---

## 阶段 4 — GDB / LLDB 验证

使用调试器单步执行函数，在每个关键位置验证寄存器状态。

### GDB 会话

```bash
gdb ./test_hot_fn
(gdb) break hot_fn
(gdb) run
(gdb) layout asm          # split ASM view
(gdb) layout regs         # show register panel
(gdb) si                  # step one instruction
(gdb) info registers      # dump all GP registers
(gdb) p/x $rax            # print register as hex
(gdb) x/8gx $rsp          # examine 8 quadwords at rsp
```

### LLDB 会话

```bash
lldb ./test_hot_fn
(lldb) b hot_fn
(lldb) run
(lldb) disassemble --pc   # disassemble around current PC
(lldb) register read      # all GP registers
(lldb) register read xmm0 # specific register
(lldb) memory read --size 8 --count 8 $rsp
(lldb) si                 # step one instruction
```

> 加载 `references/debug-commands.md` 查看完整命令参考，包括监视点 (watchpoints)、内存检查和条件断点。

### 单步执行清单

- 函数入口处：记录 `rbx`、`r12`–`r15` 的值（是否已保存到 `rsp – offset`？）
- 序言结束后：栈指针与入口的差值等于声明的帧大小
- 每个 `call` 处：验证 `rsp` 是 16 字节对齐的（`p/x $rsp % 16` 必须为 0）
- `ret` 处：`rbx`、`r12`–`r15` 与入口值一致；`rax` 持有正确的返回结果

---

## 阶段 5 — SIMD / 浮点输出验证

标准整型比较不适用于 SIMD 类型。对于精确位相等使用 `memcmp`，对浮点数使用容差检查。

```c
#include <immintrin.h>
#include <stdint.h>
#include <string.h>

/* ASM: void vec_add(float *dst, const float *src, int n) */
extern void vec_add(float *dst, const float *src, int n);

static void test_vec_add(void) {
    float dst[8] = {1,2,3,4,5,6,7,8};
    float src[8] = {1,1,1,1,1,1,1,1};
    float exp[8] = {2,3,4,5,6,7,8,9};

    vec_add(dst, src, 8);
    for (int i = 0; i < 8; i++) {
        if (dst[i] != exp[i]) {
            fprintf(stderr, "FAIL dst[%d] = %f, want %f\n", i, dst[i], exp[i]);
        }
    }
}
```

对于有舍入的浮点函数：使用 `fabsf(got - expected) < 1e-6f`。

---

## 阶段 6 — 周期度量

仅在正确性确认后进行。

```c
/* Portable RDTSC (x86-64) */
#include <stdint.h>
static inline uint64_t rdtsc(void) {
    uint32_t lo, hi;
    __asm__ volatile(
        "lfence\n"
        "rdtsc\n"
        "lfence\n"
        : "=a"(lo), "=d"(hi)
        :
        : "memory"
    );
    return ((uint64_t)hi << 32) | lo;
}

void bench_hot_fn(void) {
    const int RUNS = 10000;
    uint64_t total = 0;
    for (int i = 0; i < RUNS; i++) {
        uint64_t t0 = rdtsc();
        hot_fn(i, i+1);
        uint64_t t1 = rdtsc();
        total += t1 - t0;
    }
    printf("avg cycles: %.2f\n", (double)total / RUNS);
}
```

获得有意义的结果需要：将进程绑定到单个 CPU 核心（`taskset -c 0 ./bench`），如有可能则禁用睿频。

---

## 资源

- `references/debug-commands.md` — 完整的 GDB/LLDB/objdump/readelf/strace 命令参考
- `references/c-harness.md` — Makefile 模板、浮点比较辅助函数、内存缓冲区测试
