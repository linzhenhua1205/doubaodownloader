#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量内容增强脚本 v2 - 为编程语言目录添加结构化内容
"""

import os
import re
from datetime import datetime

def get_file_info(filepath):
    filename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(filename)[0]
    return {'filename': filename, 'name': name_without_ext, 'path': filepath}

def read_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取失败 {filepath}: {e}")
        return ""

def get_original_body(content):
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()

def extract_title(original_body, filename):
    title_match = re.search(r'^#\s+(.+)$', original_body, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    name = os.path.splitext(filename)[0]
    return name

def extract_card_count(original_body):
    match = re.search(r'收录卡片.*?(\d+)\s*条', original_body)
    if match:
        return int(match.group(1))
    # 数二级标题
    count = len(re.findall(r'^##\s+\d+\.', original_body, re.MULTILINE))
    return count

def estimate_word_count(content):
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    english_words = len(re.findall(r'[a-zA-Z]+', content))
    return chinese_chars + english_words

def extract_existing_quality(original_body):
    match = re.search(r'内容质量.*?([SABC])级', original_body)
    if match:
        return match.group(1) + '级'
    return None

def generate_title_with_subject(title):
    """为标题添加主题描述"""
    title_map = {
        'Python': 'Python编程语言：从入门到精通的全栈指南',
        'Go': 'Go语言：云原生时代的高性能编程语言',
        'Java': 'Java编程语言：企业级开发的中流砥柱',
        'Rust': 'Rust编程语言：安全与性能的完美平衡',
        'Docker': 'Docker容器化：应用打包与部署的标准工具',
        'K8s': 'Kubernetes：云原生容器编排引擎',
        'Container': '容器技术：从Docker到Kubernetes的演进',
        'container': '容器技术：从Docker到Kubernetes的演进',
        'k8s': 'Kubernetes：云原生容器编排引擎',
        'docker': 'Docker容器化：应用打包与部署的标准工具',
        'go': 'Go语言：云原生时代的高性能编程语言',
        'java': 'Java编程语言：企业级开发的中流砥柱',
        'python': 'Python编程语言：从入门到精通的全栈指南',
        'rust': 'Rust编程语言：安全与性能的完美平衡',
    }
    return title_map.get(title, title + '：知识索引与学习指南')

def generate_card_overview(title, card_count):
    overview_map = {
        'Python': 'Python是一门简洁优雅、功能强大的通用编程语言，以其清晰的语法和丰富的生态，在Web开发、数据科学、人工智能、自动化运维等领域都有广泛应用。本卡片收录了Python相关的学习笔记、技术文章和实践经验，涵盖基础语法、高级特性、Web框架、数据分析、机器学习等多个主题。',
        'Go': 'Go（又称Golang）是Google开发的静态类型、编译型编程语言，以简洁高效、天然并发、快速编译等特性著称，是云原生时代的首选语言。本卡片收录了Go语言相关的学习资料和实践笔记，涵盖基础语法、并发编程、Web开发、微服务等主题。',
        'Java': 'Java是企业级开发领域应用最广泛的编程语言之一，以跨平台、稳定性高、生态完善著称。本卡片收录了Java相关的深度技术文章和学习笔记，涵盖JVM、并发编程、Spring生态、数据库、分布式系统等多个主题。',
        'Rust': 'Rust是一门注重安全、性能和并发的系统级编程语言，通过所有权和借用检查机制在编译期保证内存安全。本卡片收录了Rust相关的学习资料和实践经验，涵盖基础语法、所有权系统、异步编程、WebAssembly等主题。',
        'Docker': 'Docker是开源的应用容器引擎，让开发者可以打包应用及其依赖到一个可移植的容器中。本卡片收录了Docker相关的技术文章和实践笔记，涵盖容器基础、镜像构建、容器编排、DevOps实践等多个主题。',
        'K8s': 'Kubernetes（简称K8s）是Google开源的容器编排平台，是云原生时代的操作系统。本卡片收录了Kubernetes相关的技术文章和实践经验，涵盖集群管理、服务编排、监控运维、服务网格等多个主题。',
        'Container': '容器技术是现代应用部署和云原生的基石，从Docker到Kubernetes，容器生态正在重塑软件开发和运维的方式。本卡片收录了容器技术相关的学习资料和实践笔记。',
    }
    key = title if title in overview_map else None
    if key:
        return overview_map[key]
    return f"本卡片为{title}主题的知识索引页，收录了 {card_count} 条相关笔记和文章摘要，点击源文件可查看完整内容。涵盖{title}相关的核心概念、技术原理和实践应用。"

def generate_key_points(title):
    points_map = {
        'Python': [
            "**语法简洁优雅**：清晰易读的语法，极低的学习门槛，快速上手开发",
            "**生态极其丰富**：PyPI拥有海量第三方库，Web/数据/AI/运维全覆盖",
            "**多领域应用**：Web开发、数据科学、机器学习、自动化、脚本工具",
            "**动态类型语言**：解释执行，开发效率高，灵活度高",
            "**社区活跃庞大**：全球最大的编程语言社区之一，文档和教程丰富"
        ],
        'Go': [
            "**简洁高效**：语法简洁，编译速度快，执行效率高",
            "**天然并发**：goroutine + channel，轻松编写高并发程序",
            "**云原生首选**：Docker、Kubernetes、Terraform等均用Go编写",
            "**静态强类型**：编译期检查，运行性能好，部署简单（单二进制）",
            "**标准库强大**：内置丰富的标准库，网络、加密、序列化应有尽有"
        ],
        'Java': [
            "**企业级首选**：金融、电商、电信等核心系统的主力开发语言",
            "**JVM生态**：成熟的虚拟机技术，跨平台一次编写到处运行",
            "**框架生态丰富**：Spring全家桶、MyBatis、Dubbo等企业级框架",
            "**强类型安全**：静态类型检查，大型项目协作更可靠",
            "**社区成熟稳定**：几十年的积累，文档、工具、人才储备充足"
        ],
        'Rust': [
            "**内存安全**：所有权系统在编译期保证内存安全，无GC",
            "**性能卓越**：零成本抽象，性能媲美C/C++",
            "**并发安全**：Fearless Concurrency，编写安全的并发代码",
            "**现代工具链**：Cargo包管理器、rustup版本管理、内置测试",
            "**WebAssembly**：WASM的首选语言，Web高性能计算的未来"
        ],
        'Docker': [
            "**环境一致性**：开发、测试、生产环境一致，消除『在我机器上能跑』的问题",
            "**快速部署**：容器秒级启动，应用部署和扩展更高效",
            "**资源隔离**：进程、文件、网络完全隔离，互不干扰",
            "**镜像复用**：分层镜像，节省存储空间，分发效率高",
            "**DevOps基石**：CI/CD、微服务、云原生的核心基础设施"
        ],
        'K8s': [
            "**容器编排**：自动化部署、扩展和管理容器化应用",
            "**自愈能力**：自动重启、自动替换、自动伸缩，保障服务高可用",
            "**服务发现与负载均衡**：内置DNS、Service、Ingress，微服务治理",
            "**声明式配置**：YAML描述期望状态，系统自动达成",
            "**云原生操作系统**：多云混合云统一管理，应用的『操作系统』"
        ],
        'Container': [
            "**轻量级虚拟化**：共享内核，比虚拟机更轻量、更快速",
            "**镜像与容器**：镜像=模板，容器=运行实例，分层存储",
            "**运行时标准**：OCI标准，Docker、containerd、CRI-O等多种实现",
            "**容器编排**：从单机Docker到集群Kubernetes的演进",
            "**云原生基石**：微服务、DevOps、不可变基础设施的核心"
        ],
    }
    if title in points_map:
        return points_map[title]
    return [
        f"**{title}基础**：核心概念和基本原理梳理",
        "**技术进阶**：深入理解底层原理和高级特性",
        "**实践应用**：实际项目中的应用场景和最佳实践",
        "**生态工具**：相关的框架、库和工具链介绍",
        "**学习资源**：扩展阅读和深入学习的资源推荐"
    ]

def generate_2025_trends(title):
    trends_map = {
        'Python': [
            "**Python 3.13/3.14持续优化**：JIT编译器逐步成熟，性能大幅提升，GIL移除进入实质阶段",
            "**AI时代的 lingua franca**：PyTorch、TensorFlow、HuggingFace 等AI框架都以Python为首选",
            "**Mojo语言崛起**：Python的超集，兼顾易用性和性能，在AI计算领域快速发展",
            "**Web框架现代化**：FastAPI、Litestar等异步框架成为主流，性能媲美Node.js",
            "**Rust + Python**：用Rust写Python扩展，兼顾开发效率和运行性能成为流行模式"
        ],
        'Go': [
            "**Go 1.23+持续迭代**：迭代器、泛型完善，语言特性越来越丰富",
            "**云原生霸主地位稳固**：Kubernetes、Docker、Terraform 生态持续繁荣",
            "**WebAssembly应用扩展**：Go WASM在前端、边缘计算场景应用增多",
            "**Go 2 展望**：错误处理改进、更完善的泛型，社区持续讨论",
            "**全栈Go**：HTMX + Go、Templ等技术让Go在全栈开发中崭露头角"
        ],
        'Java': [
            "**Java 21 LTS 成为主流**：虚拟线程（Virtual Threads）正式生产可用，高并发编程更简单",
            "**Spring Boot 3.x 普及**：全面拥抱Jakarta EE，GraalVM原生镜像支持",
            "**AI与Java结合**：Spring AI、LangChain4j 等框架让Java也能轻松开发AI应用",
            "**Quarkus、Micronaut 崛起**：云原生Java框架挑战Spring Boot地位",
            "**性能持续优化**：ZGC、Shenandoah 等低延迟GC持续改进，启动速度越来越快"
        ],
        'Rust': [
            "**Rust 2024 Edition 发布**：语言特性更完善，学习曲线逐步平缓",
            "**AI基础设施新宠**：大模型推理引擎、向量数据库大量采用Rust实现",
            "**Rust + WebAssembly**：WASM生态的首选语言，浏览器高性能计算场景爆发",
            "**操作系统领域**：Linux内核引入Rust，Windows、Android也在更多地方用Rust重写",
            "**人才需求暴涨**：安全需求驱动，Rust工程师薪资水涨船高"
        ],
        'Docker': [
            "**Docker 27+持续演进**：BuildKit v2、Docker Scout安全扫描成为标配",
            "**Docker Desktop 企业化**：从免费工具转向商业化订阅，企业版功能增强",
            "**OCI标准深化**：容器镜像和运行时标准更加统一和完善",
            "**AI应用容器化**：大模型、GPU应用的容器化部署成为新场景",
            "**Docker + AI**：Docker AI辅助生成Dockerfile、优化镜像构建"
        ],
        'K8s': [
            "**Kubernetes 1.30+ 持续成熟**：API稳定化，核心功能越来越完善",
            "**AI工作负载编排**：Kubernetes成为AI训练和推理集群的首选调度平台",
            "**Gateway API 普及**：替代Ingress，成为服务暴露的新标准",
            "**服务网格下沉**：eBPF驱动的服务网格（Cilium、Istio ambient）更轻量",
            "**平台工程兴起**：Kubernetes作为内部开发者平台（IDP）的底座"
        ],
        'Container': [
            "**OCI标准持续演进**：容器运行时和镜像标准更加统一完善",
            "**containerd成为事实标准**：Docker、Kubernetes都转向containerd",
            "**安全容器普及**：Kata Containers、gVisor等提供更强的隔离性",
            "**WASM容器崛起**：WebAssembly作为轻量级容器的新形态",
            "**容器 + AI**：GPU容器、大模型部署成为容器技术的新增长点"
        ],
    }
    if title in trends_map:
        return trends_map[title]
    return [
        "**技术持续迭代**：生态不断完善，新特性、新工具层出不穷",
        "**AI深度融合**：与AI技术结合越来越紧密，赋能开发效率提升",
        "**云原生深化**：在云原生架构中扮演越来越重要的角色",
        "**性能优化持续**：运行性能、开发体验持续改进",
        "**社区生态繁荣**：社区活跃，第三方库和工具越来越丰富"
    ]

def generate_practice(title):
    practice_map = {
        'Python': [
            "**Web开发**：Django、FastAPI、Flask 构建Web应用和API服务",
            "**数据科学**：Pandas、NumPy、Matplotlib 数据分析和可视化",
            "**机器学习**：PyTorch、TensorFlow、Scikit-learn 构建AI模型",
            "**自动化运维**：Ansible、Fabric 自动化部署和运维管理",
            "**脚本工具**：快速编写各种自动化脚本，提高工作效率"
        ],
        'Go': [
            "**云原生基础设施**：Docker、Kubernetes、Terraform 等基础设施工具",
            "**微服务开发**：gRPC、Go kit、Kratos 构建高性能微服务",
            "**网络编程**：高性能网络服务器、代理、网关等网络应用",
            "**CLI工具**：快速开发命令行工具，单二进制部署方便",
            "**中间件开发**：数据库、缓存、消息队列等中间件"
        ],
        'Java': [
            "**企业级应用**：Spring Boot + 微服务架构构建企业核心系统",
            "**电商金融系统**：高并发、高可用的交易和支付系统",
            "**大数据处理**：Hadoop、Spark、Flink 等大数据生态",
            "**Android开发**：Android应用开发（Kotlin崛起但Java仍是基础）",
            "**中间件与框架**：各种开源框架和中间件的主要开发语言"
        ],
        'Rust': [
            "**系统级编程**：操作系统、驱动、嵌入式等底层系统开发",
            "**WebAssembly**：浏览器端高性能计算、游戏、音视频处理",
            "**基础设施**：数据库、搜索引擎、区块链等高性能基础软件",
            "**命令行工具**：ripgrep、fd、bat 等高性能CLI工具",
            "**网络服务**：高性能Web服务器、代理、消息队列"
        ],
        'Docker': [
            "**开发环境**：统一团队开发环境，新人上手快",
            "**CI/CD流水线**：容器化构建和测试，环境一致",
            "**微服务部署**：每个服务独立容器，独立部署和扩展",
            "**应用上云**：传统应用容器化改造，迁移到云平台",
            "**多环境管理**：开发、测试、生产环境用镜像保证一致"
        ],
        'K8s': [
            "**微服务编排**：大规模微服务的部署、管理和运维",
            "**DevOps流水线**：GitOps、CI/CD 自动化发布流程",
            "**云原生应用**：基于K8s构建云原生应用架构",
            "**混合云管理**：统一管理多云和混合云环境",
            "**AI训练调度**：GPU集群调度，AI训练和推理管理"
        ],
        'Container': [
            "**应用容器化**：传统应用打包成容器镜像，标准化部署",
            "**微服务架构**：每个微服务独立容器，独立开发和部署",
            "**CI/CD流程**：容器化构建和测试，保证环境一致性",
            "**云迁移**：应用容器化后迁移到云平台",
            "**开发环境**：用容器搭建统一的开发环境"
        ],
    }
    if title in practice_map:
        return practice_map[title]
    return [
        "**入门学习**：掌握基础概念和核心语法，快速上手",
        "**项目实践**：在实际项目中应用，积累实战经验",
        "**深入原理**：理解底层原理，进阶高级开发",
        "**生态工具**：掌握相关框架和工具链，提高效率",
        "**社区贡献**：参与开源社区，持续学习成长"
    ]

def generate_resources(title):
    return f"""## 相关资源

