from django.urls import path 
from . import views 

app_name = "mpesa"

urlpatterns = [
    path("stk-push/", views.initiate_payment, name="initiate_payment"),
    path("callback/", views.mpesa_callback, name="mpesa_callback"),
    path("status/<str:checkout_request_id>/", views.check_status, name="check_status"),
]