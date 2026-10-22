import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder

def train_and_save():
    print("Generating synthetic clinical dataset...")
    np.random.seed(42)
    n_samples = 3000

    age = np.random.randint(18, 85, n_samples)
    gender_raw = np.random.choice(['Male', 'Female'], n_samples)
    gender = np.array([1 if g == 'Male' else 0 for g in gender_raw])
    
    blood_pressure = np.random.normal(120, 18, n_samples).clip(80, 200)
    cholesterol = np.random.normal(195, 35, n_samples).clip(120, 350)
    glucose = np.random.normal(105, 25, n_samples).clip(65, 300)
    bmi = np.random.normal(25.5, 4.5, n_samples).clip(15, 45)
    
    tumor_size = np.random.exponential(1.5, n_samples).clip(0.1, 12.0)
    bilirubin = np.random.exponential(0.8, n_samples).clip(0.2, 8.0)
    alkaline_phosphatase = np.random.normal(95, 28, n_samples).clip(30, 250)
    blood_urea = np.random.normal(32, 12, n_samples).clip(10, 100)
    serum_creatinine = np.random.exponential(0.9, n_samples).clip(0.4, 6.0)

    fever = np.random.choice([0, 1], n_samples, p=[0.75, 0.25])
    cough = np.random.choice([0, 1], n_samples, p=[0.70, 0.30])
    fatigue = np.random.choice([0, 1], n_samples, p=[0.60, 0.40])
    diff_breathing = np.random.choice([0, 1], n_samples, p=[0.82, 0.18])
    chest_pain = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    dizziness = np.random.choice([0, 1], n_samples, p=[0.80, 0.20])
    nausea = np.random.choice([0, 1], n_samples, p=[0.78, 0.22])
    freq_urination = np.random.choice([0, 1], n_samples, p=[0.80, 0.20])
    exc_thirst = np.random.choice([0, 1], n_samples, p=[0.82, 0.18])
    lump_in_breast = np.random.choice([0, 1], n_samples, p=[0.92, 0.08])
    jaundice = np.random.choice([0, 1], n_samples, p=[0.88, 0.12])
    swelling_in_legs = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    itching = np.random.choice([0, 1], n_samples, p=[0.80, 0.20])

    df = pd.DataFrame({
        'age': age, 'gender': gender, 'blood_pressure': blood_pressure,
        'cholesterol': cholesterol, 'glucose': glucose, 'bmi': bmi,
        'tumor_size': tumor_size, 'bilirubin': bilirubin,
        'alkaline_phosphatase': alkaline_phosphatase, 'blood_urea': blood_urea,
        'serum_creatinine': serum_creatinine,
        'fever': fever, 'cough': cough, 'fatigue': fatigue,
        'difficulty_breathing': diff_breathing, 'chest_pain': chest_pain,
        'dizziness': dizziness, 'nausea': nausea,
        'frequent_urination': freq_urination, 'excessive_thirst': exc_thirst,
        'lump_in_breast': lump_in_breast, 'jaundice': jaundice,
        'swelling_in_legs': swelling_in_legs, 'itching': itching
    })

    # Clinical condition rules
    conditions = [
        (df['glucose'] > 125) & ((df['frequent_urination'] == 1) | (df['excessive_thirst'] == 1)), # Diabetes
        ((df['blood_pressure'] > 140) | (df['cholesterol'] > 220)) & (df['chest_pain'] == 1), # Heart Disease
        (df['fever'] == 1) & (df['cough'] == 1) & (df['difficulty_breathing'] == 1), # Respiratory Infection
        (df['bmi'] > 29) & (df['blood_pressure'] > 130) & (df['fatigue'] == 1), # Metabolic Syndrome
        (df['tumor_size'] > 2.8) & (df['lump_in_breast'] == 1), # Breast Cancer
        (df['bilirubin'] > 1.8) & (df['jaundice'] == 1), # Liver Disease
        (df['serum_creatinine'] > 1.4) & (df['swelling_in_legs'] == 1) # Kidney Disease
    ]
    choices = ['Diabetes', 'Heart Disease', 'Respiratory Infection', 'Metabolic Syndrome', 'Breast Cancer', 'Liver Disease', 'Kidney Disease']

    df['disease'] = np.select(conditions, choices, default=None)
    # Fill remaining with probabilistic distribution across the 7 diseases
    null_idx = df[df['disease'].isna()].index
    df.loc[null_idx, 'disease'] = np.random.choice(choices, size=len(null_idx))

    # Add 8% random noise for realistic decision boundaries
    noise_idx = np.random.choice(df.index, size=int(n_samples * 0.08), replace=False)
    df.loc[noise_idx, 'disease'] = np.random.choice(choices, size=len(noise_idx))

    feature_names = [
        'age', 'gender', 'blood_pressure', 'cholesterol', 'glucose', 'bmi',
        'tumor_size', 'bilirubin', 'alkaline_phosphatase', 'blood_urea', 'serum_creatinine',
        'fever', 'cough', 'fatigue', 'difficulty_breathing', 'chest_pain',
        'dizziness', 'nausea', 'frequent_urination', 'excessive_thirst',
        'lump_in_breast', 'jaundice', 'swelling_in_legs', 'itching'
    ]

    X = df[feature_names].copy()
    y = df['disease']

    label_encoder = LabelEncoder()
    label_encoder.fit(choices)
    y_encoded = label_encoder.transform(y)

    numerical_cols = ['age', 'blood_pressure', 'cholesterol', 'glucose', 'bmi', 'tumor_size', 'bilirubin', 'alkaline_phosphatase', 'blood_urea', 'serum_creatinine']
    scaler = StandardScaler()
    X_scaled = X.copy()
    X_scaled[numerical_cols] = scaler.fit_transform(X[numerical_cols])

    print("Training RandomForestClassifier...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, class_weight='balanced')
    rf.fit(X_scaled, y_encoded)
    score = rf.score(X_scaled, y_encoded)
    print(f"Model Training Accuracy: {score * 100:.2f}%")

    # Save to both models/ and ml_prediction/saved_models/
    for target_dir in ['models', 'ml_prediction/saved_models']:
        os.makedirs(target_dir, exist_ok=True)
        joblib.dump(rf, os.path.join(target_dir, 'ensemble.pkl'))
        joblib.dump(rf, os.path.join(target_dir, 'model.pkl'))
        joblib.dump(scaler, os.path.join(target_dir, 'scaler.pkl'))
        joblib.dump(label_encoder, os.path.join(target_dir, 'label_encoder.pkl'))
        joblib.dump(feature_names, os.path.join(target_dir, 'feature_names.pkl'))
        # Save a sample background distribution for SHAP and LIME
        joblib.dump(X_scaled.sample(200, random_state=42).values, os.path.join(target_dir, 'background_data.pkl'))
        print(f"Artifacts saved in {target_dir}/")

    # Also save training dataset
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_disease_data.csv', index=False)
    print("Completed successfully!")

if __name__ == '__main__':
    train_and_save()
