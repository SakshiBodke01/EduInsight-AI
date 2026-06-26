from rest_framework import serializers
from portal.models import User, StudentProfile, Subject, Result

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'roll_number', 'class_name', 'department']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code']

class ResultSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    
    # Write support using IDs
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), source='student', write_only=True
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), source='subject', write_only=True
    )

    class Meta:
        model = Result
        fields = [
            'id', 'student', 'subject', 'student_id', 'subject_id',
            'attendance_percentage', 'study_hours', 'mid_term_marks', 'assignment_marks',
            'predicted_grade', 'predicted_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['predicted_grade', 'predicted_status']
