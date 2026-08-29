import zipfile
import os
import shutil

def unzip_chromedriver():
    zip_path = 'h:/github/md/chrome-win64.zip'
    
    if not os.path.exists(zip_path):
        print(f"错误: 文件不存在 {zip_path}")
        return
    
    print(f"正在解压: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('h:/github/md/chromedriver_temp')
    
    print("解压完成，查找chromedriver.exe...")
    
    for root, dirs, files in os.walk('h:/github/md/chromedriver_temp'):
        for file in files:
            if file == 'chromedriver.exe':
                src_path = os.path.join(root, file)
                dest_path = 'h:/github/md/chromedriver.exe'
                
                shutil.copy(src_path, dest_path)
                print(f"已复制 chromedriver.exe 到: {dest_path}")
                
                shutil.rmtree('h:/github/md/chromedriver_temp')
                print("清理临时文件完成")
                return
    
    print("警告: 未找到 chromedriver.exe")
    shutil.rmtree('h:/github/md/chromedriver_temp')

if __name__ == "__main__":
    unzip_chromedriver()