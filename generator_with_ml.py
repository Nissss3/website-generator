import json
from simple_models import SimpleMLModels

class MLWebsiteGenerator:
    def __init__(self):
        print("Loading trained ML models...")
        self.ml_models = SimpleMLModels()
        print("✓ Models loaded!\n")
        
        # Component library (same as before)
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
        """Generate complete website from text description using ML"""
        print(f"Description: {description}\n")
        
        # Use ML to generate DSL
        dsl = self.ml_models.generate_complete_dsl(description)
        
        print("=== ML Classification ===")
        print(f"Site Type: {dsl['site_type']}")
        print(f"Style: {dsl['style']}")
        print(f"Confidence: {dsl['confidence']:.2%}")
        print(f"Sections: {[s['type'] for s in dsl['sections']]}\n")
        
        # Generate HTML from DSL
        html = self.dsl_to_html(dsl, description)
        
        return {
            'dsl': dsl,
            'html': html
        }
    
    def dsl_to_html(self, dsl, description):
        """Convert DSL to HTML using component library"""
        sections_html = []
        
        for section in dsl['sections']:
            section_type = section['type']
            variant = section['variant']
            
            if section_type in self.components:
                # Generate section with variant
                html = self.components[section_type](variant, dsl, description)
                sections_html.append(html)
        
        # Get theme colors based on style
        colors = self.get_colors_for_style(dsl['style'])
        
        # Complete HTML
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Website - {dsl['site_type']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; }}
        button {{ transition: transform 0.2s, box-shadow 0.2s; }}
        button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }}
    </style>
</head>
<body>
{chr(10).join(sections_html)}
</body>
</html>"""
    
    def get_colors_for_style(self, style):
        """Get color scheme based on detected style"""
        color_schemes = {
            'modern_gradient': {'primary': '#667eea', 'secondary': '#764ba2'},
            'minimal_clean': {'primary': '#2d3748', 'secondary': '#4a5568'},
            'bold_colorful': {'primary': '#f56565', 'secondary': '#ed8936'},
            'dark_mode': {'primary': '#1a202c', 'secondary': '#2d3748'},
            'glassmorphism': {'primary': '#667eea', 'secondary': '#764ba2'}
        }
        return color_schemes.get(style, {'primary': '#667eea', 'secondary': '#764ba2'})
    
    def generate_navbar(self, variant, dsl, description):
        """Generate navbar with variant"""
        colors = self.get_colors_for_style(dsl['style'])
        
        if variant == 'transparent':
            bg = 'rgba(255,255,255,0.9)'
            style_attr = 'backdrop-filter: blur(10px);'
        else:
            bg = '#fff'
            style_attr = ''
        
        return f"""
<nav style="background:{bg};padding:20px 40px;box-shadow:0 2px 10px rgba(0,0,0,0.1);display:flex;justify-content:space-between;align-items:center;{style_attr}">
    <div style="font-size:1.5rem;font-weight:bold;color:{colors['primary']}">Brand</div>
    <div style="display:flex;gap:30px">
        <a href="#home" style="color:#333;text-decoration:none">Home</a>
        <a href="#features" style="color:#333;text-decoration:none">Features</a>
        <a href="#about" style="color:#333;text-decoration:none">About</a>
        <a href="#contact" style="color:#333;text-decoration:none">Contact</a>
    </div>
</nav>"""
    
    def generate_hero(self, variant, dsl, description):
        """Generate hero with variant"""
        colors = self.get_colors_for_style(dsl['style'])
        
        # Extract title from description (first few words)
        words = description.split()[:5]
        title = ' '.join(words).title()
        
        if variant == 'split_screen_with_image':
            return f"""
<section style="display:flex;min-height:600px;align-items:center;padding:80px 40px;background:linear-gradient(135deg,{colors['primary']},{colors['secondary']})">
    <div style="flex:1;color:#fff">
        <h1 style="font-size:3rem;margin-bottom:20px">{title}</h1>
        <p style="font-size:1.25rem;margin-bottom:30px">{description}</p>
        <button style="background:#fff;color:{colors['primary']};padding:15px 40px;border:none;border-radius:50px;font-size:1.1rem;font-weight:600;cursor:pointer">Get Started</button>
    </div>
    <div style="flex:1;display:flex;justify-content:center">
        <div style="width:400px;height:400px;background:rgba(255,255,255,0.2);border-radius:20px;backdrop-filter:blur(10px)"></div>
    </div>
