from django.shortcuts import render
import json
import logging 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import MpesaTransaction
from .utils import stk_push

# Create your views here.

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def initiate_payment(request):
    try:
        data = json.loads(request.body)
        phone_number = data.get("phone_number")
        amount = data.get("amount")

        if not phone_number or not amount:
            return JsonResponse({"error": "phone_number and amount required"}, status=400)

        response = stk_push(phone_number, amount)

        if response.get("ResponseCode") == "0":
            MpesaTransaction.objects.create(
                checkout_request_id = response["CheckoutRequestID"],
                merchant_request_id = response["MerchantRequestID"],
                phone_number = phone_number,
                amount = amount,
            )
            return JsonResponse({"message": "STK push sent", "data": response})

        return JsonResponse({"error": "STK push failed", "data": response}, status=400)

    except Exception as e:
        logger.exception("STK push initiation failed")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def mpesa_callback(request):
    try:
        data = json.loads(request.body)
        logger.info("Mpesa callback received: %s", data)

        stk_callback = data.get("Body", {}).get("stkCallback", {})
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")

        try: 
            transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
        except MpesaTransaction.DoesNotExist:
            logger.warning("No transaction found for %s", checkout_request_id)
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

        if result_code == 0:
            meatadata = stk_callback.get("CallbackMetadata", {}).get("Item", {})
            receipt = next((i["Value"] for i in meatadata if i["Name"] == "MpesaReceiptNumber"), None)

            transaction.status = "Success"
            transaction.mpesa_receipt = receipt
            transaction.result_desc = result_desc

        else:
            transaction.status = "Failed"
            transaction.result_desc = result_desc

        transaction.save()
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    except Exception as e:
        logger.exception("Callback Processing failed")
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Failed"}, status=500)