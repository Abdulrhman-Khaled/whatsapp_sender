import frappe
from frappe import _
from frappe.email.doctype.notification.notification import Notification, get_context, json
from frappe.core.doctype.role.role import get_info_based_on_role, get_user_info
import requests
import json
import io
import base64
from frappe.utils import now
import time
from frappe import enqueue
# to send whatsapp message
class ERPGulfNotification(Notification):
   
  def send_whatsapp(self,doc,context):

    token = frappe.get_doc('whatsapp message').get('token')
    url =  frappe.get_doc('whatsapp message').get('url')
    deviceId =  frappe.get_doc('whatsapp message').get('device_id')
    msg = frappe.render_template(self.message, context)

    recipients = self.get_receiver_list(doc,context)
    multiple_numbers = [str(r).strip() for r in recipients if r]
    add_multiple_numbers_to_url = ','.join(multiple_numbers) 
  
    payload = {
        "device": deviceId,
        "phone": add_multiple_numbers_to_url,
        "authKey": token,
        "message": msg
       }
    try:
        time.sleep(10)
        response = requests.post(url, data=payload)
      # when the msg send is success then its details are stored into whatsapp_sender log  
        if response.status_code == 200:
            response_json = response.json()
            if "sent" in  response_json and  response_json["sent"] == "true":
            # Log success
              current_time =now()
              msg = frappe.render_template(self.message, context)
              frappe.get_doc({"doctype":"whatsapp_sender log","title":"Whatsapp message successfully sent ","message":msg,"to_number":add_multiple_numbers_to_url,"time":current_time }).insert()
            elif "error" in  response_json:
            # Log error
              frappe.log("WhatsApp API Error: " ,  response_json.get("error"))
            else:
            # Log unexpected response
              frappe.log("Unexpected response from WhatsApp API")
        else:
        # Log HTTP error
             frappe.log("WhatsApp API returned a non-200 status code: " ,str(response.status_code))
        return response.text
    except Exception as e:
        frappe.log_error(title='Failed to send notification', message=frappe.get_traceback())  
 
  def send(self, doc):

    context = {"doc":doc, "alert": self, "comments": None}
    if doc.get("_comments"):
        context["comments"] = json.loads(doc.get("_comments"))
    if self.is_standard:
        self.load_standard_properties(context)      
    try:
      if self.channel == "whatsapp message":       
          frappe.enqueue(
          self.send_whatsapp(doc, context),
          queue="short",
          timeout=200,
          doc=doc,
          context=context
         )
    except:
            frappe.log_error(title='Failed to send notification', message=frappe.get_traceback())  
    super(ERPGulfNotification, self).send(doc)
              
                       
  def get_receiver_list(self, doc, context):
    receiver_list = []
    for recipient in self.custom_receivers_phones:
        phone = recipient.phone_number
        if phone:
            receiver_list.append(phone)
    receiver_list = list(set(filter(None, receiver_list)))               
    return receiver_list

  
    
    
 