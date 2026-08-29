# 行列式的性质全面罗列汇总

> **文件状态**: 正式版 v1.0 | **覆盖范围**: 行列式性质的 MECE 十类穷举罗列（公理层/运算/代数结构/特殊矩阵/分块/谱/不等式/微积分/函数论/组合特殊值）+ 每条性质的表述、条件、证明要点、应用
> **版本**: v1.0
> **日期**: 2026-08-22
> **核心问题**: 行列式有哪些性质？如何 MECE 分类穷举？每条性质的精确表述、适用条件、证明要点与典型应用是什么？
> **适用读者**: 需要系统查证行列式性质的技术决策者/算法工程师/科研人员
> **前置知识**: 矩阵乘法、线性方程组、特征值基础。姊妹篇 [行列式的几何与代数意义深度分析](2026-08-22-determinant-geometric-algebraic-meaning.md) 回答"行列式为什么存在"，本文回答"行列式有哪些性质"——两文互补，建议对照阅读
> **概要**: 按 MECE 原则将行列式性质穷举为十类 100 条（P1–P100），每条含数学表述/适用条件/证明要点/典型应用，附全景总览表与速查索引表
> **关键词**: 行列式, determinant, 多重线性, 交替性, Leibniz公式, Laplace展开, Hadamard不等式, Jacobi公式, Schur补, Sylvester恒等式, Vandermonde, 特征值乘积

## 目录

