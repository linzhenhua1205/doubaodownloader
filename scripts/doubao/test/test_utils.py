import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doubao_ds_sxz_auto_optimized import (
    extract_links_from_single_file,
    extract_links_with_titles,
    normalize_title,
    is_title_matched,
    sort_links_by_existing_with_info
)


class TestLinkExtraction(unittest.TestCase):
    """测试链接提取功能"""

    def setUp(self):
        """创建临时HTML文件"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extract_links_from_single_file(self):
        """测试从单个HTML文件提取链接"""
        html_content = '''
        <div class="link-name">对话标题1</div>
        <div class="link-url">https://www.doubao.com/chat/123456</div>
        <div class="link-name">对话标题2</div>
        <div class="link-url">https://www.doubao.com/chat/789012</div>
        '''
        html_path = os.path.join(self.temp_dir, "test.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        links = extract_links_from_single_file(html_path)
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0][0], "123456")
        self.assertEqual(links[0][1], "对话标题1")
        self.assertEqual(links[1][0], "789012")
        self.assertEqual(links[1][1], "对话标题2")

    def test_extract_links_from_nonexistent_file(self):
        """测试从不存在的文件提取链接"""
        links = extract_links_from_single_file("nonexistent.html")
        self.assertEqual(len(links), 0)

    def test_extract_links_with_titles_duplicate(self):
        """测试去重功能"""
        html_content1 = '''
        <div class="link-name">标题A</div>
        <div class="link-url">https://www.doubao.com/chat/111</div>
        <div class="link-name">标题B</div>
        <div class="link-url">https://www.doubao.com/chat/222</div>
        '''
        html_content2 = '''
        <div class="link-name">标题A重复</div>
        <div class="link-url">https://www.doubao.com/chat/111</div>
        <div class="link-name">标题C</div>
        <div class="link-url">https://www.doubao.com/chat/333</div>
        '''
        
        html_path1 = os.path.join(self.temp_dir, "test1.html")
        html_path2 = os.path.join(self.temp_dir, "test2.html")
        
        with open(html_path1, 'w', encoding='utf-8') as f:
            f.write(html_content1)
        with open(html_path2, 'w', encoding='utf-8') as f:
            f.write(html_content2)

        links = extract_links_with_titles([html_path1, html_path2])
        self.assertEqual(len(links), 3)
        link_ids = [lid for lid, _ in links]
        self.assertIn("111", link_ids)
        self.assertIn("222", link_ids)
        self.assertIn("333", link_ids)


class TestTitleNormalization(unittest.TestCase):
    """测试标题规范化功能"""

    def test_normalize_title_basic(self):
        """测试基本标题规范化"""
        self.assertEqual(normalize_title("Hello World"), "helloworld")
        self.assertEqual(normalize_title("  Hello World  "), "helloworld")

    def test_normalize_title_remove_suffix(self):
        """测试去除数字后缀"""
        self.assertEqual(normalize_title("标题_0605005322"), "标题")
        self.assertEqual(normalize_title("标题_v2"), "标题")
        self.assertEqual(normalize_title("标题_1"), "标题")
        self.assertEqual(normalize_title("标题_20240101_v3"), "标题")

    def test_normalize_title_remove_punctuation(self):
        """测试去除标点符号"""
        self.assertEqual(normalize_title("标题-测试"), "标题测试")
        self.assertEqual(normalize_title("标题_测试"), "标题测试")
        self.assertEqual(normalize_title("标题！测试？"), "标题测试")
        self.assertEqual(normalize_title("标题（测试）"), "标题测试")

    def test_is_title_matched_exact(self):
        """测试精确匹配"""
        existing = {"标题测试", "另一个标题"}
        self.assertTrue(is_title_matched("标题测试", existing))
        self.assertTrue(is_title_matched("标题测试_0605005322", existing))
        self.assertFalse(is_title_matched("不匹配的标题", existing))

    def test_is_title_matched_substring(self):
        """测试子串匹配"""
        existing = {"关于Python的学习笔记"}
        self.assertTrue(is_title_matched("Python学习", existing))
        self.assertTrue(is_title_matched("学习笔记", existing))

    def test_is_title_matched_similarity(self):
        """测试相似度匹配"""
        existing = {"关于Python的学习笔记"}
        self.assertTrue(is_title_matched("关于Python学习笔记", existing))


class TestSortLinks(unittest.TestCase):
    """测试链接排序功能"""

    def test_sort_links_by_existing(self):
        """测试链接排序"""
        links = [
            ("1", "新标题A"),
            ("2", "已存在标题"),
            ("3", "新标题B"),
            ("4", "已存在标题_v2")
        ]
        existing = {"已存在标题"}

        sorted_links, matched_info = sort_links_by_existing_with_info(links, existing)
        
        self.assertEqual(len(sorted_links), 4)
        self.assertEqual(matched_info["2"], True)
        self.assertEqual(matched_info["4"], True)
        self.assertNotIn("1", matched_info)
        self.assertNotIn("3", matched_info)

        new_links = [lid for lid, _ in sorted_links if lid not in matched_info]
        matched_links = [lid for lid, _ in sorted_links if lid in matched_info]
        
        self.assertEqual(set(new_links), {"1", "3"})
        self.assertEqual(set(matched_links), {"2", "4"})


if __name__ == '__main__':
    unittest.main()
