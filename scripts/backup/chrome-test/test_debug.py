import requests
import json

# 测试基本的请求功能
def test_request():
    url = "https://www.doubao.com/api/thread/list?cursor=&limit=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Cookie": "",  # 空Cookie测试
        "Referer": "https://www.doubao.com/chat"
    }
    
    print(f"测试URL: {url}")
    print(f"请求头: {json.dumps(headers, indent=2)}")
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"\n响应状态码: {r.status_code}")
        print(f"响应头: {json.dumps(dict(r.headers), indent=2)}")
        print(f"响应内容长度: {len(r.content)} bytes")
        
        if r.content:
            try:
                data = r.json()
                print(f"响应JSON: {json.dumps(data, indent=2)[:1000]}...")
            except json.JSONDecodeError:
                print(f"响应内容(前500字符): {r.text[:500]}")
                
    except Exception as e:
        print(f"请求异常: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    print("="*60)
    print("          测试调试功能")
    print("="*60)
    test_request()
