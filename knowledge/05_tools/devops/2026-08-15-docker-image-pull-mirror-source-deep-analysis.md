# Docker 镜像拉取与国内镜像源：registry 协议、故障排查与换源全解

> **来源**: discover/site/系统与运维 素材导入（深度分析加工） · 2026-08-15
> **覆盖素材**: `Docker _unable to locate image_ 错误解决方案.md` · `2025年Docker国内镜像源解决方案（含详细换源步骤）.md`
> **归档**: knowledge/05_tools/devops/2026-08-15-docker-image-pull-mirror-source-deep-analysis.md
> **姊妹篇**: [Docker 容器网络与端口映射](2026-08-15-docker-container-network-port-mapping-deep-analysis.md)

## 核心命题

`docker pull` 的失败率，是容器化落地时最先暴露的问题。**"unable to locate image" 与国内镜像源失效，表面是两类问题，底层是同一个 registry 协议链路**：客户端 → 镜像仓库 DNS/HTTPS → 认证 → manifest 解析 → 层（layer）分发。排查的本质是**逐段定位链路断点**——镜像名错了、仓库没了、网络不通、还是配置坏了。

> 一句话：**pull 失败不要只看错误文案，要按"名称 → 仓库 → 网络 → 配置"四段链路定位**；国内镜像源是"网络段"的代理修复，不是万能药。

---

## 一、原理深潜：镜像拉取的协议链路

### 1.1 镜像名的结构（一切错误的源头）

```
docker pull [registry/]repository[:tag]
           ├─────────┴──────────┴───┘
           │           │             └── tag（默认 latest）
           │           └── 仓库路径（如 library/nginx、myapp/backend）
           └── 仓库地址（默认 Docker Hub：docker.io）
```

| 错误类型 | 典型表现 | 根因 |
|:---------|:---------|:-----|
| 名称拼写错误 | `unable to locate image ngnix` | repository 名不存在 |
| tag 不存在 | `manifest unknown: manifest unknown` | 指定 tag 未发布 |
| 私有仓库未推送 | `unable to locate image myapp:1.0` | 本地有但远端仓库无 |
| 仓库地址错误 | `repository does not exist` | registry 域名/路径写错 |

### 1.2 拉取链路四段（排查框架）

```
① 镜像名解析 → ② 仓库可达性 → ③ 认证授权 → ④ 层分发
   名称/标签正确性   DNS+HTTPS+网络     login/token     manifest+blob 下载
   docker images      ping/curl        docker login     docker pull 进度
```

**Docker Hub 拉取流程**（标准 registry v2 协议）：
1. 解析 `docker.io` → 重定向到 registry 服务
2. 请求 `/v2/` 获取 token（匿名或认证）
3. 请求 `/v2/<repo>/manifests/<tag>` 获取 manifest（镜像清单，含层列表）
4. 按 manifest 逐层请求 `/v2/<repo>/blobs/<digest>` 下载层数据

**每一段都可能失败**：段1 名称错 → 段2 网络/仓库失效 → 段3 认证失败 → 段4 部分层下载超时（最常见于大镜像 + 慢网络）。

### 1.3 国内镜像源的机制：registry-mirrors 代理

```
docker pull nginx
    │
    ▼
Docker daemon（registry-mirrors 配置了 5 个源）
    │  按数组顺序逐个尝试，第一个成功即停
    ▼
mirror1 → mirror2 → ...（每个源都是 docker.io 的只读代理缓存）
```

- **本质**：`registry-mirrors` 是 Docker daemon 的**拉取代理列表**，不是 DNS 改道
- **行为**：daemon 对每个镜像名，依次尝试 `https://mirrorN/<repo>:<tag>`，全部失败才报错
- **配置多源的原因**：单源失效时自动降级到下一个——**多源 = 故障转移**
- **限制**：只影响 `docker pull`（daemon 侧），不影响 `docker run` 时从本地已有镜像启动；部分源镜像不全（如只缓存热门镜像）

---

## 二、故障排查实战（unable to locate image）

### 2.1 四步排查法

