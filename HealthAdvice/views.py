# HealthAdvice/views.py
from django.shortcuts import render

def health_advice(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/HealthAdvice.html', {"patient": patient})

def digestive(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/digestive.html', {"patient": patient})

def heart_disease(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/heartdisease.html', {"patient": patient})

def depression(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/depression.html', {"patient": patient})

def asthama(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/asthama.html', {"patient": patient})

def joint_pain(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/bodypain.html', {"patient": patient})

def diabetes(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/diabetes.html', {"patient": patient})

def balasana(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/balasana.html', {"patient": patient})

def pranayam(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/pranayam.html', {"patient": patient})

def boat_pose(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/paripurnanavasana.html', {"patient": patient})

def suryanamaskar(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/suryanamaskar.html', {"patient": patient})

def cobra_pose(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/cobra.html', {"patient": patient})

def tree_pose(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/varkasana.html', {"patient": patient})

def tadasana(request):  
    patient = None
    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        patient = request.user.patient

    return render(request, 'HealthAdvice/tadasana.html', {"patient": patient})