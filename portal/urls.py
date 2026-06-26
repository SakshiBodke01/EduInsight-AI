from django.urls import path
from portal import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Landing Page
    path('', views.landing_view, name='landing'),
    
    # Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    
    # Core Operations
    path('upload/', views.upload_csv, name='upload_csv'),
    path('result/add/', views.add_edit_result, name='add_result'),
    path('result/edit/<int:pk>/', views.add_edit_result, name='edit_result'),
    path('student/<int:pk>/', views.student_detail, name='student_detail'),
    path('student/<int:pk>/pdf/', views.download_pdf_report, name='download_pdf'),
    path('seed-demo-data/', views.seed_demo_data_view, name='seed_demo_data'),
]
