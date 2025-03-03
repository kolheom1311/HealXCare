# HealthAdvice/urls.py
from django.urls import path
from . import views

app_name = "health-advice"  # Namespacing is good!

urlpatterns = [
    path('', views.health_advice, name='health_advice'),  # Updated view name
    path('digestive-disorders/', views.digestive, name='digestive'),
    path('heart-disease/', views.heart_disease, name='heartdisease'),
    path('depression/', views.depression, name='depression'),
    path('asthama/', views.asthama, name='asthama'),
    path('joint-pain/', views.joint_pain, name='jointpain'),
    path('diabetes/', views.diabetes, name='diabetes'),
    path('balasana/', views.balasana, name='balasana'),
    path('pranayam/', views.pranayam, name='pranayam'),
    path('boat-pose/', views.boat_pose, name='boatpose'),
    path('suryanamaskar/', views.suryanamaskar, name='suryanamaskar'),
    path('cobra-pose/', views.cobra_pose, name='cobra-pose'),
    path('tree-pose/', views.tree_pose, name='tree-pose'),
    path('tadasana/', views.tadasana, name='tadasana'),
]
