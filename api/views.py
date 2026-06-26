from rest_framework import viewsets, views, permissions
from rest_framework.response import Response
from django.db.models import Avg, Count
from portal.models import Result, StudentProfile, Subject
from api.serializers import ResultSerializer

class ResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows results to be viewed or edited.
    Supports filtering by subject or student.
    """
    queryset = Result.objects.select_related('student__user', 'subject').all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = self.queryset
        subject_id = self.request.query_params.get('subject_id')
        student_id = self.request.query_params.get('student_id')
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
            
        return queryset

class AnalyticsView(views.APIView):
    """
    API endpoint that returns aggregate school/class performance analytics.
    Useful for populating external charts.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, format=None):
        results = Result.objects.all()
        total_results = results.count()
        
        if total_results == 0:
            return Response({
                'total_results': 0,
                'pass_rate': 0,
                'avg_attendance': 0,
                'avg_mid_term': 0,
                'avg_assignment': 0,
                'grade_distribution': {},
                'subject_performance': []
            })
            
        # Overall metrics
        pass_count = results.filter(predicted_status='Pass').count()
        pass_rate = round((pass_count / total_results) * 100, 2)
        
        avg_attendance = round(results.aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0.0, 2)
        avg_mid = round(results.aggregate(Avg('mid_term_marks'))['mid_term_marks__avg'] or 0.0, 2)
        avg_assign = round(results.aggregate(Avg('assignment_marks'))['assignment_marks__avg'] or 0.0, 2)
        
        # Grade Distribution
        grade_dist = results.values('predicted_grade').annotate(count=Count('id')).order_by('predicted_grade')
        grade_distribution = {item['predicted_grade']: item['count'] for item in grade_dist}
        
        # Subject-wise average grades
        subject_stats = Result.objects.values('subject__name', 'subject__code').annotate(
            avg_mid_term=Avg('mid_term_marks'),
            avg_assignment=Avg('assignment_marks'),
            avg_attendance=Avg('attendance_percentage'),
            count=Count('id')
        )
        
        subject_performance = []
        for s in subject_stats:
            subject_performance.append({
                'subject_name': s['subject__name'],
                'subject_code': s['subject__code'],
                'avg_mid_term': round(s['avg_mid_term'], 2),
                'avg_assignment': round(s['avg_assignment'], 2),
                'avg_attendance': round(s['avg_attendance'], 2),
                'total_records': s['count']
            })
            
        return Response({
            'total_results': total_results,
            'pass_rate': pass_rate,
            'avg_attendance': avg_attendance,
            'avg_mid_term': avg_mid,
            'avg_assignment': avg_assign,
            'grade_distribution': grade_distribution,
            'subject_performance': subject_performance
        })
