import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://web1.karlsruhe.de/service/Buergerdienste/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

def get_service_links(main_url):
    res = requests.get(main_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    services = []

    for item in soup.select("a.website-link"):
        title = item.text.strip()
        href = item.get("href")
        url = BASE_URL + href if href.startswith("leistung.php") else href
        short_desc = item.find_next("div", class_="link-info").text.strip() if item.find_next("div", class_="link-info") else ""
        services.append((title, url, short_desc))

    return services

def scrape_details_page(url):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    content_blocks = soup.select("div.text-extern p")
    main_text = "\n".join([p.get_text(strip=True) for p in content_blocks])

    details_data = []
    for block in soup.select("details"):
        section_title = block.select_one("summary")
        section_body = block.select_one("div.detail-contents")
        if section_title and section_body:
            name = section_title.get_text(strip=True)
            content = section_body.get_text(separator="\n", strip=True)
            details_data.append(f"\n\n## {name}\n{content}")

    full_text = main_text + "\n".join(details_data)
    return full_text.strip()

def main():
    main_url = BASE_URL + "leistungen_gesamt.php"
    services = get_service_links(main_url)

    with open("karlsruhe_rag_full.csv", mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "url", "short_description", "full_text"])

        for title, url, desc in services:
            print(f"🔍 {title}")
            try:
                full_text = scrape_details_page(url)
                writer.writerow([title, url, desc, full_text])
                time.sleep(1)
            except Exception as e:
                print(f"❌ Error in parsing {url}: {e}")

if __name__ == "__main__":
    main()
