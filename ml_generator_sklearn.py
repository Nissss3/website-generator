import pandas as pd
import joblib
import json
from generator_with_ml import MLWebsiteGenerator

class SklearnWebsiteGenerator(MLWebsiteGenerator):
    def __init__(self):
        print("Loading sklearn models...")
        
        # Load sklearn models
        self.site_type_model = joblib.load('models/site_type_classifier.pkl')
        self.style_model = joblib.load('models/style_classifier.pkl')
        self.component_selectors = joblib.load('models/component_selectors.pkl')
        self.label_encoders = joblib.load('models/label_encoders.pkl')
        
        with open('models/layout_templates.json') as f:
            self.layout_templates = json.load(f)
        
        print("✓ Models loaded!\n")
        
        # Component library
        self.components = {
            'navbar': self.generate_navbar,
            'hero': self.generate_hero,
            'features': self.generate_features,
            'footer': self.generate_footer,
            'pricing': self.generate_pricing,
            'testimonials': self.generate_testimonials,
            'contact': self.generate_contact
        }
    
    def generate_from_description(self, description):
        """Generate website using sklearn models"""
        print(f"Description: {description}\n")
        
        # Extract features from description
        features = self.extract_features(description)
        
        # Classify using sklearn
        site_type_idx = self.site_type_model.predict([features])[0]
        style_idx = self.style_model.predict([features])[0]
        
        site_type = self.label_encoders['site_type'].inverse_transform([site_type_idx])[0]
        style = self.label_encoders['style'].inverse_transform([style_idx])[0]
        
        # Get confidence
        site_type_proba = self.site_type_model.predict_proba([features])[0].max()
        
        print("=== ML Classification (sklearn) ===")
        print(f"Site Type: {site_type} (confidence: {site_type_proba:.2%})")
        print(f"Style: {style}")
        
        # Generate layout
        if site_type in self.layout_templates:
            sections = self.layout_templates[site_type][0]
        else:
            sections = ['navbar', 'hero', 'features', 'footer']
        
        print(f"Sections: {sections}\n")
        
        # Build DSL
        dsl = {
            'site_type': site_type,
            'style': style,
            'confidence': site_type_proba,
            'sections': []
        }
        
        for i, section_type in enumerate(sections):
            variant = self.select_variant_sklearn(site_type, style, section_type)
            
            dsl['sections'].append({
                'type': section_type,
                'position': i,
                'variant': variant
            })
        
        # Generate HTML
        html = self.dsl_to_html(dsl, description)
        
        return {'dsl': dsl, 'html': html}
    
    def extract_features(self, description):
        """Extract features from description"""
        desc_lower = description.lower()
        
        return [
            len(description.split()),  # num_components proxy
            len(description),  # title_length
            1,  # has_navbar (always)
            int('hero' in desc_lower or 'landing' in desc_lower),
            int('features' in desc_lower or 'services' in desc_lower),
            1,  # has_footer (always)
            int('pricing' in desc_lower or 'plans' in desc_lower),
            int('testimonial' in desc_lower or 'reviews' in desc_lower),
            int('contact' in desc_lower),
            1, 1, 1  # counts
        ]
    
    def select_variant_sklearn(self, site_type, style, component_type):
        """Select variant using sklearn model"""
        if component_type not in self.component_selectors:
            # Fallback defaults
            defaults = {
                'navbar': 'solid',
                'hero': 'centered_cta',
                'features': 'grid_3col',
                'footer': 'minimal'
            }
            return defaults.get(component_type, 'default')
        
        # Encode inputs
        site_type_enc = self.label_encoders['component_site_type'].transform([site_type])[0]
        style_enc = self.label_encoders['component_style'].transform([style])[0]
        
        # Features
        features = [site_type_enc, style_enc, 0, 1, 1]  # has_image, has_cta, position
        
        # Predict
        model = self.component_selectors[component_type]
        variant_idx = model.predict([features])[0]
        variant = self.label_encoders['variant'].inverse_transform([variant_idx])[0]
        
        return variant

if __name__ == "__main__":
    generator = SklearnWebsiteGenerator()
    
    tests = [
        "modern SaaS platform for team analytics with dashboard and pricing",
        "minimal portfolio website for photographer showcasing work",
        "ecommerce store for selling organic products"
    ]
    
    for i, desc in enumerate(tests, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}")
        print('='*60)
        
        result = generator.generate_from_description(desc)
        generator.save_website(result['html'], f'output/sklearn_website_{i}.html')

    print("\n✅ Done!")