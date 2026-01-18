import json
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

class LightweightMLScraper:
    def __init__(self):
        # Simple keyword-based "ML" (fast, no dependencies)
        self.site_type_keywords = {
            'saas_landing': ['saas', 'platform', 'software', 'analytics', 'dashboard', 'api', 'integration'],
            'portfolio': ['portfolio', 'work', 'projects', 'designer', 'photographer', 'creative'],
            'ecommerce': ['shop', 'store', 'cart', 'product', 'buy', 'checkout', 'price'],
            'blog': ['blog', 'article', 'post', 'read', 'news', 'story'],
            'restaurant': ['menu', 'food', 'dining', 'restaurant', 'order', 'delivery'],
            'corporate': ['about us', 'company', 'business', 'services', 'contact']
        }
        
        self.style_keywords = {
            'modern_gradient': ['gradient', 'modern', 'vibrant'],
            'minimal_clean': ['minimal', 'clean', 'simple', 'white'],
            'bold_colorful': ['bold', 'colorful', 'bright'],
            'dark_mode': ['dark', 'black', 'night'],
            'glassmorphism': ['glass', 'blur', 'transparent']
        }
        
    def scrape_site(self, url):
        print(f"Scraping: {url}")
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title').text if soup.find('title') else ""
            text = soup.get_text().lower()
            
            # Classify site type with confidence
            site_type = self.classify_with_confidence(text, self.site_type_keywords)
            
            # Detect style with confidence
            style = self.detect_style(soup)
            
            # Extract components
            components = self.extract_components(soup)
            
            dsl = self.generate_dsl(components, style)
            
            return {
                'url': url,
                'title': title,
                'site_type': site_type['label'],
                'site_type_confidence': site_type['confidence'],
                'style': style['label'],
                'style_confidence': style['confidence'],
                'components': components,
                'dsl': dsl
            }
            
        except Exception as e:
            print(f"  Error: {e}")
            return None
    
    def classify_with_confidence(self, text, keywords_dict):
        """Score-based classification with confidence"""
        scores = {}
        
        for category, keywords in keywords_dict.items():
            score = sum(text.count(keyword) for keyword in keywords)
            scores[category] = score
        
        total_score = sum(scores.values()) or 1
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category] / total_score
        
        # If confidence too low, default to 'other'
        if confidence < 0.2:
            return {'label': 'other', 'confidence': 0.5}
        
        return {
            'label': best_category,
            'confidence': min(confidence, 1.0)
        }
    
    def detect_style(self, soup):
        """Detect design style from HTML/CSS"""
        # Get all class names and styles
        classes = ' '.join([
            ' '.join(tag.get('class', [])) 
            for tag in soup.find_all(class_=True)
        ])
        
        styles = ' '.join([
            tag.get('style', '')
            for tag in soup.find_all(style=True)
        ])
        
        combined = (classes + ' ' + styles).lower()
        
        # Check for gradients
        has_gradient = 'gradient' in combined
        has_dark = any(word in combined for word in ['dark', 'black', '#000', '#111'])
        has_glass = any(word in combined for word in ['blur', 'glass', 'backdrop'])
        
        if has_gradient:
            return {'label': 'modern_gradient', 'confidence': 0.8}
        elif has_glass:
            return {'label': 'glassmorphism', 'confidence': 0.75}
        elif has_dark:
            return {'label': 'dark_mode', 'confidence': 0.85}
        else:
            # Count color-related terms
            color_terms = ['color', 'vibrant', 'bold', 'bright']
            color_count = sum(1 for term in color_terms if term in combined)
            
            if color_count > 2:
                return {'label': 'bold_colorful', 'confidence': 0.7}
            else:
                return {'label': 'minimal_clean', 'confidence': 0.6}
    
    def extract_components(self, soup):
        """Extract components with confidence scores"""
        components = []
        
        # Navbar
        nav = soup.find(['nav', 'header'])
        if nav:
            components.append({
                'type': 'navbar',
                'position': 0,
                'confidence': 0.95,
                'has_logo': nav.find('img') is not None,
                'num_links': len(nav.find_all('a'))
            })
        
        # Hero
        hero_candidates = soup.find_all(['section', 'div'], limit=5)
        for section in hero_candidates:
            text = section.get_text(strip=True)
            if 50 < len(text) < 500:
                has_cta = section.find(['button', 'a'], class_=lambda x: x and 'btn' in str(x).lower())
                components.append({
                    'type': 'hero',
                    'position': len(components),
                    'confidence': 0.85,
                    'has_image': section.find('img') is not None,
                    'has_cta': has_cta is not None
                })
                break
        
        # Features
        feature_sections = soup.find_all(['section', 'div'], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ['feature', 'benefit', 'service']
        ))
        if feature_sections:
            components.append({
                'type': 'features',
                'position': len(components),
                'confidence': 0.8,
                'num_items': len(feature_sections[0].find_all(['div', 'article'], recursive=False))
            })
        
        # Footer
        footer = soup.find('footer')
        if footer:
            components.append({
                'type': 'footer',
                'position': len(components),
                'confidence': 0.9,
                'has_links': len(footer.find_all('a')) > 0
            })
        
        return components
    
    def generate_dsl(self, components, style):
        return {
            'layout': 'single_page',
            'style': style['label'],
            'style_confidence': style['confidence'],
            'sections': [
                {
                    'type': c['type'],
                    'position': c['position'],
                    'confidence': c['confidence'],
                    'props': {k: v for k, v in c.items() if k not in ['type', 'position', 'confidence']}
                }
                for c in components
            ]
        }
    
    def scrape_batch(self, urls, output_file='output/training_data_ml.json'):
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
    
    print(f"Found {len(urls)} URLs to scrape\n")
    
    scraper = LightweightMLScraper()
    scraper.scrape_batch(urls[:150])