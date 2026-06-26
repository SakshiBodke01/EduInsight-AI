import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings

# Path to the serialized model file
MODEL_DIR = os.path.join(settings.BASE_DIR, 'ml_model')
MODEL_PATH = os.path.join(MODEL_DIR, 'student_grade_predictor.joblib')

_cached_model = None

def load_ml_model():
    """Loads the ML model from disk, caching it in memory."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model
    
    if os.path.exists(MODEL_PATH):
        try:
            _cached_model = joblib.load(MODEL_PATH)
            print("Successfully loaded ML model from disk.")
            return _cached_model
        except Exception as e:
            print(f"Error loading ML model from disk: {e}")
    else:
        print(f"ML model file not found at {MODEL_PATH}. Falling back to rule-based prediction.")
    return None

def predict_student_performance(attendance, study_hours, mid_term, assignment):
    """
    Predicts the grade (A, B, C, D, F) and status (Pass/Fail) for a student.
    Uses the trained ML model if available; falls back to a rule-based system if not.
    """
    model = load_ml_model()
    
    if model is not None:
        try:
            # Features must match training: attendance_percentage, study_hours, mid_term_marks, assignment_marks
            input_df = pd.DataFrame([{
                'attendance_percentage': float(attendance),
                'study_hours': float(study_hours),
                'mid_term_marks': float(mid_term),
                'assignment_marks': float(assignment)
            }])
            grade = model.predict(input_df)[0]
            status = 'Fail' if grade == 'F' else 'Pass'
            return grade, status
        except Exception as e:
            print(f"Prediction error using ML model: {e}. Falling back to rule-based.")
            
    # Fallback Rule-based engine
    # Replicates the general logic of synthetic training data
    score = 0.30 * float(attendance) + 0.10 * (float(study_hours) * 4) + 0.35 * float(mid_term) + 0.25 * float(assignment)
    if score >= 85:
        grade = 'A'
    elif score >= 70:
        grade = 'B'
    elif score >= 55:
        grade = 'C'
    elif score >= 40:
        grade = 'D'
    else:
        grade = 'F'
        
    status = 'Fail' if grade == 'F' else 'Pass'
    return grade, status

def predict_batch_performance(df):
    """
    Predicts grades and status for a pandas DataFrame.
    DataFrame must contain columns: attendance_percentage, study_hours, mid_term_marks, assignment_marks
    Returns the DataFrame with new columns: predicted_grade, predicted_status
    """
    model = load_ml_model()
    
    # Ensure float conversion
    df = df.copy()
    df['attendance_percentage'] = df['attendance_percentage'].astype(float)
    df['study_hours'] = df['study_hours'].astype(float)
    df['mid_term_marks'] = df['mid_term_marks'].astype(float)
    df['assignment_marks'] = df['assignment_marks'].astype(float)
    
    if model is not None:
        try:
            features = df[['attendance_percentage', 'study_hours', 'mid_term_marks', 'assignment_marks']]
            df['predicted_grade'] = model.predict(features)
            df['predicted_status'] = df['predicted_grade'].apply(lambda x: 'Fail' if x == 'F' else 'Pass')
            return df
        except Exception as e:
            print(f"Batch prediction error using ML model: {e}. Falling back to rule-based.")
            
    # Rule-based fallback for batch
    grades = []
    statuses = []
    for idx, row in df.iterrows():
        grade, status = predict_student_performance(
            row['attendance_percentage'], 
            row['study_hours'], 
            row['mid_term_marks'], 
            row['assignment_marks']
        )
        grades.append(grade)
        statuses.append(status)
        
    df['predicted_grade'] = grades
    df['predicted_status'] = statuses
    return df
