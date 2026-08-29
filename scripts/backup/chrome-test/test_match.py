import difflib
import re

def normalize_title(s):
    s = s.lower().strip()
    s = re.sub(r'[_\s-]*\d{6,}([_\s-]*[vV]\d+)?$', '', s)
    s = re.sub(r'[_\s-]*\d{1,5}$', '', s)
    s = re.sub(r'[\s\-_／／·•,，。、；;：:！!？?（）()【】\[\]{}""''「」『』〈〉《》～~@#$%^&*+=|\\/]+', '', s)
    return s

tests = [
    ("逻辑分析在复杂问题中的应用方法", "逻辑分析解决复杂问题"),
    ("过去一年AI领域技术演进汇总", "AI技术演进年度总结"),
    ("存储设备参数信息提供", "存储设备参数信息提供"),
    ("服务器L1-L12分级体系介绍1", "L1_L12分级体系"),
    ("复杂系统理论补充还原论不足", "复杂系统城市规划应用"),
    ("服务器制造验收1", "服务器制造验收"),
]

for a, b in tests:
    na = normalize_title(a)
    nb = normalize_title(b)
    ratio = difflib.SequenceMatcher(None, na, nb).ratio()
    substr = na in nb or nb in na
    print(f"'{a}' vs '{b}'")
    print(f"  norm: '{na}' vs '{nb}'")
    print(f"  ratio={ratio:.3f}  substr={substr}")
    print()