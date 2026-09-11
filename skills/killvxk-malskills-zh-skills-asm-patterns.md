---
name: asm-patterns
description: >
  此技能适用于用户询问关于 "asm-patterns"、"编写"、"审查"、"生成 .asm/.s/.S 文件"、"实现与 C/系统代码互操作的函数"、"建立正确的函数序言/尾声、栈管理、SIMD 循环、系统调用桩" 等内容。x86-64 和 ARM64 汇编语言模式、调用约定及代码结构规范。
---

# Assembly Patterns

x86-64 和 ARM64 汇编的标准模式与约束规则。
适用于所有 `.asm`、`.s`、`.S` 文件以及嵌入在 C/Rust/Go 中的汇编代码。

---

## 架构选择

在每个文件顶部声明目标架构：

```nasm
; x86-64, NASM, Linux/macOS
; Target: x86-64 System V ABI
; Syntax: Intel (NASM)
```

- **x86-64** — Linux/macOS 服务器、桌面、WSL
- **ARM64** — Apple Silicon、移动端、嵌入式 Linux
- 不使用 `%ifdef` / `.ifdef` 守卫时，禁止混合不同架构的代码路径

---

## 调用约定

### x86-64 System V ABI（Linux、macOS、BSD）

| 角色 | 寄存器 |
|---|---|
| 整型参数（1–6） | `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9` |
| 浮点参数（1–8） | `xmm0`–`xmm7` |
| 整型返回值 | `rax` |
| 浮点返回值 | `xmm0` |
| 调用者保存 (Caller-saved) | `rax`, `rcx`, `rdx`, `rsi`, `rdi`, `r8`–`r11` |
| 被调用者保存 (Callee-saved) | `rbx`, `rbp`, `r12`–`r15` |
| 栈对齐 | `call` 指令**执行前**需 16 字节对齐 |

### ARM64 AAPCS（Linux、macOS）

| 角色 | 寄存器 |
|---|---|
| 整型参数（1–8） | `x0`–`x7` |
| 浮点参数（1–8） | `d0`–`d7` |
| 整型返回值 | `x0` |
| 浮点返回值 | `d0` |
| 被调用者保存 (Callee-saved) | `x19`–`x28`, `x29` (FP) |
| 栈对齐 | 始终保持 16 字节对齐 |

**关键规则**：在非叶函数中，入口处使用 `stp` 将 `x29` + `x30` 一起保存；`ret` 前使用 `ldp` 恢复。

---

## 核心模式

### x86-64 — 非叶函数

```nasm
; int64_t compute(int64_t x, int64_t y)
; Args: rdi=x, rsi=y   Returns: rax
global compute
compute:
    push    rbp
    mov     rbp, rsp
    push    rbx                 ; callee-saved used below
    sub     rsp, 8              ; keep stack 16-byte aligned

    mov     rbx, rdi            ; save x across call
    call    some_helper         ; rdi..r11 may be clobbered

    imul    rax, rbx            ; result * saved x
    imul    rax, rsi            ; * y

    add     rsp, 8
    pop     rbx
    pop     rbp
    ret
```

### x86-64 — 叶函数（无调用，使用红区）

```nasm
; int64_t add3(int64_t a, int64_t b, int64_t c)
; Args: rdi=a, rsi=b, rdx=c   Returns: rax
global add3
add3:
    lea     rax, [rdi + rsi]    ; rax = a + b
    add     rax, rdx            ; rax += c
    ret
```

### ARM64 — 非叶函数

```asm
// int64_t compute(int64_t x, int64_t y)
// x0=x, x1=y  →  x0=result
    .global compute
compute:
    stp     x29, x30, [sp, #-32]!   // save fp+lr, alloc frame
    mov     x29, sp
    stp     x19, x20, [sp, #16]     // save callee-saved

    mov     x19, x0                  // save x across call
    bl      some_helper

    mul     x0, x0, x19             // result * saved x
    mul     x0, x0, x1              // * y

    ldp     x19, x20, [sp, #16]
    ldp     x29, x30, [sp], #32
    ret
```

