from mongoengine import Document, EmbeddedDocument, StringField, IntField, FloatField, DateTimeField, ListField, DictField, ReferenceField, EmbeddedDocumentField
import datetime
from models.user import User

class PatientInfo(EmbeddedDocument):
    name = StringField(required=True, max_length=150)
    age = IntField(required=True)
    gender = StringField(required=True, choices=('Male', 'Female', 'Other'))

class PredictionInputs(EmbeddedDocument):
    symptoms = ListField(StringField())
    vitals_labs = DictField()

class PredictionResults(EmbeddedDocument):
    top_predictions = DictField() # e.g. {"Diabetes": 0.85, "Hypertension": 0.15}

class ExplanationResults(EmbeddedDocument):
    shap_image_path = StringField()
    lime_image_path = StringField()
    lime_rules = ListField(DictField())
    shap_top_features = ListField(DictField())
    text_explanation = StringField()


class GeneratedReport(EmbeddedDocument):
    pdf_report_path = StringField()
    generated_date = DateTimeField(default=datetime.datetime.utcnow)

class PredictionHistory(Document):
    user_id = ReferenceField(User, required=True)
    patient_info = EmbeddedDocumentField(PatientInfo, required=True)
    prediction_inputs = EmbeddedDocumentField(PredictionInputs, required=True)
    prediction_results = EmbeddedDocumentField(PredictionResults, required=True)
    explanations = EmbeddedDocumentField(ExplanationResults)
    report = EmbeddedDocumentField(GeneratedReport)
    medical_report_type = StringField()
    medical_report_file = StringField()
    medical_report_notes = StringField()
    date_predicted = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {'collection': 'prediction_history'}

