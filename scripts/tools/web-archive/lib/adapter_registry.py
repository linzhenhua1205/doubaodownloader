#!/usr/bin/env python3
"""站点适配器注册表 — 框架化站点适配加速

按域名匹配适配器; 未命中时使用 GenericAdapter (trafilatura 通用提取)。
新增站点适配: 在 adapters/ 下新建 <site>.py, 定义 class SiteAdapter(AdapterBase),
并在本文件的 ADAPTERS 列表中注册即可 (或利用自动发现)。
"""
from pathlib import Path
import importlib
import re

from lib.adapters.base import AdapterBase, GenericAdapter

# 手动注册表 (显式优先, 稳定可控)
_ADAPTERS: list = []


def _autodiscover():
    """自动发现 adapters/ 目录下的适配器模块 (约定: 文件名=站点名, 含 register() 或 SiteAdapter 类)"""
    pkg_dir = Path(__file__).resolve().parent / "adapters"
    for mod_file in sorted(pkg_dir.glob("*.py")):
        if mod_file.name == "__init__.py" or mod_file.name == "base.py":
            continue
        mod_name = f"lib.adapters.{mod_file.stem}"
        try:
            mod = importlib.import_module(mod_name)
            for attr in dir(mod):
                obj = getattr(mod, attr)
                if isinstance(obj, type) and issubclass(obj, AdapterBase) and obj is not AdapterBase and obj is not GenericAdapter:
                    if obj not in _ADAPTERS:
                        _ADAPTERS.append(obj())
        except Exception as e:
            print(f"⚠️ 适配器加载失败 {mod_name}: {e}")


_autodiscover()


def get_adapter(url: str) -> AdapterBase:
    """按 URL 匹配最合适的适配器; 未命中返回通用适配器。"""
    for a in _ADAPTERS:
        if a.match(url):
            return a
    return GenericAdapter()


def list_adapters() -> list:
    return [(a.name, a.domain_patterns) for a in _ADAPTERS]
