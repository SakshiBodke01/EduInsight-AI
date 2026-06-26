import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def generate_synthetic_data(num_samples=1200, random_seed=42):
    np.random.seed(random_seed)
    
    # Generate realistic features
    attendance = np.random.uniform(40, 100, num_samples)
    study_hours = np.random.uniform(1, 25, num_samples)
    mid_term = np.random.uniform(20, 100, num_samples)
    assignment = np.random.uniform(20, 100, num_samples)
    
    # Formula for final score (with some noise)
    # attendance (30%), study hours (10%), mid term (35%), assignments (25%)
    noise = np.random.normal(0, 4, num_samples)
    final_score = (
        0.30 * attendance + 
        0.10 * (study_hours * 4) +  # scale study hours to ~100 max
        0.35 * mid_term + 
        0.25 * assignment + 
        noise
    )
    final_score = np.clip(final_score, 0, 100)
    
    # Map final score to grades
    # A: >= 85, B: 70-84, C: 55-69, D: 40-54, F: < 40
    grades = []
    for score in final_score:
        if score >= 85:
            grades.append('A')
        elif score >= 70:
            grades.append('B')
        elif score >= 55:
            grades.append('C')
        elif score >= 40:
            grades.append('D')
        else:
            grades.append('F')
            
    df = pd.DataFrame({
        'attendance_percentage': attendance,
        'study_hours': study_hours,
        'mid_term_marks': mid_term,
        'assignment_marks': assignment,
        'predicted_grade': grades
    })
    
    return df

def train_and_save_model():
    print("Generating synthetic student data...")
    df = generate_synthetic_data()
    
    X = df[['attendance_percentage', 'study_hours', 'mid_term_marks', 'assignment_marks']]
    y = df['predicted_grade']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training RandomForest model to predict student grades...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print("\nModel Evaluation:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    os.makedirs('ml_model', exist_ok=True)
    model_path = os.path.join('ml_model', 'student_grade_predictor.joblib')
    joblib.dump(model, model_path)
    print(f"Model successfully saved to {model_path}\n")

if __name__ == '__main__':
    train_and_save_model()
