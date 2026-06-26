import os
import json
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db.models import Avg, Count

from portal.models import User, StudentProfile, Subject, Result
from portal.forms import UserRegistrationForm, CSVUploadForm, ResultForm
from portal.decorators import teacher_required, student_required, admin_required
from portal.utils.pdf_generator import generate_student_report_pdf
from portal.utils.ml_engine import predict_student_performance

def landing_view(request):
    return render(request, 'portal/landing.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('dashboard')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
        messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def dashboard_view(request):
    role = request.user.role
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'teacher':
        return redirect('teacher_dashboard')
    elif role == 'student':
        return redirect('student_dashboard')
    return redirect('login')

@login_required
@admin_required
def admin_dashboard(request):
    users_count = User.objects.count()
    teachers_count = User.objects.filter(role='teacher').count()
    students_count = User.objects.filter(role='student').count()
    subjects_count = Subject.objects.count()
    results_count = Result.objects.count()
    
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    
    context = {
        'users_count': users_count,
        'teachers_count': teachers_count,
        'students_count': students_count,
        'subjects_count': subjects_count,
        'results_count': results_count,
        'recent_users': recent_users,
    }
    return render(request, 'dashboard/admin.html', context)

@login_required
@teacher_required
def teacher_dashboard(request):
    students = StudentProfile.objects.all()
    results = Result.objects.select_related('student__user', 'subject').all()
    
    # Calculate global analytics metrics
    total_students = students.count()
    total_results = results.count()
    
    avg_attendance = results.aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0.0
    avg_mid_term = results.aggregate(Avg('mid_term_marks'))['mid_term_marks__avg'] or 0.0
    
    # Calculate Pass/Fail counts
    pass_count = results.filter(predicted_status='Pass').count()
    fail_count = results.filter(predicted_status='Fail').count()
    pass_rate = (pass_count / total_results * 100) if total_results > 0 else 0.0
    
    # Subject breakdown
    subject_stats = Result.objects.values('subject__name', 'subject__code').annotate(
        avg_mid=Avg('mid_term_marks'),
        avg_assign=Avg('assignment_marks'),
        avg_attend=Avg('attendance_percentage'),
        total=Count('id')
    )
    
    # Structure data for Chart.js
    chart_subjects = [s['subject__name'] for s in subject_stats]
    chart_avg_mid = [float(s['avg_mid']) for s in subject_stats]
    chart_avg_assign = [float(s['avg_assign']) for s in subject_stats]
    
    context = {
        'total_students': total_students,
        'total_results': total_results,
        'avg_attendance': round(avg_attendance, 1),
        'avg_mid_term': round(avg_mid_term, 1),
        'pass_count': pass_count,
        'fail_count': fail_count,
        'pass_rate': round(pass_rate, 1),
        'students': students,
        'results': results[:20],  # show latest 20 results
        'subject_stats': subject_stats,
        'chart_subjects': json.dumps(chart_subjects),
        'chart_avg_mid': json.dumps(chart_avg_mid),
        'chart_avg_assign': json.dumps(chart_avg_assign),
    }
    return render(request, 'dashboard/teacher.html', context)

@login_required
@student_required
def student_dashboard(request):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    results = Result.objects.filter(student=student_profile).select_related('subject')
    
    # Student specific stats
    num_subjects = results.count()
    avg_attendance = results.aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0.0
    
    pass_count = results.filter(predicted_status='Pass').count()
    fail_count = results.filter(predicted_status='Fail').count()
    
    # Prepping data for student chart
    chart_subjects = [r.subject.name for r in results]
    chart_mid_marks = [r.mid_term_marks for r in results]
    chart_assign_marks = [r.assignment_marks for r in results]
    
    context = {
        'student': student_profile,
        'results': results,
        'num_subjects': num_subjects,
        'avg_attendance': round(avg_attendance, 1),
        'pass_count': pass_count,
        'fail_count': fail_count,
        'chart_subjects': json.dumps(chart_subjects),
        'chart_mid_marks': json.dumps(chart_mid_marks),
        'chart_assign_marks': json.dumps(chart_assign_marks),
    }
    return render(request, 'dashboard/student.html', context)

@login_required
@teacher_required
def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            subject = form.cleaned_data['subject']
            
            try:
                # Read file depending on extension
                if csv_file.name.endswith('.csv'):
                    df = pd.read_csv(csv_file)
                else:
                    df = pd.read_excel(csv_file)
                
                # Check for required columns
                required_cols = {'student_username', 'attendance_percentage', 'study_hours', 'mid_term_marks', 'assignment_marks'}
                if not required_cols.issubset(df.columns):
                    missing = required_cols - set(df.columns)
                    messages.error(request, f"Missing columns in file: {', '.join(missing)}")
                    return render(request, 'portal/upload.html', {'form': form})
                
                success_count = 0
                error_count = 0
                
                for _, row in df.iterrows():
                    username = str(row['student_username']).strip()
                    try:
                        # Smart parsing for names (e.g. sachin_shinde -> Sachin Shinde)
                        parts = username.split('_')
                        first_name = parts[0].capitalize()
                        last_name = parts[1].capitalize() if len(parts) > 1 else 'Student'

                        # Find or create User and Profile
                        user, created = User.objects.get_or_create(
                            username=username,
                            defaults={
                                'role': 'student',
                                'first_name': first_name,
                                'last_name': last_name,
                                'email': f"{username}@school.edu"
                            }
                        )
                        if created:
                            # Set password
                            user.set_password(f"{username}123")
                            user.save()
                        
                        profile = user.student_profile
                        
                        # Set default values if roll number not set
                        if not profile.roll_number:
                            profile.roll_number = f"R-{user.id:04d}"
                            profile.save()
                            
                        # Predict grade/status
                        grade, status = predict_student_performance(
                            row['attendance_percentage'],
                            row['study_hours'],
                            row['mid_term_marks'],
                            row['assignment_marks']
                        )
                        
                        # Update or create result
                        Result.objects.update_or_create(
                            student=profile,
                            subject=subject,
                            defaults={
                                'attendance_percentage': float(row['attendance_percentage']),
                                'study_hours': float(row['study_hours']),
                                'mid_term_marks': float(row['mid_term_marks']),
                                'assignment_marks': float(row['assignment_marks']),
                                'predicted_grade': grade,
                                'predicted_status': status
                            }
                        )
                        success_count += 1
                    except Exception as e:
                        print(f"Error importing row for student {username}: {e}")
                        error_count += 1
                
                if success_count > 0:
                    messages.success(request, f"Successfully uploaded and predicted grades for {success_count} students.")
                if error_count > 0:
                    messages.warning(request, f"Failed to import {error_count} student rows due to format errors.")
                return redirect('teacher_dashboard')
                
            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
    else:
        form = CSVUploadForm()
    return render(request, 'portal/upload.html', {'form': form})

@login_required
@teacher_required
def add_edit_result(request, pk=None):
    if pk:
        result = get_object_or_404(Result, pk=pk)
        title = "Edit Result"
    else:
        result = None
        title = "Add Result"
        
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, f"Result successfully saved.")
            return redirect('teacher_dashboard')
    else:
        form = ResultForm(instance=result)
        
    return render(request, 'portal/result_form.html', {'form': form, 'title': title})

