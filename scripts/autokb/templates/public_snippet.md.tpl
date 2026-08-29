---
title: "{{ title }}"
source: "{{ source }}"
source_file: "{{ source_file }}"
import_date: "{{ import_date }}"
date: "{{ date }}"
type: "imported"
---

## 来源

- **原始文件**: `{{ source_file }}`
- **来源**: {{ source }}
- **导入日期**: {{ import_date }}

---

{{ content }}
