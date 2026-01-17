import json
import requests
from bs4 import BeautifulSoup

class SimpleWebsiteScraper:
    def __init__(self):
        pass
        
    def scrape_site(self, url):
        """Scrape one website and extract layout data"""
        print(f"Scraping: {url}")
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title').text if soup.find('title') else ""
            site_type = self.detect_site_type(soup, title)
            components = self.extract_components(soup)
            dsl = self.generate_dsl(components)
            
            return {
                'url': url,
                'title': title,
                'site_type': site_type,
                'components': components,
                'dsl': dsl
            }
            
        except Exception as e:
            print(f"  Error: {e}")
            return None
    
    def detect_site_type(self, soup, title):
        text = (title + ' ' + soup.get_text()).lower()
        
        if any(word in text for word in ['saas', 'software', 'platform', 'analytics']):
            return 'saas_landing'
        elif any(word in text for word in ['portfolio', 'designer', 'photographer', 'work']):
            return 'portfolio'
        elif any(word in text for word in ['shop', 'store', 'buy', 'cart', 'product']):
            return 'ecommerce'
        elif any(word in text for word in ['blog', 'article', 'post']):
            return 'blog'
        elif any(word in text for word in ['restaurant', 'menu', 'food', 'dining']):
            return 'restaurant'
        else:
            return 'corporate'
    
    def extract_components(self, soup):
        components = []
        
        nav = soup.find(['nav', 'header'])
        if nav:
            components.append({
                'type': 'navbar',
                'position': 0,
                'has_logo': nav.find('img') is not None,
                'num_links': len(nav.find_all('a'))
            })
        
        hero_candidates = soup.find_all(['section', 'div'], limit=5)
        for section in hero_candidates:
            text = section.get_text(strip=True)
            if len(text) > 50 and len(text) < 500:
                has_cta = section.find(['button', 'a'], class_=lambda x: x and 'btn' in str(x).lower())
                components.append({
                    'type': 'hero',
                    'position': len(components),
                    'has_image': section.find('img') is not None,
                    'has_cta': has_cta is not None,
                    'text_length': len(text)
                })
                break
        
        sections = soup.find_all(['section', 'div'], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ['feature', 'benefit', 'service']
        ))
        if sections:
            components.append({
                'type': 'features',
                'position': len(components),
                'num_items': len(sections[0].find_all(['div', 'article'], recursive=False))
            })
        
        footer = soup.find('footer')
        if footer:
            components.append({
                'type': 'footer',
                'position': len(components),
                'has_links': len(footer.find_all('a')) > 0
            })
        
        return components
    
    def generate_dsl(self, components):
        return {
            'layout': 'single_page',
            'sections': [
                {
                    'type': c['type'],
                    'position': c['position'],
                    'props': {k: v for k, v in c.items() if k not in ['type', 'position']}
                }
                for c in components
            ]
        }
    
    def scrape_batch(self, urls, output_file='output/training_data.json'):
        results = []
        
        for i, url in enumerate(urls):
            print(f"\n[{i+1}/{len(urls)}]")
            data = self.scrape_site(url)
            
            if data:
                results.append(data)
                
                if len(results) % 10 == 0:
                    self.save_results(results, output_file)
                    print(f"  ✓ Saved {len(results)} sites")
        
        self.save_results(results, output_file)
        print(f"\n✅ Complete! Scraped {len(results)}/{len(urls)} sites")
        return results
    
    def save_results(self, results, filename):
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    try:
        with open('seed_urls.txt') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print("Error: seed_urls.txt not found!")
        exit(1)
    
    print(f"Found {len(urls)} URLs to scrape")
    scraper = SimpleWebsiteScraper()
    scraper.scrape_batch(urls[:100])