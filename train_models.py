import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os
import json

class SklearnModelTrainer:
    def __init__(self):
        self.models = {}
        self.label_encoders = {}
        
    def train_site_classifier(self):
        """Train site type and style classifiers"""
        print("\n=== Training Site Type & Style Classifiers ===\n")
        
        # Load data
        df = pd.read_csv('training/classifier_data.csv')
        print(f"Training on {len(df)} examples")
        
        # Features
        feature_cols = [col for col in df.columns if col not in ['site_type', 'style']]
        X = df[feature_cols]
        
        # Train site type classifier
        print("\n1. Site Type Classifier:")
        le_site = LabelEncoder()
        y_site = le_site.fit_transform(df['site_type'])
        self.label_encoders['site_type'] = le_site
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_site, test_size=0.2, random_state=42, stratify=y_site
        )
        
        # Try Random Forest
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        rf_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = rf_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"   Accuracy: {accuracy:.2%}")
        print(f"   Cross-validation scores: {cross_val_score(rf_model, X, y_site, cv=5).mean():.2%}")
        print("\n   Classification Report:")
        print(classification_report(y_test, y_pred, target_names=le_site.classes_))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n   Top 5 Important Features:")
        print(feature_importance.head())
        
        self.models['site_type_classifier'] = rf_model
        
        # Train style classifier
        print("\n2. Style Classifier:")
        le_style = LabelEncoder()
        y_style = le_style.fit_transform(df['style'])
        self.label_encoders['style'] = le_style
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_style, test_size=0.2, random_state=42, stratify=y_style
        )
        
        style_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
        style_model.fit(X_train, y_train)
        
        y_pred = style_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"   Accuracy: {accuracy:.2%}")
        print("\n   Classification Report:")
        print(classification_report(y_test, y_pred, target_names=le_style.classes_))
        
        self.models['style_classifier'] = style_model
        
    def train_layout_generator(self):
        """Learn layout patterns"""
        print("\n=== Training Layout Generator ===\n")
        
        df = pd.read_csv('training/layout_generator_data.csv')
        
        # Group by site_type and find common patterns
        layout_templates = {}
        
        for site_type in df['site_type'].unique():
            type_df = df[df['site_type'] == site_type]
            
            # Get most common layouts
            layout_counts = type_df['sections'].value_counts()
            
            # Store top 3 layouts
            layout_templates[site_type] = [
                layout.split(',') for layout in layout_counts.head(3).index
            ]
            
            print(f"{site_type}:")
            for i, (layout, count) in enumerate(layout_counts.head(3).items(), 1):
                print(f"   {i}. {layout} (seen {count}x)")
        
        self.models['layout_templates'] = layout_templates
        
    def train_component_selector(self):
        """Train component variant selectors"""
        print("\n=== Training Component Variant Selectors ===\n")
        
        df = pd.read_csv('training/component_selector_data.csv')
        
        # Encode categorical features
        le_site = LabelEncoder()
        le_style = LabelEncoder()
        le_comp = LabelEncoder()
        le_variant = LabelEncoder()
        
        df['site_type_enc'] = le_site.fit_transform(df['site_type'])
        df['style_enc'] = le_style.fit_transform(df['style'])
        df['component_type_enc'] = le_comp.fit_transform(df['component_type'])
        df['variant_enc'] = le_variant.fit_transform(df['variant'])
        
        self.label_encoders['component_site_type'] = le_site
        self.label_encoders['component_style'] = le_style
        self.label_encoders['component_type'] = le_comp
        self.label_encoders['variant'] = le_variant
        
        # Train one model per component type
        component_models = {}
        
        for comp_type in df['component_type'].unique():
            comp_df = df[df['component_type'] == comp_type]
            
            if len(comp_df) < 10:
                print(f"{comp_type}: Skipped (only {len(comp_df)} examples)")
                continue
            
            print(f"\n{comp_type}:")
            print(f"   Training examples: {len(comp_df)}")
            
            # Features
            feature_cols = ['site_type_enc', 'style_enc', 'has_image', 'has_cta', 'position']
            X = comp_df[feature_cols]
            y = comp_df['variant_enc']
            
            # Check if enough variety
            if len(y.unique()) < 2:
                print(f"   Skipped (only 1 variant)")
                continue
            
            # Train
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"   Accuracy: {accuracy:.2%}")
            
            component_models[comp_type] = model
        
        self.models['component_selectors'] = component_models
        
    def save_models(self):
        """Save all trained models"""
        os.makedirs('models', exist_ok=True)
        
        # Save sklearn models
        joblib.dump(self.models['site_type_classifier'], 'models/site_type_classifier.pkl')
        joblib.dump(self.models['style_classifier'], 'models/style_classifier.pkl')
        joblib.dump(self.models['component_selectors'], 'models/component_selectors.pkl')
        joblib.dump(self.label_encoders, 'models/label_encoders.pkl')
        
        # Save layout templates as JSON
        with open('models/layout_templates.json', 'w') as f:
            json.dump(self.models['layout_templates'], f, indent=2)
        
        print("\n✅ All models saved to models/")
        
    def train_all(self):
        """Train all models"""
        self.train_site_classifier()
        self.train_layout_generator()
        self.train_component_selector()
        self.save_models()

if __name__ == "__main__":
    trainer = SklearnModelTrainer()
    trainer.train_all()