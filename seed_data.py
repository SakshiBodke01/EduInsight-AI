import os
import sys
import django
import pandas as pd

def train_ml_model():
    print("Step 1: Training the scikit-learn ML model...")
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ml_model.train_model import train_and_save_model
    train_and_save_model()

def setup_django_and_seed():
    print("Step 2: Configuring Django environment and applying migrations...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_portal.settings')
    django.setup()
    
    from django.core.management import call_command
    # Run migrations
    call_command('makemigrations', 'portal')
    call_command('migrate')
    
    from portal.models import User, StudentProfile, Subject, Result
    
    print("Step 3: Seeding default role accounts...")
    # 1. Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@school.edu',
            'role': 'admin',
            'is_superuser': True,
            'is_staff': True,
            'first_name': 'System',
            'last_name': 'Administrator'
        }
    )
    if created or admin_user:
        admin_user.set_password('admin123')
        admin_user.save()
        print(" -> Created Admin user: admin / admin123")
        
    # 2. Teacher
    teacher_user, created = User.objects.get_or_create(
        username='teacher',
        defaults={
            'email': 'teacher@school.edu',
            'role': 'teacher',
            'first_name': 'Sarah',
            'last_name': 'Conner'
        }
    )
    if created or teacher_user:
        teacher_user.set_password('teacher123')
        teacher_user.save()
        print(" -> Created Teacher user: teacher / teacher123")
        
    # Delete old student users first to ensure clean database seeding and prevent duplicates
    User.objects.filter(role='student').delete()

    # 3. Default Student
    student_user, created = User.objects.get_or_create(
        username='student',
        defaults={
            'email': 'student@school.edu',
            'role': 'student',
            'first_name': 'Rohan',
            'last_name': 'Deshmukh'
        }
    )
    if created or student_user:
        student_user.set_password('student123')
        student_user.save()
        
        profile = student_user.student_profile
        profile.roll_number = 'S-1001'
        profile.class_name = 'Semester 4'
        profile.department = 'Data Science'
        profile.save()
        print(" -> Created Student user: student / student123")

    print("Step 4: Seeding standard subjects...")
    subjects_data = [
        ('Mathematics', 'MATH101'),
        ('Physics', 'PHYS101'),
        ('Introduction to AI', 'AI101'),
        ('Database Management', 'DBMS101')
    ]
    
    subjects = []
    for name, code in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=code,
            defaults={'name': name}
        )
        subjects.append(subject)
        print(f" -> Subject configured: {name} ({code})")

    print("Step 5: Seeding mock student performance records...")
    # Add a few more student users to demonstrate analytics dashboards (using Marathi names)
    mock_students = [
        # (username, first_name, last_name, roll_number, class_name, department, pass_rate_expected)
        ('snehal_patil', 'Snehal', 'Patil', 'S-1002', 'Semester 4', 'Data Science', 'high'),
        ('aditya_joshi', 'Aditya', 'Joshi', 'S-1003', 'Semester 4', 'Information Tech', 'medium'),
        ('aniket_kulkarni', 'Aniket', 'Kulkarni', 'S-1004', 'Semester 4', 'Data Science', 'low'),
    ]
    
    student_profiles = []
    for username, f_name, l_name, roll, cls, dept, rate in mock_students:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@school.edu",
                'role': 'student',
                'first_name': f_name,
                'last_name': l_name
            }
        )
        user.set_password(f"{username}123")
        user.save()
        
        profile = user.student_profile
        profile.roll_number = roll
        profile.class_name = cls
        profile.department = dept
        profile.save()
        student_profiles.append((profile, rate))
        print(f" -> Configured mock student: {f_name} {l_name} ({roll})")

    # Add default student results too
    student_profiles.append((student_user.student_profile, 'high'))

    # Seed result parameters (attendance, study_hours, mid_term, assignment)
    result_presets = {
        'high': [
            (95.0, 18.0, 92.0, 88.0), # Math
            (92.0, 15.0, 85.0, 80.0), # Physics
            (98.0, 20.0, 94.0, 96.0), # AI
            (90.0, 12.0, 80.0, 82.0), # DBMS
        ],
        'medium': [
            (76.0, 8.0, 65.0, 68.0),
            (80.0, 10.0, 60.0, 62.0),
            (72.0, 6.0, 55.0, 58.0),
            (82.0, 7.5, 70.0, 65.0),
        ],
        'low': [
            (52.0, 2.0, 30.0, 45.0), # Failure risk
            (60.0, 4.0, 42.0, 50.0),
            (45.0, 1.5, 28.0, 35.0),
            (58.0, 3.0, 38.0, 40.0),
        ]
    }

    print("Step 6: Running calculations and seeding student grades...")
    for profile, rate in student_profiles:
        presets = result_presets[rate]
        for i, subject in enumerate(subjects):
            preset = presets[i]
            # Automatically triggers prediction and saves
            Result.objects.update_or_create(
                student=profile,
                subject=subject,
                defaults={
                    'attendance_percentage': preset[0],
                    'study_hours': preset[1],
                    'mid_term_marks': preset[2],
                    'assignment_marks': preset[3],
                }
            )
    print(" -> DB Seeding complete!")

def generate_sample_csv():
    print("Step 7: Generating sample grades CSV sheet for teacher demo...")
    data = {
        'student_username': ['sachin_shinde', 'swati_kadam', 'milind_pawar', 'varsha_gaikwad'],
        'attendance_percentage': [90.5, 82.0, 55.0, 96.5],
        'study_hours': [14.5, 8.0, 22.0, 16.0],
        'mid_term_marks': [85.0, 62.0, 45.0, 94.0],
        'assignment_marks': [88.0, 70.0, 35.0, 92.0]
    }
    df = pd.DataFrame(data)
    
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    csv_path = os.path.join(static_dir, 'sample_grades.csv')
    df.to_csv(csv_path, index=False)
    print(f" -> Generated template at {csv_path}\n")

if __name__ == '__main__':
    train_ml_model()
    setup_django_and_seed()
    generate_sample_csv()
    print("All tasks finished successfully. Run 'python manage.py runserver' to launch the portal.")
