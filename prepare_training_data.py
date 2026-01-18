import json
import os

class SimpleTrainingDataPreparator:
    def __init__(self, input_file='output/training_data_ml.json'):
        with open(input_file) as f:
            self.raw_data = json.load(f)
        
        print(f"Loaded {len(self.raw_data)} scraped websites")
    
    def prepare_all(self):
        """Prepare all training data as JSON (no pandas/sklearn)"""
        os.makedirs('training', exist_ok=True)
        
        print("\n=== Preparing Training Data ===\n")
        
        # 1. Classifier data
        classifier_data = []
        for site in self.raw_data:
            classifier_data.append({
                'title': site.get('title', ''),
                'num_components': len(site.get('components', [])),
                'has_navbar': any(c['type'] == 'navbar' for c in site.get('components', [])),
                'has_hero': any(c['type'] == 'hero' for c in site.get('components', [])),
                'has_features': any(c['type'] == 'features' for c in site.get('components', [])),
                'has_footer': any(c['type'] == 'footer' for c in site.get('components', [])),
                'site_type': site.get('site_type', 'other'),
                'style': site.get('style', 'minimal_clean')
            })
        
        with open('training/classifier_data.json', 'w') as f:
            json.dump(classifier_data, f, indent=2)
        print(f"✓ Saved classifier data: {len(classifier_data)} examples")
        
        # 2. Layout generator data
        layout_data = {}
        for site in self.raw_data:
            site_type = site.get('site_type', 'other')
            sections = [c['type'] for c in site.get('components', [])]
            section_key = ','.join(sections)
            
            if site_type not in layout_data:
                layout_data[site_type] = {}
            
            if section_key not in layout_data[site_type]:
                layout_data[site_type][section_key] = 0
            
            layout_data[site_type][section_key] += 1
        
        # Find most common layout for each site type
        templates = {}
        for site_type, layouts in layout_data.items():
            sorted_layouts = sorted(layouts.items(), key=lambda x: x[1], reverse=True)
            templates[site_type] = [layout.split(',') for layout, count in sorted_layouts[:3]]
        
        with open('training/layout_templates.json', 'w') as f:
            json.dump(templates, f, indent=2)
        print(f"✓ Saved layout templates: {len(templates)} site types")
        
        # 3. Component selector data
        component_data = {}
        for site in self.raw_data:
            site_type = site.get('site_type', 'other')
            style = site.get('style', 'minimal_clean')
            
            for comp in site.get('components', []):
                comp_type = comp['type']
                variant = self.infer_variant(comp, style)
                
                key = f"{site_type}_{style}_{comp_type}"
                
                if key not in component_data:
                    component_data[key] = {}
                
                if variant not in component_data[key]:
                    component_data[key][variant] = 0
                
                component_data[key][variant] += 1
        
        # Pick most common variant for each combination
        variant_rules = {}
        for key, variants in component_data.items():
            most_common = max(variants.items(), key=lambda x: x[1])[0]
            variant_rules[key] = most_common
        
        with open('training/component_variants.json', 'w') as f:
            json.dump(variant_rules, f, indent=2)
        print(f"✓ Saved component variants: {len(variant_rules)} rules")
        
        # Print statistics
        print("\n=== Dataset Statistics ===")
        
        site_types = {}
        styles = {}
        components = {}
        
        for site in self.raw_data:
            st = site.get('site_type', 'other')
            site_types[st] = site_types.get(st, 0) + 1
            
            style = site.get('style', 'minimal_clean')
            styles[style] = styles.get(style, 0) + 1
            
            for comp in site.get('components', []):
                ct = comp['type']
                components[ct] = components.get(ct, 0) + 1
        
        print(f"\nSite Types:")
        for st, count in sorted(site_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {st}: {count}")
        
        print(f"\nStyles:")
        for style, count in sorted(styles.items(), key=lambda x: x[1], reverse=True):
            print(f"  {style}: {count}")
        
        print(f"\nComponent Types:")
        for ct, count in sorted(components.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ct}: {count}")
        
        return classifier_data, templates, variant_rules
    
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

if __name__ == "__main__":
    preparator = SimpleTrainingDataPreparator()
    preparator.prepare_all()