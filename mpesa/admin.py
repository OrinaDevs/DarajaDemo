from django.contrib import admin
from .models import MpesaTransaction

# Register your models here.
@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "amount", "status", "mpesa_receipt", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("phone_number", "checkout_request_id", "mpesa_receipt")
    readonly_fields = ("created_at", "updated_at")