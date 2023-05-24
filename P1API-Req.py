import requests
import json

url = "https://api.priority1.com/v2/ltl/shipments/status"

payload = json.dumps({
  "identifierType": "PURCHASE_ORDER",
  "identifierValue": "DEN1717"
})
headers = {
  'X-API-KEY': 'b80ebbe6-d4d7-48ce-ba19-3686d455eac4',
  'accept': 'application/json',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
