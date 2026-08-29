# AI对服务器研发图的解读方案 — 深度分析

> **概要**: 分析AI解读服务器研发各类框图（draw.io/Visio/SVG/PDF）的方案矩阵与解析流水线设计
>
> **关键词**: 图解读 · 服务器研发 · draw.io解析 · 矢量提取 · 方案矩阵

---

## 📑 目录

- [1. 问题定义：服务器研发有哪些图？](#1-问题定义服务器研发有哪些图)
  - [1.1 图类型全景](#11-图类型全景)
  - [1.2 核心矛盾](#12-核心矛盾)
  - [1.3 解读目标分级](#13-解读目标分级)
- [2. 源头分析：图的格式与信息密度](#2-源头分析图的格式与信息密度)
  - [2.1 格式维度](#21-格式维度)
  - [2.2 各格式本质差异](#22-各格式本质差异)
  - [2.3 关键洞察](#23-关键洞察)
- [3. 技术方案矩阵](#3-技术方案矩阵)
  - [3.1 三方案总览](#31-三方案总览)
  - [3.2 方案选择的决策树](#32-方案选择的决策树)
- [4. 方案一：原生结构解析（最优路径）](#4-方案一原生结构解析最优路径)
  - [4.1 draw.io 解析原理](#41-drawio-解析原理)
  - [4.2 解析流水线](#42-解析流水线)
  - [4.3 规则引擎设计](#43-规则引擎设计)
  - [4.4 Visio (.vsdx) 解析](#44-visio-vsdx-解析)
  - [4.5 SVG解析](#45-svg解析)
- [5. 方案二：PDF矢量/光栅混合方案](#5-方案二pdf矢量光栅混合方案)
  - [5.1 PDF内部结构](#51-pdf内部结构)
  - [5.2 矢量提取方法](#52-矢量提取方法)
  - [5.3 矢量→结构化的四步工作流](#53-矢量结构化的四步工作流)
    - [第1步：文本分类](#第1步文本分类)
    - [第2步：图形元素分类](#第2步图形元素分类)
    - [第3步：几何推理连接关系](#第3步几何推理连接关系)
    - [第4步：嵌入图片处理](#第4步嵌入图片处理)
  - [5.4 PDF输出为Markdown的嵌入方案](#54-pdf输出为markdown的嵌入方案)
- [图3: CPU到GPU互联拓扑](#图3-cpu到gpu互联拓扑)
  - [截图视图](#截图视图)
  - [矢量提取结果](#矢量提取结果)
  - [OCR辅助提取](#ocr辅助提取)
- [6. 方案三：全OCR方案（兜底路径）](#6-方案三全ocr方案兜底路径)
  - [6.1 OCR引擎选择](#61-ocr引擎选择)
  - [6.2 OCR的核心局限](#62-ocr的核心局限)
  - [6.3 OCR + 后处理增强](#63-ocr-后处理增强)
  - [6.4 大模型VLM的虚假自信问题](#64-大模型vlm的虚假自信问题)
- [7. 按图类型的推荐策略](#7-按图类型的推荐策略)
  - [7.1 策略矩阵](#71-策略矩阵)
  - [7.2 优先级排序](#72-优先级排序)
- [8. 输入/输出材料管理体系](#8-输入输出材料管理体系)
  - [8.1 目录结构设计](#81-目录结构设计)
  - [8.2 版本映射机制](#82-版本映射机制)
  - [8.3 关键管理规则](#83-关键管理规则)
  - [8.4 输入文件登记表](#84-输入文件登记表)
- [9. 摘要决策机制](#9-摘要决策机制)
  - [9.1 何时需要摘要](#91-何时需要摘要)
  - [9.2 摘要分级](#92-摘要分级)
  - [9.3 摘要生成规则](#93-摘要生成规则)
  - [9.4 摘要与原文的链接机制](#94-摘要与原文的链接机制)
- [10. 局限性与风险](#10-局限性与风险)
  - [10.1 当前AI能力边界（基于实测经验）](#101-当前ai能力边界基于实测经验)
  - [10.2 风险清单](#102-风险清单)
  - [10.3 红线规则](#103-红线规则)
- [总结：务实路线](#总结务实路线)
- [关联知识](#关联知识)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 问题定义：服务器研发有哪些图？

### 1.1 图类型全景

按服务器研发流程中实际出现的图类型分类：

| 类别 | 图类型 | 常见格式 | 信息密度 | 结构化程度 | 出现阶段 |
|:-----|:-------|:---------|:--------:|:----------:|:---------|
| **架构图** | 系统框图 | draw.io / Visio / SVG | 中 | 高 | 系统设计 |
| | 功能模块图 | draw.io / PNG | 中 | 中 | 需求/设计 |
| | 逻辑拓扑图 | draw.io / PNG | 中 | 高 | 系统设计 |
| **电路图** | 原理图(Schematic) | PDF (EDA导出) | **极高** | 高 | 硬件设计 |
| | 电源树/Power Tree | PDF/Visio | 高 | 中 | 硬件设计 |
| | 时钟分布图 | PDF/Visio | 中 | 中 | 硬件设计 |
| | 复位序列图 | PDF/Visio | 中 | 中 | 硬件设计 |
| **PCB图** | Layout图 | PDF/Gerber (EDA导出) | **极高** | 低 | PCB设计 |
| | 叠层图 | PDF/Excel | 中 | 中 | PCB设计 |
| | 阻抗控制图 | PDF | 中 | 中 | PCB设计 |
| **时序图** | 信号时序图 | PDF/Visio/SVG | 高 | 中 | 硬件设计 |
| | 眼图 | PNG (示波器导出) | 高 | **低** | 测试验证 |
| **结构图** | 3D装配图 | STEP/STL/PDF | **极高** | 低 | 结构设计 |
| | 2D工程图 | DWG/PDF | 高 | 低 | 结构设计 |
| | 爆炸图 | PDF/PPT | 中 | 低 | 生产/文档 |
| **流程图** | 状态机图 | draw.io/PDF | 中 | 高 | CPLD/FPGA |
| | 数据流图 | draw.io/PDF | 中 | 中 | 系统设计 |
| | 测试流程图 | draw.io/PPT | 低 | 中 | 测试 |
| **结果图** | 仿真结果图 | PNG (仿真软件导出) | 高 | **极低** | 验证 |
| | 测试曲线 | CSV/PNG/PDF | 高 | **极低** | 测试 |

### 1.2 核心矛盾

图的**信息密度**与**结构化程度**成反比：

```text
结构化程度高    信息密度高
    ^              ^
  架构图         原理图/PCB图
  (draw.io)      (EDA/PDF)
    |              |
  易被AI解析    难被AI解析
    v              v
结构化程度低    信息密度极高
```

> AI擅长解析结构化内容（节点、连线的语义关系），不擅长从光栅图中逐像素提取信息。
> 服务器研发中最需要被理解的恰恰是信息密度最高的图（原理图、PCB图、时序图）。

### 1.3 解读目标分级

不是所有图都需要完整解读。按目标分级：

| 级别 | 目标 | 适用图类型 | 对AI要求 |
|:----:|:-----|:-----------|:---------|
| **L1** | 知道存在什么图（元数据） | 所有类型 | 低（文件名+缩略图即可） |
| **L2** | 理解图的骨架结构（节点+连线） | 架构图/流程图/时序图 | 中 |
| **L3** | 提取图中的量化和标注信息 | 原理图/电源树/叠层图 | **高** |
| **L4** | 理解图中信号的精确语义 | 原理图/时序图/状态机 | **极高** |
| **L5** | 从图中推理出设计意图和约束 | 全部 | **极高**（超出当前AI能力边界） |

> **关键判定**：服务器研发场景中，L3级（提取量化+标注信息）是当前AI能力与需求的最佳平衡点。
> L4-L5需要领域知识做后验推理，不应依赖AI的"理解"，而应依赖结构化的先验知识库。

---

## 2. 源头分析：图的格式与信息密度

### 2.1 格式维度

```text
                结构化程度高
                     |
          draw.io(.drawio/.svg)   <- 原生结构可解析
          Visio(.vsdx)            <- 可解压缩为XML
          SVG                     <- 矢量结构可解析
                     |
  ------- 中间线：可结构化解析 -------
                     |
          PDF (矢量)  <- 可提取路径/文本，但丢失语义
          PDF (混合)  <- 矢量光栅混合
          PPT导出PNG  <- 只有像素
                     |
          PNG/JPG/扫描PDF  <- 只有像素
                     |
                结构化程度低
```

### 2.2 各格式本质差异

| 格式 | 内部结构 | 对AI可解析度 | 典型延迟 | 致命缺陷 |
|:-----|:---------|:------------:|:--------:|:---------|
| **draw.io (.drawio)** | XML（节点+连线+文本+样式完整） | **极高** | 即时 | 非通用格式 |
| **SVG** | XML（矢量路径+文本可提取） | 高 | 即时 | 丢失语义分组 |
| **Visio (.vsdx)** | ZIP内XML（形状+连接线） | 高 | 即时 | 微软格式 |
| **PDF (矢量导出)** | 图形操作符序列 | 中 | 低 | 文本顺序乱/分组丢失 |
| **PDF (嵌入PNG)** | 无法解析内部 | **低** | 需OCR | 像素化信息损失 |
| **PNG/JPG** | 无内部结构 | **极低** | 需OCR | 完全丢失结构化信息 |
| **EDA导出PDF** | 矢量线条+标注文本 | 中 | 低 | 层次/网络标号语义丢失 |
| **扫描件PDF** | 图片 | **极低** | OCR | 精度受限于扫描质量 |

### 2.3 关键洞察

**PDF是一个被严重低估难度的问题**。从PDF中提取结构化信息比想象中难得多：

1. **PDF不是DOCX**：PDF的设计目标是"打印出来一样"，不是"解析出原始结构"
2. **文本顺序不可靠**：PDF中文本绘制顺序是页面位置决定的，不是阅读顺序
3. **图元分组很弱**：标签应该属于哪个节点？连线的起点终点分别是什么？PDF不记录这些
4. **EDA导出的原理图PDF尤其难**：网络标号（Net Label）是文本，但属于哪根线？电源符号是图形+文本组合，但语义是什么？PDF不会告诉你"VCC_3V3"和一条粗线之间有关系

**结论**：最有效的方案是**从源头获取结构化格式**，而不是从PDF反向推算。

---

## 3. 技术方案矩阵

### 3.1 三方案总览

| 方案 | 核心思路 | 适用格式 | 准确率(估) | 工作量 | 维护成本 |
|:-----|:---------|:---------|:----------:|:------:|:--------:|
| **① 原生解析** | 直接解析draw.io/SVG/Visio XML | .drawio/.vsdx/SVG | **~95%** | 低(脚本化) | 低 |
| **② PDF复合** | PDF矢量提取+OCR辅助 | PDF(矢量/混合) | ~60-85% | 中 | 中 |
| **③ 全OCR** | 截图+大模型OCR | PNG/JPG/扫描PDF | ~40-70% | 低(调API) | **高**(模型迭代) |

### 3.2 方案选择的决策树

```text
图有原生结构化格式(draw.io/vsdx/SVG)?
+-- 是 -> 方案① (原生解析)，性价比最高
+-- 否 -> 图是PDF格式？
        +-- 是 -> PDF是矢量导出(文本可选)?
        |       +-- 是 -> 方案② (PDF矢量提取)
        |       +-- 否 -> PDF是嵌入图片?
        |               +-- 是 -> 方案③ (全OCR)
        |               +-- 否 -> 混合 -> 方案②+③
        +-- 否 -> 图是图片格式(PNG/JPG)?
                +-- 是 -> 方案③ (全OCR)
```

---

## 4. 方案一：原生结构解析（最优路径）

### 4.1 draw.io 解析原理

draw.io 文件本质是XML，结构如下（简化示意）：

```xml
<mxfile>
  <diagram name="Page-1">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>         <!-- 根节点 -->
        <mxCell id="1" parent="0"/>  <!-- 画布 -->

        <!-- 节点：CPU -->
        <mxCell id="2" value="AMD EPYC Turin"
                style="rounded=1;whiteSpace=wrap;html=1;"
                vertex="1" parent="1">
          <mxGeometry x="100" y="50" width="160" height="60"/>
        </mxCell>

        <!-- 节点：PEX89104 -->
        <mxCell id="3" value="PEX89104 #0"
                style="..."]
                vertex="1" parent="1">
          <mxGeometry x="120" y="200" width="140" height="50"/>
        </mxCell>

        <!-- 连线：CPU→PEX -->
        <mxCell id="4" value="G0 x16" style="strokeColor=#FF0000;"
                edge="1" parent="1"
                source="2" target="3">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**可提取的信息**：

- 每个节点的**位置、大小、标签文本、样式**(颜色/形状)
- 每条连线的**起点、终点、标签、颜色、线型**
- 节点编组关系（父-子层级）
- 图层/页面结构

### 4.2 解析流水线

```text
.drawio文件
    |
    v
XML解析器 (Python xml.etree / lxml)
    |
    v
提取节点表 + 连线表
    |
    v
语义映射层 (规则引擎)
|   +- "CPU"形状 -> CPU节点 (标签匹配)
|   +- 红色连线 -> PCIe数据通路 (颜色匹配)
|   +- 蓝色连线 -> 管理平面 (颜色匹配)
|   +- 绿色连线 -> 备用路径 (颜色匹配)
|   +- 箭头方向 -> 数据流向 (箭头样式)
    |
    v
结构化输出 (JSON/Markdown表格)
```

### 4.3 规则引擎设计

规则引擎不依赖外部，用确定性规则即可：

```python
# 语义映射规则（示例，基于我方图纸规范）
SEMANTIC_RULES = {
    "node_colors": {
        "#FFE6CC": "CPU",
        "#DAEEF3": "Switch/Retimer",
        "#E2EFDA": "GPU",
        "#F2F2F2": "Passive(Connector)",
    },
    "edge_colors": {
        "#FF0000": "PCIe Primary",
        "#00FF00": "PCIe Alt/Spare",
        "#0000FF": "Management(I2C/SPI)",
        "#000000": "Power/Ground",
        "#800080": "Clock/Ref",
    },
    "label_patterns": {
        r"^CPU\d?$": "cpu",
        r"^PEX\d{5}": "pcie_switch",
        r"^GPU\s*#\d": "gpu",
        r"^x\d{2}": "lane_width",
        r"(I2C|SPI|GPIO|UART)": "management_signal",
    }
}
```

### 4.4 Visio (.vsdx) 解析

Visio文件是ZIP压缩包，内含XML：

```text
file.vsdx (ZIP)
+-- docProps/
+-- visio/
|   +-- pages/
|   |   +-- page1.xml      # 页面内容
|   +-- masters/
|   |   +-- master1.xml     # 形状母版
|   +-- ...
+-- [Content_Types].xml
```

**与draw.io的关键差异**：

- Visio形状是**Master-Instance**模式（母版定义样式，实例关联母版）
- 连接线通过**Connect**元素关联起点和终点Shape
- 形状的属性（Text、Fill、Line）在 **Shape/Section/Row** 中

**解析流程**：

1. 解压ZIP
2. 读取pages/page1.xml
3. 遍历 `vis:Shape` 提取节点
4. 遍历 `vis:Connect` 提取连线
5. 关联Master读取样式语义

### 4.5 SVG解析

SVG本身就是结构化的，但比draw.io更难的原因是：

```svg
<!-- SVG 中"节点"和"连线"没有语义标签，全靠人眼判断 -->
<g id="cpu_block" transform="translate(100,50)">
  <rect x="0" y="0" width="160" height="60" rx="8" fill="#FFE6CC"/>
  <text x="80" y="35" text-anchor="middle">AMD EPYC Turin</text>
</g>
<line x1="180" y1="80" x2="190" y2="200" stroke="red" stroke-width="3"/>
```

**SVG缺点**：

- 没有"节点vs连线"的显式区分
- `g` 标签不保证是逻辑分组（可能是样式分组）
- 文本位置和图形位置需要几何推理确定归属

**SVG解析策略**：

1. 遍历所有闭合图形（rect/ellipse/path）→ 记作候选节点
2. 遍历所有不封闭线条（line/polyline）→ 记作候选连线
3. 几何推理：连线端点距离最近的节点边界 → 确定连接关系
4. 文本位置：文本在哪个图形包围盒内 → 确定标签归属

> **效率排序**: draw.io解析 > Visio解析 > SVG解析
> **推荐**: 优先保留draw.io原生格式，不导出为SVG/PDF再解析

---

## 5. 方案二：PDF矢量/光栅混合方案

### 5.1 PDF内部结构

PDF的结构与HTML/CSS完全不同：

```text
PDF Page
+-- Content Stream (绘图指令序列)
|   +-- cm (变换矩阵)          -> 坐标系变换
|   +-- re / h / f (路径)     -> 矩形/闭合/填充
|   +-- S / s / B (描边)      -> 线绘制
|   +-- Tj / TJ (文本)        -> 文本绘制
|   +-- Do (外部对象引用)     -> 嵌入图片引用
|   +-- q / Q (状态保存/恢复) -> 图形状态栈
|
+-- Resources
|   +-- XObject (图片/Form)   -> 嵌入图片
|   +-- Font (字体定义)
|
+-- Annotations (注释)
```

**关键问题**：PDF的指令序列是按"物理位置"而非"逻辑结构"排列的。文本 `VCC_3V3` 可能在页面左上角绘制，但属于页面中央的电源网络——因为PDF不知道"语义归属"。

### 5.2 矢量提取方法

使用 `pdfminer.six` 或 `PyMuPDF(fitz)` 提取：

```python
import fitz  # PyMuPDF

doc = fitz.open("schematic.pdf")
page = doc[0]

# 提取所有文本（位置+内容）
text_blocks = page.get_text("blocks")
# 返回: [(x0, y0, x1, y1, "文本内容", block_no, block_type)]

# 提取所有图片
images = page.get_images()

# 提取所有路径（矢量图形）
paths = page.get_drawings()
# 返回每条路径的: 矩形包围盒、路径点序列、颜色、线宽、填充
```

### 5.3 矢量→结构化的四步工作流

#### 第1步：文本分类

```text
文本块
+-- 大号/粗体文本 -> 标题/图名
+-- 对齐文本在矩形内 -> 标注/标签
+-- 小号文本靠近线条 -> 网络名/信号名
+-- 表格状排列文本 -> 参数表格
+-- 旋转文本 -> 竖排标注/轴标签
```

#### 第2步：图形元素分类

```text
路径/图形
+-- 矩形（粗线框） -> 芯片/模块
+-- 矩形（细线框） -> 表格/文本框
+-- 线条（多段线） -> 连线/总线
+-- 箭头 -> 数据流向/信号方向
+-- 圆形/椭圆 -> 连接点/端口
+-- 正弦/方波 -> 时钟/信号波形示意
```

#### 第3步：几何推理连接关系

```text
1. 找到所有"端口/引脚"（圆形端点/矩形边缘的小凸起）
2. 追踪连线找到两个端口
3. 端口周围最近的文本 -> 网络标号
4. 端口属于哪个模块 -> 包围盒包含端口
5. 输出: (模块A, 端口A, 网络名, 模块B, 端口B)
```

**几何推理算法的局限**：

| 场景 | 成功率 | 原因 |
|:-----|:------:|:-----|
| 直线连接两个模块 | ~80% | 线条两端易匹配 |
| 总线（多条平行线） | ~40% | 区分单根线困难 |
| 电源/地符号 | ~30% | 符号形态多样 |
| 交叉线（无跳线标记） | ~20% | 无法区分连接/跨越 |
| 带网络标号的飞线 | ~60% | 需要文本匹配 |

#### 第4步：嵌入图片处理

PDF中原理图常包含**嵌入的图片元素**（芯片内部框图、连接器布局照片等）：

```python
# 提取PDF中的嵌入图片
images = page.get_images(full=True)
for img_idx, img in enumerate(images):
    xref = img[0]  # 图片对象引用
    pix = fitz.Pixmap(doc, xref)
    pix.save(f"extracted_img_{img_idx}.png")
    img_bbox = img[2:6]  # 图片在页面上的位置
```

这些图片需要：

1. **保留原位置标注**：记录图片在PDF中的矩形坐标
2. **截图嵌入Markdown**：![图片描述](extracted_img_0.png)
3. **OCR辅助识别**：提取图片中的文字信息
4. **与周围矢量的关联**：图片的连线端口是否与矢量线条相连？

### 5.4 PDF输出为Markdown的嵌入方案

```text
# 服务器架构图（原始PDF: compute-node-arch-v2.pdf P3）

## 图3: CPU到GPU互联拓扑

### 截图视图

![CPU-GPU互联拓扑](images/fig3_cpu_gpu_topology.png)

### 矢量提取结果

| 模块 | 位置 | 提取信息 |
|:-----|:-----|:---------|
| CPU (AMD EPYC Turin) | (100,50)-(260,110) | P0-P4, G0-G3 端口 |
| PEX89104 #0 | (120,200)-(260,250) | S0,S1,S4-S8 端口 |
| OAM GPU #0 | (300,350)-(360,400) | PCIe Host Interface |

| 连线 | 起点 | 终点 | 提取信息 |
|:-----|:-----|:-----|:---------|
| G0 x16 | CPU -> PEX#0 S0 | 红色, PCIe |
| S4 x16 | PEX#0 -> Retimer#1 | 红色, PCIe |
| ... | ... | ... | ... |

### OCR辅助提取

![图片片段OCR区域](images/fig3_ocr_region1.png)

```

OCR识别结果：
Network Label: VCC_3V3_GPU0
Resistor Value: 4.7KΩ, 0402
Capacitor: 0.1μF, 0402, 16V

```text

> ⚠️ **黄色标记**: 图中DNP(不焊接)元件未在PDF矢量中标记，需人工确认
> ⚠️ **红色标记**: 此区域网络标号被总线遮挡，OCR置信度<60%
```

---

## 6. 方案三：全OCR方案（兜底路径）

### 6.1 OCR引擎选择

| 引擎 | 适用场景 | 中文识别 | 结构化输出 | 部署方式 |
|:-----|:---------|:--------:|:----------:|:---------|
| **Tesseract 5** | 通用文本 | 中（需chi_sim） | 有（hOCR/ALTO） | 本地 |
| **PaddleOCR** | 中文文档 | **好** | 有（JSON） | 本地 |
| **大模型VLM** | 图文综合理解 | **好** | 有（自然语言） | API调用 |
| **EasyOCR** | 多语言混合 | 中 | 有（文本+坐标） | 本地 |

### 6.2 OCR的核心局限

```text
OCR能做什么:
✅ 提取图中清晰的文本标签
✅ 识别表格中的文字和数字
✅ 识别图中符号（在训练集内）
✅ 标注文本位置（包围盒）

OCR不能做什么:
❌ 理解"VCC_3V3"和"GND"之间的电气关系
❌ 判断两条交叉线是连接还是跨越
❌ 识别电源符号的语义（VCC vs VDD vs VSS）
❌ 区分原理图和框图（同样的矩形可能是芯片也可能是注释框）
❌ 推理图中的隐含约束（"为什么这里放4.7K上拉？"）
```

### 6.3 OCR + 后处理增强

```python
# OCR后处理流水线（以PaddleOCR为例）

def ocr_postprocess(ocr_results):
    # 输入: PaddleOCR返回的JSON
    # [ [[x0,y0],[x1,y0],[x1,y1],[x0,y1]], "文本内容", 置信度 ]

    # 第1步：文本聚类（基于y坐标的行对齐）
    lines = cluster_by_y(ocr_results, threshold=5)

    # 第2步：表格结构重建
    tables = detect_tables(lines)
    # 判断：连续的矩形排列+对齐文本 → 输出为Markdown表格

    # 第3步：标签-图形关联
    # 找距离最近的图形元素（从PDF矢量提取的路径）
    for text_box in lines:
        nearest_graphics = find_nearest_bbox(text_box, graphics_list)
        text_box["belongs_to"] = nearest_graphics.id

    # 第4步：网络标号识别
    # 特征：短文本(4-12字符)、大写+数字+下划线、在线的端点附近
    net_labels = []
    for text_box in lines:
        if is_near_line_end(text_box, all_lines):
            if is_net_label_format(text_box.text):
                net_labels.append(text_box)

    return {
        "text_elements": lines,
        "tables": tables,
        "net_labels": net_labels,
    }
```

### 6.4 大模型VLM的虚假自信问题

> **这是最需要警惕的问题**

用大模型读图时，经常会：

1. **编造不存在的连接**："图中有CPU连接到GPU0的PCIe x16链路"——实际图上可能只有x8
2. **忽略细节**：漏掉DNP（不焊接）标记、忽略备用路径
3. **错误归纳**："图中所有GPU连接到同一个Switch"——实际是双Switch分别管理
4. **一致性幻觉**：前后两次解读同一张图，得出不同的拓扑结论

**应对策略**：

- 不要用一张完整的原理图去问大模型"这张图是什么"——必错
- 切分为小的独立区域，逐块询问
- 每次只问确定性问题（"这个矩形中标记了什么数字？"），不问开放性推理题
- 两次询问覆盖同一区域，比较结果一致性

---

## 7. 按图类型的推荐策略

### 7.1 策略矩阵

| 图类型 | 推荐方案 | 预期准确率 | 说明 |
|:-------|:---------|:----------:|:-----|
| **draw.io架构图** | 方案① 原生XML解析 | ~95% | 源头解析，最可靠 |
| **draw.io流程图** | 方案① 原生XML解析 | ~95% | 同架构图 |
| **draw.io状态机** | 方案① 原生XML解析 | ~90% | 状态+转移完整提取 |
| **Visio结构图** | 方案① ZIP+XPath | ~85% | Visio解析成熟 |
| **SVG框图** | 方案① 几何推理 | ~70% | 文本-图形关联有误差 |
| **EDA导出原理图PDF(矢量)** | 方案② 矢量+几何 | ~65% | 网络标号提取较可靠 |
| **EDA导出原理图PDF(Emf/嵌入)** | 方案②+③ 混合 | ~50% | 图片区域用OCR |
| **PPT导出架构图PNG** | 方案③ OCR+VLM | ~60% | 结构简单可接受 |
| **PCB Layout PDF** | **不推荐AI解读** | <30% | 层次太深，AI当前做不到 |
| **示波器截图PNG(眼图)** | 方案③ 定点OCR | ~70% | 只要提取数值即可 |
| **仿真曲线图PNG** | 方案③ 定点OCR | ~80% | 提取轴标签+曲线值 |
| **3D装配图PDF/STP** | **不推荐AI解读** | <20% | 需专业工具打开 |
| **测试报告截图** | 方案③ OCR | ~80% | 表格提取较成熟 |

### 7.2 优先级排序

按**投入产出比**排序，从最值得做的开始：

```text
P0（立即做）:
   1. draw.io架构图/流程图 -> 原生XML解析  -> 脚本2小时搞定
   2. 测试报告截图中的表格 -> OCR表格提取 -> 工具链成熟

P1（近期做）:
   3. EDA导出原理图PDF -> 网络标号提取  -> 价值高，需规则打磨
   4. 时序/序列图 -> 波形+标签提取  -> 中等难度

P2（评估后做）:
   5. 电源树PDF -> 电压值+电流值提取  -> 格式不统一
   6. 叠层结构图 -> 参数提取  -> 各厂输出格式差异大

P3（不做）:
   7. PCB Layout -> 层次太复杂  -> AI当前能力不够
   8. 3D装配图 -> 需专业工具  -> 交给结构工程师
```

---

## 8. 输入/输出材料管理体系

### 8.1 目录结构设计

```text
materials/
+-- input/                          <- 原始输入，只读不写
|   +-- original/                   <- 原始文件（来自供应商/设计工具）
|   |   +-- schematic_v1.2.pdf
|   |   +-- topology_v3.drawio
|   +-- screenshot/                 <- 截图/拍照（来自会议/文档）
|   |   +-- 2026-07-15_power_tree_discussion.png
|   +-- metadata.csv               <- 输入文件登记表
|
+-- output/                          <- AI输出，可追踪可回滚
|   +-- extracted/                   <- 结构化提取结果
|   |   +-- 2026-07-15/
|   |   |   +-- schematic_v1.2_extracted.json
|   |   |   +-- topology_v3_extracted.json
|   |   +-- index.json              <- 提取记录索引
|   +-- report/                      <- 解读报告
|   |   +-- 2026-07-15_schematic_analysis.md
|   |   +-- 2026-07-16_topology_report.md
|   +-- issue/                       <- 解读过程中发现的问题
|       +-- 2026-07-15_schematic_issues.md
|
+-- version_map.json                 <- 输入->输出的版本映射
+-- README.md                        <- 本目录使用说明
```

### 8.2 版本映射机制

```json
// version_map.json
{
  "mappings": [
    {
      "input": "topology_v3.drawio",
      "input_version": "v3",
      "output": [
        {
          "file": "output/extracted/2026-07-15/topology_v3_extracted.json",
          "version": "v1",
          "engine": "drawio_parser_v0.2",
          "created": "2026-07-15T10:30:00Z",
          "status": "complete"
        }
      ],
      "changelog": [
        {"date": "2026-07-15", "action": "首次解析v3图", "version": "v1"},
        {"date": "2026-07-16", "action": "修正G2-G3端口映射错误", "version": "v2"}
      ]
    },
    {
      "input": "schematic_v1.2.pdf",
      "input_version": "v1.2",
      "output": [
        {
          "file": "output/extracted/2026-07-15/schematic_v1.2_extracted.json",
          "version": "v1",
          "engine": "pdf_extractor_v0.5",
          "created": "2026-07-15T14:00:00Z",
          "status": "partial",
          "notes": "电源网络提取完毕，控制信号待补充"
        }
      ]
    }
  ]
}
```

### 8.3 关键管理规则

| 规则 | 说明 |
|:-----|:------|
| **Input只读** | 任何AI流程不得修改input/下的原始文件。要标注 → 在output/下建副本标注 |
| **版本前缀** | 输出文件命名包含输入版本号，确保可追溯 |
| **每次跑出新版本** | 不要覆盖输出文件，旧版本保留并标记"deprecated" |
| **引擎版本记录** | 每次解析记录使用什么脚本/规则/模型版本 |
| **失败也要记录** | 解析失败时，保存失败日志+截图，标记"failed"而非不记录 |
| **人工校验标记** | 输出结果中标注"auto_extracted"或"human_verified" |

### 8.4 输入文件登记表

```csv
# metadata.csv
file_name,type,source,received_date,format,size,hash,notes
topology_v3.drawio,架构图,设计部李XX,2026-07-14,drawio,2.1MB,sha256:xxx,CPU-GPU互联拓扑
schematic_v1.2.pdf,原理图,EDA导出,2026-07-14,pdf,8.4MB,sha256:yyy,含电源树页
2026-07-15_power_tree.png,草图,会议拍照,2026-07-15,png,0.5MB,sha256:zzz,白板讨论
```

---

## 9. 摘要决策机制

### 9.1 何时需要摘要

| 条件 | 做摘要 | 不做摘要 |
|:-----|:------:|:--------:|
| 图的信息量 > 1000条提取记录 | ✅ | ❌ |
| 图中有冗余重复信息 | ✅ | ❌ |
| 图中信息已结构化到数据库 | ✅ | ❌ |
| 需要快速浏览（评审/汇报） | ✅ | ❌ |
| 需要精确数值对比 | ❌ | ✅ |
| 图中信息有争议需对齐原文 | ❌ | ✅ |

### 9.2 摘要分级

```text
L1: 元数据摘要 (自动生成，不需AI)
    - 图名、类型、版本、页面数
    - 包含的模块/节点数量
    - 包含的连线/连接数量
    - 是否有未处理区域

L2: 结构摘要 (规则引擎生成)
    - 主要模块及其之间的关系
    - 关键数据通路（带宽/延迟）
    - 冗余/备用路径数量
    - 管理平面拓扑

L3: 语义摘要 (需要一定领域知识)
    - 设计意图推断
    - 关键设计约束
    - 异常/不协调之处
    - 与之前版本的差异

L4: <不应用AI做> 决策建议
    - "建议修改XX设计" — 不应由AI生成
    - "XX方案优于YY" — 需人工评审
```

### 9.3 摘要生成规则

```python
# 摘要规则引擎（确定性，不依赖LLM）
def generate_summary(extracted_data, level):
    summary = []

    if level >= 1:
        # L1: 元数据
        summary.append(f"## 图元数据")
        summary.append(f"- 图名: {extracted_data.title}")
        summary.append(f"- 类型: {extracted_data.type}")
        summary.append(f"- 版本: {extracted_data.version}")
        summary.append(f"- 模块数: {len(extracted_data.nodes)}")
        summary.append(f"- 连接数: {len(extracted_data.edges)}")

    if level >= 2:
        # L2: 结构
        summary.append(f"## 结构摘要")
        # 按类型统计模块
        for type_name, count in count_by_type(extracted_data.nodes):
            summary.append(f"- {type_name}: {count}个")
        # 关键通路
        for path in find_critical_paths(extracted_data, min_width="x16"):
            summary.append(f"- {path.name}: {path.width}, {path.color}")
        # 冗余路径
        alt_paths = [e for e in extracted_data.edges if e.color == "green"]
        summary.append(f"- 备用路径: {len(alt_paths)}条")

    if level >= 3:
        # L3: 语义
        anomalies = detect_anomalies(extracted_data)
        for anomaly in anomalies:
            summary.append(f"- ⚠️ {anomaly.description}")

    return "\n".join(summary)
```

### 9.4 摘要与原文的链接机制

摘要中每条信息必须可追溯到原文中的具体位置：

```text
摘要项: "G0 x16 (红色) 连接 CPU-P0 到 PEX89104 #0 S0"
  +-> 原文位置: topology_v3.drawio / Page-1 / Cell id=4
  +-> 子区域: CPU区域 -> PEX区域
  +-> 截图锚点: topology_v3_p1_cpu2pex.png (x=100,y=50,w=260,h=250)
```

---

## 10. 局限性与风险

### 10.1 当前AI能力边界（基于实测经验）

| 能力域 | 当前AI真实水平 | 说明 |
|:-------|:-------------:|:-----|
| 提取图中独立文本 | **优秀**(>90%) | 只要清晰即可 |
| 提取图中表格 | **良好**(~80%) | 有结构化格式时更佳 |
| 识别图中的模块关系 | **中**(~65%) | 对非标准图下降快 |
| 从原理图提取网络标号 | **中**(~60%) | 依赖PDF导出质量 |
| 理解跨页图的关系 | **差**(<30%) | 页面衔接经常断 |
| 识别DNP/NC标注 | **差**(<30%) | 小字+斜杠样式多样 |
| 从图中推断设计意图 | **不可靠**(<20%) | 编造比答对更危险 |
| PCB Layout层叠识别 | **不可用**(<10%) | 非图像识别问题 |

### 10.2 风险清单

| 风险 | 严重度 | 概率 | 缓解措施 |
|:-----|:------:|:----:|:---------|
| AI漏掉关键连接导致设计错误 | **致命** | 中 | 人工复核所有关键信号路径 |
| 错误标注网络名导致接线错误 | **致命** | 低 | 网络名必须交叉验证 |
| 图中DNP元件被误认为已焊接 | **严重** | 中 | 规则引擎标记所有DNP |
| PDF页面截断丢失跨页连接 | **严重** | 高 | 跨页连接器标记+人工核对 |
| 符号识别错误（电容vs电阻） | **中等** | 低 | 符号库比对+容差判断 |
| OCR低置信度导致数值错误 | **中等** | 中 | 阈值<80%的标记为"待确认" |
| 大模型幻觉添加不存在的路径 | **致命** | 中 | 方案①③都要求输出结构化+可溯源的JSON，不依赖LLM的自由文本摘要 |

### 10.3 红线规则

```text
【绝对不做】
1. AI自动修改基于图的设计数据 <- 修改必须走正式ECO
2. AI自动生成原理图/PCB图 <- AI输出只能作为"参考草稿"
3. AI从图中推理出的"建议"直接执行 <- 必须有人工评审
4. 用AI读PCB Layout后替换人工Review <- AI远远不够格

【必须人工复核的】
1. 所有跨页连接关系
2. 所有电源/地的连接
3. 所有标注为DNP/NC的元件
4. 所有时序图中的关键path延迟
```

---

## 总结：务实路线

```text
当前可用 (立即上)
  +-- draw.io原生解析 -> 结构化JSON
  +-- 图片OCR提取表格 -> Markdown
  +-- PDF中独立文本提取 -> 文本块列表

短期突破 (1-2月)
  +-- 原理图PDF网络标号提取 (规则引擎)
  +-- 电源树电压值提取 (模板匹配)
  +-- 截图+小区域OCR (VLM辅助)

暂缓投入 (评估后再定)
  +-- PCB Layout自动解读 (等工具链成熟)
  +-- 3D装配图AI分析 (非图片识别问题)
  +-- 大模型端到端读原理图 (幻觉问题无解)
```

## 关联知识

| 关联文档 | 关联点 |
|:---------|:-------|
| [`07_industry-research/03_server/06_enterprise-mgmt/2026-07-16-ai-in-server-rd-deep-analysis.md`](../04_ai/2026-07-16-ai-in-server-rd-deep-analysis.md) | 图处理方案 §3.4 · 全领域AI场景排查 |
| [`2026-07-15-server-competitive-analysis-methodology.md`](2026-07-15-server-competitive-analysis-methodology.md) | 竞品分析中的图纸信息来源与可信度判别 |
| [`2026-07-15-bios-ai-fault-diagnosis-trends.md`](../../02_rd/01_product/00_hardware/02_firmware/2026-07-15-bios-ai-fault-diagnosis-trends.md) | BIOS/固件中的诊断图解读需求 |
| `../02_rd/03_hardware/06_superpod/project/compute-node/compute-node-architecture-v2.md` | §7 信号连接清单的彩色连线编码与本报告§7.1的解读方案形成对照 |

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [`07_industry-research/03_server/06_enterprise-mgmt/2026-07-16-ai-in-server-rd-deep-analysis.md`](../04_ai/2026-07-16-ai-in-server-rd-deep-analysis.md) — 关联
- [`2026-07-15-server-competitive-analysis-methodology.md`](2026-07-15-server-competitive-analysis-methodology.md) — 关联
- [`2026-07-15-bios-ai-fault-diagnosis-trends.md`](../../02_rd/01_product/00_hardware/02_firmware/2026-07-15-bios-ai-fault-diagnosis-trends.md) — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
