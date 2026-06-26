from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'results', views.ResultViewSet, basename='result-api')

urlpatterns = [
    path('analytics/', views.AnalyticsView.as_view(), name='analytics-api'),
    path('', include(router.urls)),
]
