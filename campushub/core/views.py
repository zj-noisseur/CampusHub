from django.shortcuts import render
from django.http import JsonResponse
from .scraper import read
from django.conf import settings

# Create your views here.

def fetch_apify_data(request):
    try:
        data = read(api_url=settings.APIFY_API_URL, api_key=settings.APIFY_API_KEY)
        return JsonResponse({"success": True, "data": data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
