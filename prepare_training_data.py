import json
import pandas as pd
from sklearn.model_selection import train_test_split
import os

class SklearnDataPreparator:
    def __init__(self, input_file='output/training_data_ml.json'):
        with open(input_file) as f:
            self.raw_data = json.load(f)
        
        print(f"Loaded {len(self.raw_data)} scraped websites")
    
    def prepare_classifier_data(self):
        """Prepare data for site type + style classifier"""
        data = []
        
        for site in self.raw_data:
            # Count component types
            component_counts = {
                'navbar': 0, 'hero': 0, 'features': 0, 
                'footer': 0, 'pricing': 0, 'testimonials': 0, 'contact': 0
            }
            
            for comp in site.get('components', []):
                comp_type = comp['type']
                if comp_type in component_counts:
                    component_counts[comp_type] += 1
            
            # Create features
            features = {
                'num_components': len(site.get('components', [])),
                'title_length': len(site.get('title', '')),
                'has_navbar': component_counts['navbar'] > 0,
                'has_hero': component_counts['hero'] > 0,
                'has_features': component_counts['features'] > 0,
                'has_footer': component_counts['footer'] > 0,
                'has_pricing': component_counts['pricing'] > 0,
                'has_testimonials': component_counts['testimonials'] > 0,
                'has_contact': component_counts['contact'] > 0,
                'navbar_count': component_counts['navbar'],
                'hero_count': component_counts['hero'],
                'features_count': component_counts['features']
            }
            
            # Labels
            labels = {
                'site_type': site.get('site_type', 'other'),
                'style': site.get('style', 'minimal_clean')
            }
            
            data.append({**features, **labels})
        
        df = pd.DataFrame(data)
        
        # Convert boolean to int
        bool_cols = ['has_navbar', 'has_hero', 'has_features', 'has_footer', 
                     'has_pricing', 'has_testimonials', 'has_contact']
        for col in bool_cols:
            df[col] = df[col].astype(int)
        
        # Save
        os.makedirs('training', exist_ok=True)
        df.to_csv('training/classifier_data.csv', index=False)
        print(f"✓ Saved classifier training data: {len(df)} examples")
        
        return df
    
    def prepare_layout_generator_data(self):
        """Prepare layout sequence data"""
        data = []
        
        for site in self.raw_data:
            sections = [c['type'] for c in site.get('components', [])]
            
            data.append({
                'site_type': site.get('site_type', 'other'),
                'style': site.get('style', 'minimal_clean'),
                'sections': ','.join(sections),
                'num_sections': len(sections)
            })
        
        df = pd.DataFrame(data)
        df.to_csv('training/layout_generator_data.csv', index=False)
        print(f"✓ Saved layout generator data: {len(df)} examples")
        
        return df
    
    def prepare_component_selector_data(self):
        """Prepare component variant data"""
        data = []
        
        for site in self.raw_data:
            site_type = site.get('site_type', 'other')
            style = site.get('style', 'minimal_clean')
            
            for component in site.get('components', []):
                comp_type = component['type']
                variant = self.infer_variant(component, style)
                
                features = {
                    'site_type': site_type,
                    'style': style,
                    'component_type': comp_type,
                    'has_image': int(component.get('has_image', False)),
                    'has_cta': int(component.get('has_cta', False)),
                    'position': component.get('position', 0),
                    'confidence': component.get('confidence', 0.5),
                    'variant': variant
                }
                
                data.append(features)
        
        df = pd.DataFrame(data)
        df.to_csv('training/component_selector_data.csv', index=False)
        print(f"✓ Saved component selector data: {len(df)} examples")
        
        return df
    
    def infer_variant(self, component, style):
        """Infer component variant"""
        comp_type = component['type']
        
        if comp_type == 'navbar':
            return 'transparent' if style == 'modern_gradient' else 'solid'
        elif comp_type == 'hero':
            if component.get('has_image'):
                return 'split_screen_with_image'
            elif component.get('has_cta'):
                return 'centered_cta'
            else:
                return 'minimal_text'
        elif comp_type == 'features':
            num_items = component.get('num_items', 3)
            return 'grid_4col' if num_items >= 4 else 'grid_3col'
        elif comp_type == 'footer':
            return 'detailed' if component.get('has_links') else 'minimal'
        else:
            return 'default'
    
    def prepare_all(self):
        """Prepare all datasets"""
        print("\n=== Preparing Training Data ===\n")
        
        classifier_df = self.prepare_classifier_data()
        layout_df = self.prepare_layout_generator_data()
        component_df = self.prepare_component_selector_data()
        
        # Statistics
        print("\n=== Dataset Statistics ===")
        print(f"\nSite Types:")
        print(classifier_df['site_type'].value_counts())
        print(f"\nStyles:")
        print(classifier_df['style'].value_counts())
        print(f"\nComponent Types:")
        print(component_df['component_type'].value_counts())
        
        return classifier_df, layout_df, component_df

if __name__ == "__main__":
    preparator = SklearnDataPreparator()
    preparator.prepare_all()