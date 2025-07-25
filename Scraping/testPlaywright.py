from playwright.sync_api import sync_playwright, TimeoutError

def scrape_qcckyc(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        print(f"Opening: {url}")
        page.goto(url, timeout=30000)
        
        try:
            page.wait_for_selector("div.enterprise-baseinfo", timeout=10000)
        except TimeoutError:
            print("❌ Timeout: Content didn't load properly.")
            page.screenshot(path="error_screenshot.png")
            browser.close()
            return {}
        
        data = {}
        try:
            rows = page.query_selector_all("div.info-item")
            for row in rows:
                key = row.query_selector("div.item-label").inner_text().strip()
                value = row.query_selector("div.item-value").inner_text().strip()
                data[key] = value
        except Exception as e:
            print("Failed to extract data:", e)

        browser.close()
        return data

# Example usage:
url = "https://www.qcckyc.com/enterprise-details?token=QCN7ED9K97-1753325330427-35b424531c8d58a008807c5a4c336964"
result = scrape_qcckyc(url)
print(result)