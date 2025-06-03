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

    msg1 = frappe.render_template(self.message, context)
    recipients = self.get_receiver_list(doc,context) 
    multiple_numbers=[] 
    for receipt in recipients:
      number = receipt
      multiple_numbers.append(number)
    add_multiple_numbers_to_url=','.join(multiple_numbers)
    payload = {
        "device": deviceId,
        "phone": add_multiple_numbers_to_url,
        "authKey": token,
        "message": msg1
       }
    try:
        time.sleep(10)
        response = requests.post(url, data=payload)
      # when the msg send is success then its details are stored into whatsapp_sender log  
        if response.status_code == 200:
            response_json = response.json()
            if "sent" in  response_json and  response_json["sent"] == "true":
            # Log success
              current_time =now()# for geting current time
              msg1 = frappe.render_template(self.message, context)
              frappe.get_doc({"doctype":"whatsapp_sender log","title":"Whatsapp message successfully sent ","message":msg1,"to_number":doc.custom_mobile_phone,"time":current_time }).insert()
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
 

# directly pass the function 
  # call the  send whatsapp with pdf function and send whatsapp without pdf function and it work with the help of condition 
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
    """return receiver list based on the doc field and role specified"""
    receiver_list = []
    for recipient in self.recipients:
            if recipient.condition:
                if not frappe.safe_eval(recipient.condition, None, context):
                    continue
            if recipient.receiver_by_document_field:
              fields = recipient.receiver_by_document_field.split(",")
              if len(fields)>1:
                for d in doc.get(fields[1]):
                  phone_number = d.get(fields[0])
                  receiver_list.append(phone_number)
              
			# For sending messages to the owner's mobile phone number
            if recipient.receiver_by_document_field == "owner":
                    receiver_list += get_user_info([dict(user_name=doc.get("owner"))], "mobile_no")
                    
			# For sending messages to the number specified in the receiver field
            elif recipient.receiver_by_document_field:
                    receiver_list.append(doc.get(recipient.receiver_by_document_field))
			# For sending messages to specified role
            if recipient.receiver_by_role:
                receiver_list += get_info_based_on_role(recipient.receiver_by_role, "mobile_no")
            # return receiver_list
    receiver_list = list(set(receiver_list))
    # removing none_object from the list
    final_receiver_list = [item for item in receiver_list if item is not None]
    return final_receiver_list

  
    
    
 