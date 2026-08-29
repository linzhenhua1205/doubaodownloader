import os
import requests
import zipfile
import shutil

def download_chromedriver():
    chrome_version = "148.0.7778.168"
    
    mirrors = [
        f"https://npm.taobao.org/mirrors/chromedriver/{chrome_version}/chromedriver_win32.zip",
        f"https://mirrors.huaweicloud.com/chromedriver/{chrome_version}/chromedriver_win32.zip",
        f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/win64/chromedriver-win64.zip"
    ]
    
    print(f"检测到Chrome版本: {chrome_version}")
    print("正在尝试从国内镜像下载ChromeDriver...")
    
    for idx, url in enumerate(mirrors, 1):
        print(f"\n尝试第 {idx} 个源: {url}")
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            zip_path = "chromedriver.zip"
            with open(zip_path, "wb") as f:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end="")
            
            print("\n下载完成，正在解压...")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            if os.path.exists("chromedriver-win64"):
                shutil.move("chromedriver-win64/chromedriver.exe", "chromedriver.exe")
                shutil.rmtree("chromedriver-win64")
            elif os.path.exists("chromedriver.exe"):
                pass
            else:
                files = zip_ref.namelist()
                for f in files:
                    if f.endswith("chromedriver.exe"):
                        shutil.move(f, "chromedriver.exe")
            
            os.remove(zip_path)
            
            print("✅ ChromeDriver配置完成！")
            print(f"路径: {os.path.abspath('chromedriver.exe')}")
            
            return os.path.abspath("chromedriver.exe")
        
        except requests.exceptions.RequestException as e:
            print(f"❌ 下载失败: {e}")
            continue
    
    print("\n❌ 所有镜像源都无法下载，请手动下载")
    print("下载地址：https://googlechromelabs.github.io/chrome-for-testing/")
    print(f"选择版本: {chrome_version} → win64 → chromedriver-win64.zip")
    return None

if __name__ == "__main__":
    download_chromedriver()