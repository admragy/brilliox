import os
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CRMService:
    """
    خدمة CRM متقدمة (HubSpot/Salesforce)
    تستخدم كـ Proxy لتبسيط عملية إضافة العملاء المحتملين وتحديثهم.
    """
    
    def __init__(self):
        # افتراض استخدام HubSpot كـ CRM أساسي
        self.hubspot_api_key = os.getenv("HUBSPOT_API_KEY")
        self.hubspot_base_url = "https://api.hubapi.com/crm/v3/objects/contacts"
        self.headers = {
            "Authorization": f"Bearer {self.hubspot_api_key}",
            "Content-Type": "application/json"
        }
        
        # يمكن إضافة منطق Salesforce هنا لاحقًا
        self.provider = "HubSpot" if self.hubspot_api_key else "MockCRM"

    def is_ready(self) -> bool:
        """التحقق من جاهزية الخدمة"""
        return self.provider != "MockCRM"

    def add_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        إضافة عميل محتمل جديد إلى CRM
        
        Args:
            lead_data: بيانات العميل المحتمل (الاسم، البريد، الهاتف، المصدر)
        
        Returns:
            حالة العملية
        """
        if not self.is_ready():
            logger.warning("CRM Service is not configured. Using Mock.")
            return {
                "success": True,
                "provider": "MockCRM",
                "message": "Lead added successfully to Mock CRM.",
                "lead_id": f"mock-{hash(lead_data.get('email'))}"
            }

        # تحويل البيانات إلى صيغة HubSpot
        hubspot_data = {
            "properties": {
                "firstname": lead_data.get("name", "").split(" ")[0],
                "lastname": " ".join(lead_data.get("name", "").split(" ")[1:]),
                "email": lead_data.get("email"),
                "phone": lead_data.get("phone"),
                "lead_source": lead_data.get("source", "Brilliox AI"),
                "lifecyclestage": "lead"
            }
        }

        try:
            response = requests.post(self.hubspot_base_url, headers=self.headers, json=hubspot_data)
            response.raise_for_status()
            
            return {
                "success": True,
                "provider": self.provider,
                "message": "Lead added successfully to HubSpot.",
                "lead_id": response.json().get("id")
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"HubSpot API Error: {e}")
            return {
                "success": False,
                "provider": self.provider,
                "error": f"Failed to add lead to HubSpot: {str(e)}",
                "status_code": e.response.status_code if e.response else 500
            }

    def update_lead_status(self, lead_id: str, status: str) -> Dict[str, Any]:
        """
        تحديث حالة عميل محتمل موجود
        """
        if not self.is_ready():
            return {
                "success": True,
                "provider": "MockCRM",
                "message": f"Lead {lead_id} status updated to {status} in Mock CRM."
            }

        update_url = f"{self.hubspot_base_url}/{lead_id}"
        update_data = {
            "properties": {
                "hs_lead_status": status
            }
        }

        try:
            response = requests.patch(update_url, headers=self.headers, json=update_data)
            response.raise_for_status()
            
            return {
                "success": True,
                "provider": self.provider,
                "message": f"Lead {lead_id} status updated to {status} in HubSpot."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"HubSpot API Error: {e}")
            return {
                "success": False,
                "provider": self.provider,
                "error": f"Failed to update lead status: {str(e)}",
                "status_code": e.response.status_code if e.response else 500
            }

# مثال للاستخدام
if __name__ == '__main__':
    crm = CRMService()
    print(f"CRM Provider: {crm.provider}")
    
    test_lead = {
        "name": "أحمد محمد",
        "email": "ahmed.mohamed@example.com",
        "phone": "00966501234567",
        "source": "AI Assistant Chat"
    }
    
    result = crm.add_lead(test_lead)
    print(result)
