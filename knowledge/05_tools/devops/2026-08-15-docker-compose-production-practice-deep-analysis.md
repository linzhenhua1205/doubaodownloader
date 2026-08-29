# Docker Compose 生产实践：资源管理、数据持久化与质量工具链部署

> **来源**: discover/site/系统与运维 素材导入（深度分析加工） · 2026-08-15
> **覆盖素材**: `Docker Compose 性能优化与资源管理全解析.md` · `Docker Compose部署PostgreSQL数据库实践指南 📦.md` · `Docker Compose部署SonarQube详细教程.md`
> **归档**: knowledge/05_tools/devops/2026-08-15-docker-compose-production-practice-deep-analysis.md
> **姊妹篇**: [Docker 容器网络与端口映射](2026-08-15-docker-container-network-port-mapping-deep-analysis.md) ｜ [Docker 单容器多服务管理](2026-08-15-docker-single-container-multi-service-supervisord.md)

## 核心命题

Compose 的价值不只是"一个 YAML 起多个容器"，而是**把生产环境的关键决策提前到声明式配置里**：资源边界（cgroup 限制）、数据生命周期（命名卷 vs 绑定挂载）、镜像构建策略（多阶段）、网络拓扑（overlay/external）。三个实战案例（性能优化 / PostgreSQL / SonarQube）共同指向一个原则：**Compose 配置的每一行，都是对"容器在真实环境中如何被约束、如何存活、如何恢复"的预回答**。

> 一句话：**生产级 Compose = 资源限制 + 数据卷策略 + 网络拓扑 + 可恢复性设计**——缺一项，开发环境能跑，生产环境必出问题。

---

## 一、原理深潜：Compose 的四层能力底座

### 1.1 资源限制：cgroup 的声明式入口

```
services:
  web:
    deploy:
      resources:
        limits:          # 硬上限（超过即 OOM/节流）
          cpus: '0.5'    # 0.5 核 CPU
          memory: 512M   # 512MB 内存
        reservations:    # 软保证（调度器预留）
          cpus: '0.25'
          memory: 256M
```

**原理**：`deploy.resources` 映射到 **cgroup v2 的 cpu.max / memory.max 控制组**。为什么必须限制：
- 未限制的容器可耗尽宿主机全部内存 → 触发内核 OOM Killer 随机杀进程（可能杀到别人的容器）
- CPU 不限制 → 单容器占满所有核，影响同机其他服务
- 生产多租户场景：**资源限制是"容器间公平"的底线保障**

> ⚠️ 注意：`deploy.resources` 在 **docker-compose（v1/V2 standalone）会被忽略**，只在 Docker Swarm 部署时生效；standalone 模式请用 `docker run --cpus/--memory` 或 `cgroup_parent`。这是最常见的"配置了没生效"坑。

### 1.2 数据卷三形态：生命周期差异决定选型

| 形态 | 存储位置 | 生命周期 | 适用场景 |
|:-----|:---------|:---------|:---------|
| 匿名卷 | /var/lib/docker/volumes | 随容器删除而消失 | 临时数据 |
| **命名卷** | /var/lib/docker/volumes/<name> | **独立于容器，删除容器不删数据** | **数据库持久化（生产首选）** |
| 绑定挂载 | 宿主机任意路径 | 跟随宿主机文件 | 配置注入、代码热更新 |

**命名卷为什么优于绑定挂载（性能场景）**：
- 命名卷由 Docker 管理，使用**原生文件系统挂载**（无跨平台路径转换开销）
- 绑定挂载在 macOS/Windows（Docker Desktop 的 gRPC-FUSE）上**性能显著下降**（I/O 慢 10-100 倍），数据库类负载尤其明显
- 命名卷天然支持 `docker volume` 系列命令（备份/迁移/驱动扩展）

### 1.3 镜像构建：多阶段构建的层复用

```dockerfile
# 构建阶段：装依赖、编代码
FROM python:3.9-slim AS build
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# 运行阶段：只留运行产物
FROM python:3.9-slim
COPY --from=build /app /app
CMD ["python", "app.py"]
```

**原理**：镜像 = 只读层栈（Union FS）。多阶段构建的价值：
- 构建工具（编译器、依赖缓存）只存在于 build 阶段，**不进入最终镜像** → 镜像体积可减少 60-90%
- 体积小 → 拉取快、启动快、攻击面小（不含 gcc/curl 等工具）

### 1.4 网络拓扑：overlay 与 external

```
networks:
  my_overlay_network:
    driver: overlay    # 跨主机（Swarm 模式）：VXLAN 隧道 + 服务发现
  pub-network:
    external: true     # 引用已存在的网络（由 docker network create 创建）
```

- **overlay**：跨多台宿主机时，用 VXLAN 封装容器流量，实现跨主机服务发现与负载均衡——Compose 单机不需要
- **external**：网络由外部（`docker network create`）创建，Compose 只引用——避免 Compose 管理网络导致的服务名/网段不一致（LangBot/Dify 案例即此模式）

---

## 二、案例深潜：PostgreSQL 生产部署

### 2.1 生产级 Compose 配置拆解

