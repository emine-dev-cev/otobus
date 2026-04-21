import requests
import json

API_URL = "http://localhost:80"

def ensure_user():
    user_data = {
        "email": "emine123@gmail.com",
        "password": "password123", # Default password for testing
        "full_name": "Emine"
    }
    
    print(f"Attempting to register user: {user_data['email']}")
    try:
        res = requests.post(f"{API_URL}/auth/register", json=user_data)
        if res.status_code == 201:
            print("User registered successfully.")
        elif res.status_code == 409:
            print("User already exists.")
        else:
            print(f"Failed to register: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ensure_user()
