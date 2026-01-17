import json
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import torch

class MLWebsiteScraper:
    def __init__(self):
        print("Loading ML models...")
        
        # Model 1: Zero-shot classifier for site type
        self.site_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Model 2: Text classifier for components
        self.text_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        print("✓ ML models loaded!\n")
        
    def scrape_site(self, url):
        """Scrape one website using ML"""
        print(f"Scraping: {url}")
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title').text if soup.find('title') else ""
            
            # ML-based site type detection
            site_type = self.detect_site_type_ml(soup, title)
            
            # ML-based style detection
            style = self.detect_style_ml(soup)
            
            # ML-based component extraction
            components = self.extract_components_ml(soup)
            
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
    
    def detect_site_type_ml(self, soup, title):
        """Use ML to classify site type"""
        # Get text content
        text = title + ' ' + soup.get_text()[:1000]  # First 1000 chars
        
        # Classify with ML
        result = self.site_classifier(
            text,
            candidate_labels=[
                "saas landing page",
                "portfolio website",
                "ecommerce store",
                "corporate business website",
                "blog or news site",
                "restaurant or food website",
                "creative agency website",
                "app showcase"
            ],
            multi_label=False
        )
        
        return {
            'label': result['labels'][0].replace(' ', '_'),
            'confidence': result['scores'][0]
        }
    
    def detect_style_ml(self, soup):
        """Detect visual style using ML"""
        # Extract style indicators from HTML
        classes = ' '.join([
            ' '.join(tag.get('class', [])) 
            for tag in soup.find_all(class_=True)
        ])[:500]
        
        # Look at meta description
        meta = soup.find('meta', {'name': 'description'})
        description = meta['content'] if meta else ""
        
        style_text = classes + ' ' + description
        
        # Classify style
        result = self.text_classifier(
            style_text,
            candidate_labels=[
                "modern gradient design",
                "minimal clean design",
                "bold colorful design",
                "dark mode theme",
                "glassmorphism style",
                "brutalist design",
                "classic professional"
            ],
            multi_label=False
        )
        
        return {
            'label': result['labels'][0].replace(' ', '_'),
            'confidence': result['scores'][0]
        }
    
    def extract_components_ml(self, soup):
        """Extract components using ML classification"""
        components = []
        
        # Find all potential sections
        all_sections = soup.find_all(['nav', 'header', 'section', 'div', 'footer'], limit=20)
        
        for i, section in enumerate(all_sections):
            # Get section text
            text = section.get_text(strip=True)[:300]
            
            if len(text) < 20:  # Skip if too short
                continue
            
            # Get HTML structure hints
            tag_name = section.name
            classes = ' '.join(section.get('class', []))
            
            # Combine for classification
            context = f"{tag_name} {classes} {text}"
            
            # Classify component type with ML
            result = self.text_classifier(
                context,
                candidate_labels=[
                    "navigation bar",
                    "hero section",
                    "features section",
                    "pricing section",
                    "testimonials section",
                    "gallery or portfolio",
                    "contact form",
                    "footer",
                    "call to action",
                    "content block"
                ],
                multi_label=False
            )
            
            # Only include if confidence is high enough
            if result['scores'][0] > 0.3:
                component_type = result['labels'][0].replace(' ', '_')
                
                components.append({
                    'type': component_type,
                    'position': len(components),
                    'confidence': result['scores'][0],
                    'has_image': section.find('img') is not None,
                    'has_cta': section.find(['button', 'a']) is not None,
                    'text_length': len(text)
                })
        
        return components
    
    def generate_dsl(self, components, style):
        """Generate DSL with ML-detected info"""
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
        """Scrape multiple URLs with ML"""
        results = []
        
        for i, url in enumerate(urls):
            print(f"\n[{i+1}/{len(urls)}]")
            data = self.scrape_site(url)
            
            if data:
                results.append(data)
                
                if len(results) % 5 == 0:
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
    
    scraper = MLWebsiteScraper()
    scraper.scrape_batch(urls[:150])  # Start with 10