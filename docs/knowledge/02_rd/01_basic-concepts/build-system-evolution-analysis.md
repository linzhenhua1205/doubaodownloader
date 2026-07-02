# 🏗️ 编译构建工具演进全分析：从手工编译到现代构建系统

> **范围**: 覆盖从人工编译到Make→Autotools→CMake→Ninja→Meson→Bazel→Cargo等构建工具的完整演进路线，围绕**构建模型、依赖管理、增量机制、并行能力、跨平台支持、配置范式**六大维度展开，含核心概念统一框架与选型决策树
>
> **写作原则**: 以"构建图(DAG)"为主线贯穿所有工具，每代工具解答前一代未解决的核心问题，量化性能数据出处理论引出处
>
> **创建**: 2026-07-02 v1.0

---

## 📑 目录

- [1. 引言：构建系统的本质](#1-引言构建系统的本质)
  - [1.1 为什么需要构建工具](#11-为什么需要构建工具)
  - [1.2 构建系统核心抽象：依赖图(DAG)](#12-构建系统核心抽象依赖图dag)
  - [1.3 评价维度框架](#13-评价维度框架)
  - [1.4 演进路线全景](#14-演进路线全景)
- [2. 前构建时代：手工编译](#2-前构建时代手工编译)
  - [2.1 工作模式](#21-工作模式)
  - [2.2 核心问题：不满足任何非平凡需求](#22-核心问题不满足任何非平凡需求)
- [3. 第一代构建工具：Make](#3-第一代构建工具make)
  - [3.1 Make的诞生与哲学](#31-make的诞生与哲学)
  - [3.2 Makefile基础模型](#32-makefile基础模型)
  - [3.3 Make家族：GNU Make \> BSD Make \> nmake](#33-make家族gnu-make--bsd-make--nmake)
  - [3.4 Make的优缺点](#34-make的优缺点)
- [4. 第一代扩展：Autotools（GNU构建系统）](#4-第一代扩展autotoolsgnu构建系统)
  - [4.1 解决的问题：跨平台可移植性](#41-解决的问题跨平台可移植性)
  - [4.2 工具链：Autoconf + Automake + Libtool](#42-工具链autoconf--automake--libtool)
  - [4.3 工作流与原理](#43-工作流与原理)
  - [4.4 Autotools的局限性](#44-autotools的局限性)
- [5. 第二代构建工具：CMake——元构建系统](#5-第二代构建工具cmake元构建系统)
  - [5.1 CMake的诞生背景](#51-cmake的诞生背景)
  - [5.2 元构建模型](#52-元构建模型)
  - [5.3 CMakeLists.txt 基础](#53-cmakeliststxt-基础)
  - [5.4 关键能力：靶向式配置与第三方依赖管理](#54-关键能力靶向式配置与第三方依赖管理)
  - [5.5 CMake的优缺点](#55-cmake的优缺点)
- [6. 构建后端：Ninja——为速度而生](#6-构建后端ninja为速度而生)
  - [6.1 Ninja的设计哲学](#61-ninja的设计哲学)
  - [6.2 核心机制](#62-核心机制)
  - [6.3 性能基准](#63-性能基准)
  - [6.4 Ninja的适用边界](#64-ninja的适用边界)
- [7. 第三代构建系统：Meson——现代CMake挑战者](#7-第三代构建系统meson现代cmake挑战者)
  - [7.1 设计目标](#71-设计目标)
  - [7.2 Meson构建描述](#72-meson构建描述)
  - [7.3 Meson vs CMake](#73-meson-vs-cmake)
- [8. 第四代构建系统：Bazel与Hermetic构建](#8-第四代构建系统bazel与hermetic构建)
  - [8.1 问题：递增构建的脆弱性](#81-问题递增构建的脆弱性)
  - [8.2 封闭(Hermetic)构建原则](#82-封闭hermetic构建原则)
  - [8.3 Bazel的核心机制](#83-bazel的核心机制)
  - [8.4 Bazel家族：Buck \> Pants \> Please](#84-bazel家族buck--pants--please)
  - [8.5 Bazel的代价](#85-bazel的代价)
- [9. 语言原生构建工具](#9-语言原生构建工具)
  - [9.1 Cargo (Rust)](#91-cargo-rust)
  - [9.2 Go Modules](#92-go-modules)
  - [9.3 Gradle (JVM生态)](#93-gradle-jvm生态)
  - [9.4 Xmake (C/C++)](#94-xmake-cc)
  - [9.5 Vcpkg/Conan (依赖管理)](#95-vcpkgconan-依赖管理)
- [10. 新兴边界工具](#10-新兴边界工具)
  - [10.1 Buck2 (Meta)](#101-buck2-meta)
  - [10.2 Soong + Blueprint (Android)](#102-soong--blueprint-android)
  - [10.3 GN + Ninja (Chromium)](#103-gn--ninja-chromium)
- [11. 全谱系对比矩阵](#11-全谱系对比矩阵)
  - [11.1 核心维度对比](#111-核心维度对比)
  - [11.2 配置格式对比](#112-配置格式对比)
  - [11.3 增量机制对比](#113-增量机制对比)
  - [11.4 选型决策树](#114-选型决策树)
- [12. 总结与趋势](#12-总结与趋势)
  - [12.1 六个演化的根本驱动力](#121-六个演化的根本驱动力)
  - [12.2 未来趋势](#122-未来趋势)
- [参考来源](#参考来源)
- [变更记录](#变更记录)

---

## 1. 引言：构建系统的本质

### 1.1 为什么需要构建工具

构建(Build)是将源代码转化为可交付产物（可执行文件、库、包）的过程。一个中等规模的现代项目（如Chromium ~3000万行C++）包含：

- **上万**个源文件
- **数百**个"仅编译其中一个"的配置选项
- **数十**个第三方依赖库
- **多平台**（Linux/macOS/Windows/Android/iOS）输出需求

没有构建工具的辅助，人工管理这些依赖和步骤是完全不可能的。

### 1.2 构建系统核心抽象：依赖图(DAG)

所有构建工具的核心都是同一个抽象——**有向无环图(DAG)**：

```
┌──────────┐
│ source.c │
└────┬─────┘
     │ 预处理+编译
     ▼
┌──────────┐    ┌──────────┐
│ source.o │    │ libfoo.a│
└────┬─────┘    └────┬─────┘
     │  链接          │
     └───────┬────────┘
             ▼
      ┌────────────┐
      │ executable │
      └────────────┘
```

每个节点是一个**构建目标**(target)，每条边是一个**依赖关系**(dependency)。构建工具的职责就是**根据DAG拓扑序执行各节点的构建动作，并尽可能复用已有结果**。

**DAG的三种边**：

| 依赖类型 | 含义 | 示例 |
|:---------|:-----|:-----|
| **直接依赖** | A需要B先完成 | 链接前需要所有.o文件 |
| **间接依赖** | A需要B，B需要C | 程序→库→头文件 |
| **顺序依赖(Order-only)** | A需要B存在但不影响内容判断 | 输出目录先创建 |

### 1.3 评价维度框架

本报告用六个核心维度评价每个构建工具：

| # | 维度 | 核心问题 |
|:-:|:-----|:---------|
| **① 构建模型** | 任务驱动(recipe)还是依赖驱动(DAG)？元构建还是直接构建？ |
| **② 增量机制** | 如何判断哪些文件需要重新构建？时间戳？哈希？内容指纹？ |
| **③ 并行能力** | 支持并行构建吗？依赖图怎样调度到多核/多机？ |
| **④ 跨平台** | 多OS支持、交叉编译、工具链抽象程度如何？ |
| **⑤ 配置范式** | 声明式(declarative) vs 命令式(imperative) vs 函数式？ |
| **⑥ 依赖管理** | 如何表达、解析、隔离第三方依赖？ |

### 1.4 演进路线全景

```
手工编译 ──→ Make ────→ Autotools ────→ CMake ────→ Meson ────→ Bazel
  (1950s)    (1976)      (1990s)         (2000)      (2013)     (2015)
                                                 ↘            ↘
                                                   Ninja        Cargo
                                                   (2012)       (2015)
                                                       ↘          ↘
                                                          GN/Buck2  Go.Mod
                                                          (2019)    (2018)
```

六个时代解决的问题：

| 时代 | 代表工具 | 解决的核心问题 |
|:-----|:---------|:--------------|
| **0-手工** | Shell脚本 | — |
| **1-依赖驱动** | Make | 增量构建 = 避免全量重编 |
| **1.5-跨平台配置** | Autotools | 跨Unix平台检测+配置 |
| **2-元构建** | CMake | 跨平台生成+统一配置语言 |
| **2.5-高速后端** | Ninja | 构建性能极致优化 |
| **3-现代声明式** | Meson | 开发友好+原生速度 |
| **4-Hermetic** | Bazel/Cargo | 绝对可复现+增量正确性 |

---

## 2. 前构建时代：手工编译

### 2.1 工作模式

最早的"构建工具"是**Shell脚本**：

```sh
#!/bin/sh
# 构建foo程序

# 编译每个源文件
cc -c -o main.o main.c
cc -c -o utils.o utils.c
cc -c -o parser.o parser.c

# 链接
cc -o foo main.o utils.o parser.o
```

改进版：添加条件检查

```sh
# 增量构建：检查时间戳
[ main.c -nt main.o ] && cc -c -o main.o main.c
[ utils.c -nt utils.o ] && cc -c -o utils.o utils.c
[ parser.c -nt parser.o ] && cc -c -o parser.o parser.c

[ main.o -nt foo ] || [ utils.o -nt foo ] || [ parser.o -nt foo ] && \
    cc -o foo main.o utils.o parser.o
```

### 2.2 核心问题：不满足任何非平凡需求

| 问题 | 描述 | 严重性 |
|:-----|:-----|:-------|
| **依赖手动维护** | 头文件变化不会自动触发重新编译 | 🔴 |
| **增量判断粗糙** | 时间戳比较无法处理头文件链（a.c → a.o → b.h → b.c → ...） | 🔴 |
| **无并行** | 必须手动 `&` 后台运行，竞态风险高 | 🔴 |
| **无模式规则** | 每个.c文件都要独立写编译命令 | 🟡 |
| **不可移植** | cc/gcc/windows编译器路径都写死 | 🟡 |

---

## 3. 第一代构建工具：Make

### 3.1 Make的诞生与哲学

Make 由 Stuart Feldman 于 1976 年在贝尔实验室创造，是计算机科学史上最具影响力的工程工具之一。它的核心洞察是：

> **与其告诉计算机"怎么做"，不如告诉它"什么依赖什么"，让计算机自己决定做什么。**

### 3.2 Makefile基础模型

```makefile
# 目标(target): 依赖(prerequisites)
# 规则(recipe)
foo: main.o utils.o parser.o
    cc -o foo main.o utils.o parser.o

main.o: main.c main.h defs.h
    cc -c -o main.o main.c

utils.o: utils.c utils.h
    cc -c -o utils.o utils.c

parser.o: parser.c parser.h
    cc -c -o parser.o parser.c
```

**核心机制**：如果一个目标的依赖比目标更新，则执行规则。

**模式规则**的引入大幅简化了重复：

```makefile
# 模式规则：所有 .c → .o
%.o: %.c $(HEADERS)
    $(CC) $(CFLAGS) -c -o $@ $<

# 隐式规则链：.c → .o → 可执行文件
# make 内置了大量此类规则
```

### 3.3 Make家族：GNU Make > BSD Make > nmake

| 变体 | 平台 | 关键差异 |
|:-----|:-----|:---------|
| **GNU Make** | Linux/Unix/Windows | 功能最全，支持 `$(shell)`、`$(eval)`、条件语句、`include` 指令 |
| **BSD Make** (pmake) | BSD系 | 支持条件语句 `.\`if`，语法简洁 |
| **nmake** (Microsoft) | Windows | 微软实现，语法差异大，部分GNU扩展不支持 |
| **dmake** (Solaris) | SunOS | 已基本淘汰 |

**GNU Make的重要扩展**：

```makefile
# 条件判断
ifeq ($(CC), gcc)
    CFLAGS += -Wall -Wextra
endif

# 函数
SOURCES := $(wildcard src/*.c)
OBJECTS := $(patsubst %.c, %.o, $(SOURCES))

# .PHONY 避免和目标文件重名
.PHONY: clean
clean:
    rm -f $(OBJECTS) foo

# 并行构建
# make -j$(nproc)  ← 并发N个任务
```

### 3.4 Make的优缺点

#### ✅ 优点

| 优点 | 说明 |
|:-----|:-----|
| **无处不在** | 几乎所有Unix/Linux系统预装，30年不变的基础设施 |
| **模型简洁** | 目标-依赖-规则三元组，30分钟可掌握基本用法 |
| **增量正确** | 基于文件时间戳的增量构建逻辑直观 |
| **灵活性极高** | `$(shell)` 可以嵌入任意Shell逻辑 |
| **递归Make** | 支持大型项目按目录分层 |

#### ❌ 缺点

| 缺点 | 说明 | 严重性 |
|:-----|:-----|:-------|
| **隐式依赖缺失** | Make只跟踪Makefile中显式书写的依赖。**头文件变化不会触发重新编译包含了它的.c文件**——除非手动在Makefile中列出所有头文件依赖 | 🔴 |
| **Tab符陷阱** | Recipe必须以Tab开头，非空格——这是无数新手的第一个坑 | 🔴 |
| **递归Make不可扩展** | 大型项目用递归Make（每个目录一个Makefile）时，构建调度粒度粗、跨目录依赖无法高效表达 | 🔴 |
| **无交叉编译支持** | 必须手动处理工具链切换 | 🟡 |
| **命令式语言** | Makefile本质是带缩写的Shell脚本，变量作用域混乱、函数式编程能力弱 | 🟡 |
| **字符串比较而非结构化数据** | 所有数据都是字符串，没有列表/字典/对象概念 | 🟡 |

#### 💡 Make的"隐式依赖缺失"问题详解

```c
// main.c
#include "defs.h"    // 如果defs.h修改，main.c需要重新编译

// Makefile中通常只写：
main.o: main.c
    cc -c main.c    // ← 没有列defs.h为依赖！
```

**解决方案**：GCC可以自动生成依赖：

```makefile
# 让gcc生成.d文件，包含所有头文件依赖
%.o: %.c
    $(CC) -MMD -MP -c -o $@ $<
    # -MMD 生成 .d 文件（不含系统头文件）
    # -MP  为每个头文件生成空目标（避免头文件删除后make报错）

-include $(wildcard *.d)    # 包含所有依赖文件
```

这个"补丁"方案一直在用，但它暴露了Make的根本设计局限——**依赖关系必须手动维护，工具本身无法自动推断**。

---

## 4. 第一代扩展：Autotools（GNU构建系统）

### 4.1 解决的问题：跨平台可移植性

到1990年代，Unix已分裂为数十个变种（Solaris、AIX、HP-UX、Irix……），每个平台的函数名、头文件位置、库链接方式各不相同。手动为每个平台写Makefile不可维护。

**Autotools解决了"我的程序要在20个不同Unix平台上编译"的问题**。

### 4.2 工具链：Autoconf + Automake + Libtool

```
configure.ac (M4宏)
    │ autoconf
    ▼
configure (Shell脚本) ← 在用户机器上运行，检测平台特性
    │ 运行 ./configure
    ▼
config.status + config.h ← 生成Makefile（替换@变量@）
    │
    ▼
Makefile ← 由 Automake 从 Makefile.am 生成
```

| 组件 | 功能 |
|:-----|:-----|
| **Autoconf** | 从 `configure.ac` 生成可移植的 `configure` Shell脚本 |
| **Automake** | 从 `Makefile.am`（简化语法）生成符合GNU标准的 `Makefile` |
| **Libtool** | 处理跨平台动态库(.so/.dylib/.dll)的创建和链接 |
| **pkg-config** | 查询第三方库的编译和链接标志 |

### 4.3 工作流与原理

```m4
# configure.ac — M4宏语言
AC_INIT([myapp], [1.0], [bug@myapp.com])
AM_INIT_AUTOMAKE

# 检查编译器
AC_PROG_CC

# 检查函数是否存在
AC_CHECK_FUNC([strdup], [], [AC_LIBOBJ([strdup])])

# 检查头文件
AC_CHECK_HEADERS([stdlib.h unistd.h])

# 检查库
AC_CHECK_LIB([pthread], [pthread_create])

# 生成输出
AC_CONFIG_FILES([Makefile src/Makefile])
AC_OUTPUT
```

```automake
# Makefile.am — 简化的Makefile语法
bin_PROGRAMS = myapp
myapp_SOURCES = main.c utils.c parser.c
myapp_CFLAGS = -Wall -O2
myapp_LDADD = -lpthread

# 安装头文件
include_HEADERS = myapp.h
```

**经典的"三件套"安装模式**：

```sh
./configure --prefix=/usr/local
make          # 构建
make install  # 安装
```

### 4.4 Autotools的局限性

| 问题 | 说明 | 严重性 |
|:-----|:-----|:-------|
| **配置与构建分离** | `./configure` 生成构建文件——这是对的，但生成过程本身极其脆弱 | 🟡 |
| **M4宏语言不可调试** | `configure.ac` 的M4宏没有类型系统、没有调试器、错误信息天书 | 🔴 |
| **配置慢** | 大型项目的 `./configure` 耗时数分钟 | 🟡 |
| **生成的configure巨大** | 一个简单项目的configure脚本可达10万行 | 🟡 |
| **Windows支持差** | 设计时只考虑Unix，后来加入的Cygwin/MSYS是折衷方案 | 🔴 |
| **递归Make结构** | GNU标准的子目录递归Make = 分层但效率低 | 🟡 |
| **依赖管理原始** | 没有第三方包的概念，全靠系统级安装 | 🟡 |
| **并行构建支持弱** | 递归Make导致并行调度效率低 | 🟡 |

> **核心矛盾**：Autotools诞生在一个Unix为主的世界，它完美地解决了"跨Unix可移植性"，但无法应对Windows的崛起和大型项目的复杂度。

---

## 5. 第二代构建工具：CMake——元构建系统

### 5.1 CMake的诞生背景

CMake（Cross-platform Make）由 Bill Hoffman 于 2000 年在 Kitware 公司创立，最初服务于 ITK/VTK 可视化工具包的跨平台构建需求。

**核心创新**：引入"元构建"(Meta-Build)概念——CMake不直接构建项目，而是生成其他构建工具的输入文件（Makefile、Ninja、Xcode project、Visual Studio solution等）。

### 5.2 元构建模型

```
CMakeLists.txt (声明式+命令式混合)
        │
        │ cmake -B build -G "Ninja"
        ▼
     ┌──── CMake 前端 ────┐
     │ 解析CMakeLists.txt  │
     │ 检测工具链和库      │
     │ 计算依赖图          │
     └────────┬────────────┘
              │
              ▼ 生成层
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
 Makefile   build.ninja   .sln/.vcxproj
 (Unix)     (fast)        (Visual Studio)
```

**为什么需要元构建**？因为构建前端（配置语言、依赖声明、变量管理）和构建后端（编译、链接、增量判断）的关切完全不同：
- **前端**需要：强大的配置语言、条件逻辑、循环、模块化、包管理
- **后端**需要：极致性能、简单执行模型、最小解析开销

很多人不理解CMake为什么要经历"配置→生成→构建"三步：

| 阶段 | CMake命令 | 功能 |
|:-----|:----------|:-----|
| **1. 配置(Configure)** | `cmake -B build` | 解析CMakeLists.txt，检测工具链和库，创建反悔缓冲区 |
| **2. 生成(Generate)** | `cmake --build build` | 根据配置结果生成指定构建后端的输入文件 |
| **3. 构建(Build)** | `cmake --build build` | 调用Ninja/Make执行实际编译链接 |

### 5.3 CMakeLists.txt 基础

```cmake
cmake_minimum_required(VERSION 3.20)
project(MyApp LANGUAGES C CXX)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找第三方包
find_package(OpenSSL REQUIRED)
find_package(Python3 COMPONENTS Development)

# 添加可执行文件
add_executable(myapp
    src/main.cpp
    src/utils.cpp
    src/parser.cpp
)

# 设置包含路径
target_include_directories(myapp PRIVATE include)

# 链接库
target_link_libraries(myapp PRIVATE
    OpenSSL::SSL
    OpenSSL::Crypto
    Python3::Python
)

# 添加测试
enable_testing()
add_test(NAME basic_test COMMAND myapp --test)
```

**靶向式(Target-based)设计**是现代CMake最关键的设计决策：

```cmake
# 创建一个库目标
add_library(mylib STATIC
    src/lib.cpp
)

# 为这个库指定包含路径——只对这个库及其使用者生效
target_include_directories(mylib
    PUBLIC  include     # 使用者也能看到
    PRIVATE src         # 只有库本身能看到
    INTERFACE           # 只有使用者能看到（纯头文件库）
)

# 使用者自动继承PUBLIC/INTERFACE属性
target_link_libraries(myapp PRIVATE mylib)
# myapp 自动获得 mylib 的 PUBLIC include 路径
```

### 5.4 关键能力：靶向式配置与第三方依赖管理

**靶向式(Per-target)属性**是CMake对比Make/Autotools的质变：

| 属性 | Make | CMake |
|:-----|:-----|:------|
| 变量作用域 | 全局 | 目标级(PUBLIC/PRIVATE/INTERFACE) |
| 头文件路径 | `-I`在全局CFLAGS | `target_include_directories` |
| 编译宏 | 全局 `-D` | `target_compile_definitions` |
| 库依赖 | 全局LDLIBS | `target_link_libraries` → 传递依赖 |

**依赖管理生态**：

CMake原生支持 `find_package` 查找系统级第三方库，并通过以下方式扩展：

- **FetchContent**：在配置时自动下载依赖源码
- **CPack**：打包系统（生成deb/rpm/NSIS等格式）
- **CTest**：测试框架集成
- **CDash**：持续集成

### 5.5 CMake的优缺点

#### ✅ 优点

| 优点 | 说明 |
|:-----|:-----|
| **跨平台** | Linux/macOS/Windows/Android/iOS全支持 |
| **多后端生成** | Makefile/Ninja/Xcode/VS等十余种后端 |
| **大型项目验证** | LLVM ~3000万行、VTK ~100万行、KDE Plasma 等 |
| **靶向属性** | PUBLIC/PRIVATE/INTERFACE 解决了变量污染问题 |
| **模块化** | `add_subdirectory`、`include`、`FetchContent` 支持分层 |
| **包管理生态** | Conan/vcpkg/Hunter 等构建在CMake之上 |
| **现代化** | CMake 3.x 支持 `target_*` 命令、`COMPILE_FEATURES`、`CUDA` 等 |

#### ❌ 缺点

| 缺点 | 说明 | 严重性 |
|:-----|:-----|:-------|
| **语言设计糟糕** | 变量拼写错误不报错（`set(MY_VAR blah)`，使用时 `$(MY_VAR)` vs `${MY_VAR}`？） | 🔴 |
| **调试困难** | `message()` 是唯一的调试方式，无类型系统 | 🔴 |
| **生成不是构建** | 配置(Config)和构建(Build)的两阶段分离导致配置错误不构件时暴露 | 🟡 |
| **缓存陷阱** | CMakeCache.txt 被认为修改即失效，但实际经常缓存错误检测结果 | 🟡 |
| **语法不一致** | 现代CMake(taget_*) 和传统CMake(set) 并存，新旧写法混用 | 🟡 |
| **学习曲线陡峭** | 简单项目30分钟能写，复杂项目（如处理CUDA+Fortran+Python绑定）需数月经验 | 🟡 |
| **配置-构建转换** | CMake生成的Makefile/Ninja文件极难直接读取或手动修改 | 🟡 |

---

## 6. 构建后端：Ninja——为速度而生

### 6.1 Ninja的设计哲学

Ninja 由 Evan Martin（Google Chrome团队）于 2012 年创建，专为解决**构建性能瓶颈**而设计。

**核心哲学**：**构建系统应该快得像 'rm -rf build && cmake --build build' 一样快**——即使在全量构建时也不例外。

Ninja故意不做任何"人类友好"的设计：

```ninja
# build.ninja — 设计目标：机器生成，机器解析
rule cc
  command = gcc -MMD -MT $out -MF $out.d $cflags -c $in -o $out
  depfile = $out.d

build main.o: cc main.c
build utils.o: cc utils.c
build myapp: link main.o utils.o
```

**Ninja不做的事情**（与Make对比）：

| 功能 | Make | Ninja |
|:-----|:----:|:-----:|
| 模式规则(%.o: %.c) | ✅ | ❌ — 必须由生成器展开 |
| 变量自动展开 | ✅ | ❌ — 只有最基础的变量 |
| 函数(`$(wildcard)`) | ✅ | ❌ |
| 自动依赖生成 | 需手动-MMD | ✅ `depfile` 指令 |
| 并行控制 | `-jN` | `-jN` (原生更强) |
| 重新执行失败命令 | ❌ | ✅ 比Make更健壮 |

### 6.2 核心机制

**Ninja 的核心性能来源**：

1. **解析极致快**：语法极度简化，无函数求值、无条件判断、无变量展开链
2. **构建图内存化**：启动时完整读取并解析整个 `build.ninja`（百万行级别）到内存中
3. **去中心化调度**：使用工作窃取(Work-stealing)算法调度并行任务
4. **文件描述符池**：同时管理大量子进程

```ninja
# Ninja 的并行调度示意
# build.ninja 中每个 build 语句就是一个DAG节点
# Ninja 运行时构建内存DAG，从叶子节点开始调度

build a.o: cc a.c          # 深度0
build b.o: cc b.c          # 深度0
build c.o: cc c.c          # 深度0
build lib.a: ar a.o b.o    # 深度1 — 等a.o和b.o完成
build app: link lib.a c.o  # 深度2 — 等lib.a和c.o完成
```

### 6.3 性能基准

| 项目 | 源文件数 | Make (单线程) | Make (-j8) | Ninja (-j8) | 加速比 |
|:-----|:--------:|:-------------:|:----------:|:----------:|:------:|
| LLVM | 20,000+ | ~320s | ~45s | ~38s | 1.2x |
| Chromium | 30,000+ | - | ~15min | ~12min | 1.25x |
| 增量(改1文件) | - | ~2s(扫描) | ~0.5s | ~0.08s | **6x** |

> 增量构建场景的6x加速是Ninja最核心的实战优势——大项目中，开发者的"改一行代码→重新编译→等待"周期被大幅缩短。

### 6.4 Ninja的适用边界

| 场景 | 适用性 | 原因 |
|:-----|:------:|:-----|
| 大型C++项目(>10万行) | ✅ 首选 | 增量性能优势明显 |
| 小型项目(<5000行) | ❌ 过度设计 | CMake直接生成Makefile即可 |
| 纯C项目 | 🟡 可选 | 如果追求极致构建速度 |
| 跨平台项目 | ✅ 配合CMake/Meson使用 | Ninja本身不处理跨平台 |
| 需要IDE集成 | 🟡 间接 | 通过CMake生成Ninja文件 |

> **关键洞察**：Ninja的成功证明了一个重要的工程原则——**分离关注点(Seperation of Concerns)**。把构建输出配置（复杂、人类需要）和构建执行调度（简单、需要速度）分开，让各自做到极致。

---

## 7. 第三代构建系统：Meson——现代CMake挑战者

### 7.1 设计目标

Meson 由 Jussi Pakkanen 于 2013 年创建，旨在解决CMake的各种"历史债"。

**Meson的设计目标**：
1. **开发者友好的构建描述语言**：清晰、简洁、可读
2. **原生高速**：始终以Ninja为后端
3. **内置模块**：对i18n、Qt、Python、CUDA、Rust等有一流支持
4. **正确的增量构建**：不依赖时间戳，始终维护完整依赖图

### 7.2 Meson构建描述

```meson
# meson.build
project('myapp', 'c', 'cpp',
  version: '1.0',
  default_options: ['c_std=c11', 'cpp_std=c++17'])

# 查找依赖
glib_dep = dependency('glib-2.0', version: '>=2.58')
gtest_dep = dependency('gtest', required: false)

# 可执行文件
executable('myapp',
  'src/main.c',
  'src/utils.c',
  dependencies: [glib_dep],
  install: true)

# 条件性添加测试
if gtest_dep.found()
  test_exe = executable('test_myapp',
    'test/main_test.c',
    dependencies: [glib_dep, gtest_dep])
  test('unit', test_exe)
endif

# 子项目
subproject('libfoo')
```

### 7.3 Meson vs CMake

| 对比维度 | CMake | Meson |
|:---------|:------|:------|
| **构建语言** | 自定义(C-like，无类型) | 自定义(类似Python，有类型基础) |
| **后端默认** | Makefile | **Ninja**（唯一官方后端） |
| **字典/列表支持** | ❌ 只有字符串 | ✅ 列表、字典、布尔、整数 |
| **编译时间检测** | 配置时 | 构建时（更准） |
| **IDE支持** | Visual Studio/Xcode等**原生**生成 | 需要额外工具 |
| **跨编译器** | ✅ 支持广泛 | ✅ 但小众工具链支持较少 |
| **非编译目标** | `add_custom_target`（命令式） | `run_target()`（同等） |
| **学习曲线** | 中等（历史版本混乱） | 低（语法一致） |
| **资源消耗** | 配置时可花数分钟（大型项目） | 配置时通常<10秒 |
| **社区生态** | 极其庞大（LLVM/KDE/ROS/VTK等） | 中等(GNOME, Systemd, Mesa) |
| **成熟度** | 1999年至今≈25年 | 2013年至今≈13年 |

**Meson的关键设计选择**：

1. **唯一后端**：强制使用Ninja——避免了CMake"后端实现差异导致行为不一致"的问题
2. **不支持自定义目标命令**（早期版本）：后来通过 `run_target()` 加入，但不够灵活
3. **内置subproject支持**：比CMake的FetchContent更原生
4. **wrap文件**：声明式依赖管理格式——描述从哪里获取第三方源码

**典型吐槽**：
- Meson是"Python语法+CMake语义"——学习成本低，但自定义扩展能力（没有CMake的`function()`和`macro()`）受限
- 极端边缘场景（如生成汇编后插入额外处理）的兜底能力不如CMake

---

## 8. 第四代构建系统：Bazel与Hermetic构建

### 8.1 问题：递增构建的脆弱性

传统构建工具（包括CMake和Meson）的增量构建基于**文件时间戳**。这存在根本性问题：

| 问题 | 场景 | 后果 |
|:-----|:-----|:-----|
| **时间戳抖动** | Git checkout后所有文件时间戳被改变 | 全量重编——即使文件内容没变 |
| **隐式输入** | 编译器版本、环境变量、系统库的隐式依赖 | "在我的机器上能编译" |
| **并行冲突** | 两个构建共享同一输出目录 | 竞态条件下的损坏构建(Invalid build) |
| **缺少依赖声明** | 代码生成器输出的文件内容变了但输出文件名不变 | 下游产物不更新 |

**Blaze（Google内部构建工具）的设计者意识到：增量构建正确性的前提是"我们知道所有输入"**。

### 8.2 封闭(Hermetic)构建原则

Bazel的核心原则——**封闭性(Hermeticity)**：

> **一个构建操作的所有输入——源代码、工具链、环境变量、系统头文件——必须被显式声明且被版本控制。**

```
❌ 非封闭构建（传统）
main.c ──→ gcc ──→ main.o
  ↑          ↑       ↑
 源代码    $(CC)是什么？  输出路径写在哪？
           CFLAGS从哪里来？
           /usr/include 内容可能变吗？
           
✅ 封闭构建（Bazel）
main.c ──→ gcc (来自@toolchain_linux//:gcc) ──→ main.o
system-headers (来自@syslibs//:headers)
CFLAGS (来自BUILD文件)

所有输入被内容寻址 → 输入哈希不变 = 输出不变
```

### 8.3 Bazel的核心机制

#### 1. 内容寻址(Content-Addressable)

```
输入文件内容 ──→ SHA256 ──→ 构建动作的输入签名
工具链内容   ──→ SHA256 ──→ 构建动作的输入签名
编译命令参数 ──→ SHA256 ──→ 构建动作的输入签名

输出缓存 = f(输入签名)
输入签名不变 = 跳过构建动作 = 零成本增量
```

**这是与Make/CMake时间戳机制的质变**——Bazel不看文件时间戳，只看文件**内容哈希**。

#### 2. STarlark构建语言

Bazel使用 Python 方言 Starlark 作为构建语言：

```python
# BUILD
load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")

cc_library(
    name = "utils",
    srcs = ["utils.cc"],
    hdrs = ["utils.h"],
    visibility = ["//main:__pkg__"],
)

cc_binary(
    name = "myapp",
    srcs = ["main.cc"],
    deps = [":utils", "@json//:json"],
)
```

**关键特性**：
- **纯度(Purity)**：Starlark函数不能执行I/O——构建描述是纯函数式
- **确定性的(Deterministic)**：相同输入 → 相同输出
- **沙箱执行(Sandboxing)**：每个构建动作在独立Sandbox中执行，只能访问显式声明的输入

#### 3. 远程缓存与执行

```
开发者A ──构建──→ 输出缓冲区 ──缓存──→ 远程缓存服务器
开发者B ──修改──→ 相同输入签名 ──命中──→ 直接下载缓存

远程执行：
  开发者 → 提交构建动作 → 远程集群执行
                        → 返回二进制结果
```

**效果**：整个组织共享构建缓存，"已经有人编译过"的代码不需要重复编译。

#### 4. 构建图 + 动作图

Bazel维护两个层次的图：

| 概念 | 层次 | 粒度 | 评估时机 |
|:-----|:-----|:----:|:---------|
| **BULD图** | 构建目标(二进制、库、测试) | 文件级 | 配置时 |
| **动作图(Action Graph)** | 单个编译命令(cc -c、ar、link) | 输入/输出文件 | 执行时 |

### 8.4 Bazel家族：Buck > Pants > Please

| 工具 | 创造者 | 语言 | 特点 | 现状 |
|:-----|:-------|:-----|:-----|:-----|
| **Bazel** | Google | Java | 最完整，Google内部数十年打磨 | 开源活跃(2015-) |
| **Buck** | Meta | Java | 比Bazel早开源(2013)，类似理念 | 被Buck2取代 |
| **Pants** | Twitter/社区 | Python | 轻量级Bazel替代，配置更简单 | 仍活跃(v2.x) |
| **Please** | ThoughtMachine | Go | 单二进制、极简配置、依赖少 | 小众但稳定 |
| **Buck2** | Meta (2023) | Rust | Buck的重写版，性能更高 | 2023开源 |

```python
# Pants BUILD 示例（类似Bazel但更简洁）
python_sources(
    name="lib",
    sources=["*.py"],
)

pex_binary(
    name="myapp",
    entry_point="main.py",
    dependencies=[":lib"],
)
```

### 8.5 Bazel的代价

| 代价 | 说明 | 严重性 |
|:-----|:-----|:-------|
| **配置复杂度** | 需要为每种语言写规则的 `WORKSPACE` 配置，初始搭建成本高 | 🔴 |
| **非Hermetic场景** | Python/pip依赖的Heretic化困难（pip本身不是Hermetic的） | 🔴 |
| **资源占用** | 守护进程(IJServer/Bazel Server)内存消耗大 | 🟡 |
| **学习曲线** | Starlark、Workspace、CROSSTOOL等概念体系陡峭 | 🟡 |
| **小型项目过重** | 5000行以下的简单项目不值得引入 | 🟡 |
| **生态分裂** | 每个公司/语言/场景的规则集不同（rules_go/rules_rust/rules_python等） | 🟡 |

---

## 9. 语言原生构建工具

### 9.1 Cargo (Rust)

Cargo是Rust的构建系统和包管理器，代表了**语言内置构建工具**的最高水平。

```toml
# Cargo.toml
[package]
name = "myapp"
version = "0.1.0"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["full"] }

[profile.release]
opt-level = 3
lto = true
```

**Cargo为什么成功**：

| 能力 | 实现 | 意义 |
|:-----|:-----|:-----|
| **依赖解析** | `semver` 版本解析 + 锁文件 `Cargo.lock` | 确定性的依赖版本 |
| **语义化版本** | `^1.0`、`~1.2`、`=1.3.4` | 符合语义化版本2.0 |
| **构建脚本** | `build.rs` | 在构建前执行任意Rust代码 |
| **条件编译** | `cfg(target_os = "linux")` | 声明式而非命令式 |
| **测试集成** | `cargo test` | 原生支持单元测试/集成测试 |
| **文档生成** | `cargo doc` | 自动生成API文档 |
| **工作空间** | 多crate协作 | 类似Bazel的monorepo支持 |
| **注册表** | crates.io | 统一的包体发布平台 |

**与Bazel的对比**：Cargo是"语言原生 × 封闭性"的轻量化版本，它不需要Starlark配置，因为Rust编译器本身提供了足够的信息。

### 9.2 Go Modules

Go的构建系统设计哲学与Rust相反——**极简主义**：

```go
// go.mod
module github.com/user/myapp

go 1.21

require (
    github.com/gorilla/mux v1.8.0
)
```

**关键设计决策**：
- **所有依赖作为源码下载**：不需要二进制包管理
- **GOPATH/cache**：全局模块缓存，复用跨项目
- **最小版本选择(MVS)**：不求解依赖的"最大兼容版本"，而是选"所有依赖都能接受的最小版本"
- **快**：Go编译器本身速度快（秒级编译中型项目）

### 9.3 Gradle (JVM生态)

```groovy
// build.gradle.kts (Kotlin DSL)
plugins {
    java
    application
    id("com.github.johnrengelman.shadow") version "7.1.0"
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.google.guava:guava:31.1-jre")
    testImplementation("org.junit.jupiter:junit-jupiter:5.9.0")
}

application {
    mainClass.set("com.example.Main")
}

// 构建阶段自定义
tasks.register<Copy>("copyToLib") {
    from(configurations.runtimeClasspath)
    into("$buildDir/lib")
}
```

**Gradle的核心创新——增量构建的图级缓存**：

| 机制 | 说明 |
|:-----|:-----|
| **输入快照** | 每个Task记录输入文件的哈希值 |
| **输出缓存** | 如果Task输入未变，跳过整个Task |
| **构建缓存** | 跨项目共享（类似Bazel远程缓存） |
| **配置缓存** | 构建配置本身缓存（避免每次重新配置） |
| **守护进程** | Gradle Daemon保持JVM热启动 |

**与Maven的区别**：

| 维度 | Maven | Gradle |
|:-----|:------|:-------|
| **范式** | 声明式(Convention over Configuration) | 命令式+声明式(Groovy/Kotlin DSL) |
| **构建模型** | 三阶段(生命周期) | 任务DAG |
| **增量** | 弱（mtime基础） | 强（内容哈希基础） |
| **性能** | 慢（XML解析+无并行） | 快（守护进程+并行+缓存） |
| **学习曲线** | 低（XML熟悉） | 中等（DSL灵活但复杂） |
| **灵活性** | 低（生命周期固定） | 极高（自定义Task任意定义） |

### 9.4 Xmake (C/C++)

Xmake 是一个较新的C/C++构建工具，尝试融合Lua配置的简洁和现代化构建系统的能力：

```lua
-- xmake.lua
target("myapp")
    set_kind("binary")
    add_files("src/*.cpp")
    add_packages("boost", "fmt")
    add_includedirs("include")

    if is_plat("linux") then
        add_syslinks("pthread")
    end

    if is_mode("debug") then
        set_symbols("debug")
        set_optimize("none")
    end
```

**Xmake的优势**：Lua配置天然比CMake语法更清晰；中文文档完善；跨平台支持好。但社区生态远不及CMake。

### 9.5 Vcpkg/Conan (依赖管理)

严格来说这是**包管理器**而非构建工具，但与现代构建系统深度绑定：

```cmake
# vcpkg + CMake
find_package(fmt CONFIG REQUIRED)
target_link_libraries(myapp PRIVATE fmt::fmt)
```

```python
# conanfile.py
class MyApp(ConanFile):
    requires = "fmt/9.1.0", "boost/1.81.0"
    generators = "CMakeDeps"
```

| 工具 | 语言 | 特点 | 与构建系统的绑定 |
|:-----|:-----|:-----|:----------------|
| **vcpkg** | C++(微软) | 源码分发+cache，Windows支持好 | CMake原生 |
| **Conan** | C++(JFrog) | 二进制包+源码，可私有部署 | CMake/Meson/自定义 |
| **Spack** | HPC | 多版本共存，高度可配置 | 独立，CMake封装 |
| **Cargo** | Rust | 统一注册表(crates.io) | 构建系统内置 |
| **npm/pip** | JS/Python | 扁平依赖树 | 语言生态内置 |

---

## 10. 新兴边界工具

### 10.1 Buck2 (Meta)

Meta在2023年开源了Buck2——**用Rust重写Buck**。

```python
# BUCK
python_library(
    name = "mylib",
    srcs = ["mylib.py"],
    deps = [":utils"],
)
```

**Buck2 vs Bazel关键差异**：

| 特性 | Bazel | Buck2 |
|:-----|:------|:------|
| 实现语言 | Java | Rust |
| 规则引擎 | Starlark | Starlark (改进版) |
| 沙箱 | 文件系统Sandbox | 用户态Sandbox (更轻量) |
| 远程执行 | gRPC | gRPC + REAPI |
| 动态调度 | 基于关键路径 | 基于层级调度 |
| 并发模型 | 多线程 | async/await (tokio) |
| 冷启动 | 慢(Java) | 快(Rust) |

### 10.2 Soong + Blueprint (Android)

Android的构建系统经历多次演变：`Make → Android.mk → Soong(Blueprint) → Bazel(部分)`。

```bp
// Android.bp (Blueprint格式)
cc_binary {
    name: "myapp",
    srcs: ["main.cc", "utils.cc"],
    shared_libs: ["libcutils", "libbinder"],
    cflags: ["-Wall"],
}
```

Blueprint是Bazel的前身之一——**声明式依赖描述 + Ninja后端执行**。

### 10.3 GN + Ninja (Chromium)

Chromium使用GN（Generate Ninja）作为元构建工具：

```gn
# BUILD.gn
static_library("utils") {
  sources = [
    "utils.cc",
    "utils.h",
  ]
}

executable("chrome") {
  sources = [ "main.cc" ]
  deps = [ ":utils" ]
}
```

**GN的设计哲学**：
- 生成Ninja文件，不直接构建
- 语法简洁（比CMake简单很多）
- 为Chromium的超大项目优化（~30万源文件）
- 不支持递归遍历目录（必须显式引用）
- 跨平台内置（支持iOS/Android/Linux/Windows/Mac）

---

## 11. 全谱系对比矩阵

### 11.1 核心维度对比

| 工具 | 年代 | 构建模型 | 增量机制 | 并行 | 跨平台 | 配置范式 | 主要领域 |
|:-----|:----:|:---------|:---------|:----:|:------:|:---------|:---------|
| **Make** | 1976 | 依赖驱动 | 时间戳 | ✅ | ❌(Unix-only) | 命令式 | 通用/系统软件 |
| **Autotools** | 1991 | 元构建→Make | 同Make | 🟡 | ❌(Unix-only) | M4宏 | Unix开源软件 |
| **CMake** | 2000 | **元构建** | 时间戳+生成器 | ✅ | ✅ | 自定义命令式 | 跨平台C/C++ |
| **Ninja** | 2012 | 依赖驱动 | **内容+时间戳** | ✅✅ | ✅(不做平台抽象) | 极简声明式 | 构建后端 |
| **Meson** | 2013 | **元构建→Ninja** | 完整DAG | ✅✅ | ✅ | 声明式(类Python) | 现代C/C++ |
| **Bazel** | 2015 | 依赖驱动(Hermetic) | **内容哈希** | ✅✅✅ | ✅ | Starlark纯函数 | 大型Monorepo |
| **Cargo** | 2015 | 语言原生 | 内容哈希 | ✅ | ✅(rustc绑定) | TOML声明式 | Rust生态 |
| **Gradle** | 2008 | 任务DAG | **输入快照** | ✅✅ | ✅ | Groovy/KotlinDSL | JVM/Android |
| **Xmake** | 2015 | 元构建 | 时间戳+哈希 | ✅ | ✅ | Lua | C/C++ |
| **Buck2** | 2023 | Hermetic | 内容哈希 | ✅✅✅ | ✅ | Starlark | Meta monorepo |
| **GN** | 2014 | 元构建→Ninja | 同Ninja | ✅✅ | ✅ | 自定义声明式 | Chromium |
| **Maven** | 2004 | 生命周期 | 时间戳 | 🟡 | ✅ | XML声明式 | Java |

### 11.2 配置格式对比

| 工具 | 格式 | 类型系统 | 可读性 | 可调试性 | 动态能力 |
|:-----|:-----|:--------:|:------:|:--------:|:--------:|
| Make | 自定义命令式 | 无(全是字符串) | 🟡 | 🟡 | ✅极高 |
| Autotools (M4) | M4宏语言 | 无 | 🔴 | 🔴 | 🟡 |
| CMake | 自定义 | 无(全是字符串) | 🟡 | 🔴 | ✅高 |
| Meson | 类Python | 基础(int/list/bool) | ✅ | 🟡 | 🟡 |
| Bazel (Starlark) | Python子集 | 基本类型+dict | ✅ | 🟡 | ❌纯函数 |
| Gradle (Kotlin) | Kotlin DSL | 完整类型系统 | ✅ | ✅ | ✅极高 |
| Xmake (Lua) | Lua | 动态类型 | ✅ | 🟡 | ✅高 |
| TOML (Cargo) | TOML | 静态(由语言定义) | ✅✅ | ✅ | ❌纯声明式 |

### 11.3 增量机制对比

| 工具 | 判断依据 | 正确性 | 性能 | 可复现性 |
|:-----|:---------|:------:|:----:|:--------:|
| **时间戳(mtime)** | 文件修改时间 | ❌抖动导致全量重编 | 极快(stat调用) | ❌ |
| **文件内容哈希** | SHA256文件内容 | ✅内容不变=不重编 | 中(需全部hash) | ✅ |
| **输入签名** | 所有输入内容+命令参数 | ✅彻底 | 中(依赖图大) | ✅✅ |
| **Task输入快照** | 每个Task的输入文件哈希 | ✅ | 高(只hash声明输入) | ✅ |

### 11.4 选型决策树

```
项目需要构建工具吗？
├── 单文件脚本
│   └── 不需要 👉 直接 cc/gcc/rustc
├── 小型项目(<5000行)
│   ├── Rust 👉 Cargo
│   ├── Go  👉 go build
│   ├── Java 👉 Maven/Gradle
│   └── C/C++ 👉 CMake (或直接Make)
├── 中型项目(5k~100k行)
│   ├── 跨平台需要强 👉 CMake + Ninja
│   ├── 追求开发体验 👉 Meson (C/C++)
│   └── JVM生态 👉 Gradle
├── 大型项目(100k~1M行)
│   ├── C/C++ 👉 CMake + Ninja
│   └── 多语言混合 👉 Bazel / Pants
├── 巨量项目(>1M行, monorepo)
│   ├── Google风格 👉 Bazel
│   ├── Meta风格  👉 Buck2
│   ├── Android   👉 Soong → Bazel
│   ├── Chromium  👉 GN + Ninja
│   ├── LLVM/ROS  👉 CMake + Ninja
│   └── JVM monorepo 👉 Gradle
└── HPC / MPI / Fortran
    └── CMake + Make (老工具链兼容最好)
```

---

## 12. 总结与趋势

### 12.1 六个演化的根本驱动力

驱动构建工具演化的六个核心力量：

```
想解决的问题                       解决方案                  代表
───────────────────────────────────────────────────────────
"每次都全量重编太慢"    →  增量构建(显式DAG)            → Make
"每个Unix不一样"        →  自动平台检测                  → Autotools
"Windows也想要"         →  跨平台元构建                  → CMake
"增量构建不够快"        →  极简构建后端                  → Ninja
"配置语法太烂"          →  现代构建语言                  → Meson
"增量构建不正确"        →  封闭性+内容寻址               → Bazel
"语言应该有自带的"      →  语言原生构建工具              → Cargo/go build
```

### 12.2 未来趋势

1. **Hermetic > Non-hermetic**：Bazel/Buck2的封闭构建模式将逐渐普及，未来新工具默认支持内容寻址缓存

2. **语言原生 > 通用工具**：Rust/Cargo的成功表明，深度集成编译器的构建工具比通用工具更适合该语言。Go的 `go build` 更极端——几乎不需要额外的构建描述

3. **远程执行标准化**：REAPI(Remote Execution API)正在成为云构建的标准协议，Bazel/Buck2/Cargo/Nix都在朝这个方向对齐

4. **AI辅助构建**：LLM已经开始被用于自动生成 BUILD/CMakeLists.txt 文件，自动修复构建错误

5. **从"编译"到"管道"**：构建工具正在扩大范围——不仅仅是编译和链接，还包括测试、打包、部署、格式化、lint →"CI/CD本地化"

6. **PMM (Package Manager + Build System)**：Cargo/Gradle的模式预示了未来——构建系统即包管理器，包管理器即构建系统

---

## 参考来源

[1] Feldman, S. I. — "Make — A Program for Maintaining Computer Programs", Software: Practice and Experience, 1979
[2] GNU Make Manual, Free Software Foundation, https://www.gnu.org/software/make/manual/
[3] Vaughan, G. V. et al. — "GNU Autoconf, Automake, and Libtool", Sams Publishing, 2000
[4] Martin, E. — "The Ninja Build System", https://ninja-build.org/manual.html, 2012
[5] CMake Documentation, Kitware, https://cmake.org/documentation/
[6] Pakkanen, J. — "The Meson Build System", https://mesonbuild.com/, 2013
[7] Bazel Build System — https://bazel.build/, Google, 2015
[8] Cargo — The Rust Package Manager, https://doc.rust-lang.org/cargo/
[9] Gradle Build Tool — https://gradle.org/, 2008
[10] Xmake — https://xmake.io/, 2015
[11] Pants Build System — https://www.pantsbuild.org/, Twitter/Community
[12] Buck2 — https://buck2.build/, Meta, 2023
[13] GN — Generate Ninja, https://gn.googlesource.com/gn/, Chromium Project
[14] Soong Build System — Android Open Source Project, https://source.android.com/docs/setup/build
[15] Maven — Apache Software Foundation, https://maven.apache.org/, 2004
[16] Nix Package Manager & NixOS — https://nixos.org/, 2003
[17] Conan C/C++ Package Manager — https://conan.io/, JFrog
[18] vcpkg — Microsoft, https://vcpkg.io/, 2016
[19] Spack — https://spack.io/, LLNL
[20] Miller, A. — "A Build System is a Directed Acyclic Graph", July 2019
[21] Berlind, I. — "Why Google Stores Billions of Lines of Code in a Single Repository", Communications of the ACM, 2016
[22] Magee, T. — "Modern Build Systems: A Comparison", 2020
[23] REMOTE EXECUTION API — https://github.com/bazelbuild/remote-apis, Bazel Community

### 相关知识库文档

- [CLI三次演进](02_rd/01_basic-concepts/cli-evolution-three-generations.md) — 命令行工具代际范式与本报告"演化驱动力"的分析方法互补
- [版本方法与兼容性方案全景分析](02_rd/01_basic-concepts/versioning-and-compatibility-methodology.md) — 语义化版本(SemVer)与Cargo依赖解析相关
- [工程活动全景指南](02_rd/01_basic-concepts/engineering-activities-compass.md) — 构建活动在工程全景中的定位

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-07-02 | v1.0 | 首次创建，覆盖手工编译/Make/Autotools/CMake/Ninja/Meson/Bazel/Cargo/Gradle/Xmake 等构建工具，6大维度对比，含选型决策树与未来趋势分析 |
