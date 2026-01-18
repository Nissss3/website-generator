import json
import os

class SimpleMLModels:
    """Rule-based models using frequency analysis (no sklearn needed)"""
    
    def __init__(self):
        self.load_training_data()
    
    def load_training_data(self):
        """Load prepared training data"""
        with open('training/classifier_data.json') as f:
            self.classifier_data = json.load(f)
        
        with open('training/layout_templates.json') as f:
            self.layout_templates = json.load(f)
        
        with open('training/component_variants.json') as f:
            self.component_variants = json.load(f)
        
        print("✓ Loaded training data")
    
    def classify_site(self, features):
        """Classify site type and style based on features"""
        # Score each site type based on similarity
        scores = {}
        
        for example in self.classifier_data:
            site_type = example['site_type']
            
            # Calculate similarity
            similarity = 0
            if features.get('has_navbar') == example['has_navbar']:
                similarity += 1
            if features.get('has_hero') == example['has_hero']:
                similarity += 1
            if features.get('has_features') == example['has_features']:
                similarity += 1
            if features.get('has_footer') == example['has_footer']:
                similarity += 1
            
            scores[site_type] = scores.get(site_type, 0) + similarity
        
        # Most common site type
        best_site_type = max(scores.items(), key=lambda x: x[1])[0]
        
        # Get most common style for this site type
        styles = {}
        for example in self.classifier_data:
            if example['site_type'] == best_site_type:
                style = example['style']
                styles[style] = styles.get(style, 0) + 1
        
        best_style = max(styles.items(), key=lambda x: x[1])[0] if styles else 'minimal_clean'
        
        return {
            'site_type': best_site_type,
            'style': best_style,
            'confidence': scores[best_site_type] / sum(scores.values())
        }
    
    def generate_layout(self, site_type, style):
        """Generate layout sections for site type"""
        if site_type in self.layout_templates:
            # Return most common layout
            return self.layout_templates[site_type][0]
        else:
            # Default layout
            return ['navbar', 'hero', 'features', 'footer']
    
    def select_variant(self, site_type, style, component_type):
        """Select variant for component"""
        key = f"{site_type}_{style}_{component_type}"
        
        if key in self.component_variants:
            return self.component_variants[key]
        else:
            # Default variants
            defaults = {
                'navbar': 'solid',
                'hero': 'centered_cta',
                'features': 'grid_3col',
                'footer': 'minimal'
            }
            return defaults.get(component_type, 'default')
    
    def generate_complete_dsl(self, user_description):
        """Generate complete DSL from user description"""
        # Extract features from description
        desc_lower = user_description.lower()
        features = {
            'has_navbar': True,  # Always assume navbar
            'has_hero': any(word in desc_lower for word in ['hero', 'landing', 'main']),
            'has_features': any(word in desc_lower for word in ['features', 'services', 'benefits']),
            'has_footer': True  # Always assume footer
        }
        
        # Classify
        classification = self.classify_site(features)
        
        # Generate layout
        sections = self.generate_layout(classification['site_type'], classification['style'])
        
        # Build DSL
        dsl = {
            'site_type': classification['site_type'],
            'style': classification['style'],
            'confidence': classification['confidence'],
            'sections': []
        }
        
        for i, section_type in enumerate(sections):
            variant = self.select_variant(
                classification['site_type'],
                classification['style'],
                section_type
            )
            
            dsl['sections'].append({
                'type': section_type,
                'position': i,
                'variant': variant
            })
        
        return dsl
    
    def save_models(self):
        """Save models"""
        os.makedirs('models', exist_ok=True)
        
        with open('models/simple_ml_models.json', 'w') as f:
            json.dump({
                'layout_templates': self.layout_templates,
                'component_variants': self.component_variants
            }, f, indent=2)
        
        print("✓ Models saved to models/simple_ml_models.json")

if __name__ == "__main__":
    # Test the models
    models = SimpleMLModels()
    
    # Test classification
    test_desc = "modern SaaS platform for analytics with dashboard and pricing"
    result = models.generate_complete_dsl(test_desc)
    
    print("\n=== Test Generation ===")
    print(f"Input: {test_desc}")
    print(f"\nGenerated DSL:")
    print(json.dumps(result, indent=2))
    
    # Save models
    models.save_models()