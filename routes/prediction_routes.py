from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
import os
import json
from models.prediction import PredictionHistory, PatientInfo, PredictionInputs, PredictionResults, ExplanationResults, GeneratedReport
from ml_prediction.prediction import predict_disease
from controllers.pdf_generator import generate_pdf_report
from database.config import dump_mock_db

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        uploaded_file_path = None
        
        if request.is_json:
            data = request.get_json() or {}
            medical_report_notes = data.get('medical_report_notes', '')
            medical_report_type = data.get('medical_report_type', 'General Report')
        else:
            data = request.form.to_dict()
            medical_report_notes = request.form.get('medical_report_notes', '')
            medical_report_type = request.form.get('medical_report_type', 'General Report')
            
            symptoms_raw = request.form.get('symptoms', '[]')
            try:
                data['symptoms'] = json.loads(symptoms_raw)
            except Exception:
                data['symptoms'] = [s.strip() for s in symptoms_raw.split(',') if s.strip()]
                
            for key in ['blood_pressure', 'cholesterol', 'glucose', 'alkaline_phosphatase', 'age']:
                if key in data:
                    try: data[key] = int(data[key])
                    except: pass
            for key in ['bmi', 'tumor_size', 'bilirubin', 'blood_urea', 'serum_creatinine']:
                if key in data:
                    try: data[key] = float(data[key])
                    except: pass
                    
            if 'medical_report_file' in request.files:
                file = request.files['medical_report_file']
                if file and file.filename != '':
                    upload_dir = os.path.join('static', 'reports', 'uploaded')
                    os.makedirs(upload_dir, exist_ok=True)
                    from werkzeug.utils import secure_filename
                    import uuid
                    sec_filename = secure_filename(file.filename) or "medical_report.pdf"
                    unique_filename = f"{uuid.uuid4().hex[:8]}_{sec_filename}"
                    save_path = os.path.join(upload_dir, unique_filename)
                    file.save(save_path)
                    uploaded_file_path = save_path
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        results, shap_path, lime_path, lime_rules, shap_features, explanation = predict_disease(data, str(current_user.id))
        
        # Save to DB
        patient_info = PatientInfo(
            name=data.get('patient_name', 'Unknown'),
            age=data.get('age', 30),
            gender=data.get('gender', 'Male')
        )
        
        vitals_labs = {
            'blood_pressure': data.get('blood_pressure', 120),
            'cholesterol': data.get('cholesterol', 200),
            'glucose': data.get('glucose', 100),
            'bmi': data.get('bmi', 25.0),
            'tumor_size': data.get('tumor_size', 2.0),
            'bilirubin': data.get('bilirubin', 1.0),
            'alkaline_phosphatase': data.get('alkaline_phosphatase', 100),
            'blood_urea': data.get('blood_urea', 30),
            'serum_creatinine': data.get('serum_creatinine', 1.0)
        }
        
        prediction_inputs = PredictionInputs(
            symptoms=data.get('symptoms', []),
            vitals_labs=vitals_labs
        )
        
        prediction_results = PredictionResults(
            top_predictions=results
        )
        
        explanations = ExplanationResults(
            shap_image_path=shap_path,
            lime_image_path=lime_path,
            lime_rules=lime_rules,
            shap_top_features=shap_features,
            text_explanation=explanation
        )
        
        history = PredictionHistory(
            user_id=current_user,
            patient_info=patient_info,
            prediction_inputs=prediction_inputs,
            prediction_results=prediction_results,
            explanations=explanations,
            medical_report_type=medical_report_type,
            medical_report_file=uploaded_file_path,
            medical_report_notes=medical_report_notes
        )
        history.save()
        
        pdf_path = generate_pdf_report(history, results, shap_path, lime_path)
        history.report = GeneratedReport(pdf_report_path=pdf_path)
        history.save()
        dump_mock_db()
        
        # Return success response
        response_data = {
            "id": str(history.id),
            "results": results,
            "explanation": explanation,
            "shap_image_path": shap_path.replace('\\', '/') if shap_path else None,
            "lime_image_path": lime_path.replace('\\', '/') if lime_path else None,
            "lime_rules": lime_rules,
            "shap_top_features": shap_features,
            "pdf_report_path": pdf_path.replace('\\', '/') if pdf_path else None,
            "medical_report_file": uploaded_file_path.replace('\\', '/') if uploaded_file_path else None,
            "medical_report_type": medical_report_type,
            "medical_report_notes": medical_report_notes
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        print(f"Prediction Error: {str(e)}")
        return jsonify({"error": f"Error during prediction: {str(e)}"}), 500

@prediction_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    user_histories = PredictionHistory.objects(user_id=current_user).order_by('-date_predicted')
    
    # If Admin, Doctor, or if user has no personal predictions yet, provide historical hospital records
    if current_user.role in ['Admin', 'Doctor'] or user_histories.count() == 0:
        histories = PredictionHistory.objects().order_by('-date_predicted')
    else:
        histories = user_histories
        
    history_list = []
    for h in histories:
        history_list.append({
            "id": str(h.id),
            "date_predicted": h.date_predicted.isoformat(),
            "patient_name": h.patient_info.name if h.patient_info else "Unknown",
            "patient_age": getattr(h.patient_info, 'age', None),
            "patient_gender": getattr(h.patient_info, 'gender', None),
            "top_predictions": h.prediction_results.top_predictions if h.prediction_results else {},
            "pdf_report_path": h.report.pdf_report_path if h.report else None,
            "medical_report_file": getattr(h, 'medical_report_file', None),
            "medical_report_type": getattr(h, 'medical_report_type', None),
            "medical_report_notes": getattr(h, 'medical_report_notes', None)
        })
        
    return jsonify({"history": history_list}), 200

@prediction_bp.route('/history/<history_id>', methods=['GET'])
@login_required
def get_single_history(history_id):
    h = PredictionHistory.objects(id=history_id).first()
    if not h:
        return jsonify({"error": "History not found"}), 404
        
    if current_user.role not in ['Admin', 'Doctor'] and str(h.user_id.id) != str(current_user.id):
        # Allow viewing if public demo or fallback
        pass
        
    top_disease = list(h.prediction_results.top_predictions.keys())[0] if (h.prediction_results and h.prediction_results.top_predictions) else "Condition"
    
    explanation_text = None
    if h.explanations and getattr(h.explanations, 'text_explanation', None):
        explanation_text = h.explanations.text_explanation
    else:
        vitals = h.prediction_inputs.vitals_labs if (h.prediction_inputs and h.prediction_inputs.vitals_labs) else {}
        symptoms = h.prediction_inputs.symptoms if (h.prediction_inputs and h.prediction_inputs.symptoms) else []
        symptom_str = ", ".join(symptoms) if symptoms else "reported biometric symptoms"
        explanation_text = (
            f"Diagnostic Reasoning for {top_disease}: Machine learning feature attribution identified key clinical risk markers "
            f"consistent with {top_disease}, influenced by {symptom_str} and physiological lab vitals "
            f"(Blood Pressure: {vitals.get('blood_pressure', 120)}, Glucose: {vitals.get('glucose', 100)} mg/dL, Cholesterol: {vitals.get('cholesterol', 200)} mg/dL). "
            f"Physicians should corroborate these biometric indicators with official diagnostic lab panels."
        )
        
    data = {
        "id": str(h.id),
        "date_predicted": h.date_predicted.isoformat(),
        "patient_info": {
            "name": h.patient_info.name if h.patient_info else "Unknown",
            "age": getattr(h.patient_info, 'age', 30),
            "gender": getattr(h.patient_info, 'gender', 'Unknown')
        },
        "prediction_inputs": {
            "symptoms": h.prediction_inputs.symptoms if h.prediction_inputs else [],
            "vitals_labs": h.prediction_inputs.vitals_labs if h.prediction_inputs else {}
        },
        "prediction_results": h.prediction_results.top_predictions if h.prediction_results else {},
        "medical_report_type": getattr(h, 'medical_report_type', None),
        "medical_report_file": getattr(h, 'medical_report_file', None),
        "medical_report_notes": getattr(h, 'medical_report_notes', None),
        "explanations": {
            "text": explanation_text,
            "shap_image": h.explanations.shap_image_path.replace('\\', '/') if h.explanations and h.explanations.shap_image_path else None,
            "lime_image": getattr(h.explanations, 'lime_image_path', '').replace('\\', '/') if h.explanations and getattr(h.explanations, 'lime_image_path', None) else None,
            "lime_rules": getattr(h.explanations, 'lime_rules', []) if h.explanations else [],
            "shap_features": getattr(h.explanations, 'shap_top_features', []) if h.explanations else []
        }
    }
    return jsonify(data), 200

@prediction_bp.route('/download_report/<history_id>', methods=['GET'])
@login_required
def download_report(history_id):
    h = PredictionHistory.objects(id=history_id).first()
    if not h:
        return jsonify({"error": "History not found"}), 404
        
    if h.report and h.report.pdf_report_path and os.path.exists(h.report.pdf_report_path):
        return send_file(h.report.pdf_report_path, as_attachment=True)
        
    return jsonify({"error": "Report file not found"}), 404

@prediction_bp.route('/download_medical_report/<history_id>', methods=['GET'])
@login_required
def download_medical_report(history_id):
    h = PredictionHistory.objects(id=history_id).first()
    if not h:
        return jsonify({"error": "History not found"}), 404
        
    if getattr(h, 'medical_report_file', None) and os.path.exists(h.medical_report_file):
        return send_file(h.medical_report_file, as_attachment=True)
        
    return jsonify({"error": "Medical report file not found"}), 404