| 步骤 | 命令 | 判断 |
|:-----|:-----|:-----|
| ① 验证名称 | `docker search nginx` / Docker Hub 网页搜索 | 名称存在？tag 正确？ |
| ② 检查本地 | `docker images` | 镜像在本地但仓库缺失？→ `docker push` |
| ③ 网络连通 | `ping hub.docker.com` / `curl -I https://registry-1.docker.io/v2/` | 网络可达？DNS 解析？ |
| ④ 配置认证 | `docker info`（看 Registry Mirrors / Insecure Registries）· `docker login` | 配置正确？认证有效？ |

### 2.2 常见错误速查表

| 错误信息 | 根因 | 解决方案 |
|:---------|:-----|:---------|
| `unable to locate image <name>` | 名称/仓库不存在 | 核对名称，`docker search` 验证 |
| `manifest unknown` | tag 不存在 | 换 tag 或重新构建推送 |
| `dial tcp ...:443: i/o timeout` | 网络不通（典型国内直连 Hub） | 配置镜像源 / 代理 |
| `no matching manifest for linux/amd64` | 架构不匹配 | 指定平台 `--platform` |
| `unauthorized: authentication required` | 私有仓库未登录 | `docker login` |
| `TLS handshake timeout` | 中间网络设备干扰 HTTPS | 换源 / 换网络环境 |

---

## 三、国内镜像源配置全解（2025 实测方案）

### 3.1 政策背景

- 2024 年 6 月起，国内多数公共镜像源**陆续关闭或限速**
- 典型症状：`dial tcp 199.66.33.53:443: i/o timeout`（Docker Hub 直连超时）
- 阿里云等镜像站因**未同步最新镜像**被移出可用列表

### 3.2 永久换源（推荐，三步）

```bash
# ① 创建配置目录
sudo mkdir -p /etc/docker

# ② 写入多源配置（5 源故障转移）
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.imgdb.de",
    "https://docker-0.unsee.tech",
    "https://docker.hlmirror.com",
    "https://cjie.eu.org"
  ]
}
EOF

# ③ 重启生效
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 3.3 临时换源（单次测试）

```bash
# 拉取时显式指定源前缀
sudo docker pull docker.m.daocloud.io/hello-world
# 拉取后重新打 tag，恢复标准名称
sudo docker tag docker.m.daocloud.io/hello-world hello-world:latest
```

### 3.4 验证与注意事项

- **验证命令**：`docker pull hello-world`，成功提示 `Status: Downloaded newer image`
- **充分非必要**：能拉 hello-world 说明源可用，但**极少数源可能不支持 hello-world 却支持其他镜像**——多试几个业务镜像更可靠
- **镜像源动态性**：第三方镜像源生命周期不稳定，建议：①定期测试；②核心环境自建 **Harbor 私有仓库**（镜像同步 + 内网分发）
- **企业方案**：生产环境应使用 `docker pull` + Harbor 同步（`skopeo copy` 或 Harbor 的 proxy cache 功能），不依赖公共源

---

## 四、应用场景

| 场景 | 方案 |
|:-----|:-----|
| 个人开发（国内网络） | 多源 registry-mirrors 配置 |
| CI/CD 流水线 | 自建 Harbor + 内网镜像仓库（构建缓存加速） |
| 多集群/边缘节点 | Harbor 复制 + 边缘节点本地缓存 |
| 离线环境 | 镜像导出/导入（docker save/load）或 Harbor 离线同步 |
| 快速验证源可用性 | hello-world 临时拉取测试 |

---

## 五、结论

1. **链路思维**：pull 失败按"名称→仓库→网络→配置"四段排查，错误文案只是入口不是答案
2. **镜像源是网络段代理**：`registry-mirrors` 解决"连不上 Docker Hub"，不解决"镜像名写错"
3. **多源 + 自建才是正解**：公共镜像源是过渡方案；**生产环境必须自建 Harbor**，公共源只做开发兜底
4. **可操作原则**：配置改完必须 `daemon-reload && restart docker` 才生效；镜像源可用性要定期复测

---

## Changelog

- 2026-08-15: 创建（素材导入深度加工；覆盖 2 个源文件，补 registry v2 协议链路/排查框架/Harbor 生产方案）
