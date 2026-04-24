import os

AUTH_USER_MODEL = 'core.User'
# Apify API Configuration
APIFY_API_URL = os.getenv("APIFY_API_URL", "https://api.apify.com/v2/actor-runs")
APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")

TIME_ZONE = 'Asia/Kuala_Lumpur'


USE_TZ = True