@login_required
def student_detail(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    # Check if student is requesting their own profile, or user is teacher/admin
    if request.user.role == 'student' and request.user.student_profile.pk != student.pk:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    results = Result.objects.filter(student=student).select_related('subject')
    
    # Calculate stats
    num_subjects = results.count()
    avg_attendance = results.aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0.0
    avg_mid_term = results.aggregate(Avg('mid_term_marks'))['mid_term_marks__avg'] or 0.0
    avg_assignment = results.aggregate(Avg('assignment_marks'))['assignment_marks__avg'] or 0.0
    
    pass_count = results.filter(predicted_status='Pass').count()
    fail_count = results.filter(predicted_status='Fail').count()
    
    context = {
        'student': student,
        'results': results,
        'num_subjects': num_subjects,
        'avg_attendance': round(avg_attendance, 1),
        'avg_mid_term': round(avg_mid_term, 1),
        'avg_assignment': round(avg_assignment, 1),
        'pass_count': pass_count,
        'fail_count': fail_count,
    }
    return render(request, 'portal/student_detail.html', context)

@login_required
def download_pdf_report(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    
    # Role-based access control
    if request.user.role == 'student' and request.user.student_profile.pk != student.pk:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    results = Result.objects.filter(student=student).select_related('subject')
    if not results.exists():
        messages.error(request, "No result data available to generate PDF report.")
        return redirect('student_detail', pk=pk)
        
    try:
        pdf_buffer = generate_student_report_pdf(student, results)
        
        filename = f"Result_Report_{student.roll_number or student.user.username}.pdf"
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, f"Error generating PDF: {e}")
        return redirect('student_detail', pk=pk)

@login_required
@teacher_required
def seed_demo_data_view(request):
    try:
        from portal.models import User, StudentProfile, Subject, Result
        
        # 1. Ensure subjects exist
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
            
        # Delete old student users first to ensure clean database seeding and prevent duplicates
        User.objects.filter(role='student').delete()

        # 2. Configure mock student profiles (using Marathi names)
        mock_students = [
            ('student', 'Rohan', 'Deshmukh', 'S-1001', 'Semester 4', 'Data Science', 'high'),
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
            if created:
                user.set_password(f"{username}123")
                user.save()
            
            profile = user.student_profile
            profile.roll_number = roll
            profile.class_name = cls
            profile.department = dept
            profile.save()
            student_profiles.append((profile, rate))
            
        # 3. Presets for seeding results
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
        
        # 4. Save results
        seeded_count = 0
        for profile, rate in student_profiles:
            presets = result_presets[rate]
            for i, subject in enumerate(subjects):
                preset = presets[i]
                res, created = Result.objects.update_or_create(
                    student=profile,
                    subject=subject,
                    defaults={
                        'attendance_percentage': preset[0],
                        'study_hours': preset[1],
                        'mid_term_marks': preset[2],
                        'assignment_marks': preset[3],
                    }
                )
                if created:
                    seeded_count += 1
                    
        if seeded_count > 0:
            messages.success(request, f"Successfully seeded {seeded_count} academic results.")
        else:
            messages.info(request, "Database already populated with standard demo datasets.")
            
    except Exception as e:
        messages.error(request, f"Seeding failed: {e}")
        
    return redirect('dashboard')

