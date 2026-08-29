import os
import sys
import time

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError as e:
    print(f"错误: 无法导入selenium模块 - {e}")
    sys.exit(1)

CHROME_PATH = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
EXTENSION_PATH = r"h:\github\md\dssxz"

def main():
    print("测试Chrome启动（带插件）...")
    
    if not os.path.exists(CHROME_PATH):
        print(f"错误: Chrome路径不存在: {CHROME_PATH}")
        return
    
    if not os.path.exists(EXTENSION_PATH):
        print(f"错误: 插件目录不存在: {EXTENSION_PATH}")
        return
    
    user_data_dir = r"h:\github\md\chrome_profile_test"
    os.makedirs(user_data_dir, exist_ok=True)
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.binary_location = CHROME_PATH
    options.add_argument(f"--load-extension={EXTENSION_PATH}")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✓ Chrome启动成功")
        
        driver.get("https://www.doubao.com/chat/")
        print("✓ 页面加载成功")
        
        time.sleep(5)
        
        result = driver.execute_script("""
            var info = {
                __doubao: !!window.__doubao,
                _doubaoInstance: !!window._doubaoInstance,
                hasToggleBatchMode: typeof window.__doubao?.toggleBatchMode === 'function' || 
                                    typeof window._doubaoInstance?.toggleBatchMode === 'function'
            };
            return info;
        """)
        
        print(f"\n插件API检测结果:")
        print(f"  window.__doubao: {result.get('__doubao', 'N/A')}")
        print(f"  window._doubaoInstance: {result.get('_doubaoInstance', 'N/A')}")
        print(f"  有toggleBatchMode函数: {result.get('hasToggleBatchMode', 'N/A')}")
        
        input("\n按 Enter 关闭浏览器...")
        driver.quit()
        
    except Exception as e:
        print(f"✗ 启动失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()