</section>"""
        
        else:  # centered_cta or minimal_text
            return f"""
<section style="background:linear-gradient(135deg,{colors['primary']},{colors['secondary']});color:#fff;padding:100px 20px;text-align:center;min-height:600px;display:flex;flex-direction:column;justify-content:center">
    <h1 style="font-size:3rem;margin-bottom:20px">{title}</h1>
    <p style="font-size:1.25rem;margin-bottom:30px;max-width:600px;margin-left:auto;margin-right:auto">{description}</p>
    <div>
        <button style="background:#fff;color:{colors['primary']};padding:15px 40px;border:none;border-radius:50px;font-size:1.1rem;font-weight:600;cursor:pointer">Get Started</button>
    </div>
</section>"""
    
    def generate_features(self, variant, dsl, description):
        """Generate features section"""
        colors = self.get_colors_for_style(dsl['style'])
        
        # Default features
        features = [
            {'icon': '⚡', 'title': 'Fast', 'desc': 'Lightning fast performance'},
            {'icon': '🎨', 'title': 'Beautiful', 'desc': 'Stunning designs'},
            {'icon': '📱', 'title': 'Responsive', 'desc': 'Works everywhere'}
        ]
        
        if variant == 'grid_4col':
            features.append({'icon': '🔒', 'title': 'Secure', 'desc': 'Bank-level security'})
            grid_cols = 'repeat(4,1fr)'
        else:
            grid_cols = 'repeat(3,1fr)'
        
        features_html = ''.join([
            f"""<div style="background:#fff;padding:30px;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,0.1);text-align:center">
                <div style="font-size:3rem;margin-bottom:15px">{f['icon']}</div>
                <h3 style="font-size:1.5rem;margin-bottom:10px">{f['title']}</h3>
                <p style="color:#718096">{f['desc']}</p>
            </div>"""
            for f in features
        ])
        
        return f"""
<section style="padding:80px 20px;background:#f7fafc">
    <h2 style="text-align:center;font-size:2.5rem;margin-bottom:50px">Features</h2>
    <div style="display:grid;grid-template-columns:{grid_cols};gap:30px;max-width:1200px;margin:0 auto">
        {features_html}
    </div>
</section>"""
    
    def generate_pricing(self, variant, dsl, description):
        """Generate pricing section"""
        return f"""
<section style="padding:80px 20px;background:#fff">
    <h2 style="text-align:center;font-size:2.5rem;margin-bottom:50px">Pricing</h2>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:30px;max-width:1000px;margin:0 auto">
        <div style="border:2px solid #e2e8f0;padding:40px;border-radius:10px;text-align:center">
            <h3 style="font-size:1.5rem;margin-bottom:10px">Starter</h3>
            <p style="font-size:3rem;font-weight:bold;margin:20px 0">$9</p>
            <button style="background:#667eea;color:#fff;padding:12px 30px;border:none;border-radius:8px;cursor:pointer;width:100%">Choose Plan</button>
        </div>
        <div style="border:2px solid #667eea;padding:40px;border-radius:10px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.1)">
            <h3 style="font-size:1.5rem;margin-bottom:10px">Pro</h3>
            <p style="font-size:3rem;font-weight:bold;margin:20px 0">$29</p>
            <button style="background:#667eea;color:#fff;padding:12px 30px;border:none;border-radius:8px;cursor:pointer;width:100%">Choose Plan</button>
        </div>
        <div style="border:2px solid #e2e8f0;padding:40px;border-radius:10px;text-align:center">
            <h3 style="font-size:1.5rem;margin-bottom:10px">Enterprise</h3>
            <p style="font-size:3rem;font-weight:bold;margin:20px 0">$99</p>
            <button style="background:#667eea;color:#fff;padding:12px 30px;border:none;border-radius:8px;cursor:pointer;width:100%">Choose Plan</button>
        </div>
    </div>
</section>"""
    
    def generate_testimonials(self, variant, dsl, description):
        """Generate testimonials section"""
        return f"""
<section style="padding:80px 20px;background:#f7fafc">
    <h2 style="text-align:center;font-size:2.5rem;margin-bottom:50px">What People Say</h2>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:30px;max-width:1000px;margin:0 auto">
        <div style="background:#fff;padding:30px;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,0.1)">
            <p style="font-style:italic;margin-bottom:20px">"This product changed my life!"</p>
            <p style="font-weight:bold">- Happy Customer</p>
        </div>
        <div style="background:#fff;padding:30px;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,0.1)">
            <p style="font-style:italic;margin-bottom:20px">"Best decision we ever made."</p>
            <p style="font-weight:bold">- Satisfied Client</p>
        </div>
    </div>
