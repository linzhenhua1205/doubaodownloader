import zipfile

with zipfile.ZipFile('h:/github/md/chrome-win64.zip', 'r') as zip_ref:
    print("ZIP文件内容:")
    for name in zip_ref.namelist()[:20]:
        print(f"  {name}")
    print(f"... 共 {len(zip_ref.namelist())} 个文件")