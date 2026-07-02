# 🏗️🧊 服务器形态 + 液冷散热动态跟踪 — 2026-06-17（第6波）

> **搜索范围**: ServeTheHome (HPE Discover 2026, Tensordyne Napier) + Tom's Hardware (Noctua AIO, Frore LiquidJet) + DIGITIMES Asia (6/17头条·空间液冷·铜散热材料)
> **本期焦点**: **HPE Discover 2026—整机柜+UALoE超节点标准落地 · Tensordyne Napier对数数学新形态 · Noctua首款AIO散热器 · 空间数据中心冷却壁垒**
> **写入时间**: 2026-06-17 10:15

---

## 🔥 核心趋势判断（第6波更新）

| # | 趋势 | 更新内容 | 影响等级 |
|:-:|:-----|:---------|:---------|
| 1️⃣ | **超节点Scale-Up互联标准落地** | HPE×Juniper QFS5252首个UALoE交换机亮相，液冷双TH6 | 🔴 重大 |
| 2️⃣ | **新形态因子：对数数学AI处理器** | Tensordyne Napier：3nm/138B晶体管/68PFLOPS/120kW空冷整机柜 | 🔴 重大 |
| 3️⃣ | **空冷vs液冷再平衡** | Tensordyne 120kW空冷推理整机柜 + Noctua AIO工作站级 → 空冷空间仍大 | 🟡 中等 |
| 4️⃣ | **散热材料供应链活跃** | Gem Terminal铜散热材料出货增 + Superior Plating转液冷/CPO | 🟡 中等 |
| 5️⃣ | **空间数据中心冷却壁垒** | 真·太空散热，散热+成本双重障碍 | 🟢 新兴 |

---

## 🏗️ 服务器形态 — 7条

### 1️⃣ HPE Discover 2026：整机柜+UALoE超节点标准落地 🔴

**来源**: ServeTheHome, Patrick Kennedy, 2026-06-16
**链接**: https://www.servethehome.com/hpe-discover-2026-keynote-coverage/

**关键发布矩阵**:

| 产品 | 定位 | 对形态的冲击 |
|:-----|:-----|:------------|
| **HPE AMD Helios AI Rack** | 整机柜 AI 方案 | ✅ 深度集成 Jnuiper 网络 + UALoE |
| **Juniper QFS5252 (UALoE Scale-Up)** | UALink over Ethernet，双 Broadcom TH6，液冷 | ✅ **首个UALoE交换机商用落地**，超节点互联标准里程碑 |
| **Juniper QFS5250 (Scale-Out)** | 液冷, 102.5Tbps | ✅ 超节点=液冷交换机标配 |
| **Juniper PTX12000 (DC-to-DC)** | 800G ZR/ZR+ 跨DC路由 | ✅ 跨数据中心互联规格明确 |
| **Juniper SRX4700 (防火墙)** | 量子安全 1.4Tbps 1U | ✅ 超节点安全层新标准 |
| **Juniper MX301 (Inference Edge)** | 1.6Tbps 1U全双工 | ✅ 推理网络独立架构化 |
| **Juniper QFX5140 (Inference)** | 16Tbps 1RU | ✅ 推理专用交换机形态 |

**HPE三层AI方案矩阵**:
- **HPE Private Cloud AI** → 企业级（共享KVCache + MCP集成 + Alletra Storage MP X10000实时数据）
- **HPE AI Factory at Scale** → Neocloud/超大规模（NVIDIA Vera + 机密计算标准化）
- **HPE AI Factory Sovereign** → 政府/国防（合规级）

**关键形态信号**: HPE这次Keynote以「网络先行」开场（而非计算），与Dell Tech World 2026的「计算为重」形成鲜明对比。**超节点时代网络枢纽地位已从"可选"升级为"开场话题"**。

---

### 2️⃣ Tensordyne Napier：对数数学AI处理器，新形态因子诞生 🔴

**来源**: ServeTheHome, Vic A, 2026-06-15
**链接**: https://www.servethehome.com/tensordyne-napier-ai-processor-announced-with-logarithmic-math/

**核心规格**:

| 参数 | 值 |
|:-----|:----|
| 制程 | TSMC 3nm |
| 晶体管数 | **138B** |
| 计算 | 2.1 PFLOPS/die |
| SRAM | 256MB（**5× Blackwell**） |
| HBM3E | 144GB/die |
| 加速核 | 1.33GHz + 1.5GHz CPU |

**宏大的整机柜设计（TDN72）**:

