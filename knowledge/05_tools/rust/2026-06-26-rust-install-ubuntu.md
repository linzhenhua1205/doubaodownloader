# Ubuntu 24.04 安装 Rust 教程

> **概要**: Ubuntu 24.04安装Rust教程，含国内源配置与Cargo镜像代理设置
>
> **关键词**: Rust安装 · Ubuntu · rustup · Cargo镜像 · 国内源

---

## 📑 目录

- [1. 切换国内源（推荐先配）](#1-切换国内源推荐先配)
  - [临时设置（当前终端生效）](#临时设置当前终端生效)
  - [永久写入 `~/.bash_profile`](#永久写入-bash_profile)
- [2. 安装 `rustc` 和 `rustup`](#2-安装-rustc-和-rustup)
  - [❌ 官方脚本（极慢，不推荐）](#官方脚本极慢不推荐)
  - [✅ 阿里云脚本（推荐）](#阿里云脚本推荐)
  - [验证安装](#验证安装)
- [3. 配置 Cargo 包管理镜像代理](#3-配置-cargo-包管理镜像代理)
  - [中科大国内容器镜像](#中科大国内容器镜像)
  - [阿里云容器镜像](#阿里云容器镜像)
  - [离线包 / 本地源](#离线包-本地源)
- [4. 更新 rustup](#4-更新-rustup)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 1. 切换国内源（推荐先配）

### 临时设置（当前终端生效）

```bash
# 中科大源
export RUSTUP_DIST_SERVER=https://mirrors.ustc.edu.cn/rust-static
export RUSTUP_UPDATE_ROOT=https://mirrors.ustc.edu.cn/rust-static/rustup

# 阿里云源
export RUSTUP_UPDATE_ROOT=https://mirrors.aliyun.com/rustup/rustup
export RUSTUP_DIST_SERVER=https://mirrors.aliyun.com/rustup
```

### 永久写入 `~/.bash_profile`

```bash
echo 'export RUSTUP_UPDATE_ROOT=https://mirrors.aliyun.com/rustup/rustup' >> ~/.bash_profile
echo 'export RUSTUP_DIST_SERVER=https://mirrors.aliyun.com/rustup' >> ~/.bash_profile
source ~/.bash_profile
```

---

## 2. 安装 `rustc` 和 `rustup`

### ❌ 官方脚本（极慢，不推荐）

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### ✅ 阿里云脚本（推荐）

```bash
curl --proto '=https' --tlsv1.2 -sSf https://mirrors.aliyun.com/repo/rust/rustup-init.sh | sh
```

- 安装时会提示选择路径，输入 `1`（默认安装）即可
- 安装成功后提示：`Rust is installed now. Great!`

### 验证安装

```bash
rustc --version   # 输出: rustc 1.86.0 (05f9846f8 2025-03-31)
cargo --version   # 输出: cargo 1.86.0 (adf9b6ad1 2025-02-28)
```

---

## 3. 配置 Cargo 包管理镜像代理

编辑 `$HOME/.cargo/config`：

### 中科大国内容器镜像

```toml
[source.crates-io]
registry = "https://github.com/rust-lang/crates.io-index"
replace-with = 'ustc'

[source.ustc]
registry = "git://mirrors.ustc.edu.cn/crates.io-index"
```

### 阿里云容器镜像

```toml
[registry]
index = "https://github.com/rust-lang/crates.io-index"

[source.crates-io]
replace-with = 'aliyun'

[source.aliyun]
registry = "sparse+https://mirrors.aliyun.com/crates.io-index/"
```

> 📌 `sparse+` 协议是 Cargo 稀疏注册协议，比 git clone 整个 index 快得多。配置后 `cargo build` 自动走镜像下载依赖。

### 离线包 / 本地源

可为单个项目配置本地 `.cargo/config.toml`，指向本地缓存的 crate 目录。

---

## 4. 更新 rustup

```bash
rustup self update
rustup component add rls rust-analysis rust-src
```

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

- 来源: [博客园 - hugingface](https://www.cnblogs.com/tryst/p/18853948) (2025-04-29)
- 来源: [Rust Crates](https://crates.io/)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
