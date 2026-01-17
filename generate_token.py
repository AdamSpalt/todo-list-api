import jwt
import os
from dotenv import load_dotenv
import time

load_dotenv()

secret = os.getenv("SUPABASE_JWT_SECRET")
if not secret:
    print("❌ Error: SUPABASE_JWT_SECRET not found in .env")
    exit(1)

def generate_token(user_id, days=1):
    payload = {
        "sub": user_id,           # Subject (User ID)
        "role": "authenticated",  # Supabase role
        "exp": int(time.time()) + 3600 * 24 * days # Expires in X days
    }
    return jwt.encode(payload, secret, algorithm="HS256")

if __name__ == "__main__":
    print("--- 🔑 API Token Generator ---")
    user_id = input("Enter User ID (e.g., 'partner-name' or 'test-user'): ") or "test-user-001"
    days_input = input("Enter validity in days (default 1): ") or "1"
    
    try:
        days = int(days_input)
    except ValueError:
        print("Invalid days. Using 1.")
        days = 1

    token = generate_token(user_id, days)
    
    print(f"\n✅ Generated Token for '{user_id}' valid for {days} days:\n")
    print(token)
    print("\n👉 Send this token to your third-party integration.")