```yaml
services:
  postgres_db:
    image: postgres:15.7          # ✅ 固定版本，禁止 latest
    container_name: docker_postgres
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}   # ✅ 环境变量注入，禁止硬编码
    ports:
      - "5432:5432"               # 外部访问才需要；仅内部使用可不映射
    volumes:
      - data:/var/lib/postgresql/data   # ✅ 数据持久化（命名卷）
      - log:/var/log/postgresql         # 日志卷，便于排障
    logging:
      options:
        max-size: "10m"           # ✅ 日志轮转，防磁盘撑爆
        max-file: "3"
    networks:
      - pub-network               # 外部网络跨项目通信
volumes:
  data:
  log:
networks:
  pub-network:
    external: true
```

**五个生产要点**：
1. **固定版本**：`postgres:15.7` 而非 `latest`——latest 漂移导致环境不可复现
2. **密钥不硬编码**：用 `${DB_PASSWORD}` 环境变量 + `.env` 文件（或 Docker Secrets）
3. **数据在命名卷**：容器 `docker rm` 后数据保留；定期 `docker run --rm -v data:/data -v $(pwd):/backup alpine tar czvf ...` 备份
4. **日志轮转**：`max-size: 10m` + `max-file: 3`——避免容器日志无限增长
5. **网络 external**：跨项目共享网络，用服务名 `postgres_db` 通信

### 2.2 验证命令

```bash
docker compose up -d                 # 启动
docker compose ps                    # 状态检查
psql -h localhost -p 5432 -U postgres  # 宿主机连接
docker exec -it docker_postgres psql -h postgres_db -U postgres  # 容器内连接
```

---

## 三、案例深潜：SonarQube 质量平台部署

### 3.1 架构与版本约束

```
┌──────────┐      JDBC       ┌─────────────┐
│ postgres │ ◄────────────── │ sonarqube   │
│ :12      │  jdbc:postgresql│ :9000       │
└──────────┘  //postgres:5432└─────────────┘
```

**关键版本决策**：
- **SonarQube 7.9+ 不再支持 MySQL** → 必须 PostgreSQL（避免未来升级迁移）
- 素材用 postgres:12 + sonarqube:8.9.10-community，新项目建议用最新 LTS（sonarqube 9.9 LTS / 10.x）
- `depends_on` 保证启动顺序：先 postgres 后 sonar

### 3.2 插件与 CI/CD 集成

```bash
# 中文包（离线安装到 extensions/plugins 后重启）
wget https://github.com/xuhuisheng/sonar-l10n-zh/releases/download/.../sonar-l10n-zh-plugin-1.24.jar
docker restart sonar
```

**实践价值**（素材核心）：SonarQube 不只是静态分析工具，而是**质量门禁（Quality Gate）**：
- 代码扫描 → 技术债务量化 → 质量门禁判定 → CI 流水线阻断不合格代码合并
- 与 Jenkins/GitLab CI 集成：`sonar-scanner` 扫描后调用 API 获取质量报告

### 3.3 部署目录规划（素材要点）

```
/opt/sonarqube/
├── docker-compose.yml
├── sonarqube/
│   ├── logs/        # 应用日志（卷挂载）
│   ├── conf/        # 配置
│   ├── data/        # 数据（含 H2 迁移后的 PG 数据）
│   └── extensions/  # 插件（升级时保留）
└── postgres/
    ├── postgresql/  # PG 配置
    └── data/        # PG 数据
```

> 目录挂载的意义：**升级容器镜像时，logs/conf/data/extensions 全部保留**——这是"容器可重建、数据不丢失"的核心实践。

---

## 四、Compose 生产 Checklist（可直接用于评审）

| # | 检查项 | 判断标准 |
|:--|:-------|:---------|
| 1 | 镜像版本 | 全部固定版本，无 latest？ |
| 2 | 资源限制 | 每个服务有 cpus/memory limits？（standalone 用 cgroup 或运行时参数） |
| 3 | 数据持久化 | 数据库/状态数据用命名卷？ |
| 4 | 密钥管理 | 无硬编码密码，用 env/secrets？ |
| 5 | 日志策略 | 有 max-size/max-file 轮转？ |
| 6 | 网络拓扑 | 内部服务不暴露端口？external 网络正确引用？ |
| 7 | 启动顺序 | 依赖服务用 depends_on + healthcheck？ |
| 8 | 恢复能力 | restart: always？数据卷备份方案？ |
| 9 | 镜像构建 | 多阶段构建？体积可控？ |
| 10 | 环境一致性 | 有 .env.example？配置可复现？ |

---

## 五、结论

1. **Compose 是生产决策的声明式载体**：资源/数据/网络/恢复四类决策前置，比运行时临时参数更可审计、可复现
2. **三案例的共同模式**：固定版本 + 命名卷 + 日志轮转 + external 网络——这是容器化数据库/中间件的通用生产模板
3. **性能三杠杆**：资源限制（cgroup）、命名卷（原生文件系统）、多阶段构建（层瘦身）
4. **演进方向**：Compose 是单机/小规模编排的正解；规模化后（多机、自动伸缩、滚动更新）迁移 K8s，但**Compose 里养成的生产习惯（卷/限制/健康检查）全部复用**

---

## Changelog

- 2026-08-15: 创建（素材导入深度加工；覆盖 3 个源文件，补 cgroup 原理/卷生命周期/多阶段构建/生产 Checklist）
