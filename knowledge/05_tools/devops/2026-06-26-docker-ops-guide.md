# Docker 典型操作速查与排障指南

> **概要**: Docker典型操作速查与排障指南，含多架构构建、镜像源与K8s部署
>
> **关键词**: Docker · 多架构构建 · 镜像管理 · K8s · 容器排障

---

## 📑 目录

- [一、镜像管理](#一镜像管理)
  - [1.1 删除无用镜像（清理磁盘空间）](#11-删除无用镜像清理磁盘空间)
  - [1.2 镜像标签与批量删除](#12-镜像标签与批量删除)
  - [1.3 镜像导入导出（离线传输）](#13-镜像导入导出离线传输)
- [二、跨平台多架构镜像构建（✨ 高频场景）](#二跨平台多架构镜像构建-高频场景)
  - [2.1 前置条件：启用 QEMU 模拟](#21-前置条件启用-qemu-模拟)
  - [2.2 创建构建器实例](#22-创建构建器实例)
  - [2.3 一次构建多平台](#23-一次构建多平台)
  - [2.4 Dockerfile 跨平台兼容写法](#24-dockerfile-跨平台兼容写法)
  - [2.5 查看镜像架构信息](#25-查看镜像架构信息)
- [三、更换镜像源（加速拉取）](#三更换镜像源加速拉取)
  - [3.1 Docker Engine 配置（Linux）](#31-docker-engine-配置linux)
  - [3.2 macOS / Windows (WSL2)](#32-macos-windows-wsl2)
  - [3.3 拉取时临时切换源](#33-拉取时临时切换源)
  - [3.4 自建私有 Registry](#34-自建私有-registry)
- [四、容器运行与生命周期](#四容器运行与生命周期)
  - [4.1 常用运行参数](#41-常用运行参数)
  - [4.2 进入容器调试](#42-进入容器调试)
  - [4.3 容器导出与导入](#43-容器导出与导入)
- [五、Kubernetes 指定命名空间运行特定镜像](#五kubernetes-指定命名空间运行特定镜像)
  - [5.1 创建命名空间](#51-创建命名空间)
  - [5.2 在指定命名空间部署](#52-在指定命名空间部署)
  - [5.3 避免忘记指定 namespace](#53-避免忘记指定-namespace)
  - [5.4 从特定 ImageRegistry 拉取](#54-从特定-imageregistry-拉取)
- [六、启动失败问题定位（🔍 高频排障）](#六启动失败问题定位-高频排障)
  - [6.1 快速排查三板斧](#61-快速排查三板斧)
  - [6.2 常见启动失败原因](#62-常见启动失败原因)
  - [6.3 Debug 模式启动](#63-debug-模式启动)
  - [6.4 K8s 中 Pod 启动排障](#64-k8s-中-pod-启动排障)
- [七、权限相关问题](#七权限相关问题)
  - [7.1 Docker Socket 权限](#71-docker-socket-权限)
  - [7.2 挂载卷权限问题](#72-挂载卷权限问题)
  - [7.3 容器内权限不足](#73-容器内权限不足)
  - [7.4 K8s 权限问题](#74-k8s-权限问题)
  - [7.5 查看和修改容器权限](#75-查看和修改容器权限)
- [八、网络问题](#八网络问题)
  - [8.1 容器网络模型速查](#81-容器网络模型速查)
  - [8.2 主机网络模式](#82-主机网络模式)
  - [8.3 DNS 与代理问题](#83-dns-与代理问题)
- [九、常用 Dockerfile 最佳实践](#九常用-dockerfile-最佳实践)
- [十、容器日志管理](#十容器日志管理)
- [附：快速排障流程图](#附快速排障流程图)
- [关联知识](#关联知识)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、镜像管理

### 1.1 删除无用镜像（清理磁盘空间）

```bash
# 清理 dangling 镜像（无标签、无引用的 <none>:<none>）
docker image prune

# 清理所有未使用的镜像（未被任何容器引用的）
docker image prune -a

# 清理所有未使用的资源（容器、网络、镜像、构建缓存）
docker system prune

# 最强清理（含 volumes，⚠️ 数据卷会丢失）
docker system prune -a --volumes

# 查看磁盘占用
docker system df
```

**安全建议**: 先 `-a` 前加 `--filter "until=24h"` 保留最近 24h 的镜像。

### 1.2 镜像标签与批量删除

```bash
# 列出所有镜像
docker images

# 按条件过滤
docker images --filter "reference=*/dev-*" --format "{{.Repository}}:{{.Tag}}"

# 批量删除特定仓库的镜像
docker images | grep "my-registry.cn/" | awk '{print $3}' | xargs docker rmi

# 删除所有 dangling 镜像（none标签）
docker rmi $(docker images -f "dangling=true" -q)
```

### 1.3 镜像导入导出（离线传输）

```bash
# 导出为 tar 文件
docker save nginx:latest -o nginx.tar

# 从 tar 文件导入
docker load -i nginx.tar

# 查看镜像分层
docker history nginx:latest
```

---

## 二、跨平台多架构镜像构建（✨ 高频场景）

### 2.1 前置条件：启用 QEMU 模拟

```bash
# 安装 QEMU 模拟器（Linux）
docker run --privileged --rm tonistiigi/binfmt --install all

# 确认支持的架构
docker buildx ls
```

### 2.2 创建构建器实例

```bash
# 创建多架构构建器
docker buildx create --name multiarch --driver docker-container --use

# 启动构建器
docker buildx inspect --bootstrap
```

### 2.3 一次构建多平台

```bash
# 构建并推送多平台镜像（需要登录 registry）
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t myapp:latest \
  --push .

# 仅构建不推送（需指定 --load，但仅支持单平台）
docker buildx build \
  --platform linux/amd64 \
  -t myapp:latest \
  --load .
```

> **⚠️ 注意**: `--load` 不支持多平台同时构建，`--push` 可以。本地测试先用单平台 `--load`，CI/CD 用 `--push` 直接推送多平台。

### 2.4 Dockerfile 跨平台兼容写法

```dockerfile
# ❌ 不兼容写法（硬编码路径）
RUN apt-get update && apt-get install -y libssl-dev

# ✅ 兼容写法（使用 ARG 判断架构）
ARG TARGETARCH
RUN if [ "$TARGETARCH" = "arm64" ]; then \
      echo "arm64 specific setup"; \
    else \
      echo "amd64 specific setup"; \
    fi

# 📌 下载二进制时按架构区分
RUN curl -LO "https://example.com/tool-${TARGETARCH}.tar.gz"
```

### 2.5 查看镜像架构信息

```bash
# 查看镜像支持的架构
docker buildx imagetools inspect myapp:latest

# 查看本地镜像架构
docker inspect myapp:latest --format '{{.Architecture}}'
```

---

## 三、更换镜像源（加速拉取）

### 3.1 Docker Engine 配置（Linux）

编辑 `/etc/docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "insecure-registries": [
    "192.168.1.100:5000"
  ]
}
```

```bash
# 生效
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证
docker info | grep "Registry Mirrors"
```

### 3.2 macOS / Windows (WSL2)

Docker Desktop → Settings → Docker Engine → 编辑 `daemon.json`，同上。
或者通过 Docker Desktop 界面：Settings → Resources → Advanced → Registry mirrors。

### 3.3 拉取时临时切换源

```bash
# 从特定仓库拉取（非 Docker Hub）
docker pull registry.cn-hangzhou.aliyuncs.com/library/nginx:latest

# 添加 tag 重命名
docker tag registry.cn-hangzhou.aliyuncs.com/library/nginx:latest nginx:latest
```

### 3.4 自建私有 Registry

```bash
# 启动 Registry
docker run -d -p 5000:5000 --name registry registry:2

# 推送镜像
docker tag myapp:latest localhost:5000/myapp:latest
docker push localhost:5000/myapp:latest

# 拉取
docker pull localhost:5000/myapp:latest
```

---

## 四、容器运行与生命周期

### 4.1 常用运行参数

```bash
# 交互运行并自动删除
docker run -it --rm alpine sh

# 后台运行 + 端口映射 + 命名
docker run -d --name my-web -p 8080:80 nginx:latest

# 挂载目录 + 时区
docker run -d \
  --name my-app \
  -p 3000:3000 \
  -v /host/path:/container/path \
  -v /etc/localtime:/etc/localtime:ro \
  -e NODE_ENV=production \
  --restart unless-stopped \
  myapp:latest

# 资源限制
docker run -d \
  --memory=512m \
  --cpus=1.5 \
  --memory-reservation=256m \
  nginx:latest
```

### 4.2 进入容器调试

```bash
# 进入运行中容器
docker exec -it container_name bash

# 无 bash 时用 sh
docker exec -it container_name sh

# 以 root 进入
docker exec -u root -it container_name bash

# 查看运行进程
docker top container_name

# 查看容器日志
docker logs -f --tail 100 container_name
```

### 4.3 容器导出与导入

```bash
# 导出容器为 tar
docker export my_container -o my_container.tar

# 从 tar 导入为镜像
cat my_container.tar | docker import - my_image:latest
```

---

## 五、Kubernetes 指定命名空间运行特定镜像

### 5.1 创建命名空间

```bash
kubectl create namespace my-namespace

# 或通过 YAML
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
EOF
```

### 5.2 在指定命名空间部署

```bash
# 运行一个 Pod 在指定命名空间
kubectl run my-pod \
  --image=nginx:latest \
  --namespace=my-namespace \
  --restart=Never \
  -- /bin/sh -c "while true; do echo hello; sleep 10; done"

# 创建 Deployment
kubectl create deployment my-deploy \
  --image=myapp:latest \
  --namespace=my-namespace \
  --replicas=3

# 暴露服务
kubectl expose deployment my-deploy \
  --name=my-svc \
  --port=80 \
  --target-port=8080 \
  --namespace=my-namespace
```

### 5.3 避免忘记指定 namespace

```bash
# 设置默认 namespace（避免每次加 --namespace）
kubectl config set-context --current --namespace=my-namespace

# 查看当前 context 的 namespace
kubectl config view --minify | grep namespace:

# 给 kubectl 加别名 + 自动补全
alias k='kubectl -n my-namespace'
```

### 5.4 从特定 ImageRegistry 拉取

```bash
# 使用私有仓库时需要 ImagePullSecret
kubectl create secret docker-registry my-reg-secret \
  --docker-server=my-registry.cn \
  --docker-username=user \
  --docker-password=pass \
  --namespace=my-namespace

# 在 Deployment 中引用
kubectl set image-deployment my-deploy my-container=my-registry.cn/myapp:v2
kubectl patch deployment my-deploy -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"my-reg-secret"}]}}}}'
```

---

## 六、启动失败问题定位（🔍 高频排障）

### 6.1 快速排查三板斧

```bash
# ① 看容器状态
docker ps -a | grep <name>

# ② 看退出日志
docker logs <container_id>

# ③ 看详细信息（ExitCode 是核心线索）
docker inspect <container_id> | jq '.[0].State'
# ExitCode: 0=正常, 1=通用错误, 137=SIGKILL(OOM/超时), 139=SIGSEGV(段错误), 143=SIGTERM(优雅退出)
```

### 6.2 常见启动失败原因

| 现象 | ExitCode | 常见原因 | 解决 |
|:----|:--------:|:---------|:-----|
| 容器启动后立即退出 | 1 | 入口命令执行失败 | 改 `CMD` 为 `tail -f /dev/null` 或 `sleep infinity` 调试 |
| 容器闪退、无日志 | 0 | 后台进程 fork 后父进程退出 | 用 `CMD ["sh", "-c", "your-daemon & wait"]` |
| 被系统杀死 | 137 | **OOM（内存超限）** | 加 `--memory` 限制或用 `docker stats` 观察 |
| 段错误崩溃 | 139 | 二进制不兼容架构 | 检查镜像架构 vs 宿主机架构（`uname -m`） |
| 端口冲突 | 125 | 宿主机端口已被占用 | 换端口或 `lsof -i :<port>` 查占用 |
| `exec format error` | 1 | **架构不匹配**（如 arm64 镜像跑在 amd64） | 用 `--platform linux/amd64` 指定 |
| 文件系统只读 | 1 | 镜像内写操作未定义 Volume | 加 `-v` 挂载或改代码写 `/tmp` |
| `no such file or directory`| 1 | 入口脚本缺少 shebang 或权限 | 加 `#!/bin/sh` 或用 `ENTRYPOINT ["sh", "file.sh"]` |

### 6.3 Debug 模式启动

```bash
# 覆盖入口，以交互式 shell 启动
docker run -it --rm --entrypoint sh myimage:latest

# 如果镜像无 shell，加一层 shell 镜像
docker run -it --rm --entrypoint sh alpine:latest

# 挂载全部权限调试
docker run --rm -it --privileged --pid=host myimage:latest bash
```

### 6.4 K8s 中 Pod 启动排障

```bash
# 查看 Pod 状态和事件
kubectl describe pod my-pod -n my-namespace

# 查看容器日志（含之前退出的）
kubectl logs my-pod -n my-namespace --previous

# Debug 临时 Pod
kubectl run debug-pod --rm -it \
  --image=nicolaka/netshoot \
  --namespace=my-namespace \
  -- /bin/bash

# Pod 一直 Pending
kubectl describe pod my-pod | grep -A10 Events
```

---

## 七、权限相关问题

### 7.1 Docker Socket 权限

```bash
# 错误：permission denied while trying to connect
# 原因：当前用户不在 docker 组

# ✅ 方案一：加入 docker 组
sudo usermod -aG docker $USER
newgrp docker  # 或退出重新登录

# ✅ 方案二：sudo 运行（不推荐）
sudo docker ps

# ⚠️ 安全提示：docker 组等同于 root 权限
```

### 7.2 挂载卷权限问题

```bash
# 问题：容器内进程无法写入挂载目录
# 原因：容器内外 UID/GID 不一致

# ✅ 方案一：指定容器用户 UID
docker run -u $(id -u):$(id -g) -v $(pwd)/data:/data myapp

# ✅ 方案二：Dockerfile 中固定 UID
# RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser appuser
# USER appuser

# ✅ 方案三：宿主机目录赋予 777（不推荐生产）
chmod 777 ./data

# ✅ 方案四：Docker Desktop (macOS) 需在 Settings → File Sharing 中添加目录
```

### 7.3 容器内权限不足

```bash
# 问题：Operation not permitted
# 原因：容器默认以非特权用户运行

# 🔓 授予额外 capability
docker run --cap-add SYS_PTRACE --cap-add NET_ADMIN myapp

# 🔓 完全特权模式（不推荐生产）
docker run --privileged myapp

# 🔓 关闭 seccomp / AppArmor
docker run --security-opt seccomp=unconfined myapp

# 常见 capability 速查
# SYS_PTRACE  → strace/gdb 调试
# NET_ADMIN   → 网络配置
# SYS_ADMIN   → mount/命名空间操作
# SYS_NICE    → 调整进程优先级
# IPC_LOCK    → mlock 锁定内存
```

### 7.4 K8s 权限问题

```bash
# Pod 以 root 运行被拒绝（PodSecurityPolicy）
# 解决：Pod 中明确指定 securityContext
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  containers:
  - name: myapp
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
      readOnlyRootFilesystem: true
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

### 7.5 查看和修改容器权限

```bash
# 查看容器实际用户
docker exec myapp id

# 查看容器 capabilites
docker inspect myapp | jq '.[0].HostConfig.CapAdd'
docker inspect myapp | jq '.[0].HostConfig.Privileged'

# 修改运行中容器的权限（不重启！）
docker update --cpus=2 --memory=512m myapp
docker update --restart=unless-stopped myapp
```

---

## 八、网络问题

### 8.1 容器网络模型速查

```bash
# 查看网络列表
docker network ls

# 创建自定义网络（推荐，支持 DNS 解析）
docker network create --driver bridge my-network

# 指定网络运行
docker run -d --name app1 --network my-network myapp

# 同网络内容器间直接用容器名通信
# app1 可以直接 ping app2
```

### 8.2 主机网络模式

```bash
# 使用宿主机网络（性能优，无端口映射）
docker run --network host myapp

# 固定 IP 地址
docker run --network my-network --ip 172.20.0.10 myapp
```

### 8.3 DNS 与代理问题

```bash
# 容器内 DNS 配置
docker run --dns 8.8.8.8 --dns 114.114.114.114 myapp

# 配置 HTTP 代理（Docker build 时有用）
docker build --build-arg HTTP_PROXY=http://proxy:8080 \
             --build-arg HTTPS_PROXY=http://proxy:8080 \
             -t myapp .
```

---

## 九、常用 Dockerfile 最佳实践

```dockerfile
# 多阶段构建（减小镜像体积）
FROM golang:1.22 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o myapp .

FROM alpine:3.19
RUN addgroup -g 1000 appuser && adduser -u 1000 -G appuser -D appuser
COPY --from=builder /app/myapp /app/myapp
USER appuser
EXPOSE 8080
ENTRYPOINT ["/app/myapp"]

# 📦 常用精简 base 镜像大小对比
# alpine:3.19  ~ 7MB
# debian:12-slim ~ 80MB
# distroless/base  ~ 20MB
# gcr.io/distroless/static-debian12  ~ 2MB（纯静态编译）
```

---

## 十、容器日志管理

```bash
# 限制日志大小（全局配置 /etc/docker/daemon.json）
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# 实时查看日志
docker logs -f --timestamps container_name

# 按时间范围过滤
docker logs --since "2026-06-01T00:00:00" --until "2026-06-02T00:00:00" container_name

# 配合 grep
docker logs container_name 2>&1 | grep ERROR

# 获取日志文件路径
docker inspect --format='{{.LogPath}}' container_name
```

---

## 附：快速排障流程图

```text
容器启动失败
    |
    +- docker ps -a 看 Status
    |    |
    |    +- Exited (0)  -> 入口命令执行完退出
    |    |                  +- 改用 `CMD sleep infinity` 调试
    |    |
    |    +- Exited (1)  -> 进程错误
    |    |                  +- docker logs -> 看 STDERR
    |    |
    |    +- Exited (137) -> 被 SIGKILL 杀死
    |    |                  +- OOM -> docker inspect 看 OOMKilled: true
    |    |                  +- 超时 -> docker inspect 查看 State.FinishedAt
    |    |
    |    +- Exited (139) -> SIGSEGV 段错误
    |                       +- 检查架构 -> docker inspect Arch
    |
    +- docker inspect 看 State 详细
    |
    +- 最终手段：--entrypoint sh 进入容器调试
```

---

## 关联知识

- Kubernetes 基础操作 — （如已收录）
- 容器网络与 CNI 概述 — （如已收录）
- [研发工具总览](../../README.md)

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- Kubernetes 基础操作 — 关联
- 容器网络与 CNI 概述 — 关联
- [研发工具总览](../../README.md) — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
