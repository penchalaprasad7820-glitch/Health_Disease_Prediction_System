import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# 1. Generate Synthetic Dataset
def generate_synthetic_data(n_samples=2000):
    np.random.seed(42)
    
    # Features
    age = np.random.randint(20, 80, n_samples)
    gender = np.random.choice(['Male', 'Female'], n_samples)
    blood_pressure = np.random.normal(120, 15, n_samples)
    cholesterol = np.random.normal(200, 40, n_samples)
    glucose = np.random.normal(100, 20, n_samples)
    bmi = np.random.normal(25, 5, n_samples)
    
    # Symptoms (binary 0/1)
    fever = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    cough = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    fatigue = np.random.choice([0, 1], n_samples, p=[0.5, 0.5])
    diff_breathing = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    chest_pain = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    dizziness = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    nausea = np.random.choice([0, 1], n_samples, p=[0.75, 0.25])
    freq_urination = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    exc_thirst = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    
    # New features
    tumor_size = np.random.normal(2, 1, n_samples)
    bilirubin = np.random.normal(1.0, 0.5, n_samples)
    alkaline_phosphatase = np.random.normal(100, 30, n_samples)
    blood_urea = np.random.normal(30, 10, n_samples)
    serum_creatinine = np.random.normal(1.0, 0.3, n_samples)
    
    lump_in_breast = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
    jaundice = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    swelling_in_legs = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    itching = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    
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
    
    # Target Disease Logic (synthetic rules with noise)
    conditions = [
        (df['glucose'] > 125) & (df['frequent_urination'] == 1) & (df['excessive_thirst'] == 1), # Diabetes
        (df['blood_pressure'] > 140) & (df['cholesterol'] > 240) & (df['chest_pain'] == 1), # Heart Disease
        (df['fever'] == 1) & (df['cough'] == 1) & (df['difficulty_breathing'] == 1), # Respiratory Infection
        (df['bmi'] > 30) & (df['fatigue'] == 1) & (df['blood_pressure'] > 130), # Metabolic Syndrome
        (df['tumor_size'] > 3) & (df['lump_in_breast'] == 1), # Breast Cancer
        (df['bilirubin'] > 2.0) & (df['jaundice'] == 1), # Liver Disease
        (df['serum_creatinine'] > 1.5) & (df['swelling_in_legs'] == 1) # Kidney Disease
    ]
    choices = ['Diabetes', 'Heart Disease', 'Respiratory Infection', 'Metabolic Syndrome', 'Breast Cancer', 'Liver Disease', 'Kidney Disease']
    
    df['disease'] = np.select(conditions, choices, default='Healthy')
    
    # Introduce some noise to make it harder
    noise_idx = np.random.choice(df.index, size=int(n_samples * 0.1), replace=False)
    df.loc[noise_idx, 'disease'] = np.random.choice(choices + ['Healthy'], size=len(noise_idx))
    
    return df

print("Generating synthetic data...")
df = generate_synthetic_data(3000)
df.to_csv('data/synthetic_disease_data.csv', index=False)
print("Data saved to data/synthetic_disease_data.csv")

# 2. Preprocessing
print("Preprocessing data...")
# Encode gender
df['gender'] = df['gender'].map({'Male': 1, 'Female': 0, 'Other': 2})

X = df.drop('disease', axis=1)
y = df['disease']

# Encode target
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Save the feature names and label encoder classes
feature_names = X.columns.tolist()
joblib.dump(label_encoder, 'models/label_encoder.pkl')
joblib.dump(feature_names, 'models/feature_names.pkl')

# Scale numerical features
scaler = StandardScaler()
numerical_cols = ['age', 'blood_pressure', 'cholesterol', 'glucose', 'bmi', 'tumor_size', 'bilirubin', 'alkaline_phosphatase', 'blood_urea', 'serum_creatinine']
X[numerical_cols] = scaler.fit_transform(X[numerical_cols])
joblib.dump(scaler, 'models/scaler.pkl')

# Train/Val/Test Split (80/10/10)
X_train_val, X_test, y_train_val, y_test = train_test_split(X, y_encoded, test_size=0.1, stratify=y_encoded, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.1111, stratify=y_train_val, random_state=42)

# Handle imbalance using SMOTE
print("Applying SMOTE...")
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# 3. Model Training & Hyperparameter Tuning
print("Training models...")

# Random Forest
rf = RandomForestClassifier(random_state=42)
rf_param_grid = {'n_estimators': [50, 100], 'max_depth': [10, None]}
rf_grid = GridSearchCV(rf, rf_param_grid, cv=3, scoring='accuracy', n_jobs=-1)
rf_grid.fit(X_train_resampled, y_train_resampled)
best_rf = rf_grid.best_estimator_
print(f"Best RF Params: {rf_grid.best_params_}")

# XGBoost
xgb = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
xgb_param_grid = {'n_estimators': [50, 100], 'learning_rate': [0.01, 0.1]}
xgb_grid = GridSearchCV(xgb, xgb_param_grid, cv=3, scoring='accuracy', n_jobs=-1)
xgb_grid.fit(X_train_resampled, y_train_resampled)
best_xgb = xgb_grid.best_estimator_
print(f"Best XGB Params: {xgb_grid.best_params_}")

# MLP (Neural Network)
mlp = MLPClassifier(max_iter=300, random_state=42)
mlp_param_grid = {'hidden_layer_sizes': [(50,), (100, 50)], 'alpha': [0.0001, 0.001]}
mlp_grid = GridSearchCV(mlp, mlp_param_grid, cv=3, scoring='accuracy', n_jobs=-1)
mlp_grid.fit(X_train_resampled, y_train_resampled)
best_mlp = mlp_grid.best_estimator_
print(f"Best MLP Params: {mlp_grid.best_params_}")

# 4. Ensemble (Soft Voting)
print("Creating Ensemble...")
ensemble = VotingClassifier(
    estimators=[('rf', best_rf), ('xgb', best_xgb), ('mlp', best_mlp)],
    voting='soft'
)
ensemble.fit(X_train_resampled, y_train_resampled)

# 5. Evaluation
y_pred = ensemble.predict(X_test)
print("\n--- Ensemble Evaluation on Test Set ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision (macro): {precision_score(y_test, y_pred, average='macro'):.4f}")
print(f"Recall (macro): {recall_score(y_test, y_pred, average='macro'):.4f}")
print(f"F1 (macro): {f1_score(y_test, y_pred, average='macro'):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Save the best model
joblib.dump(ensemble, 'models/ensemble.pkl')
print("\nModel saved to models/ensemble.pkl")
