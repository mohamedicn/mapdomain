import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from datetime import datetime
from xml.dom import minidom
import sys
from art import text2art

def main():
    banner = text2art("Map Domain")
    print(banner)
    print("# Coded By Mohamed - @mohamedicn\n")
    print("# Visit us - https://icneg.com\n")

    print('1 - Crawling All URL ')
    print('2 - Create Sidemap ')
    x= int(input('Enter Number Of Your Service :'))

    if x==1:
        def get_subdomains(domain):
            """Fetch subdomains from crt.sh."""
            url = f"https://crt.sh/?q=%25.{domain}&output=json"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    subdomains = set()
                    for entry in data:
                        name_value = entry.get("name_value", "")
                        subdomains.update(name_value.split("\n"))
                    return sorted(subdomains)
                else:
                    print(f"Error fetching data: {response.status_code}")
                    return []
            except Exception as e:
                print(f"An error occurred: {e}")
                return []
        def crawl_url(url, visited, domain, total_count):
            """Recursively crawl a URL to find all links."""
            if url in visited:
                return total_count
            visited.add(url)
            total_count += 1
            progress = int((len(visited) / total_count) * 100)
            sys.stdout.write(f"\rProgress: {progress}% - Pages Found: {len(visited)}")
            sys.stdout.flush()
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link["href"].strip()
                        # Normalize and resolve relative URLs
                        full_url = urljoin(url, href)
                        parsed_url = urlparse(full_url)
                        if domain in parsed_url.netloc and full_url not in visited:
                            total_count = crawl_url(full_url, visited, domain, total_count)
            except Exception as e:
                print(f"\nError crawling {url}: {e}")
            return total_count
        def get_all_links(domain):
            """Get all links including subdomains and paths."""
            subdomains = get_subdomains(domain)
            print("\nDiscovered Subdomains:")
            for subdomain in subdomains:
                print(subdomain)
            visited = set()
            total_count = 1  # Start with the main domain as the first page
            for subdomain in subdomains:
                url = f"https://{subdomain}"
                print(f"\nCrawling {url}...")
                total_count = crawl_url(url, visited, domain, total_count)
            return visited
        if __name__ == "__main__":
            domain = input("Enter the domain (e.g., icneg.com): ").strip()
            all_links = get_all_links(domain)
            print("\n\nAll Discovered URLs:")
            for link in sorted(all_links):
                print(link)
    else:
        def crawl_website(base_url):
            """
            Crawl a website and discover all unique paths, tracking failed URLs.
            """
            visited = set()
            to_visit = {base_url}
            total_urls = 1  # Assume at least the base URL
            failed_urls = []
            discovered_count = 0
            while to_visit:
                current_url = to_visit.pop()
                if current_url in visited:
                    continue
                visited.add(current_url)
                discovered_count += 1
                try:
                    response = requests.get(current_url)
                    response.raise_for_status()
                except requests.RequestException:
                    failed_urls.append(current_url)
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href'].strip()  # Remove any leading/trailing whitespace
                    full_url = urljoin(base_url, href)
                    parsed_url = urlparse(full_url)
                    # Only add URLs that belong to the same domain
                    if parsed_url.netloc == urlparse(base_url).netloc and full_url not in visited:
                        to_visit.add(full_url)
                        total_urls += 1
                # Update progress
                progress = min(100, int((discovered_count / total_urls) * 100))
                sys.stdout.write(f"\rProgress: {progress}% - Pages Found: {len(visited)}")
                sys.stdout.flush()
            print("\nCrawling completed.")
            # Convert full URLs to relative paths for the sitemap
            paths = {urlparse(url).path for url in visited}
            return paths, failed_urls
        def generate_sitemap(base_url, paths, output_file):
            """
            Generate a formatted sitemap.xml for a website.
            """
            urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
            for path in paths:
                # Avoid trailing spaces in <loc> content
                url_element = ET.SubElement(urlset, "url")
                loc = ET.SubElement(url_element, "loc")
                loc.text = f"{base_url.rstrip('/')}{path.strip()}"
                
                lastmod = ET.SubElement(url_element, "lastmod")
                lastmod.text = datetime.now().strftime("%Y-%m-%d")
                
                changefreq = ET.SubElement(url_element, "changefreq")
                changefreq.text = "daily"
                
                priority = ET.SubElement(url_element, "priority")
                priority.text = "1.00"
            # Convert the ElementTree to a string and prettify it
            rough_string = ET.tostring(urlset, encoding="utf-8", method="xml")
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="    ")
            # Save to file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(pretty_xml)
            print(f"Sitemap has been generated and saved as '{output_file}'")
        if __name__ == "__main__":
            # Prompt user for the base URL
            base_url = input("Enter the base URL of the website (e.g., https://icneg.com): ").strip()
            
            print("Crawling website to discover paths...")
            paths, failed_urls = crawl_website(base_url)
            print(f"\nDiscovered {len(paths)} unique paths.")
            
            # Output sitemap file
            output_file = "sitemap.xml"
            generate_sitemap(base_url, paths, output_file)
            # Print failed URLs
            if failed_urls:
                print("\nFailed to fetch the following URLs:")
                for url in failed_urls:
                    print(url)

if __name__ == "__main__":
    main()