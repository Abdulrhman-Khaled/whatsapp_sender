
import frappe
import requests
import frappe
from frappe.model.document import Document
class whatsappmessage(Document):  
 @frappe.whitelist()
 def msg(self, token, recipient, url, deviceId):
   payload = {
        "device": deviceId,
        "phone": recipient,
        "authKey": token,
        "message": "This message is for testing"
       }
   
   try:
           response = requests.post(url, data=payload)
           return response.text
   except Exception as e:
          return e
   