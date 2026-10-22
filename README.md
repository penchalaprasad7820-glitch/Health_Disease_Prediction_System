# Disease Prediction System

An advanced disease prediction and decision-support system built with Flask, MongoDB Atlas, and Machine Learning.

## Features

* **Machine Learning Prediction**: Uses an ensemble model (Random Forest, etc.) to predict probabilities of various diseases based on patient vitals and symptoms.
* **REST APIs**: Clean backend API architecture with Flask and MongoEngine.
* **MongoDB Atlas Integration**: Securely stores users, patient inputs, predictions, and report references in MongoDB.
* **SHAP Interpretability**: Generates feature importance charts to explain predictions.
* **PDF Reports**: Automatically generates and stores downloadable PDF reports.
* **Secure Authentication**: Flask-Login and Bcrypt for secure user authentication.

## Project Structure
* `models/` - MongoDB database schemas
* `routes/` - API endpoints (Authentication, Predictions)
* `controllers/` - Helper logic (e.g., PDF generation)
* `database/` - MongoDB configuration and initialization
* `ml_prediction/` - ML prediction scripts and saved models
* `authentication/` - Flask-Login setup
* `templates/` - Frontend HTML UI (served by Flask)
* `static/` - JS, CSS, and output files (reports/shap images)

## Setup Instructions

### 1. Create MongoDB Atlas Database
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create a free account/cluster.
2. Under "Database Access", create a new database user with a password.
3. Under "Network Access", allow your IP address (or `0.0.0.0/0` for testing).
4. Click "Connect" on your cluster, select "Drivers", and copy the connection string.

### 2. Configure Environment Variables
1. Rename `.env.example` to `.env` (or just edit the generated `.env` file).
2. Replace the `MONGO_URI` value with the connection string you copied from Atlas, inserting your username and password.
   ```
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/disease_prediction?retryWrites=true&w=majority
   ```
   *Note: Never hard-code these credentials in your source code!*

### 3. Install Dependencies
Make sure you have Python 3.8+ installed.
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Start the Application
```bash
python app.py
```
The application will start on `http://localhost:5000`.

### 5. Using the Application
1. Open `http://localhost:5000` in your browser.
2. Register a new user account.
3. Log in and go to "New Prediction".
4. Fill out the patient vitals and symptoms and click Predict.
5. View the prediction results, SHAP explanation, and download the PDF report!
