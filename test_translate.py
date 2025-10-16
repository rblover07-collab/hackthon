import requests

print('Testing /translate/ endpoint')
try:
    r = requests.post('http://127.0.0.1:8000/translate/', json={'text':'Hola, ¿cómo estás?'})
    print('Status:', r.status_code)
    print('Body:', r.text)
except Exception as e:
    print('Request failed:', e)