- [1. 引言：本文定位与组织方式](#1-引言本文定位与组织方式)
- [2. 性质全景总览（一张表）](#2-性质全景总览一张表)
- [3. 定义性性质（公理层）](#3-定义性性质公理层)
- [4. 基本运算性质（初等变换与转置）](#4-基本运算性质初等变换与转置)
- [5. 代数结构性质（乘法/逆/幂/伴随/相似/合同）](#5-代数结构性质乘法逆幂伴随相似合同)
- [6. 特殊矩阵的行列式性质](#6-特殊矩阵的行列式性质)
- [7. 分块矩阵的行列式性质](#7-分块矩阵的行列式性质)
- [8. 谱性质（特征值/特征多项式纽带）](#8-谱性质特征值特征多项式纽带)
- [9. 不等式与界的性质](#9-不等式与界的性质)
- [10. 微积分与变分性质](#10-微积分与变分性质)
- [11. 函数论与群论性质](#11-函数论与群论性质)
- [12. 组合恒等式与特殊行列式](#12-组合恒等式与特殊行列式)
- [13. 判定性应用性质（含反例警告）](#13-判定性应用性质含反例警告)
- [14. 性质速查索引表](#14-性质速查索引表)
- [参考文献](#参考文献)

---

## 1. 引言：本文定位与组织方式

行列式（determinant）是 $n \times n$ 矩阵到标量域的一个函数 $\det: \mathbb{F}^{n\times n} \to \mathbb{F}$。经过两个世纪的发展（Leibniz 1693 → Vandermonde 1772 → Cauchy 1812 → Weierstrass 19 世纪公理化），其性质已完全定型，是线性代数中**性质密度最高**的单对象之一。

姊妹篇 [行列式的几何与代数意义](2026-08-22-determinant-geometric-algebraic-meaning.md) 从第一性原理回答"行列式为什么是那个唯一的函数、它的几何本质是什么"；本文承接其结论，**穷举式罗列**行列式的全部经典性质，按 MECE 原则分为十类：

| 类别 | 回答的问题 | 性质编号 |
|:-----|:-----------|:--------:|
| ① 定义性性质 | 行列式由什么唯一确定？ | P1–P6 |
| ② 基本运算性质 | 初等变换/转置如何改变行列式？ | P7–P17 |
| ③ 代数结构性质 | 乘法/逆/幂/伴随下如何变换？ | P18–P31 |
| ④ 特殊矩阵性质 | 常见结构矩阵的行列式是什么？ | P32–P46 |
| ⑤ 分块矩阵性质 | 分块结构如何化简计算？ | P47–P53 |
| ⑥ 谱性质 | 与特征值/特征多项式什么关系？ | P54–P62 |
| ⑦ 不等式性质 | 行列式的大小受什么约束？ | P63–P70 |
| ⑧ 微积分性质 | 行列式如何随矩阵光滑变化？ | P71–P77 |
| ⑨ 函数论/群论性质 | 行列式作为映射有何结构？ | P78–P84 |
| ⑩ 组合/特殊行列式 | 著名构造的行列式闭式？ | P85–P93 |

**使用约定**：每条性质给出【表述】【条件】【证明要点】【应用/注意】。$\mathbb{F}$ 表示数域（实/复），$n$ 为矩阵阶数，$I_n$ 为 $n$ 阶单位阵，$\operatorname{adj} A$ 为伴随矩阵，$\operatorname{tr}$ 为迹，$\sigma_i$ 为奇异值。性质间的推论关系用"⟸ 由 P-x 推出"标注。

---

## 2. 性质全景总览（一张表）

> 十类性质的核心结论浓缩（完整表述见对应章节）：

| # | 类别 | 核心性质一句话 | 关键编号 |
|:-:|:-----|:--------------|:--------:|
| ① | 定义 | 唯一的多重线性、交替、归一化函数 | P1–P4 |
| ① | 定义 | Leibniz 求和公式 / Laplace 递归展开 | P5–P6 |
| ② | 运算 | 转置不变；行交换变号；行加倍数不变 | P7, P8, P10 |
| ② | 运算 | $\det(cA) = c^n \det A$；零行/相同行 ⟹ 0 | P16, P11, P12 |
| ③ | 结构 | $\det(AB)=\det A \cdot \det B$（一切代数性质的源头） | P18 |
| ③ | 结构 | 可逆 ⟺ $\det \neq 0$；$\det(A^{-1})=1/\det A$ | P20, P21 |
| ③ | 结构 | $\det(\operatorname{adj} A) = \det(A)^{n-1}$；秩 1 更新公式 | P23, P30 |
| ④ | 特殊阵 | 三角/对角 = 对角线乘积；正交/酉 = ±1/模 1 | P32–P35 |
| ④ | 特殊阵 | 反对称奇阶 = 0，偶阶 = Pfaffian² ≥ 0 | P39 |
| ⑤ | 分块 | 分块三角 = 分块对角元之积；Schur 补公式 | P48, P49 |
| ⑥ | 谱 | $\det A = \prod \lambda_i$（一切复矩阵成立） | P55 |
| ⑥ | 谱 | Sylvester: $\det(I_m + AB) = \det(I_n + BA)$ | P59 |
| ⑦ | 不等式 | Hadamard: $\lvert \det A \rvert \le \prod \lVert a_i \rVert$ | P63 |
| ⑦ | 不等式 | Minkowski: $\det(A+B)^{1/n} \ge \det A^{1/n} + \det B^{1/n}$ | P65 |
| ⑧ | 微积分 | Jacobi 公式 $d\det A = \det A \cdot \operatorname{tr}(A^{-1}dA)$ | P71–P72 |
| ⑨ | 函数论 | $\det$ 是 $n$ 次齐次多项式、连续、群同态 | P78–P80 |
| ⑩ | 组合 | Vandermonde / Cauchy / Wronskian / 矩阵树定理 | P85–P89 |

---

## 3. 定义性性质（公理层）

### P1 多重线性性（Multilinearity）
【表述】固定其他行，$\det$ 对第 $i$ 行是线性的：
$$\det(\dots, \alpha u + \beta v, \dots) = \alpha\det(\dots,u,\dots) + \beta\det(\dots,v,\dots)$$
【条件】对每一行（列）成立 [1]
【证明要点】这是"体积对边长线性"的代数化：平行体一边拉伸 $\alpha$ 倍，体积乘 $\alpha$ [3]
【应用】行列式求导、多线性代数的根基；是公理化定义的三个支柱之一

### P2 交替性（Alternating）
【表述】交换任意两行（列），行列式变号：
$$\det(\dots, r_i, \dots, r_j, \dots) = -\det(\dots, r_j, \dots, r_i, \dots)$$
【条件】任意两行/两列 [1]
【证明要点】由多重线性 + 反对称性推导；几何上对应"定向反转" [3]
【应用】定向（orientation）概念的代数源头；符号判据（P84）

### P3 归一化（Normalization）
【表述】$\det(I_n) = 1$。
【条件】$n \ge 1$ [1]
【证明要点】单位立方体体积为 1 的公理化 [2]
【应用】锁定唯一性（P4）；一切公式的标定基准

### P4 唯一性定理
【表述】同时满足 P1、P2、P3 的函数 $\det: \mathbb{F}^{n\times n} \to \mathbb{F}$ **存在且唯一**。
【条件】$n \ge 1$ [3]
【证明要点】所有 $n$ 重交替多重线性形式构成一维空间；在 $I_n$ 上取值 1 即唯一 [3]
【应用】解释为何 Leibniz/Laplace/几何体积三种定义殊途同归 [2]

### P5 Leibniz 显式公式
【表述】$$\det A = \sum_{\sigma \in S_n} \operatorname{sgn}(\sigma) \prod_{i=1}^{n} a_{i,\sigma(i)}$$
其中 $S_n$ 为 $n$ 阶置换群，$\operatorname{sgn}$ 为置换符号（逆序数奇偶性）[1]
【条件】任意 $n$；计算复杂度 $O(n!)$（$n=20$ 约 $2.4\times10^{18}$ 项，仅理论用）[5]
【证明要点】交替性强制每项只能"每行每列各取一元素" [3]
【应用】理论推导（如证明 P7、P18 的代数版本）；定义置换符号

### P6 Laplace 展开（余子式递归）
【表述】按第 $i$ 行展开：$$\det A = \sum_{j=1}^{n} (-1)^{i+j} a_{ij} \det(M_{ij})$$
$M_{ij}$ 为删去第 $i$ 行第 $j$ 列后的 $(n-1)$ 阶余子阵；$C_{ij}=(-1)^{i+j}\det M_{ij}$ 称代数余子式 [1]
【条件】任意行/列均可；计算复杂度同样 $O(n!)$，适合稀疏/符号计算 [5]
【证明要点】由 Leibniz 公式按行分拆 [2]
【应用】伴随矩阵定义（P23）、Cramer 法则（P94）的推导基础

---

## 4. 基本运算性质（初等变换与转置）

### P7 转置不变性
【表述】$\det(A^T) = \det(A)$。
【条件】任意方阵 [1]
【证明要点】Leibniz 公式中 $\sigma$ 与 $\sigma^{-1}$ 符号相同，行列对称 [1]
【推论】凡"行"性质自动对"列"成立（P8–P13 双向适用）——**行列式是唯一对行列完全对称的重要矩阵函数**

### P8 行（列）交换变号
【表述】交换两行（列），$\det$ 变号。等价：$\det(E_1 A) = -\det A$，$E_1$ 为交换型初等矩阵。
【条件】任意两行 [1]
【证明要点】即 P2 本身 [3]
【应用】高斯消元中跟踪符号；LU 分解的符号修正（P45 姊妹篇 5.5 节）

### P9 某行（列）乘常数
【表述】$\det$ 对单行是齐次的：$\det(\dots, cr_i, \dots) = c\det(\dots, r_i, \dots)$。
【条件】$c \in \mathbb{F}$ [1]
【证明要点】P1 多重线性的特例（$\beta=0$）[2]
【推论】与 P16 区分：P9 只乘**一行**，P16 乘**整个矩阵**

### P10 行（列）加另一行的倍数
【表述】$\det(\dots, r_i + c r_j, \dots) = \det(\dots, r_i, \dots)$（$i \ne j$）。
【条件】任意 $c$ [1]
【证明要点】由 P1 拆开，第二项因 P13（两行成比例）为 0 [2]
【应用】**消元不改变行列式**——高斯消元到三角阵后只需乘对角线（P32）

### P11 零行（列）⟹ 行列式为零
【表述】某行全零 ⟹ $\det A = 0$。
【证明要点】P9 取 $c=0$ [2]
【应用】快速奇异判定（含零行/零列的矩阵必奇异）

### P12 两行（列）相同 ⟹ 行列式为零
【表述】$r_i = r_j$（$i \ne j$）⟹ $\det A = 0$。
【证明要点】P2 中交换两行：$\det = -\det$ ⟹ $\det = 0$（要求数域特征 $\ne 2$）[3]
【应用】线性相关性的第一判据（P95）

### P13 两行（列）成比例 ⟹ 行列式为零
【表述】$r_i = c r_j$ ⟹ $\det A = 0$。
【证明要点】P9 提出 $c$ 后用 P12 [2]
【应用】P12 的推广；秩亏缺的快速识别

### P14 行列对称性
【表述】P1–P13 中所有"行"版本对"列"同样成立。
【证明要点】P7（转置不变）作为桥 [1]
【应用】计算时自由选择"按行消元"或"按列消元"

### P15 初等矩阵的行列式
【表述】三种初等矩阵 $E$ 的 $\det$：
$$\det(E_1) = -1 \ (\text{交换}), \quad \det(E_2(c)) = c \ (\text{乘常数}), \quad \det(E_3) = 1 \ (\text{加倍数})$$
【条件】$E_2(c)$ 中 $c \ne 0$（否则不可逆）[1]
【证明要点】P8/P9/P10 的直接特例 [1]
【应用】$A = E_k \cdots E_1$ 分解时 $\det A$ = 各初等矩阵 $\det$ 之积（P18）

### P16 矩阵整体缩放
【表述】$\det(cA) = c^n \det(A)$（$A$ 为 $n$ 阶方阵）。
【条件】$c \in \mathbb{F}$，$n$ 阶 [1]
【证明要点】每行乘 $c$ 共 $n$ 次，P9 连用 [2]
【应用】尺度分析：$\det(0.1 I_{10}) = 10^{-10}$ 但矩阵良态——**det 对尺度敏感，非病态判据**（P100）

### P17 分块对角特例（预告）
【表述】$\det\begin{pmatrix} A & 0 \\ 0 & B \end{pmatrix} = \det A \cdot \det B$。
【证明要点】Laplace 展开沿零块 [1]
【应用】块对角矩阵计算捷径；完整分块理论见 P47–P53

---

## 5. 代数结构性质（乘法/逆/幂/伴随/相似/合同）

### P18 乘法性（Binet–Cauchy 定理）
【表述】$$\det(AB) = \det(A) \cdot \det(B)$$
【条件】$A, B$ 均为 $n$ 阶方阵 [1]
【证明要点】固定 $A$，$B \mapsto \det(AB)$ 满足 P1–P3，由 P4 唯一性等于 $\det(A)\det(B)$ [3]
【推论】$\det: GL_n \to \mathbb{F}^\times$ 是群同态（P80）；可逆性乘积保持（P20）
【应用】**行列式所有代数性质的源头**：逆、幂、相似、特征值乘积皆由此推出

### P19 乘积可交换（det 意义下）
【表述】$\det(AB) = \det(BA)$，**即使 $AB \ne BA$**。
【条件】$A, B$ 同阶方阵 [1]
【证明要点】P18 两侧同时等于 $\det A \det B$ [1]
【注意】$\det(A+B)$ 一般 $\ne \det A + \det B$（P29 给出正确展开）；此条是"det 抹平非交换性"的经典例子

### P20 可逆判据
【表述】$A$ 可逆 ⟺ $\det A \ne 0$。
【条件】方阵 [1]
【证明要点】$\det A \ne 0$ ⟺ 行线性无关（P13 逆否）⟺ 满秩 [2]
【推论】与 rank、零空间、特征值零（P61）等价（P95）

### P21 逆的行列式
【表述】$\det(A^{-1}) = \dfrac{1}{\det A}$。
【条件】$A$ 可逆 [1]
【证明要点】P18 应用于 $AA^{-1} = I$ 与 P3 [1]
【应用】条件数/误差分析中的量级估计

### P22 幂的行列式
【表述】$\det(A^k) = (\det A)^k$，$k \in \mathbb{Z}$（$k<0$ 要求可逆）。
【条件】方阵 [1]
【证明要点】P18 归纳 [1]
【应用】马尔可夫链转移矩阵：$\det P = 1$ 保测度（det 对迭代不变）

### P23 伴随矩阵
【表述】$A \cdot \operatorname{adj} A = \operatorname{adj} A \cdot A = (\det A) I_n$，且
$$\det(\operatorname{adj} A) = (\det A)^{n-1}$$
【条件】方阵；伴随元素为 $(\operatorname{adj} A)_{ji} = C_{ij}$（代数余子式转置）[1]
【证明要点】$A \operatorname{adj} A$ 对角线为 $\det A$（Laplace），非对角线为 0（P12 型展开）；后式对 $A$ 可逆时取 $A^{-1} = \operatorname{adj} A / \det A$ 两边 $\det$ [2]
【推论】$\operatorname{adj}(\operatorname{adj} A) = (\det A)^{n-2} A$（$n \ge 2$，可逆时）
【应用】逆矩阵的余子式表达；$\partial \det / \partial a_{ij} = (\operatorname{adj} A)_{ji}$（P73）

### P24 相似不变性
【表述】$\det(P^{-1} A P) = \det(A)$。
【条件】$P$ 可逆 [1]
【证明要点】P18 + P21：$\det P^{-1} \det A \det P = \det A$ [1]
【推论】$\det$ 是**相似不变量**（与 trace、rank、特征多项式并列，见姊妹篇 §4.4）

### P25 合同变换
【表述】$\det(C^T A C) = (\det C)^2 \det A$。
【条件】$C$ 可逆，$A$ 为方阵（实矩阵合同）[4]
【注意】合同下 det **数值**不守恒（乘 $(\det C)^2 > 0$），但**符号**守恒（实矩阵）——正定/负定分类的基石

### P26 共轭转置
【表述】$\det(A^*) = \overline{\det(A)}$（共轭转置 = det 的共轭）。
【条件】复矩阵 [1]
【推论】埃尔米特矩阵 $\det$ 为实数；酉矩阵 $|\det| = 1$（P35）

### P27 逆/伴随的共轭组合
【表述】$A$ 酉相似于三角阵（Schur）时 $\det$ 为特征值乘积——见 P55。

### P28 幂等/对合/幂零预告
【表述】幂等 $P^2=P$：$\det P \in \{0, 1\}$；对合 $A^2=I$：$\det A = \pm 1$；幂零 $N^k=0$：$\det N = 0$。
【证明要点】P22 分别代入 $P^2=P$、$A^2=I$、$N^k=0$ 并利用 P11 [2]
【应用】投影矩阵/反射矩阵/严格上三角的结构判定（详见 P36–P38）

### P29 det(A+B) 的展开式
【表述】$$\det(A+B) = \sum_{k=0}^{n} \sum_{\substack{|S|=|T|=k \\ \text{行列指标集}}} \det(A_S) \det(B_{T}) \cdot (\text{符号项})$$
【条件】一般方阵 [3]
【证明要点】外代数：$\det(A+B)$ 展开为外幂的混合楔积 [3]
【通俗形式】$n=2$: $\det(A+B) = \det A + \det B + \operatorname{tr}A\operatorname{tr}B - \operatorname{tr}(AB)$
【注意】**一般 $\det(A+B) \ne \det A + \det B$**；只有 $n=1$ 或特殊结构才可加

### P30 秩 1 更新公式（行列式引理）
【表述】$$\det(A + uv^T) = \det(A)\,(1 + v^T A^{-1} u)$$
【条件】$A$ 可逆，$u, v$ 为 $n$ 维列向量 [4]
【证明要点】分块矩阵 $\det\begin{pmatrix} A & u \\ -v^T & 1 \end{pmatrix}$ 两种 Schur 补展开（P49）[4]
【应用】Woodbury 公式的姊妹式；秩 1 扰动敏感性分析；统计中协方差更新

### P31 特征多项式形态（预告）
【表述】$p_A(\lambda) = \det(\lambda I - A)$ 是 $\lambda$ 的 $n$ 次首一多项式——见 P54–P57。

---

## 6. 特殊矩阵的行列式性质

### P32 三角矩阵
【表述】上（下）三角矩阵 $\det$ = 主对角线元素之积。
【条件】方阵 [1]
【证明要点】Laplace 沿第一行（列）递归 [1]
【应用】高斯消元终点；LU 分解算 det 的标准路径（姊妹篇 §5.5）

### P33 对角矩阵
【表述】$\det(\operatorname{diag}(d_1,\dots,d_n)) = d_1 d_2 \cdots d_n$。
【证明要点】P32 特例 [1]
【应用】缩放矩阵、协方差（对角化后）的行列式

### P34 正交矩阵
【表述】$Q^T Q = I$ ⟹ $\det Q = \pm 1$。
【条件】实正交阵 [1]
【证明要点】P18 + P7：$\det(Q^T Q) = (\det Q)^2 = \det I = 1$ [1]
【推论】正交变换保体积（$|\det|=1$）；反射类 det = $-1$，旋转类 det = $+1$

### P35 酉矩阵
【表述】$U^* U = I$ ⟹ $|\det U| = 1$。
【条件】复酉阵 [1]
【证明要点】P26 + P18：$\det(U^* U) = \overline{\det U} \cdot \det U = 1$ [1]
【应用】量子力学/DFT 等酉变换不改变概率体积

### P36 幂等矩阵
【表述】$P^2 = P$ ⟹ $\det P \in \{0, 1\}$。
【证明要点】P22：$\det P = (\det P)^2$ ⟹ $\det P \in \{0,1\}$ [2]
【应用】投影算子：满射投影 det=1，真投影 det=0

### P37 对合矩阵
【表述】$A^2 = I$ ⟹ $\det A = \pm 1$。
【证明要点】P22 同理 [2]
【应用】反射/对合变换；分块对合结构

### P38 幂零矩阵
【表述】$N^k = 0$（某 $k$）⟹ $\det N = 0$。
【证明要点】P22 + P11 [2]
【应用】严格上三角阵、导数算子、Jordan 块均幂零

### P39 反对称矩阵
【表述】$A^T = -A$：$n$ 奇数 ⟹ $\det A = 0$；$n$ 偶数 ⟹ $\det A = \operatorname{Pf}(A)^2 \ge 0$（$\operatorname{Pf}$ 为 Pfaffian）。
【条件】实反对称阵；$n$ 偶时 Pfaffian 是 $\det$ 的"平方根"多项式 [3]
【证明要点】$\det A = \det(-A^T) = (-1)^n \det A$；$n$ 奇 ⟹ $\det A = -\det A$ [2]
【应用】辛几何、实反对称标准型（谱为纯虚数共轭对）；偶数阶反对称 det 非负是"平方结构"

### P40 斜埃尔米特矩阵
【表述】$A^* = -A$ ⟹ $\det A = \overline{\det A} \cdot (-1)^n$：$n$ 奇时 $\det A$ 为纯虚数，$n$ 偶时为实数。
【证明要点】P26 + 条件代入 [4]
【应用】酉群的李代数 $\mathfrak{u}(n)$ 元素（det 落在单位圆上特定点）

### P41 正定矩阵
【表述】$A \succ 0$（正定）⟹ $\det A > 0$。
【证明要点】特征值全正（P55）+ 乘积正 [4]
【推论】正定的主子式全正（Sylvester 判据的"必要性"方向）；半正定 $A \succeq 0$ ⟹ $\det A \ge 0$ 且 $=0$ ⟺ 奇异（P42）

### P42 半正定矩阵
【表述】$A \succeq 0$ ⟹ $\det A \ge 0$，且 $\det A = 0$ ⟺ $A$ 奇异（至少一个零特征值）。
【证明要点】特征值非负（P55）[4]
【应用】协方差矩阵：$\det \Sigma = 0$ ⟺ 数据退化到低维子空间（姊妹篇 §5.1）

### P43 随机矩阵
【表述】$P$ 为（双）随机矩阵（非负、行/列和 = 1）⟹ $|\det P| \le 1$。
【证明要点】Hadamard 不等式（P63）+ 每列范数 $\le 1$ [4]
【应用】马尔可夫链：唯一平稳分布的存在性与 det 无关，但 $|\det| < 1$ 蕴含特征值 $\ne 1$ 的信息

### P44 幺模矩阵
【表述】$A \in SL_n(\mathbb{F}) = \{A : \det A = 1\}$——幺模群。
【证明要点】P18 保证 $SL_n$ 是 $GL_n$ 的子群（P81）[3]
【应用】格论（幺模格）、辛群、数论

### P45 置换矩阵
【表述】置换矩阵 $P_\sigma$ 的 $\det = \operatorname{sgn}(\sigma)$（置换符号）。
【证明要点】$P_\sigma$ 由 $I$ 经 $\operatorname{sgn}$ 次行交换得到，P8 [1]
【应用】行交换的符号跟踪；组合恒等式验证

### P46 循环矩阵
【表述】$n$ 阶循环矩阵 $\det = \prod_{k=0}^{n-1} f(\omega^k)$，$\omega = e^{2\pi i/n}$ 为 $n$ 次单位根，$f(x) = c_0 + c_1 x + \cdots + c_{n-1}x^{n-1}$ 为生成多项式。
【证明要点】循环矩阵被 DFT 矩阵对角化，特征值为 $f(\omega^k)$ [4]
【应用】卷积/周期边界问题；$n$ 次单位根结构

---

## 7. 分块矩阵的行列式性质

### P47 分块对角
【表述】$\det\begin{pmatrix} A & 0 \\ 0 & D \end{pmatrix} = \det A \cdot \det D$。
【证明要点】Laplace 递归 [1]
【应用】块对角系统；概率中的块对角协方差

### P48 分块（上/下）三角
【表述】$\det\begin{pmatrix} A & B \\ 0 & D \end{pmatrix} = \det A \cdot \det D$（$B$ 任意！）。
【证明要点】对 $A, D$ 做消元到三角，P10 不变性 [2]
【应用】广义 Schur 补的快速化简；块上三角矩阵可逆 ⟺ 对角块可逆

### P49 Schur 补公式（分块矩阵行列式引理）
【表述】设 $A$ 可逆：
$$\det\begin{pmatrix} A & B \\ C & D \end{pmatrix} = \det(A) \cdot \det(D - CA^{-1}B)$$
其中 $D - CA^{-1}B$ 称为 $A$ 的 **Schur 补**；若 $D$ 可逆则对称地
$$\det\begin{pmatrix} A & B \\ C & D \end{pmatrix} = \det(D) \cdot \det(A - BD^{-1}C)$$
【条件】$A$（或 $D$）可逆；$B, C$ 为任意矩形块 [4]
【证明要点】分块消元（左下乘 $-CA^{-1}$ 加右下，P10 推广）[4]
【应用】**分块矩阵理论的枢纽**：条件协方差、边际化高斯分布、P30 秩 1 更新、最小二乘分块求解

### P50 分块 2×2 的交换情形
【表述】若 $A, B$ 可交换（$AB = BA$）：
$$\det\begin{pmatrix} A & B \\ B & A \end{pmatrix} = \det(A+B) \cdot \det(A-B)$$
【证明要点】分块对角化：$\begin{pmatrix} A & B \\ B & A \end{pmatrix} = \begin{pmatrix} I & I \\ I & -I \end{pmatrix}^{-1}\begin{pmatrix} A+B & 0 \\ 0 & A-B \end{pmatrix}\begin{pmatrix} I & I \\ I & -I \end{pmatrix}$ [4]
【应用】二聚体/周期结构；$\mathbb{Z}_2$ 对称系统

### P51 分块矩阵的行列式与秩
【表述】$\det\begin{pmatrix} A & B \\ C & D \end{pmatrix} = 0$ ⟺ 四块构成的行向量组线性相关。
【证明要点】P20 的块版本 [2]
【应用】广义特征值、代数 Riccati 方程可解性

### P52 分块反对称（辛块）
【表述】$\det\begin{pmatrix} 0 & I \\ -I & 0 \end{pmatrix} = 1$（$n$ 偶时标准辛形式）。
【证明要点】P49 或行列交换 [3]
【应用】辛几何；正交辛矩阵群 $Sp(2n)$ 的 det = 1

### P53 一般分块展开（Cauchy–Binet 推广）
【表述】若 $A$ 为 $m \times n$、$B$ 为 $n \times m$（$m \le n$）：
$$\det(AB) = \sum_{S \subset \{1..n\}, |S|=m} \det(A_{:,S}) \cdot \det(B_{S,:})$$
【条件】$m \le n$，$A_{:,S}$ 取 $A$ 的 $S$ 列，$B_{S,:}$ 取 $B$ 的 $S$ 行 [3]
【证明要点】Binet–Cauchy 公式；P18 的矩形推广 [3]
【应用】子式理论、随机矩阵、图论（矩阵树定理的证明工具）

---

## 8. 谱性质（特征值/特征多项式纽带）

### P54 特征多项式
【表述】$p_A(\lambda) = \det(\lambda I - A) = \lambda^n - \operatorname{tr}(A)\lambda^{n-1} + \cdots + (-1)^n \det A$。
【条件】方阵 [1]
【证明要点】Leibniz 展开中 $\lambda^{n-k}$ 系数 = 主子式之和的符号组合 [1]
【推论】特征值 = $p_A$ 的根（含重数）

### P55 特征值乘积
【表述】$$\det A = \prod_{i=1}^{n} \lambda_i(A)$$（含代数重数）。
【条件】**一切**复矩阵（含不可对角化的 Jordan 形）[4]
【证明要点】Schur 三角化 $A = UTU^*$（$T$ 上三角、对角线 = 特征值），P24 + P32 [4]
【注意】"只对可对角化成立"是常见误区——Schur 三角化消除该限制（姊妹篇 §6 误区 3）

### P56 迹（补充恒等式）
【表述】$\operatorname{tr}(A) = \sum \lambda_i$ 与 $\det A = \prod \lambda_i$ 构成特征值的两个初等对称函数。
【证明要点】P54 系数比较 [1]
【应用】$\det$ 提供乘积信息、$\operatorname{tr}$ 提供求和信息（姊妹篇 §4.4 互补性）

### P57 特征多项式系数
【表述】$p_A(\lambda)$ 的 $\lambda^{n-k}$ 系数 $= (-1)^k \cdot (\text{全部 } k \times k \text{ 主子式之和})$。
【证明要点】Leibniz 公式按对角线选法分拆 [3]
【应用】无需特征分解即得 det 与 tr；小矩阵快速验证

### P58 Cayley–Hamilton 定理
【表述】$p_A(A) = 0$——矩阵满足自己的特征方程。
【证明要点】伴随矩阵恒等式 $(A - \lambda I)\operatorname{adj}(A - \lambda I) = p_A(\lambda) I$ 的矩阵化论证 [3]
【应用】矩阵多项式降次；$A^{-1}$ 用 $A$ 的低次幂表示

### P59 Sylvester 行列式恒等式
【表述】对 $A \in \mathbb{F}^{m \times n}$、$B \in \mathbb{F}^{n \times m}$：
$$\det(I_m + AB) = \det(I_n + BA)$$
【条件】$m \ne n$ 也成立！（两侧阶数不同但值相等）[4]
【证明要点】P49 对 $\det\begin{pmatrix} I_m & -A \\ B & I_n \end{pmatrix}$ 的两种 Schur 补展开 [4]
【应用】Woodbury 公式推导；$\det(I + uv^T) = 1 + v^T u$（$m=n=1$ 特例）

### P60 奇异值之积
【表述】$|\det A| = \prod_{i=1}^{n} \sigma_i(A)$（奇异值之积）。
【条件】任意矩阵（含复）[4]
【证明要点】SVD $A = U\Sigma V^*$，P24 + P34/P35 + P33 [4]
【推论】$|\det A| \le \lVert A \rVert^n$（P69）；Hadamard 不等式（P63）的奇异值视角

### P61 零特征值判据
【表述】$\det A = 0$ ⟺ $0$ 是 $A$ 的特征值。
【证明要点】P55 特例 [1]
【应用】谱与可逆性（P20）的桥梁；特征值问题中"奇异 ⟺ 谱含 0"

### P62 det 与谱半径无单调关系
【表述】$\det$ 不刻画谱半径 $\rho(A) = \max|\lambda_i|$：存在 $\det$ 相同但 $\rho$ 天差地别的矩阵。
【例】$\lambda = (100, 0.01)$ 与 $\lambda = (1, 1)$ 都有 $\det = 1$，但 $\rho$ 分别为 100 与 1 [4]
【注意】迭代法收敛性看 $\rho$，不看 $\det$——工程中两者勿混用

---

## 9. 不等式与界的性质

### P63 Hadamard 不等式
【表述】$$\lvert \det A \rvert \le \prod_{i=1}^{n} \lVert a_i \rVert$$（$a_i$ 为列向量，欧氏范数）
正定版本：$\det A \le \prod_i a_{ii}$（对角线之积）。
等号条件：列向量两两正交（正定版本：$A$ 为对角阵）[4]
【证明要点】QR 分解：$\lvert\det A\rvert = \prod |r_{ii}| \le \prod \lVert a_i\rVert$（Cauchy–Schwarz）[4]
【应用】体积上界估计；协方差矩阵的 det 上界；统计中的信息不等式

### P64 Fischer 不等式
【表述】$A \succ 0$ 分块为 $\begin{pmatrix} A_{11} & A_{12} \\ A_{21} & A_{22} \end{pmatrix}$：
$$\det A \le \det(A_{11}) \cdot \det(A_{22})$$
等号 ⟺ $A_{12} = 0$ [4]
【证明要点】Schur 补 + 半正定 $A_{22} - A_{21}A_{11}^{-1}A_{12} \succeq 0$ 的 det 界（P63 正定版）[4]
【应用】Hadamard 的块推广；多元正态的边际-条件分解

### P65 Minkowski 行列式不等式
【表述】$A, B \succ 0$：
$$\det(A + B)^{1/n} \ge \det(A)^{1/n} + \det(B)^{1/n}$$
【证明要点】$\log\det$ 凹性（P66）+ 齐次性 [4]
【应用】体积的凸性；混合协方差的散度下界

### P66 log det 的凹性
【表述】$f(A) = \log\det(A)$ 在正定锥上**严格凹**。
【证明要点】沿直线 $A + tB$ 二阶导 $< 0$（P76 Hessian 负定）[4]
【应用】**凸优化中的王牌**：D-optimal 设计、最大熵、Gaussian 推断都最大化 $\log\det$

### P67 奇异值形式的 Hadamard
【表述】$\lvert\det A\rvert = \prod \sigma_i \le \left(\frac{1}{n}\sum \sigma_i^2\right)^{n/2} = \left(\frac{\lVert A \rVert_F^2}{n}\right)^{n/2}$（AM–GM）。
【证明要点】P60 + 算术-几何平均不等式 [4]
【应用】Frobenius 范数约束下的 det 上界

### P68 Weyl 型乘积界
【表述】$\lvert\det A\rvert \le \lVert A\rVert^n$（任意相容矩阵范数）。
【证明要点】$\sigma_i \le \lVert A\rVert$ + P60 [4]
【应用】算子范数框架下的体积界

### P69 迹-行列式不等式（Schur）
【表述】$A$ 半正定：$\operatorname{tr}(A) \ge n \cdot \det(A)^{1/n}$。
【证明要点】AM–GM 应用于特征值（P55/P56）[4]
【应用】$\det$ 与 $\operatorname{tr}$ 的互相约束；正定矩阵族的紧性

### P70 det 的凸性边界
【表述】$\det$ 本身在正定锥上既非凸也非凹（$\log\det$ 才凹）；在**整个**矩阵空间上 $\det$ 无界。
【证明要点】反例：$\det(\lambda A + (1-\lambda)B)$ 与 $\lambda\det A + (1-\lambda)\det B$ 无一致大小关系 [4]
【应用】提醒：优化中直接处理 det 要小心，一般用 $\log\det$ 或 det 的凸包

---

## 10. 微积分与变分性质

### P71 Jacobi 公式（一般形式）
【表述】$A(t)$ 为可微矩阵函数：
$$\frac{d}{dt}\det(A(t)) = \det(A(t)) \cdot \operatorname{tr}\!\left(A(t)^{-1} \frac{dA(t)}{dt}\right)$$
【条件】$A(t)$ 可逆（可微地）[4]
【证明要点】$\det(A + \varepsilon B) = \det A \cdot \det(I + \varepsilon A^{-1}B)$，再用 $\det(I + \varepsilon M) = 1 + \varepsilon\operatorname{tr} M + O(\varepsilon^2)$（P74）[4]
【应用】**流形上的体积演化**：动力系统相体积、ODE 解算器的误差传播（对 $d\det$ 积分）

### P72 微分形式
【表述】$$d(\det A) = \det(A) \cdot \operatorname{tr}(A^{-1} dA)$$
【条件】$A$ 可逆 [4]
【证明要点】P71 的坐标无关写法 [4]
【应用】变分法、最优传输、几何测度论

### P73 偏导数公式
【表述】$$\frac{\partial \det A}{\partial a_{ij}} = (\operatorname{adj} A)_{ji} = \det(A)\,(A^{-1})_{ji}$$
【条件】$A$ 可逆（不可逆时用 $\operatorname{adj}$ 形式仍成立）[4]
【证明要点】Laplace 展开对 $a_{ij}$ 求导 [2]
【应用】**机器学习反向传播**：多层感知机/流模型中 det 层对参数的梯度

### P74 一阶泰勒展开
【表述】$\det(I + \varepsilon A) = 1 + \varepsilon\operatorname{tr}(A) + O(\varepsilon^2)$。
【证明要点】P55：$\prod(1 + \varepsilon\lambda_i) = 1 + \varepsilon\sum\lambda_i + O(\varepsilon^2)$ [4]
【应用】$\operatorname{tr}$ 作为 $\det$ 的"对数导数"（姊妹篇 §4.4 互补性）；特征值微扰

### P75 log det 的梯度
【表述】$A \succ 0$：$$\nabla_A \log\det(A) = A^{-1} = (A^{-1})^T \ \text{（对称）}$$
【条件】正定域内 [4]
【证明要点】P73 + 链式法则 [4]
【应用】**矩阵求导的核心公式**：高斯最大似然估计 $\hat\Sigma = \frac{1}{N}\sum x_i x_i^T$ 的推导终点

### P76 log det 的 Hessian
【表述】$d^2 \log\det(A)[X, Y] = -\operatorname{tr}(A^{-1} X A^{-1} Y)$，Hessian 负定 ⟹ 凹（P66）。
【条件】$A \succ 0$ [4]
【证明要点】对 P75 再求导 [4]
【应用】牛顿法中的二阶信息；Bregman 散度（矩阵情形）

### P77 det 在约束流形上的极值
【表述】在 $\lVert A \rVert_F = 1$（或列范数固定）约束下，$|\det A|$ 在正交（列正交等长）矩阵处取最大。
【证明要点】P67 等号条件 [4]
【应用】Hadamard 不等式的变分视角；正交设计（正交表）的最优性

---

## 11. 函数论与群论性质

### P78 齐次多项式
【表述】$\det$ 是 $n^2$ 个矩阵元上的**$n$ 次齐次多项式**（Leibniz 每项 $n$ 个因子）。
【证明要点】P5 结构 [1]
【推论】$\det(cA) = c^n \det A$（P16）是其齐次性表现

### P79 连续性
【表述】$\det$ 作为多项式函数在 $\mathbb{F}^{n\times n}$ 上**连续**（甚至光滑）。
【证明要点】多项式连续 [2]
【推论】$GL_n = \{\det \ne 0\}$ 是开集；$\det$ 的零点集（奇异矩阵）是闭集

### P80 群同态
【表述】$\det: GL_n(\mathbb{F}) \to \mathbb{F}^\times$ 是**乘法群同态**：$\det(AB) = \det A \det B$。
【证明要点】P18 [3]
【推论】$\ker(\det) = SL_n$ 是正规子群（P81）；商群 $GL_n / SL_n \cong \mathbb{F}^\times$

### P81 幺模群的正规性
【表述】$SL_n$ 是 $GL_n$ 的**正规子群**（$gSL_n g^{-1} = SL_n$）。
【证明要点】共轭下 det 不变（P24）[3]
【应用】射影几何：$PGL_n = GL_n/\mathbb{F}^\times$ 的构造基础

### P82 奇异矩阵集是代数簇
【表述】$\{\det A = 0\}$ 是 $\mathbb{F}^{n\times n}$ 中的闭代数簇（不可约、余维 1）。
【证明要点】单个多项式方程的零点集 [3]
【应用】代数几何中"一般位置"的数学化：随机矩阵几乎必然可逆（概率 1）

### P83 可逆矩阵稠密
【表述】$GL_n$ 是 $M_n$ 的**开稠密**子集。
【证明要点】任意矩阵 $A$ 可被 $A - \varepsilon I$ 逼近，而后者至多有限个 $\varepsilon$ 奇异（特征值）[3]
【应用】数值分析中"扰动即可逆"的理论依据；随机扰动正则化

### P84 符号与定向
【表述】$\det A > 0$ / $< 0$ / $= 0$ 分别对应保定向 / 反定向 / 退化线性变换。
【证明要点】姊妹篇 §3.4 的几何论证 [1]
【应用】手性/旋向性判断；混合积 $a \cdot (b \times c)$ 的符号（3D 体积定向）

---

## 12. 组合恒等式与特殊行列式

### P85 Vandermonde 行列式
【表述】$$V(x_1,\dots,x_n) = \det\begin{pmatrix} 1 & x_1 & \cdots & x_1^{n-1} \\ \vdots & \vdots & & \vdots \\ 1 & x_n & \cdots & x_n^{n-1} \end{pmatrix} = \prod_{1 \le i < j \le n} (x_j - x_i)$$
【证明要点】逐列差分消元（$x_n$ 列减 $x_1$ 倍），归纳 [1]
【推论】$V \ne 0$ ⟺ $x_i$ 两两不同 ⟺ 多项式插值唯一
【应用】**插值唯一性定理**、多项式根对称函数、离散傅里叶

### P86 Cauchy 行列式
【表述】$$\det\left(\frac{1}{x_i + y_j}\right)_{i,j=1}^{n} = \frac{\prod_{i<j}(x_j - x_i)(y_j - y_i)}{\prod_{i,j}(x_i + y_j)}$$
【证明要点】从首行/首列提取公因子，化为 Vandermonde 型 [3]
【应用】Cauchy 矩阵（每主子式有闭式）；快速线性代数的结构矩阵

### P87 Wronskian（函数行列式）
【表述】函数组 $f_1, \dots, f_n$ 的 Wronskian $W = \det[f_j^{(i-1)}]_{i,j}$；$W \not\equiv 0$ ⟹ 函数组线性无关（对 $C^{n-1}$ 函数）。
【注意】$W \equiv 0$ **不**一定蕴含线性相关（非解析情形有反例）[1]
【应用】ODE 的线性无关解判定；Sturm–Liouville 理论

### P88 结式（Resultant）
【表述】多项式 $f(x) = a_n\prod(x - \alpha_i)$、$g(x) = b_m\prod(x - \beta_j)$ 的结式
$$\operatorname{Res}(f, g) = a_n^m b_m^n \prod_{i,j}(\alpha_i - \beta_j) = \det(\text{Sylvester 矩阵})$$
【推论】$\operatorname{Res}(f, g) = 0$ ⟺ $f, g$ 有公共根 [3]
【应用】消元理论、代数方程组的公共零点判定、判别式

### P89 矩阵树定理（Kirchhoff）
【表述】连通图 $G$ 的生成树数目 = Laplacian 矩阵 $L$ 的**任意** $(n-1) \times (n-1)$ 主子式。
【证明要点】Cauchy–Binet（P53）+ 每棵树的贡献恰为 1 [3]
【应用】图论/网络可靠性/随机游走；化学（分子结构计数）

### P90 Cayley–Menger 行列式
【表述】$n+1$ 个点两两距离 $d_{ij}$ 决定的 $n$ 维体积 $V$ 满足
$$(-1)^{n+1} 2^n (n!)^2 V^2 = \det\begin{pmatrix} 0 & 1 & \cdots & 1 \\ 1 & 0 & d_{12}^2 & \cdots \\ \vdots & & \ddots & \\ 1 & d_{n+1,1}^2 & \cdots & 0 \end{pmatrix}$$
【应用】分子构象、几何约束求解、距离几何 [3]
【注意】该行列式 $\ge 0$ 是距离可实现为欧氏构型的充要条件

### P91 置换符号恒等式
【表述】$\operatorname{sgn}(\sigma\tau) = \operatorname{sgn}(\sigma)\operatorname{sgn}(\tau)$，且 $\sum_{\sigma \in S_n}\operatorname{sgn}(\sigma) = 0$（$n \ge 2$）。
【证明要点】P45 + 群同态 [3]
【应用】Leibniz 公式的符号理论；行列式的置换群视角

### P92 外幂视角
【表述】$\det A$ 是 $A$ 在最高阶外幂 $\wedge^n \mathbb{F}^n$ 上的作用系数：$\wedge^n A(\omega) = (\det A)\omega$。
【证明要点】姊妹篇 §4.1 [3]
【应用】**现代定义**：det = 体积元的缩放因子；微分形式理论

### P93 格点与整数矩阵
【表述】整数矩阵 $A \in \mathbb{Z}^{n\times n}$ 的 $\det$ 是整数；$A^{-1}$ 为整数矩阵 ⟺ $\det A = \pm 1$（幺模）。
【证明要点】$A^{-1} = \operatorname{adj} A / \det A$（P23）[3]
【应用】整数格基、密码学（格密码）、Smith 标准型

---

## 13. 判定性应用性质（含反例警告）

### P94 Cramer 法则（解的唯一性）
【表述】$\det A \ne 0$ 时 $Ax = b$ 唯一解 $x_i = \det(A_i)/\det A$（$A_i$ 为第 $i$ 列替换为 $b$）。
【注意】复杂度 $O(n!)$——**理论价值 > 计算价值**，实际用高斯消元 $O(n^3)$ [1][5]

### P95 线性无关判据（等价链）
【表述】以下等价（$n$ 阶方阵）：$\det A \ne 0$ ⟺ 行线性无关 ⟺ 列线性无关 ⟺ $\operatorname{rank} A = n$ ⟺ $A$ 可逆 ⟺ $Ax = 0$ 仅零解 ⟺ $0$ 非特征值。
【证明要点】P20 + P61 [1]
【应用】满秩判定的**一站式等价链**

### P96 解的存在性分类
【表述】$\det A \ne 0$：$Ax = b$ 对任意 $b$ 有唯一解；$\det A = 0$：无解或无穷多解（取决于 $b \in \operatorname{Col}(A)$）。
【注意】"$\det = 0$ 意味着无解"是**错误**说法（可能无穷多解）——姊妹篇 §6 误区 1 [1]

### P97 特征方程
【表述】谱 = 特征方程 $\det(\lambda I - A) = 0$ 的根（P54）。
【应用】所有谱方法（PCA/谱聚类/振动分析）的起点

### P98 Jacobian 与局部可逆
【表述】$f: \mathbb{R}^n \to \mathbb{R}^n$ 光滑，$\det J_f(x) \ne 0$ ⟹ $f$ 在 $x$ 附近局部微分同胚（隐函数定理）；积分换元 $\int_{f(S)} g\,dy = \int_S g(f(x))\,|\det J_f(x)|\,dx$。
【证明要点】姊妹篇 §3.6 [6]
【应用】变量替换、概率密度变换、Normalizing Flow（$O(n)$ 三角 Jacobian 设计）

### P99 体积缩放
【表述】线性变换 $T(x) = Ax$：$\operatorname{vol}(T(S)) = |\det A|\,\operatorname{vol}(S)$。
【证明要点】姊妹篇 §3.3 [1]
【应用】概率归一化（多元高斯 $\propto |\det\Sigma|^{-1/2}$）、几何测度

### P100 反例警告：det 不是病态判据
【表述】数值上**不可用** $\det$ 判断病态性/可逆性。
【反例】$\det\begin{pmatrix} 1 & 1000 \\ 0 & 1 \end{pmatrix} = 1$ 但条件数 $\approx 10^6$（严重病态）[5]
【正解】用秩（QR/SVD）与条件数 $\operatorname{cond} A = \sigma_{\max}/\sigma_{\min}$ 判断；det 只适合理论/精确算术 [5]
【注意】$\det(cA) = c^n \det A$（P16）使 det 对尺度敏感，与病态无单调关系（P62）

---

## 14. 性质速查索引表

> 按"想查什么"反查编号：

| 我想知道… | 性质 |
|:----------|:-----|
| 行列式被什么唯一确定 | P1–P4 |
| 交换两行/乘常数/加倍数怎么变 | P8–P10, P15 |
| 转置会不会变 | P7 |
| 乘积/逆/幂的行列式 | P18–P22 |
| 伴随矩阵的行列式 | P23 |
| 正交/酉/幂等/对合/幂零/反对称矩阵 | P34–P39 |
| 三角/对角/分块对角矩阵 | P32–P33, P47–P48 |
| 分块矩阵怎么拆 | P49–P53 |
| 与特征值什么关系 | P54–P57, P61 |
| det(I+AB) 的交换公式 | P59 |
| 奇异值/范数与 det | P60, P67–P69 |
| det 多大算大 | P63–P70 |
| 行列式求导 | P71–P76 |
| 行列式作为函数/映射 | P78–P84 |
| Vandermonde/Cauchy/Wronskian/结式 | P85–P88 |
| 图/树/几何体积 | P89–P90, P99 |
| 解方程组/可逆判定 | P94–P96 |
| 何时不能用 det | P100, P62 |

---

## 参考文献

[1] Strang G. *Introduction to Linear Algebra*, 5th ed. Wellesley-Cambridge Press, 2016. （第 5 章：行列式性质全集）
[2] Axler S. *Linear Algebra Done Right*, 4th ed. Springer, 2023. （第 10 章：行列式的公理化与唯一性）
[3] Artin M. *Algebra*, 2nd ed. Pearson, 2010. （第 12 章：行列式、外代数、结式、矩阵树定理）
[4] Horn R A, Johnson C R. *Matrix Analysis*, 2nd ed. Cambridge University Press, 2012. （不等式、Schur 补、Jacobi 公式、Sylvester 恒等式、log det 凹性）
[5] Golub G H, Van Loan C F. *Matrix Computations*, 4th ed. Johns Hopkins University Press, 2013. （LU 分解算 det、条件数反例、数值稳定性）
[6] Bishop C M. *Pattern Recognition and Machine Learning*. Springer, 2006. （多元高斯、Jacobian 换元、流模型）
[7] 张贤达. *矩阵分析与应用*, 2nd ed. 清华大学出版社, 2013. （中文系统整理：行列式与矩阵函数、更新公式）

> 姊妹篇：[行列式的几何与代数意义深度分析](2026-08-22-determinant-geometric-algebraic-meaning.md)（同目录）——"为什么"与"有哪些"对照阅读。

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-22 | v1.0 | 首次创建：行列式性质 MECE 十类穷举（100 条性质），含表述/条件/证明要点/应用/反例，与几何代数意义姊妹篇互补 |