| 层级 | 组成 | 规格 |
|:-----|:-----|:-----|
| **AI Compute Tray** | 1RU, 9× Napier 芯片 | 1.3TB HBM3E + 8TB 存储 + Intel Xeon 主机 + 双200GbE |
| **TDN Pod** | 4× Compute Tray | 36× Napier |
| **TDN72 Rack** | 4× Pod = **52RU 整机柜** | **72节点, 68 PFLOPS, 42TB HBM, 120kW** |
| TDN Link | 片间互联 | **<1μs延迟, 1TB/s带宽**, 72芯片全互联 |

**关键形态创新点**:
- **对数数学**：乘法→加法，加法器更小→省出面积放SRAM → 不是"更大GPU"而是"不同数学"
- **120kW 空冷**：整机柜72节点68 PFLOPS全部**风冷**，挑战"超节点必须液冷"的假设
- **推理效率对比**：Tensordyne宣称单TDN72机柜= 1,300 tok/s/user，对比NVIDIA+Groq需9柜1500kW，AWS+Cerebras需14柜800kW
- **时间线**：Beta Q1 2027 → 出货 Q2 2027
- **生态**：Hugging Face模型Hub + PyTorch/Triton直接编译 + tensordyne.nn Python eDSL + HPE/Juniper合作伙伴

**潜在风险**: CUDA生态深度和软件栈成熟度是最大不确定因素；2027年出货时NVIDIA/AMD/Cerebras/Groq格局已变

---

### 3️⃣ Foxconn × 电力设备巨头 → AI数据中心整厂集成 🔴

**来源**: DIGITIMES, 2026-06-16 19:04 (头条)
**标题**: "Foxconn teams with major power equipment players to expand into AI data centers"

**核心**: Foxconn 联合电力设备大厂（对标 Schneider 等），从AI机架制造延伸到**数据中心整厂集成**
- 覆盖：供电、冷却、运维
- 形态影响：整机柜从"计算单元"升级为"包含供电+冷却+运维的数据中心模块"
- 与本周ODCC算电织网研讨会同频：标志着**整机柜=供电+冷却+计算三合一产品**的行业共识加速

---

### 4️⃣ 空间数据中心：冷却壁垒与成本障碍 🟢

**来源**: DIGITIMES, 2026-06-17 08:40
**标题**: "Space data centers face cooling hurdles and cost barriers"

**核心**: 太空部署数据中心面临真·散热挑战：
- 真空环境无对流散热，需依赖辐射冷却
- 散热基板面积需求巨大，推高发射成本
- 当前仍有重大成本障碍

**形态意义**: 极端的形态因子约束（真空散热 × 发射重量 × 辐射防护）→ 推动散热技术的极限探索，可能反哺地面高密度散热方案

---

### 5️⃣ AMD EFB 超越 CoWoS：台湾基板三强入局 🔴

**来源**: DIGITIMES, 2026-06-17
**标题**: "AMD opens EFB front beyond CoWoS, putting Taiwan substrate trio in play"

**核心**: AMD Extended Force-Balance (EFB) 封装技术作为 CoWoS 的替代/超越方案推出，台湾三大基板厂商（欣兴/南电/景硕）入局
- 形态影响：封装基板选择从 TSMC CoWoS 单一路线走向多路线
- 对超节点形态：更大的封装可能性 → 更大的OAM尺寸 → 整机柜布局设计变化

---

### 6️⃣ Superior Plating Technology 转型液冷+CPO 🟡

**来源**: DIGITIMES, 2026-06-17 09:30
**标题**: "Superior Plating Technology turns to AI liquid cooling and CPO"

**核心**: 台湾表面处理/电镀企业转向AI液冷与共封装光学（CPO）
- 形态影响：供应链非传统玩家进入液冷领域 → 液冷产能和成本或将改善
- 体现 AI 硬件热潮对传统制造商的拉动效应

---

### 7️⃣ 中国AI算力价格战 + 芯片出货 🟡

**来源**: DIGITIMES, 2026-06-17 headlines
**标题**: "China cuts AI compute prices, revealing pressure to fill supercomputing capacity"
**相关**: "ByteDance in talks for Iluvatar, Baidu Kunlunxin AI chips as Doubao demand grows"

**核心**:
- 中国算力中心空置压力 → 算力价格战启动
- 百度字节采购壁仞/昆仑芯 → 国产AI芯片生态加速
- 形态影响：国产芯片入局 → 服务器形态双轨（NVIDIA x86 + 国产Arm/RISC-V）

---

## 🧊 液冷散热方案 — 6条

### 1️⃣ Noctua 首款 AIO 液冷散热器正式发布 🟡