</section>"""
    
    def generate_contact(self, variant, dsl, description):
        """Generate contact section"""
        return f"""
<section style="padding:80px 20px;background:#fff">
    <h2 style="text-align:center;font-size:2.5rem;margin-bottom:50px">Get In Touch</h2>
    <div style="max-width:600px;margin:0 auto;display:flex;flex-direction:column;gap:20px">
        <input type="text" placeholder="Name" style="padding:15px;border:2px solid #e2e8f0;border-radius:8px;font-size:1rem">
        <input type="email" placeholder="Email" style="padding:15px;border:2px solid #e2e8f0;border-radius:8px;font-size:1rem">
        <textarea placeholder="Message" rows="5" style="padding:15px;border:2px solid #e2e8f0;border-radius:8px;font-size:1rem;resize:vertical"></textarea>
        <button onclick="alert('Message sent!')" style="background:#667eea;color:#fff;padding:15px;border:none;border-radius:8px;font-size:1.1rem;font-weight:600;cursor:pointer">Send Message</button>
    </div>
</section>"""
    
    def generate_footer(self, variant, dsl, description):
        """Generate footer"""
        if variant == 'detailed':
            return f"""
<footer style="background:#2d3748;color:#fff;padding:60px 40px">
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:40px;max-width:1200px;margin:0 auto 40px">
        <div>
            <h4 style="margin-bottom:20px">Company</h4>
            <div style="display:flex;flex-direction:column;gap:10px">
                <a href="#" style="color:#a0aec0;text-decoration:none">About</a>
                <a href="#" style="color:#a0aec0;text-decoration:none">Careers</a>
                <a href="#" style="color:#a0aec0;text-decoration:none">Blog</a>
            </div>
        </div>
        <div>
            <h4 style="margin-bottom:20px">Product</h4>
            <div style="display:flex;flex-direction:column;gap:10px">
                <a href="#" style="color:#a0aec0;text-decoration:none">Features</a>
                <a href="#" style="color:#a0aec0;text-decoration:none">Pricing</a>
                <a href="#" style="color:#a0aec0;text-decoration:none">Security</a>
            </div>
        </div>
        <div>
            <h4 style="margin-bottom:20px">Legal</h4>
            <div style="display:flex;flex-direction:column;gap:10px">
                <a href="#" style="color:#a0aec0;text-decoration:none">Privacy</a>
                <a href="#" style="color:#a0aec0;text-decoration:none">Terms</a>
                <a href="#" style="color:#a0aec0;text-decoration:none">Contact</a>
            </div>
        </div>
    </div>
    <div style="text-align:center;padding-top:40px;border-top:1px solid #4a5568">
        <p>© 2024 Company. All rights reserved.</p>
    </div>
</footer>"""
        else:  # minimal
            return f"""
<footer style="background:#2d3748;color:#fff;padding:40px 20px;text-align:center">
    <p style="margin-bottom:10px">© 2024 Company. All rights reserved.</p>
    <div style="display:flex;gap:20px;justify-content:center;margin-top:20px">
        <a href="#" style="color:#a0aec0;text-decoration:none">Privacy</a>
        <a href="#" style="color:#a0aec0;text-decoration:none">Terms</a>
        <a href="#" style="color:#a0aec0;text-decoration:none">Contact</a>
    </div>
</footer>"""
    
    def save_website(self, html, filename='output/generated_website.html'):
        """Save generated HTML"""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Website saved to {filename}")

if __name__ == "__main__":
    generator = MLWebsiteGenerator()
    
    # Test with different descriptions
    test_descriptions = [
        "modern SaaS platform for team analytics with dashboard and pricing",
        "minimal portfolio website for photographer showcasing work",
        "ecommerce store for selling organic products with featured items"
    ]
    
    for i, desc in enumerate(test_descriptions, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}")
        print('='*60)
        
        result = generator.generate_from_description(desc)
        generator.save_website(result['html'], f'output/test_website_{i}.html')
        
        print(f"\nGenerated {len(result['html'])} characters of HTML")

    print("\n✅ All test websites generated!")