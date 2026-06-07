import os
import sys
import json
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doubao_ds_sxz_auto_optimized import load_config, validate_config, DEFAULT_CONFIG, CONFIG


class TestConfig(unittest.TestCase):
    """测试配置加载功能"""

    def setUp(self):
        """在每个测试前创建临时目录和配置文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_config = CONFIG

    def tearDown(self):
        """在每个测试后清理"""
        global CONFIG
        CONFIG = self.original_config
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_default_config(self):
        """测试加载默认配置（配置文件不存在时）"""
        config_path = os.path.join(self.temp_dir, "nonexistent.json")
        load_config(config_path)
        
        self.assertIsNotNone(CONFIG)
        self.assertEqual(CONFIG["chrome_path"], DEFAULT_CONFIG["chrome_path"])
        self.assertEqual(CONFIG["download_timeout"], DEFAULT_CONFIG["download_timeout"])

    def test_load_custom_config(self):
        """测试加载自定义配置文件"""
        custom_config = {
            "chrome_path": "C:\\custom\\chrome.exe",
            "download_dir": "C:\\custom\\downloads",
            "download_timeout": 20,
            "max_concurrent_downloads": 100
        }
        config_path = os.path.join(self.temp_dir, "config.json")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(custom_config, f)
        
        load_config(config_path)
        
        self.assertEqual(CONFIG["chrome_path"], "C:\\custom\\chrome.exe")
        self.assertEqual(CONFIG["download_dir"], "C:\\custom\\downloads")
        self.assertEqual(CONFIG["download_timeout"], 20)
        self.assertEqual(CONFIG["max_concurrent_downloads"], 100)
        self.assertEqual(CONFIG["export_timeout"], DEFAULT_CONFIG["export_timeout"])

    def test_config_merging(self):
        """测试配置合并（用户配置覆盖默认配置）"""
        custom_config = {
            "download_timeout": 30,
            "page_load_timeout": 15
        }
        config_path = os.path.join(self.temp_dir, "config.json")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(custom_config, f)
        
        load_config(config_path)
        
        self.assertEqual(CONFIG["download_timeout"], 30)
        self.assertEqual(CONFIG["page_load_timeout"], 15)
        self.assertEqual(CONFIG["export_timeout"], DEFAULT_CONFIG["export_timeout"])

    def test_invalid_config_file(self):
        """测试无效配置文件（JSON格式错误）"""
        config_path = os.path.join(self.temp_dir, "invalid.json")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("{invalid json}")
        
        load_config(config_path)
        
        self.assertIsNotNone(CONFIG)
        self.assertEqual(CONFIG["chrome_path"], DEFAULT_CONFIG["chrome_path"])

    def test_missing_required_keys(self):
        """测试缺失必填配置项时使用默认值"""
        custom_config = {
            "chrome_path": "C:\\custom\\chrome.exe"
        }
        config_path = os.path.join(self.temp_dir, "config.json")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(custom_config, f)
        
        load_config(config_path)
        
        self.assertEqual(CONFIG["chrome_path"], "C:\\custom\\chrome.exe")
        self.assertEqual(CONFIG["chromedriver_path"], DEFAULT_CONFIG["chromedriver_path"])
        self.assertEqual(CONFIG["download_timeout"], DEFAULT_CONFIG["download_timeout"])

    def test_empty_index_html_files(self):
        """测试空的索引文件列表"""
        custom_config = {
            "index_html_files": []
        }
        config_path = os.path.join(self.temp_dir, "config.json")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(custom_config, f)
        
        load_config(config_path)
        
        self.assertEqual(CONFIG["index_html_files"], DEFAULT_CONFIG["index_html_files"])


if __name__ == '__main__':
    unittest.main()
