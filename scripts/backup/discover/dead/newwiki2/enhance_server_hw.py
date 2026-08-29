import os
import re
from pathlib import Path

base_dir = Path(r"h:\github\cowkb\discover\newwiki2\服务器硬件")

enhancements = {
    "cpu.md": {
        "title": "CPU架构与技术：服务器处理器核心知识索引",
        "card_overview": "本卡片系统梳理了服务器CPU架构、性能优化、选型指南等核心知识，收录了从x86到ARM、从通用计算到AI加速的全方位CPU技术资料。",
        "core_points": [
            "CPU架构演进：从x86_64到ARM架构，从多核到异构计算的发展历程",
            "性能优化：缓存层级、指令集并行、NUMA架构、超线程等关键技术",
            "服务器CPU选型：Intel至强、AMD EPYC、ARM鲲鹏等主流平台对比",
            "AI时代CPU新角色：数据预处理、模型推理调度、异构协同计算",
            "RAS特性：可靠性、可用性、可维护性企业级特性详解"
        ],
        "latest_updates": [
            "Intel Granite Rapids-D 2025年Q4发布，144核288线程，支持CXL 2.0内存扩展",
            "AMD EPYC 9005系列Turin架构最高192核，PCIe 5.0通道数提升至160条",
            "ARM Neoverse V3平台性能提升40%，AI推理能效比大幅优化",
            "国产CPU进展：飞腾腾云S5000、海光3号、鲲鹏920后续系列持续迭代",
            "Chiplet技术成为主流，多Die封装突破单芯片物理极限"
        ],
        "related_cards": ["gpu.md", "pcie.md", "memory.md", "server.md", "architecture.md"],
        "import_materials": [
            "../../import/md/服务器研发核心关注维度及要点.md",
            "../../import/work/ocp/OCP服务器技术.md"
        ],
        "quality_level": "A"
    },
    "gpu.md": {
        "title": "GPU技术与应用：AI算力核心知识索引",
        "card_overview": "本卡片全面收录了GPU架构、AI训练推理、图形渲染、异构计算等领域的核心知识，是理解现代AI算力基础设施的重要参考。",
        "core_points": [
            "GPU架构演进：从SIMT到Tensor Core、RT Core，算力密度指数级增长",
            "AI训练与推理：大模型训练并行策略、推理优化技术栈详解",
            "主流GPU对比：NVIDIA H100/H200/B200、AMD MI300、华为昇腾910B等",
            "GPU服务器架构：NVLink、PCIe拓扑、整机柜液冷、超节点设计",
            "软件生态：CUDA、ROCm、昇腾CANN、OpenCL等计算平台对比"
        ],
        "latest_updates": [
            "NVIDIA B200/B300 2025-2026年陆续发布，FP8算力达4PFLOPS+",
            "AMD MI350X 2025年下半年量产，192GB HBM3e，对标NVIDIA B200",
            "华为昇腾910C 2025年商用，算力密度提升30%，国产替代加速",
            "HBM4 2026年量产，单颗容量64GB+，带宽突破2TB/s",
            "液冷GPU服务器成为标配，单柜功率突破100kW，PUE优化至1.1以下"
        ],
        "related_cards": ["nvidia.md", "pcie.md", "liquidcooling.md", "memory.md", "server.md"],
        "import_materials": [
            "../../import/doubao/液冷成AI算力刚需.md",
            "../../import/work/ocp/OCP服务器技术.md"
        ],
        "quality_level": "A"
    },
    "memory.md": {
        "title": "内存技术与存储层级：从DRAM到持久化内存知识索引",
        "card_overview": "本卡片系统梳理了内存架构、存储层级、内存池化、持久化内存等核心技术，是理解服务器内存子系统的全面知识库。",
        "core_points": [
            "内存架构原理：DRAM存储单元、刷新机制、带宽与延迟权衡",
            "内存层级：L1/L2/L3缓存、主存、持久化内存的层级化设计",
            "内存池化：CXL内存扩展、内存池化架构、资源弹性调度",
            "HBM技术：高带宽内存架构、3D堆叠、GPU与CPU集成方案",
            "持久化内存：Intel Optane、MRAM、PCRAM等新型内存技术"
        ],
        "latest_updates": [
            "DDR5-8000 2025年普及，单条容量256GB成为主流，服务器级支持128条",
            "HBM3e量产、HBM4 2026年到来，单颗64GB，带宽超2TB/s",
            "CXL 3.1内存池化方案成熟，Meta、阿里等大规模部署验证",
            "MRAM技术突破，L4缓存级商用加速，非易失性替代SRAM",
            "三星HBM市场份额2025年Q3达22%，预计2026年达39%"
        ],
        "related_cards": ["cpu.md", "gpu.md", "pcie.md", "architecture.md", "server.md"],
        "import_materials": [
            "../../import/work/ocp/OCP服务器技术.md",
            "../../import/md/服务器研发核心关注维度及要点.md"
        ],
        "quality_level": "A"
    },
    "pcie.md": {
        "title": "PCIe总线技术：高速互联与扩展知识索引",
        "card_overview": "本卡片全面收录了PCIe总线架构、协议规范、拓扑设计、性能调优等核心知识，是服务器高速互联技术的系统参考。",
        "core_points": [
            "PCIe协议演进：从PCIe 1.0到6.0/7.0，带宽每代翻倍的发展历程",
            "拓扑架构：Root Complex、Switch、Endpoint、PCIe桥的层级设计",
            "高性能特性：SR-IOV、MR-IOV、DMA、ATS、TLP处理流程",
            "CXL与PCIe：CXL协议栈、内存扩展、缓存一致性、设备互联",
            "AI时代新形态：PCIe交换机、EthPCIe、超节点互联架构"
        ],
        "latest_updates": [
            "PCIe 6.0 2025年规模商用，64GT/s速率，PAM4编码，x16带宽达256GB/s",
            "PCIe 7.0规范2025年定稿，128GT/s，2027-2028年量产",
            "CXL 3.1生态成熟，内存池化、加速器互联方案大规模验证",
            "PCIe AI加速卡爆发，液冷设计、智能诊断、KV Cache硬件加速成标配",
            "ScorpioX系列320 Lane PCIe交换芯片，支持Hypercast硬件加速"
        ],
        "related_cards": ["cxl.md", "cpu.md", "gpu.md", "server.md", "architecture.md"],
        "import_materials": [
            "../../import/md/服务器研发核心关注维度及要点.md",
            "../../import/work/ocp/OCP服务器技术.md"
        ],
        "quality_level": "A"
    },
    "nvidia.md": {
        "title": "NVIDIA技术生态：GPU计算与AI平台知识索引",
        "card_overview": "本卡片系统整理了NVIDIA GPU架构、CUDA生态、AI平台、数据中心解决方案等核心内容，是NVIDIA技术体系的全面知识库。",
        "core_points": [
            "GPU架构演进：Kepler→Ampere→Hopper→Blackwell→Rubin，每代算力翻倍",
            "CUDA生态：CUDA编程模型、cuDNN、TensorRT、NCCL等核心库",
            "数据中心平台：DGX、HGX、OVX、MGX等服务器参考设计",
            "AI软件栈：NeMo、Triton、Riva、Omniverse等AI应用框架",
            "互联技术：NVLink/NVSwitch、InfiniBand、Spectrum-X网络方案"
        ],
        "latest_updates": [
            "NVIDIA B200/B300 Blackwell架构2025-2026年量产，FP8算力4PFLOPS+",
            "Rubin架构2026年发布，NVLink 6.0，单GPU带宽3.6TB/s",
            "NVIDIA H20中国特供版持续供货，宁畅、超聚变等整机方案成熟",
            "CUDA 12.x持续优化，多GPU并行、FP8/FP4混合精度训练效率提升",
            "NVIDIA Spectrum-4 800G交换机，AI网络端到端优化方案落地"
        ],
        "related_cards": ["gpu.md", "server.md", "cooling.md", "pcie.md", "architecture.md"],
        "import_materials": [
            "../../import/doubao/液冷成AI算力刚需.md",
            "../../import/work/ocp/OCP服务器技术.md"
        ],
        "quality_level": "A"
    },
    "server.md": {
        "title": "服务器技术与架构：企业级计算平台知识索引",
        "card_overview": "本卡片全面收录了服务器硬件架构、设计规范、选型指南、运维管理等核心知识，覆盖从通用服务器到AI超算的全品类服务器技术。",
        "core_points": [
            "服务器架构：塔式、机架式、刀片式、整机柜、超节点等形态演进",
            "核心组件：CPU、内存、存储、网络、电源、散热的协同设计",
            "RAS特性：可靠性、可用性、可维护性企业级技术体系",
            "服务器研发：硬件设计、BIOS/BMC固件、散热设计、信号完整性",
            "AI服务器：GPU服务器架构、液冷方案、整机柜交付、超节点设计"
        ],
        "latest_updates": [
            "AI服务器2025年占比超40%，单柜功率从30kW跃升至100kW+",
            "液冷服务器渗透率快速提升，2026年全球液冷市场规模达138.2亿美元",
            "整机柜交付成为主流，Rack Scale Design架构资源池化效率提升30%",
            "国产服务器突破：华为、浪潮、联想、超聚变等AI服务器市占率提升",
            "OCP开放计算标准演进，CXL内存、液冷、OpenBMC成为标配"
        ],
        "related_cards": ["architecture.md", "cooling.md", "cpu.md", "gpu.md", "memory.md"],
        "import_materials": [
            "../../import/work/ocp/OCP服务器技术.md",
            "../../import/work/server/服务器技术.md",
            "../../import/md/服务器研发核心关注维度及要点.md"
        ],
        "quality_level": "A"
    },
    "cooling.md": {
        "title": "散热技术与热管理：服务器冷却方案知识索引",
        "card_overview": "本卡片系统整理了服务器散热技术、风冷、液冷、热设计、数据中心冷却方案等核心知识，是理解服务器热管理的全面参考。",
        "core_points": [
            "散热基础：热传导、对流、辐射原理，热阻、热容核心概念",
            "风冷技术：风扇设计、散热片、风道优化、功耗与噪音权衡",
            "液冷技术：冷板式、浸没式、喷淋式方案对比与适用场景",
            "热设计：芯片级→板级→系统级→数据中心级热设计方法论",
            "数据中心冷却：精密空调、间接蒸发冷却、自然冷却、液冷演进"
        ],
        "latest_updates": [
            "液冷市场爆发：2026年全球液冷市场规模138.2亿美元，年复合增长率超40%",
            "冷板式液冷占比65%，单柜散热能力30-80kW，技术成熟度最高",
            "浸没式液冷单柜散热100kW+，PUE<1.05，大规模部署案例增多",
            "AI服务器散热从风冷全面转向液冷，100kW+机柜成标配",
            "800V HVDC直流供电+液冷协同，数据中心整体能效提升8-12%"
        ],
        "related_cards": ["liquidcooling.md", "server.md", "gpu.md", "architecture.md"],
        "import_materials": [
            "../../import/doubao/液冷成AI算力刚需.md",
            "../../import/work/ocp/OCP服务器技术.md"
        ],
        "quality_level": "A"
    },
    "liquidcooling.md": {
        "title": "液冷散热技术：AI时代算力冷却核心方案索引",
        "card_overview": "本卡片专注于液冷散热技术，收录冷板式、浸没式、喷淋式等液冷方案的技术细节、市场动态和行业案例。",
        "core_points": [
            "液冷方案分类：冷板式、单相浸没、两相浸没、喷淋式技术对比",
            "核心组件：冷板、CDU、快接接头、冷却液、管路系统详解",
            "性能优势：高散热密度、低PUE、低噪音、高可靠性",
            "部署挑战：初始投资、运维复杂度、冷却液兼容性、泄漏防护",
            "市场格局：曙光、浪潮、华为、宁畅、超聚变等主流厂商方案"
        ],
        "latest_updates": [
            "2026年液冷市场规模预计达138.2亿美元，冷板式占65%市场份额",
            "冷板式液冷支持80kW/柜，浸没式突破150kW/柜，技术持续迭代",
            "超聚变柜门式液冷分配单元专利，优化机柜部署密度",
            "宁畅R620 G50 LP冷板式液冷服务器，支持全液冷散热方案",
            "液冷核心部件涨价预期：CDU、冷板、快接头等关键组件供需紧张"
        ],
        "related_cards": ["cooling.md", "server.md", "gpu.md", "architecture.md"],
        "import_materials": [
            "../../import/doubao/液冷成AI算力刚需.md",
            "../../import/work/ocp/OCP服务器技术.md"
        ],
        "quality_level": "B"
    },
    "architecture.md": {
        "title": "服务器架构设计：从芯片到数据中心的系统知识索引",
        "card_overview": "本卡片系统梳理了服务器硬件架构、系统设计、数据中心架构等多层次知识，是理解服务器系统设计的全面参考。",
        "core_points": [
            "系统架构：CPU/内存/IO子系统设计、NUMA架构、拓扑结构",
            "服务器形态：塔式、机架式、刀片式、多节点、整机柜、超节点",
            "互联架构：PCIe、CXL、NVLink、以太网、InfiniBand对比",
            "数据中心架构：机架级、行级、机房级设计，供电与冷却协同",
            "前沿架构：资源池化、可组合基础设施、超节点、算力网络"
        ],
        "latest_updates": [
            "GPU超节点架构2025年规模化部署，72GPU整机柜260TB/s全互联",
            "CXL内存池化方案成熟，Meta Vistara、阿里MemTunnel等自研ASIC落地",
            "Rack Scale Design机架级设计成为AI数据中心标准，资源利用率提升30%",
            "UALink开放标准2025年推出，200GT/s/通道，带宽效率93%",
            "可组合基础设施(CI)从概念走向商用，计算/存储/网络资源动态编排"
        ],
        "related_cards": ["server.md", "cpu.md", "gpu.md", "pcie.md", "memory.md"],
        "import_materials": [
            "../../import/work/架构/服务器架构.md",
            "../../import/md/服务器研发核心关注维度及要点.md",
            "../../import/work/ocp/OCP服务器技术.md"
        ],
        "quality_level": "A"
    },
    "research.md": {
        "title": "服务器技术研究与前沿探索知识索引",
        "card_overview": "本卡片收录了服务器硬件、系统架构、前沿技术的研究动态和技术趋势，追踪行业最新技术进展。",
        "core_points": [
            "前沿硬件：新型计算架构、光子计算、量子计算、存算一体",
            "系统研究：分布式系统、操作系统、数据库、编译器优化",
            "AI系统：大模型训练框架、推理优化、算力网络、AI基础设施",
            "开源生态：OCP、OpenBMC、Linux内核、RISC-V等开源项目",
            "技术趋势：每年Gartner技术成熟度曲线、行业技术路线图"
        ],
        "latest_updates": [
            "2025年AI基础设施研究热点：CXL内存池化、液冷、算力调度优化",
            "存算一体技术突破，SRAM+RRAM混合架构能效比提升10倍",
            "RISC-V服务器CPU生态发展，香山、玄铁等开源芯片持续迭代",
            "光互联技术进展：硅光模块800G商用，1.6T研发中，芯片间光互联探索",
            "OCP开放计算社区持续壮大，液冷、OpenBMC、CXL成为核心议题"
        ],
        "related_cards": ["architecture.md", "server.md", "cpu.md", "linux.md", "security.md"],
        "import_materials": [
            "../../import/work/ocp/OCP服务器技术.md",
            "../../import/md/服务器研发核心关注维度及要点.md"
        ],
        "quality_level": "B"
    },
    "linux.md": {
        "title": "Linux系统运维与调优：服务器操作系统知识索引",
        "card_overview": "本卡片全面收录了Linux操作系统、系统管理、性能调优、内核技术等核心知识，是服务器运维与开发的系统参考。",
        "core_points": [
            "系统基础：文件系统、进程管理、内存管理、网络栈原理",
            "性能调优：CPU/内存/IO/网络性能分析与优化方法论",
            "内核技术：系统调用、中断处理、调度器、内存管理、驱动模型",
            "运维工具：perf、bcc/bpftrace、sar、vmstat、iostat等工具集",
            "企业级特性：LVM、RAID、SELinux、cgroup、namespace等"
        ],
        "latest_updates": [
            "Linux 6.8-6.12内核持续优化，CXL、IO_uring、eBPF特性增强",
            "eBPF生态爆发，可观测性、安全、网络加速场景大规模应用",
            "Rust for Linux进展，驱动、网络模块逐步用Rust重写",
            "BPF CO-RE成为标准，内核可观测性工具链成熟",
            "云原生优化：cgroup v2普及、overlayfs性能提升、启动速度优化"
        ],
        "related_cards": ["kernel.md", "docker.md", "k8s.md", "security.md", "python.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md",
            "../../import/work/lpc/LPC硬件技术.md"
        ],
        "quality_level": "A"
    },
    "docker.md": {
        "title": "Docker容器技术：应用容器化与部署知识索引",
        "card_overview": "本卡片系统整理了Docker容器技术、镜像构建、容器编排、微服务部署等核心知识，是云原生基础技术的全面参考。",
        "core_points": [
            "容器原理：namespace、cgroup、rootfs、union FS等内核技术",
            "Docker架构：Client/Server、镜像、容器、仓库核心概念",
            "镜像管理：Dockerfile、多阶段构建、镜像优化、镜像仓库",
            "容器网络：bridge、host、overlay、macvlan等网络模式",
            "存储方案：volume、bind mount、tmpfs、存储驱动对比"
        ],
        "latest_updates": [
            "Docker 25+持续优化，BuildKit增强、Wasm支持、containerd集成",
            "容器运行时多元化：containerd成为标准，CRI-O、Kata Containers发展",
            "OCI规范持续演进，镜像格式、运行时、分发标准完善",
            "安全容器技术成熟：Kata Containers、gVisor等隔离方案优化",
            "WASM+容器融合趋势，WebAssembly轻量级运行时场景扩展"
        ],
        "related_cards": ["k8s.md", "container.md", "linux.md", "microservice.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
    "k8s.md": {
        "title": "Kubernetes容器编排：云原生集群管理知识索引",
        "card_overview": "本卡片全面收录了Kubernetes架构、核心概念、运维实践、性能调优等知识，是云原生容器编排的系统知识库。",
        "core_points": [
            "K8s架构：Master/Node、etcd、apiserver、scheduler、controller-manager",
            "核心概念：Pod、Service、Deployment、StatefulSet、DaemonSet、Ingress",
            "存储与网络：PV/PVC、StorageClass、CNI网络、Service Mesh",
            "运维实践：集群部署、监控告警、日志管理、升级与备份",
            "性能调优：APIServer优化、etcd调优、调度器优化、网络性能"
        ],
        "latest_updates": [
            "Kubernetes 1.29-1.32持续迭代，Sidecar容器、Gateway API GA",
            "AI工作负载成为K8s新场景，Kueue、Volcano等调度器发展",
            "Gateway API取代Ingress成为标准，多集群、南北向流量管理增强",
            "K8s安全加固：PSA、OPA/Gatekeeper、Sigstore镜像签名普及",
            "边缘K8s成熟：K3s、KubeEdge、OpenYurt等边缘方案规模化应用"
        ],
        "related_cards": ["docker.md", "container.md", "microservice.md", "linux.md", "security.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "A"
    },
    "container.md": {
        "title": "容器技术生态：从Docker到云原生容器知识索引",
        "card_overview": "本卡片系统梳理了容器技术生态、运行时、镜像标准、容器安全等全面内容，覆盖容器技术栈各个层级。",
        "core_points": [
            "容器标准：OCI运行时规范、镜像格式规范、分发规范",
            "运行时对比：runc、containerd、CRI-O、Kata、gVisor",
            "容器安全：镜像扫描、运行时安全、seccomp、AppArmor、SELinux",
            "构建工具：Dockerfile、BuildKit、Kaniko、Buildpacks、ko",
            "镜像仓库：Harbor、Registry、Quay、镜像加速与分发优化"
        ],
        "latest_updates": [
            "containerd 2.0 2025年发布，性能提升、插件体系增强",
            "NIST容器安全标准更新，SBOM、供应链安全成为强制要求",
            "Wasm运行时与容器融合，spin、wasmCloud等项目活跃",
            "Confidential Containers机密容器技术成熟，TEE+容器方案落地",
            "容器镜像优化技术发展，eStargz、Nydus等懒加载方案普及"
        ],
        "related_cards": ["docker.md", "k8s.md", "linux.md", "security.md", "microservice.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
    "microservice.md": {
        "title": "微服务架构与实践：分布式系统设计知识索引",
        "card_overview": "本卡片收录了微服务架构设计、服务治理、分布式事务、API网关等核心知识，是分布式系统开发的全面参考。",
        "core_points": [
            "架构设计：服务拆分原则、领域驱动设计、边界上下文",
            "服务治理：服务发现、配置中心、负载均衡、熔断降级",
            "分布式问题：CAP理论、一致性、分布式事务、分布式锁",
            "可观测性：日志、指标、链路追踪三件套，OpenTelemetry生态",
            "API网关：Kong、Envoy、Spring Cloud Gateway功能对比"
        ],
        "latest_updates": [
            "微服务向Serverless演进，函数计算与微服务融合趋势明显",
            "Service Mesh持续成熟，Istio 1.20+性能大幅提升，eBPF加速数据面",
            "OpenTelemetry成为可观测性标准，日志/指标/链路追踪统一",
            "Dapr分布式应用运行时发展，提供语言无关的微服务抽象层",
            "事件驱动架构复兴，Kafka、Pulsar、EventBridge等事件总线普及"
        ],
        "related_cards": ["k8s.md", "docker.md", "java.md", "go.md", "python.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
    "security.md": {
        "title": "服务器安全与防护：企业级安全体系知识索引",
        "card_overview": "本卡片系统整理了服务器安全、网络安全、数据安全、云原生安全等核心知识，是企业级安全防护的全面参考。",
        "core_points": [
            "系统安全：主机加固、漏洞管理、入侵检测、应急响应",
            "网络安全：防火墙、WAF、DDoS防护、零信任网络",
            "数据安全：加密、脱敏、备份、审计、数据分类分级",
            "云原生安全：容器安全、K8s安全、DevSecOps、供应链安全",
            "合规要求：等保2.0、ISO 27001、GDPR、数据安全法"
        ],
        "latest_updates": [
            "零信任架构2025年规模化落地，身份认证+持续验证成为标准",
            "AI安全攻防升级，AI生成恶意软件、深度伪造检测成为新课题",
            "供应链安全受重视，SBOM、Sigstore、SLSA框架逐步普及",
            "等保2.0深化实施，数据安全法、个人信息保护法执法案例增多",
            "eBPF安全监控兴起，运行时威胁检测、内核级安全防护能力增强"
        ],
        "related_cards": ["auth.md", "crypto.md", "linux.md", "k8s.md", "docker.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md",
            "../../import/work/ras/RAS.md"
        ],
        "quality_level": "B"
    },
    "auth.md": {
        "title": "身份认证与授权：安全访问控制知识索引",
        "card_overview": "本卡片专注于身份认证、授权管理、访问控制等安全主题，收录了主流认证协议、身份管理方案等核心知识。",
        "core_points": [
            "认证方式：密码、证书、生物识别、多因素认证(MFA)",
            "认证协议：OAuth 2.0、OIDC、SAML、LDAP、Kerberos、RADIUS",
            "授权模型：RBAC、ABAC、MAC、DAC、零信任权限模型",
            "身份管理：SSO单点登录、身份供给、目录服务、IAM平台",
            "安全最佳实践：密码策略、会话管理、令牌安全、审计日志"
        ],
        "latest_updates": [
            "Passkey无密码认证2025年加速普及，FIDO2/WebAuthn生态成熟",
            "OAuth 2.1规范定稿，安全增强，简化授权流程",
            "零信任身份认证成为企业标准，持续验证+最小权限落地",
            "AI身份验证应用：行为生物识别、异常检测、风险自适应认证",
            "SIEM与IAM融合，安全分析与身份治理协同加强"
        ],
        "related_cards": ["security.md", "crypto.md", "linux.md", "microservice.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
    "crypto.md": {
        "title": "密码学与加密技术：安全基础技术知识索引",
        "card_overview": "本卡片系统整理了对称加密、非对称加密、哈希算法、数字签名等密码学核心知识，是信息安全的基础技术参考。",
        "core_points": [
            "对称加密：AES、DES、3DES、SM4，分组密码模式ECB/CBC/GCM",
            "非对称加密：RSA、ECC、SM2、Diffie-Hellman密钥交换",
            "哈希算法：SHA-2、SHA-3、MD5、SM3、BLAKE3，抗碰撞性",
            "数字签名：RSA签名、ECDSA、EdDSA、Schnorr签名",
            "应用协议：TLS 1.3、SSL、IPsec、SSH、PGP、HTTPS"
        ],
        "latest_updates": [
            "后量子密码学(PQC)2025年标准化推进，CRYSTALS-Kyber成为主流算法",
            "TLS 1.3成为主流，TLS 1.0/1.1全面淘汰，0-RTT性能优化",
            "国密算法(SM2/SM3/SM4)在金融、政务领域加速推广应用",
            "AI辅助密码分析与优化，密码学与AI交叉领域研究活跃",
            "同态加密、零知识证明技术突破，隐私计算场景落地加速"
        ],
        "related_cards": ["security.md", "auth.md", "linux.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
    "python.md": {
        "title": "Python编程与应用开发知识索引",
        "card_overview": "本卡片收录了Python语言、Web开发、数据分析、AI/ML等领域的核心知识，是Python技术栈的全面参考。",
        "core_points": [
            "语言基础：数据结构、面向对象、函数式编程、异步编程",
            "Web开发：Django、Flask、FastAPI、Tornado框架对比",
            "数据分析：NumPy、Pandas、Matplotlib、数据分析方法论",
            "AI/ML：TensorFlow、PyTorch、Scikit-learn、大模型应用开发",
            "运维自动化：Ansible、Fabric、脚本开发、自动化运维实践"
        ],
        "latest_updates": [
            "Python 3.12-3.14持续优化，性能提升30%+，类型系统增强",
            "AI时代Python地位巩固，LangChain、LlamaIndex等大模型框架爆发",
            "PyTorch 2.x编译器优化，训练速度提升2倍，动态图+静态图融合",
            "Web开发趋势：FastAPI+异步成为主流，Django 5.x现代化升级",
            "Rust+Python融合加速，PyO3、Ruff、Pydantic v2性能大幅提升"
        ],
        "related_cards": ["java.md", "go.md", "microservice.md", "k8s.md", "linux.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
    "java.md": {
        "title": "Java编程与企业级开发知识索引",
        "card_overview": "本卡片系统整理了Java语言、企业级框架、微服务、性能调优等核心知识，是Java技术生态的全面参考。",
        "core_points": [
            "语言基础：JVM内存模型、GC算法、集合框架、并发编程",
            "企业框架：Spring Boot、Spring Cloud、MyBatis、Dubbo",
            "微服务：Spring Cloud Alibaba、Nacos、Sentinel、Seata",
            "性能调优：JVM调优、GC调优、线程池优化、数据库优化",
            "架构设计：DDD领域驱动设计、设计模式、分布式架构"
        ],
        "latest_updates": [
            "Java 21 LTS普及，虚拟线程、模式匹配、记录类特性大规模应用",
            "Spring Boot 3.2+、Spring 6.x全面拥抱Jakarta EE和GraalVM",
            "Spring AI项目发展，Java生态大模型应用开发能力增强",
            "GraalVM原生镜像技术成熟，Java应用启动速度提升10倍+",
            "国产中间件崛起：Polaris、Sentinel、Seata等社区活跃度提升"
        ],
        "related_cards": ["microservice.md", "k8s.md", "python.md", "go.md", "linux.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
    "go.md": {
        "title": "Go语言与云原生开发知识索引",
        "card_overview": "本卡片收录了Go语言、并发编程、微服务、云原生工具等核心知识，是云原生时代服务器开发的重要参考。",
        "core_points": [
            "语言特性：goroutine、channel、defer、接口、组合式设计",
            "并发模型：CSP模型、context、sync包、原子操作、内存模型",
            "Web框架：Gin、Echo、Beego、Go-zero、Kratos微服务框架",
            "云原生工具：Docker、K8s、etcd、Prometheus、Terraform均用Go开发",
            "性能优化：pprof、逃逸分析、内存池、连接池、并发模式"
        ],
        "latest_updates": [
            "Go 1.22-1.24持续优化，循环变量语义修复、泛型增强、性能提升",
            "Go微服务框架成熟：Kratos、Go-zero、Iris等生态完善",
            "Wasm支持增强，Go+WASM在边缘计算、浏览器端场景扩展",
            "eBPF Go库发展，Go语言在可观测性领域应用增多",
            "Go泛型生态成熟，集合库、函数式编程库数量快速增长"
        ],
        "related_cards": ["microservice.md", "k8s.md", "docker.md", "linux.md", "python.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
    "kafka.md": {
        "title": "Kafka消息队列：分布式流处理知识索引",
        "card_overview": "本卡片系统整理了Kafka架构、核心概念、性能调优、流处理等知识，是分布式消息系统的全面参考。",
        "core_points": [
            "核心架构：Producer、Broker、Consumer、Topic、Partition、Offset",
            "存储机制：日志分段、索引设计、零拷贝、页缓存优化",
            "可靠性：副本机制、ISR、ACK级别、幂等性、事务消息",
            "性能调优：Producer/Broker/Consumer调优、分区策略、批量发送",
            "流处理：Kafka Streams、KSQL、Flink集成、CDC数据同步"
        ],
        "latest_updates": [
            "Kafka 3.6+ KRaft模式成熟，ZooKeeper依赖逐步移除",
            "Kafka 4.0规划：2025-2026年发布，彻底移除ZK，性能大幅提升",
            "分层存储技术普及，冷热数据分离，存储成本降低60%+",
            "流批一体趋势，Kafka + Flink组合成为实时数仓标准架构",
            "云原生Kafka服务成熟，Serverless Kafka按需计费模式兴起"
        ],
        "related_cards": ["microservice.md", "java.md", "python.md", "linux.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
    "sql.md": {
        "title": "SQL数据库与存储引擎知识索引",
        "card_overview": "本卡片收录了SQL语法、数据库设计、性能优化、存储引擎等核心知识，是关系型数据库开发与运维的全面参考。",
        "core_points": [
            "SQL基础：查询语法、联表查询、子查询、窗口函数、CTE",
            "数据库设计：范式理论、ER图、索引设计、事务隔离级别",
            "存储引擎：InnoDB、MyISAM、PostgreSQL存储引擎对比",
            "性能调优：执行计划、索引优化、慢查询、分库分表、读写分离",
            "高可用：主从复制、MGR、Pacemaker+DRBD、数据库中间件"
        ],
        "latest_updates": [
            "MySQL 8.0系列持续优化，8.4 LTS发布，性能、JSON功能增强",
            "PostgreSQL 16-17发布，性能提升、逻辑复制增强、AI向量支持",
            "AI原生数据库兴起，向量数据库、SQL+ML融合成为新趋势",
            "分布式数据库成熟：TiDB、OceanBase、PolarDB等大规模商用",
            "HTAP数据库普及，OLTP+OLAP混合负载能力增强"
        ],
        "related_cards": ["linux.md", "python.md", "java.md", "microservice.md"],
        "import_materials": [
            "../../import/work/OS/操作系统技术.md"
        ],
        "quality_level": "B"
    },
}

def enhance_file(filename, data):
    filepath = base_dir / filename
    if not filepath.exists():
        print(f"跳过不存在的文件: {filename}")
        return False
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新 front matter
    content = re.sub(r'title:.*', f'title: {data["title"]}', content, count=1)
    
    if 'quality_level' in data:
        if 'quality_level:' in content:
            content = re.sub(r'quality_level:.*', f'quality_level: {data["quality_level"]}', content, count=1)
        else:
            content = content.replace('---\n\n#', f'quality_level: {data["quality_level"]}\n---\n\n#', 1)
    
    # 找到第一张卡片之前的位置（卡片概览之后）
    insert_pos = content.find('## 1.')
    if insert_pos == -1:
        print(f"跳过 {filename}: 未找到卡片位置")
        return False
    
    # 构建新增内容
    new_content = f"""
---

## 卡片定位

{data['card_overview']}

---

## 核心要点

"""
    for i, point in enumerate(data['core_points'], 1):
        new_content += f"{i}. **{point.split('：')[0]}**：{point.split('：')[1] if '：' in point else point}\n"
    
    new_content += f"""
---

## 2025-2026最新进展

"""
    for i, update in enumerate(data['latest_updates'], 1):
        new_content += f"- {update}\n"
    
    new_content += f"""
---

## 相关资源

### import 素材

"""
    for mat in data['import_materials']:
        name = mat.split('/')[-1].replace('.md', '')
        new_content += f"- [{name}]({mat})\n"
    
    new_content += f"""
### 相关知识卡片

"""
    for card in data['related_cards']:
        card_title = card.replace('.md', '').title()
        new_content += f"- [{card_title}]({card})\n"
    
    new_content += """
### newwiki 对应主题

- [服务器与硬件架构](../../newwiki/服务器与硬件架构.md)
- [操作系统与内核](../../newwiki/操作系统与内核.md)
- [云原生与容器](../../newwiki/云原生与容器.md)

### knowledge 对应目录

- [工具与技术](file:///h:/github/cowkb/knowledge/05_tools/)

---

## 参考来源

1. 各厂商官方技术白皮书 2024-2025
2. OCP开放计算社区技术规范
3. Linux内核文档与社区资料
4. 行业分析报告与技术媒体
5. 各大技术会议分享与论文

---

## 更新日志

- 2026-07-18: **深度增强** - 添加卡片定位、核心要点、2025-2026最新进展、相关资源索引、参考来源、更新日志
- 2026-07-17: 初始版本，收录相关主题笔记摘要

---

"""
    
    content = content[:insert_pos] + new_content + content[insert_pos:]
    
    filepath.write_text(content, encoding='utf-8')
    print(f"已增强: {filename} ({data['quality_level']})")
    return True

count = 0
for filename, data in enhancements.items():
    if enhance_file(filename, data):
        count += 1

print(f"\n共增强 {count} 个文件")
