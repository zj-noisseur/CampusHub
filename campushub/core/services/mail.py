import os
from dotenv import load_dotenv
load_dotenv()
import resend


if __name__ == "__main__":
    key = os.getenv('RESEND')
    print(key)
    resend.api_key = os.getenv('RESEND')
    params: resend.Emails.SendParams = {
        "from": "CampusHub <onboarding@resend.dev>",
        "to": ["delivered@resend.dev"],
        "subject": "Sandboxed testing mail",
        "html": "<strong>Hi there!</strong>",
    }

    email = resend.Emails.send(params)
    print(email)