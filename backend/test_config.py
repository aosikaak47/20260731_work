import requests

response = requests.get("http://localhost:8000/api/v1/config")
print("Status:", response.status_code)
print("Response:", response.text)