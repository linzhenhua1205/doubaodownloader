import asyncio
import os
from urllib.parse import urlparse
import re
from playwright.async_api import async_playwright

OUTPUT_DIR = "cnblogs_articles_test"
TEST_URLS = [
    "https://www.cnblogs.com/ChenAI-TGF/p/20336781",
    "https://www.cnblogs.com/f20171110/p/20336719",
    "https://www.cnblogs.com/Yzu-EtherealYz/p/20334937",
]

def sanitize_filename(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    if not path:
        path = "index"
    filename = re.sub(r'[\\/*?:"<>|]', "_", path)
    return filename[:120] + ".mhtml"

async def download_one(url, output_dir, browser):
    page = await browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
    )
    try:
        print(f"  加载: {url}")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(2000)

        # 通过 CDP 保存 MHTML
        cdp = await page.context.new_cdp_session(page)
        result = await cdp.send("Page.captureSnapshot", {"format": "mhtml"})
        mhtml_data = result["data"]

        filename = sanitize_filename(url)
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(mhtml_data)

        size_kb = len(mhtml_data) / 1024
        print(f"  保存: {filename} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        print(f"  失败: {e}")
        return False
    finally:
        await page.close()

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
        )
        for url in TEST_URLS:
            await download_one(url, OUTPUT_DIR, browser)
        await browser.close()

    print(f"\n文件保存在: {os.path.abspath(OUTPUT_DIR)}")
    for f in os.listdir(OUTPUT_DIR):
        print(f"  {f}")

if __name__ == "__main__":
    asyncio.run(main())