#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选和分类服务器研发相关问题
"""
import re
from pathlib import Path

# 服务器研发相关的关键词
SERVER_RELATED_KEYWORDS = [
    '服务器', 'server', 'BMC', 'BIOS', '主板', '内存', 'CPU', 'GPU', 'PCIe', 'PCI-E',
    '电源', '散热', '液冷', '风冷', '机架', '机柜', '网络', '网卡', '交换机',
    '存储', '硬盘', 'SSD', 'NVMe', 'RAID', '机箱', '设计', '研发', '测试',
    '运维', 'RFP', '投标', '招标', 'SR需求', '规格', '标准', '协议',
    '系统', '固件', '驱动', '性能', '功耗', '可靠性', '可用性', '可维护性',
    '供应链', '生产', '制造', '装配', 'ODM', 'OEM', '国产化', '国产替代',
    'AI服务器', '智算', '算力', '集群', '互连', '拓扑', 'POD', '整机',
    '热设计', '结构设计', 'EMC', '安规', '认证', '兼容性', '集成', '整机柜',
    'Switch', 'PCIe', 'GPU', 'CPLD', 'PCB', 'PDB', 'PMBus', 'Redfish', 'IPMI',
    '供电', '散热', '风扇', '滑轨', '标签', 'SN', '热插拔', '冗余', 'MTBF',
    'RAS', 'DPC', 'AER', 'SRIOV', '固件', 'Flash', 'EEPROM', 'I2C', 'SMBus',
    'PCIe Switch', 'PCIe Retimer', 'NVMe-MI', 'UCE', 'CE', '800VDC', '数据中心'
]

# 分类关键词与对应的类别
CATEGORIES = {
    '硬件架构与设计': [
        '架构', '设计', '结构', '拓扑', '互连', '布局', '外形', '尺寸', '机械', '工艺',
        '主板', 'PCB', '组件', '部件', '选型', '元器件', '封装', '机箱', '机柜', '整机柜',
        '滑轨', '标签', 'SN', '铭牌', '丝印', '装配', '工艺', '整机', '外形', '结构'
    ],
    '性能与功耗优化': [
        '性能', '功耗', '能效', '能耗', '效率', '优化', '算力', '加速', '吞吐', '延迟',
        '散热', '热管理', '温度', '冷却', '液冷', '风冷', '水冷', '效率', '风扇', '降额',
        '降带宽', '降速率', '性能衰减', '性能指标', '功耗封顶'
    ],
    'BMC与系统管理': [
        'BMC', '基板管理控制器', '带外', '带内', '管理', '监控', '日志', '告警', '诊断',
        '巡检', '升级', '刷新', '固件', 'Redfish', 'IPMI', 'SNMP', 'SOL', '虚拟媒体',
        '基板', '控制器', 'Redfish', '带外', 'I2C', 'SMBus', 'UART', 'MCTP', 'PMBus',
        'FRU', '资产管理', '故障监控', '温度监控', '点灯', 'Identify灯', 'Active灯',
        'Fault灯', 'Pre-Fail灯', '心跳', '扁平管理', '卫星控制器'
    ],
    'BIOS与初始化': [
        'BIOS', 'UEFI', '固件', '初始化', '启动', '引导', '配置', '设置', '参数', 'POST',
        '启动项', '引导项', '上电时序', '自检', '告警', '安全启动'
    ],
    '网络与互联': [
        '网络', '网卡', '以太网', 'InfiniBand', '光纤', 'PCIe', 'PCI-E', '拓扑', '互连',
        '通信', '协议', 'TCP', 'UDP', 'RDMA', 'RoCE', 'Switch', '交换机', '端口', '带宽', '延迟',
        '互联', '链路', 'PCIe Switch', 'PCIe Retimer', 'P2P', 'DPC', 'ACS', 'SRIOV',
        '级联', 'Fabric', '隔离', 'BDF', 'Slot', 'Port', 'AER', 'UCE', 'CE'
    ],
    '存储系统': [
        '存储', '硬盘', 'HDD', 'SSD', 'NVMe', 'SATA', 'SAS', '磁盘', '阵列', 'RAID',
        '固件', '驱动', 'IOPS', '吞吐', '备份', '恢复', '擦除', '文件系统',
        'NVMe-MI', 'SMART', 'Telemetry', 'Locate点灯', '上下电', '预故障'
    ],
    '内存与计算': [
        'CPU', 'GPU', '内存', 'HBM', 'DDR', '计算', '处理器', '加速器', '核数', '主频', '缓存',
        '芯片', '计算卡', '模组', '载板', '白牌化', '四元组', '部件显示'
    ],
    '电源与供电': [
        '电源', '供电', '功耗', '电源模块', 'PSU', '冗余', '效率', '功率', '电压', '电流',
        '短路', '保护', '直流', '交流', '800VDC', 'PDU', 'PDB', '电源分配板',
        '闪断', '功率封顶', 'Active-Active', 'N+N', '保险', '浪涌', '防雷', 'ESD'
    ],
    '可靠性与测试': [
        '可靠性', '可用', '可用率', '容错', '冗余', '故障', '恢复', '测试', '验证', '校验',
        '压力测试', '老化', '高低温', '湿热', '振动', '冲击', 'EMC', '安规', '认证', '合规',
        '稳定性', 'MTBF', 'MTTR', 'RAS', '故障注入', '容错测试', '断电上电', '电压拉偏',
        '机械耐久', '跌落', '温度循环', '温度冲击'
    ],
    '可维护性与运维': [
        '可维护性', '维护', '运维', '检修', '拆卸', '装配', '热插拔', '更换', '保养',
        '备件', '库存', '物流', '服务', '维修', 'RMA', '运维', '易维护', '易交付',
        '抽屉式维护', '推拉', '防回流', '阻燃'
    ],
    '供应链与生产': [
        '生产', '制造', '装配', 'ODM', 'OEM', '供应链', '供应商', '采购', '成本',
        'BOM', '物料', '库存', '备货', '交期', '产能', '质量', '检验', 'QC', '质量',
        '生产拦截', '来料管控', '备件筛选'
    ],
    '国产化与替代': [
        '国产化', '国产', '替代', '自主可控', '信创', '鲲鹏', '昇腾', '海光', '兆芯', '龙芯',
        '飞腾', '麒麟', '统信', '欧拉', 'openEuler'
    ],
    'AI与智算': [
        'AI', '人工智能', '大模型', 'LLM', '训练', '推理', '智算', '算力', '集群',
        'GPU', '加速', '多卡', '分布式', '并行计算', 'POD', '液冷', '智算中心',
        '大语言模型', 'ChatGPT', 'Claude'
    ],
    '投标与RFP应答': [
        '投标', '招标', 'RFP', '需求', '应答', '标书', '规格', '标准', 'SR需求',
        '规格需求', '项目', '报价', '成本', '交付', '招投标', 'RFP', '投标策略',
        '里程碑', '风险规避', '优先级排序', '最佳实践', '对标', '成功因素'
    ],
    '标准与规范': [
        '标准', '规范', '协议', 'ODCC', 'Open19', 'OCP', 'OCP-Telco', 'TCG', 'RoHS',
        'REACH', 'CE', 'FCC', 'CCC', '安全', '合规', '认证', '标准', '电子标签',
        'PCN', '变更通知', 'UBM', '腾讯', '机房', '数据中心'
    ],
    '配置与兼容性': [
        '配置', '兼容', '兼容性', '适配', '匹配', '支持', '不支持', '限制', '选项',
        '清单', 'BOM', '选型', '验证', '测试清单', '隔离', '预留'
    ],
    '系统集成与解决方案': [
        '集成', '解决方案', '系统', '方案', '架构', '交付', '部署', '上线', '迁移',
        '调优', '优化', 'POD', '机柜', '机房', '数据中心', 'IDC', '集群', '分布式'
    ],
    '技术文档与知识库': [
        '文档', '手册', '指南', '规范', '标准', '知识库', 'FAQ', '问题', '故障',
        '排查', '案例', '培训', '学习', '教程', '示例', '模板', '技术文档', '规格'
    ]
}

# 问题特征
QUESTION_INDICATORS = [
    '需要', '希望', '请', '详细描述', '全面分析', '重新创建', '结合', '整理', '提炼',
    '细化补充', '改用', '参考', '工作点', '详细说明', '补充内容', '进行分析',
    '进行研究', '生成报告', '制定方案', '设计', '创建', '补充', '整理', '分类',
    '维度', '规格', '需求', '应答', '投标', 'RFP', 'SR', '是否', '能否', '能不能',
    '如何', '怎么', '怎样', '哪些', '什么', '为什么', '多少', '哪里', '何时'
]

# 要排除的AI回复特征
AI_RESPONSE_PATTERNS = [
    r'^我将', r'^即将开始', r'^接下来', r'^为了', r'^补充内容', r'^这份', r'^我还用',
    r'^来自', r'^创建时间', r'^网页-', r'^（共', r'^生成时间', r'^分类统计', r'^详细分类',
    r'^###', r'^##', r'^\|', r'^---', r'^•', r'^-', r'^\d+\.', r'^[a-z]\.',
    r'^\[', r'^https?://', r'^来源文件:', r'^文件:', r'^好的', r'^明白了', r'^是的',
    r'^为什么关键', r'^我将严格', r'^我将围绕', r'^我将按'
]

def is_server_related(question):
    """判断问题是否与服务器研发相关"""
    question = question.lower()
    for keyword in SERVER_RELATED_KEYWORDS:
        if keyword.lower() in question:
            return True
    return False

def is_real_question(text):
    """判断是否是真正的问题"""
    text = text.strip()
    
    # 太短的不是问题
    if len(text) < 8:
        return False
    
    # 排除AI回复
    for pattern in AI_RESPONSE_PATTERNS:
        if re.match(pattern, text):
            return False
    
    # 检查是否有问题特征
    has_indicator = False
    for indicator in QUESTION_INDICATORS:
        if indicator in text:
            has_indicator = True
            break
    
    if has_indicator:
        return True
    
    # 检查是否以问号结尾
    if text.endswith('？') or text.endswith('?'):
        return True
    
    return False

def categorize_question(question):
    """将问题分类到最匹配的类别"""
    question = question.lower()
    category_scores = {}
    
    for category, keywords in CATEGORIES.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in question:
                score += 1
        if score > 0:
            category_scores[category] = score
    
    if category_scores:
        # 返回得分最高的类别
        return max(category_scores.items(), key=lambda x: x[1])[0]
    else:
        return '其他服务器相关'

def main():
    input_file = Path(r"H:\github\md\用户提问汇总.md")
    output_file = Path(r"H:\github\md\服务器研发问题分类汇总.md")
    
    server_questions = []
    current_file = ""
    
    print("正在读取问题汇总文件...")
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if line.startswith("### 文件:"):
                current_file = line.replace("### 文件:", "").strip()
            elif re.match(r'^\d+\. ', line):  # 问题行
                question = re.sub(r'^\d+\. ', '', line)
                if is_server_related(question) and is_real_question(question):
                    server_questions.append({
                        'question': question,
                        'source_file': current_file,
                        'category': categorize_question(question)
                    })
    
    # 按类别分组
    categorized = {}
    for item in server_questions:
        category = item['category']
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(item)
    
    # 生成输出文件
    print(f"正在生成分类汇总文件，共 {len(server_questions)} 个服务器相关问题...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 服务器研发相关问题分类汇总\n\n")
        f.write(f"- 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- 原始问题总数: 8502\n")
        f.write(f"- 服务器相关问题数: {len(server_questions)}\n")
        f.write(f"- 分类数: {len(categorized)}\n\n")
        
        # 按问题数量排序类别
        sorted_categories = sorted(categorized.items(), 
                                  key=lambda x: len(x[1]), 
                                  reverse=True)
        
        f.write("## 分类统计\n\n")
        for category, items in sorted_categories:
            f.write(f"- {category}: {len(items)} 个问题\n")
        f.write("\n")
        
        f.write("## 详细分类\n\n")
        for category, items in sorted_categories:
            f.write(f"### {category}\n\n")
            f.write(f"（共 {len(items)} 个问题）\n\n")
            
            # 按来源文件分组
            by_source = {}
            for item in items:
                source = item['source_file']
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(item)
            
            for source, source_items in by_source.items():
                f.write(f"**来源文件: {source}**\n\n")
                for i, item in enumerate(source_items, 1):
                    f.write(f"{i}. {item['question']}\n")
                f.write("\n")
    
    print(f"分类汇总完成！结果已保存到: {output_file}")
    print(f"服务器相关问题数量: {len(server_questions)}")

if __name__ == "__main__":
    main()
