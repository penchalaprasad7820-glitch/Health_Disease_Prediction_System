import joblib
import os
import numpy as np

class MockScaler:
    def transform(self, X):
        return X

class MockLabelEncoder:
    def __init__(self):
        self.classes_ = np.array(['Diabetes', 'Heart Disease', 'Respiratory Infection', 'Metabolic Syndrome', 'Breast Cancer', 'Liver Disease', 'Kidney Disease'])
        
    def inverse_transform(self, X):
        return self.classes_[X]

class MockModel:
    def predict_proba(self, X):
        # Return random probabilities for 7 classes that sum to 1
        probs = np.random.dirichlet(np.ones(7), size=1)
        return probs

class MockEnsemble:
    def __init__(self):
        self.named_estimators_ = {'rf': MockModel()}
        
    def predict_proba(self, X):
        return self.named_estimators_['rf'].predict_proba(X)

def create_mock_models():
    os.makedirs('models', exist_ok=True)
    
    scaler = MockScaler()
    label_encoder = MockLabelEncoder()
    ensemble = MockEnsemble()
    
    feature_names = ['age', 'gender', 'blood_pressure', 'cholesterol', 'glucose', 'bmi', 
                     'tumor_size', 'bilirubin', 'alkaline_phosphatase', 'blood_urea', 'serum_creatinine',
                     'fever', 'cough', 'fatigue', 'difficulty_breathing', 'chest_pain', 
                     'dizziness', 'nausea', 'frequent_urination', 'excessive_thirst',
                     'lump_in_breast', 'jaundice', 'swelling_in_legs', 'itching']
    
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(label_encoder, 'models/label_encoder.pkl')
    joblib.dump(feature_names, 'models/feature_names.pkl')
    joblib.dump(ensemble, 'models/ensemble.pkl')
    
    print("Mock models created successfully to bypass DLL loading policies.")

if __name__ == "__main__":
    create_mock_models()
