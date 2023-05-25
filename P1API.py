import requests
import json

class P1Helper():
  url = "https://api.priority1.com/v2/ltl/shipments/status"

  def getTracking(self, shipmentID:str) -> str:

    payload = json.dumps({
    "identifierType": "PURCHASE_ORDER",
    "identifierValue": f"{shipmentID}"
    })
    headers = {
      'X-API-KEY': 'b80ebbe6-d4d7-48ce-ba19-3686d455eac4',
      'accept': 'application/json',
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", self.url, headers=headers, data=payload)

    print(response.text)
    return response.text

    
  def track(self, shipmentID:str):
    trackingResultJSON = json.loads(self.getTracking(shipmentID))
    statuses = trackingResultJSON['shipments'][0]['trackingStatuses']

    status = 'In Transit'
    deliveryDate = ''

    for i in statuses:
      if (i['status'] == 'Completed') or ('Completed' in i['statusReason']) :
        status = 'Delivered'
        deliveryDate = i['timeStamp'][:10]

    return {'status' : status,
            'deliveryDate' : deliveryDate}


    