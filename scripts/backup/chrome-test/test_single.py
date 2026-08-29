"""测试单个页面下载"""
import os
from download_mhtml import create_driver, download_one_page

TEST_URL = "https://www.cnblogs.com/ChenAI-TGF/p/20336781"
TEST_DIR = "test_output"

os.makedirs(TEST_DIR, exist_ok=True)

print(f"测试下载: {TEST_URL}")
driver = create_driver()
try:
    ok, info = download_one_page(driver, TEST_URL, TEST_DIR)
    print(f"结果: {'成功' if ok else '失败'} - {info}")
    if ok:
        print(f"查看文件: {os.path.abspath(TEST_DIR)}")
finally:
    driver.quit()