**来源**: Tom's Hardware, Jowi Morales, 2026-06-16
**标题**: "Noctua finally releases its first AIO coolers"

**核心**:
- 240mm 版本起价 ~**$250**
- 搭载 **Asetek 第8代泵** 技术
- 配备 **NF-A12/A14** 猫头鹰经典风扇
- 工作站/桌面级，非数据中心级别
- 市场信号：**顶级风冷厂商正式进入一体水冷市场**，PC级→专业工作站级

**行业意义**：Noctua 作为全球风冷标杆的转身，反映了 **2026年散热行业"液冷化"的不可逆性**

---

### 2️⃣ Frore LiquidJet Nexus — 4,400W+ 固态冷板 🟡

**来源**: Tom's Hardware, Anton Shilov, 2026-06-04
**标题**: "Frore shows off LiquidJet Nexus coldplate for Nvidia Vera Rubin, other AI accelerators"

**核心**:
- MEMS（微机电）射流技术，**无活动部件**
- 4,400W+ 散热能力，覆盖Vera Rubin级AI加速器
- MTBF 10倍于传统泵方案
- 直接冷却（消除TIM层）

**行业意义**：非泵液冷的第三条路径，降低数据中心液冷部署的机械故障风险

---

### 3️⃣ Superior Plating → AI液冷（见形态第6条）🟡

**来源**: DIGITIMES, 2026-06-17
**核心**: 台湾表面处理企业跨界进入液冷（冷板/CPO冷却）

**供应链信号**: 液冷已从"少数专业厂商"转向"广泛的传统制造能力转型" → 液冷产能和成本曲线将快速改善

---

### 4️⃣ Gem Terminal：AI散热铜材料出货增长 🟡

**来源**: DIGITIMES, 2026-06-17 08:41
**标题**: "Gem Terminal eyes new growth curve in 2026 with shipments of AI-related thermal materials"
**标签**: copper, thermal module, cooling

**核心**:
- 台湾铜材料厂商AI散热铜材出货增长
- 台湾铜厂产能持续拉升（季度环比增长）
- 铜散热基板在液冷冷板/热管/VC中的需求随AI密度提升

**形态影响**: 散热材料的供应链本土化趋势→降低成本→液冷推广加速

---

### 5️⃣ 空间数据中心冷却壁垒 🟢

**来源**: DIGITIMES, 2026-06-17
**核心**: 太空真空环境下，传统风冷/液冷均不适用，需纯辐射冷却方案
- 无冷却液 → 排除液冷
- 无空气 → 排除风冷
- 当前仅有的方案：大面积辐射散热板 + 热管/环路热管

---

### 6️⃣ 第5波趋势回顾

**来自 2026-06-16 的液冷趋势**:
- **Wiwynn 总裁散热瓶颈喊话**：150kW+ 液冷已成必需品
- **Foxconn×Schneider 液冷出厂预集成**：从"DC工程"变为"ODM预装"
- **BESS 储能转型** → 备用冷却供电保障，冷却泵/CDU在电网波动时保持运行

---

## 📊 本周累计（06-12→06-17）

| 日期 | 文件 | 服务器形态 | 液冷散热 | 累计 |
|:-----|:-----|:----------|:---------|:-----|
| 06-12 | `2026-06-12.md` | 11条 | 10条 | 21 |
| 06-13 | `2026-06-13.md` | 6条 | 4条 | 31 |
| 06-14 | `2026-06-14.md` | 13条 | 10条 | 54 |
| 06-15 | `2026-06-15-supplement.md` | 7条 | 4条 | 65 |
| 06-16 | `2026-06-16-supplement.md` | 12条 | 4条 | 81 |
| **06-17** | **`2026-06-17-form-factor-cooling.md`** | **7条** | **6条** | **94** |

---

## 🔗 交叉引用

- [HPE Discover 2026 Keynote Coverage (STH)](https://www.servethehome.com/hpe-discover-2026-keynote-coverage/)
- [Tensordyne Napier AI Processor (STH)](https://www.servethehome.com/tensordyne-napier-ai-processor-announced-with-logarithmic-math/)
- [Noctua First AIO Coolers (Tom's Hardware)](https://www.tomshardware.com/pc-components/cooling/)
- [DIGITIMES Asia (6/17)](https://www.digitimes.com/)
- [超节点第十三次跟踪](../../01_survey/bmc-system/2026-06-17.md) — HPE Helios+UALoE 超节点标准
- [2026-06-17 芯片与市场格局跟踪] — NVIDIA/Qualcomm 融资并购动态
