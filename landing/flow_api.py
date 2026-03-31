import os
import hmac
import hashlib
import requests

# Flow Credentials (Usaremos variables de entorno para Producción)
# Con fallback a Sandbox localmente
FLOW_API_KEY = os.environ.get('FLOW_API_KEY', "53ECCF14-B94A-49F1-B71D-71EFBABL5364")
FLOW_SECRET_KEY = os.environ.get('FLOW_SECRET_KEY', "c012fa658bfada9c4ab73015eba6f7aee8550227")

# 'produccion' cargará la URL oficial, de lo contrario probará en sandbox.
FLOW_ENV = os.environ.get('FLOW_ENV', "sandbox")
if FLOW_ENV == "produccion":
    FLOW_API_URL = "https://www.flow.cl/api"
else:
    FLOW_API_URL = "https://sandbox.flow.cl/api"

def make_flow_signature(params: dict) -> str:
    """Generate the HMAC SHA256 signature required by Flow"""
    keys = sorted(params.keys())
    to_sign = "".join(f"{k}{params[k]}" for k in keys)
    hmac_obj = hmac.new(
        FLOW_SECRET_KEY.encode('utf-8'), 
        to_sign.encode('utf-8'), 
        hashlib.sha256
    )
    return hmac_obj.hexdigest()

def create_payment(commerce_order: str, subject: str, amount: int, email: str, return_url: str, confirm_url: str):
    """Hits the /payment/create endpoint and returns a redirect URL"""
    url = f"{FLOW_API_URL}/payment/create"
    
    # Parameter dictionary
    params = {
        "apiKey": FLOW_API_KEY,
        "commerceOrder": str(commerce_order),
        "subject": subject,
        "currency": "CLP",
        "amount": amount,
        "email": email,
        "paymentMethod": 9,
        "urlConfirmation": confirm_url,
        "urlReturn": return_url,
    }
    
    params['s'] = make_flow_signature(params)
    
    try:
        response = requests.post(url, data=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "url": f"{data['url']}?token={data['token']}",
                "token": data['token']
            }
        else:
            try:
                error = response.json()
                return {"success": False, "error": f"{error.get('code')}: {error.get('message')}"}
            except Exception:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_payment_status(token: str):
    """Hits the /payment/getStatus endpoint to verify a payment"""
    url = f"{FLOW_API_URL}/payment/getStatus"
    
    params = {
        "apiKey": FLOW_API_KEY,
        "token": token
    }
    
    params['s'] = make_flow_signature(params)
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
