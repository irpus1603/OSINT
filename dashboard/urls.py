from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('threat-classification/', views.threat_classification_view, name='threat_classification'),
    path('regional-security/', views.regional_security_view, name='regional_security'),
    path('sentiment/', views.sentiment_analysis_view, name='sentiment_analysis'),
    path('sources/', views.sources_view, name='sources'),
    path('keywords/', views.keywords_view, name='keywords'),
    path('security-summary/', views.security_summary_view, name='security_summary'),
    path('security-summary/pdf/', views.security_summary_pdf_view, name='security_summary_pdf'),
    path('alerts/', views.alerts_view, name='alerts'),
]