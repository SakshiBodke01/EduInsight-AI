import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_portal.settings')

application = get_wsgi_application()
app = application

# Run database setup on Vercel if /tmp/db.sqlite3 does not exist
if os.environ.get('VERCEL'):
    db_path = '/tmp/db.sqlite3'
    if not os.path.exists(db_path):
        try:
            print("Vercel deployment detected. Initializing database in /tmp...")
            from django.core.management import call_command
            # Run migrations
            call_command('migrate', '--noinput')
            print("Migrations completed.")
            
            # Run seeding inline
            from portal.models import User, StudentProfile, Subject, Result
            
            # Seed Admin
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
                
            # Seed Teacher
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
                
            # Seed Default Student (Rohan Deshmukh)
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
                
            # Seed Subjects
            subjects_data = [
                ('Mathematics', 'MATH101'),
                ('Physics', 'PHYS101'),
                ('Introduction to AI', 'AI101'),
                ('Database Management', 'DBMS101')
            ]
            subjects = []
            for name, code in subjects_data:
                subject, _ = Subject.objects.get_or_create(code=code, defaults={'name': name})
                subjects.append(subject)
                
            # Seed mock Marathi students
            mock_students = [
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
                
            # Seed Results
            result_presets = {
                'high': [
                    (95.0, 18.0, 92.0, 88.0),
                    (92.0, 15.0, 85.0, 80.0),
                    (98.0, 20.0, 94.0, 96.0),
                    (90.0, 12.0, 80.0, 82.0),
                ],
                'medium': [
                    (76.0, 8.0, 65.0, 68.0),
                    (80.0, 10.0, 60.0, 62.0),
                    (72.0, 6.0, 55.0, 58.0),
                    (82.0, 7.5, 70.0, 65.0),
                ],
                'low': [
                    (52.0, 2.0, 30.0, 45.0),
                    (60.0, 4.0, 42.0, 50.0),
                    (45.0, 1.5, 28.0, 35.0),
                    (58.0, 3.0, 38.0, 40.0),
                ]
            }
            
            student_profiles.append((student_user.student_profile, 'high'))
            for profile, rate in student_profiles:
                presets = result_presets[rate]
                for i, subject in enumerate(subjects):
                    preset = presets[i]
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
            print("Database successfully initialized and seeded on Vercel.")
        except Exception as e:
            print("Error initializing database on Vercel startup:", e)
