import requests

try:
    res = requests.post('http://localhost:8000/api/suggest-medicine', json={"transcript": "Patient: I have a headache and fever for 3 days."})
    print("Status:", res.status_code)
    print("Response:", res.text)
except Exception as e:
    print("Error:", str(e))