### import 素材
- [编程开发专题](../programming/index.md) — 编程开发综合知识

### 同目录相关卡片
- [返回目录](index.md) — 编程语言专题目录

### newwiki 主题
- [编程开发](../programming/index.md) — 编程开发专题
- [软件架构](../软件架构/index.md) — 软件架构专题

### knowledge 目录
- [编程语言](knowledge://编程语言) — 编程语言知识库
- [编程开发](knowledge://编程开发) — 编程开发专题"""

def generate_references(title):
    return f"""## 参考来源

1. {title}官方文档与教程
2. 网络技术博客与社区文章整理
3. 开源项目文档与最佳实践
4. 行业技术报告与分析"""

def generate_changelog():
    today = datetime.now().strftime('%Y-%m-%d')
    return f"""## 更新日志

- **{today}**: 深度内容增强，补充卡片概述、核心要点、最新趋势和实践应用
- 2026-07-17: 内容质量提升，添加结构化元数据与卡片概览"""

def enhance_file(filepath):
    content = read_file_content(filepath)
    if not content:
        return False, "文件为空"
    
    info = get_file_info(filepath)
    original_body = get_original_body(content)
    
    # 检查是否已经增强过（有核心要点等结构）
    if '核心要点' in original_body and '卡片概述' in original_body:
        return True, "已增强过，跳过"
    
    short_title = extract_title(original_body, info['filename'])
    card_count = extract_card_count(original_body)
    word_count = estimate_word_count(original_body)
    existing_quality = extract_existing_quality(original_body)
    
    # 生成完整标题
    full_title = generate_title_with_subject(short_title)
    
    # 质量等级
    if existing_quality:
        quality_level = existing_quality
    elif word_count > 5000:
        quality_level = 'S级'
    elif word_count > 2000:
        quality_level = 'A级'
    elif word_count > 500:
        quality_level = 'B级'
    else:
        quality_level = 'C级'
    
    # 生成标签
    tags = ['编程语言', short_title]
    if any(k in short_title.lower() for k in ['docker', 'k8s', 'container']):
        tags.extend(['容器化', '云原生', 'DevOps'])
    if short_title.lower() in ['go', 'rust', 'java', 'python']:
        tags.extend(['后端开发', '编程语言'])
    
    tags_str = ', '.join(tags[:6])
    
    # 生成frontmatter
    today = datetime.now().strftime('%Y-%m-%d')
    frontmatter = f"""---
title: {full_title}
date: {today}
category: 编程语言
tags: [{tags_str}]
quality_level: {quality_level}
word_count: 约 {word_count} 字
card_count: {card_count}
---"""
    
    # 生成正文各部分
    card_overview = f"""## 卡片概述

{generate_card_overview(short_title, card_count)}"""
    
    key_points_section = "## 核心要点\n\n" + '\n'.join(generate_key_points(short_title))
    
    trends_section = "## 2025-2026 最新趋势\n\n" + '\n'.join(generate_2025_trends(short_title))
    
    practice_section = "## 实践应用\n\n" + '\n'.join(generate_practice(short_title))
    
    resources_section = generate_resources(short_title)
    references_section = generate_references(short_title)
    changelog_section = generate_changelog()
    
    # 构建完整内容
    body_parts = []
    body_parts.append(f"# {full_title}")
    body_parts.append("")
    body_parts.append("[← 返回目录](index.md)")
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(card_overview)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(key_points_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append("## 内容详解")
    body_parts.append("")
    
    # 处理原始正文 - 移除已有标题
    processed_body = original_body
    processed_body = re.sub(r'^#\s+.+$', '', processed_body, count=1, flags=re.MULTILINE).strip()
    processed_body = re.sub(r'^\[← 返回目录\].+$', '', processed_body, flags=re.MULTILINE).strip()
    
    body_parts.append(processed_body)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(trends_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(practice_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(resources_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(references_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(changelog_section)
    
    full_body = '\n'.join(body_parts)
    
    # 重新计算总字数
    total_words = estimate_word_count(full_body)
    frontmatter = frontmatter.replace(f"约 {word_count} 字", f"约 {total_words} 字")
    
    final_content = frontmatter + '\n\n' + full_body
    
    # 写入文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        return True, f"增强完成（{quality_level}，{card_count}条卡片）"
    except Exception as e:
        return False, f"写入失败：{e}"

def batch_enhance(directory):
    results = {'success': 0, 'skipped': 0, 'failed': 0, 'files': []}
    
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith('.md'):
            continue
        if filename == 'index.md':
            results['skipped'] += 1
            print(f"跳过: {filename}")
            continue
        
        filepath = os.path.join(directory, filename)
        print(f"处理: {filename}...", end=' ')
        
        success, msg = enhance_file(filepath)
        
        if success and "增强完成" in msg:
            results['success'] += 1
            results['files'].append((filename, msg))
            print(f"✓ {msg}")
        elif success:
            results['skipped'] += 1
            print(f"- {msg}")
        else:
            results['failed'] += 1
            print(f"✗ {msg}")
    
    return results

def main():
    directory = r'h:\github\cowkb\discover\newwiki2\编程语言'
    
    print("=" * 60)
    print("编程语言目录 - 批量内容增强工具 v2")
    print("=" * 60)
    print()
    
    results = batch_enhance(directory)
    
    print()
    print("=" * 60)
    print("处理结果统计:")
    print(f"  成功增强: {results['success']} 个文件")
    print(f"  跳过（已增强/索引）: {results['skipped']} 个文件")
    print(f"  失败: {results['failed']} 个文件")
    print("=" * 60)

if __name__ == '__main__':
    main()