### SIMD — SSE2 浮点循环（x86-64）

```nasm
; void vadd_f32(float *dst, const float *a, const float *b, size_t n)
; n must be a multiple of 4; dst/a/b may be unaligned
global vadd_f32
vadd_f32:
    test    rcx, rcx
    jz      .done
    shr     rcx, 2              ; n /= 4
.loop:
    movups  xmm0, [rsi]
    addps   xmm0, [rdx]
    movups  [rdi], xmm0
    add     rsi, 16
    add     rdx, 16
    add     rdi, 16
    dec     rcx
    jnz     .loop
.done:
    ret
```

### SIMD — NEON 浮点循环（ARM64）

```asm
// void vadd_f32(float *dst, const float *a, const float *b, size_t n)
    .global vadd_f32
vadd_f32:
    cbz     x3, .done
    lsr     x3, x3, #2          // n /= 4
.loop:
    ld1     {v0.4s}, [x1], #16
    ld1     {v1.4s}, [x2], #16
    fadd    v0.4s, v0.4s, v1.4s
    st1     {v0.4s}, [x0], #16
    subs    x3, x3, #1
    b.ne    .loop
.done:
    ret
```

### Linux x86-64 系统调用

```nasm
; syscall(number, arg1, arg2, arg3)
; Note: r10 replaces rcx (syscall clobbers rcx and r11)
SYS_WRITE equ 1
SYS_EXIT  equ 60

section .data
    msg  db "hello", 10
    mlen equ $ - msg

section .text
global _start
_start:
    mov  rax, SYS_WRITE
    mov  rdi, 1
    lea  rsi, [rel msg]     ; RIP-relative — required for PIC/PIE
    mov  rdx, mlen
    syscall

    mov  rax, SYS_EXIT
    xor  edi, edi
    syscall
```

### 位置无关代码 (PIC)

```nasm
default rel                 ; make ALL memory refs RIP-relative (NASM)

section .data
    counter dq 0

section .text
global get_counter
get_counter:
    mov  rax, [counter]     ; compiles to: mov rax, [rip + offset]
    ret
```

---

## 代码风格规则

1. **文件头** — 用途、架构、语法、作者
2. **函数头** — C 原型注释、寄存器映射、返回值
3. **行内注释** — 解释*为什么*，而非*是什么*（`; pointer alignment check`，而非 `; compare`）
4. **标签命名** — `module_function_sublabel`（如 `crypto_sha256_loop`）
5. **常量** — 始终使用 `equ` / `.equ` 加描述性名称，禁止魔法数字
6. **被调用者保存寄存器** — 使用前必须保存，以逆序恢复
7. **栈** — 每次 `call` 前保持 16 字节对齐；尾声中不留脏状态
8. **对齐指令** — x86-64 热循环前使用 `align 16`；SSE/AVX 加载时为必须项

---

## 工具链快速参考

```bash
# NASM → Linux ELF64 (debug info)
nasm -f elf64 -g -F dwarf file.asm -o file.o

# NASM → macOS Mach-O 64
nasm -f macho64 file.asm -o file.o

# GAS (AT&T syntax)
as --64 -g file.s -o file.o

# Link (no libc)
ld -o prog file.o

# Link (with libc / C interop)
gcc -o prog file.o

# Shared library (PIC required)
gcc -shared -o libfoo.so foo.o

# Inspect symbols
nm -u file.o                 # undefined references
readelf -S file.o            # section layout

# Disassemble with Intel syntax
objdump -d -M intel prog

# Verify calling convention at runtime (GDB)
gdb prog
(gdb) set disassembly-flavor intel
(gdb) layout asm
(gdb) p/x $rsp & 0xf        # must be 0 at every call boundary
```

---

## 资源

按需加载：

- [references/x86-64.md](references/x86-64.md) — 完整寄存器表、指令选择指南、SSE/AVX 模式、x86-64 ABI 边界情况
- [references/arm64.md](references/arm64.md) — ARM64 寄存器表、NEON/SVE 模式、AAPCS 边界情况、Apple Silicon 特性
