import jwt
import os
from dotenv import load_dotenv
import time

load_dotenv()

secret = os.getenv("SUPABASE_JWT_SECRET")
if not secret:
    print("❌ Error: SUPABASE_JWT_SECRET not found in .env")
    exit(1)

# Create a token for a test user
user_id = "test-user-001"
payload = {
    "sub": user_id,           # Subject (User ID)
    "role": "authenticated",  # Supabase role
    "exp": int(time.time()) + 3600 * 24 # Expires in 24 hours
}

token = jwt.encode(payload, secret, algorithm="HS256")
print(f"\n🔑 Generated Token for user '{user_id}':\n")
print(token)
print("\n👉 Copy this token and paste it into the 'Authorize' button in Swagger UI.")