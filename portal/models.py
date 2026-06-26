from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    class_name = models.CharField(max_length=50, default='Class A')
    department = models.CharField(max_length=50, default='Data Science')
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.roll_number or 'No Roll No'}"

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Result(models.Model):
    STATUS_CHOICES = (
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
    )
    GRADE_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    )
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='results')
    
    attendance_percentage = models.FloatField(default=75.0)
    study_hours = models.FloatField(default=5.0)
    mid_term_marks = models.FloatField(default=60.0)
    assignment_marks = models.FloatField(default=60.0)
    
    predicted_grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    predicted_status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'subject')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} - Predicted: {self.predicted_grade}"
        
    def save(self, *args, **kwargs):
        # Automatically run prediction on save if not already defined
        from portal.utils.ml_engine import predict_student_performance
        
        grade, status = predict_student_performance(
            self.attendance_percentage,
            self.study_hours,
            self.mid_term_marks,
            self.assignment_marks
        )
        self.predicted_grade = grade
        self.predicted_status = status
        
        super().save(*args, **kwargs)

# Automatically create profile for student user
@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'student':
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    if instance.role == 'student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
