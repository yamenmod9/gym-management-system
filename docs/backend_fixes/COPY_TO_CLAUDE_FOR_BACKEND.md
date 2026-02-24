# 🚀 QUICK START: Copy This to Claude Sonnet

---

## 📋 TASK OVERVIEW

I need you to implement a **separate backend API module for a gym client mobile app** that works alongside the existing staff backend.

**Key Requirement:** The activation code system must automatically detect if the user entered a phone number or email, then send the code via SMS (for phone) or Email (for email).

---

## 🎯 WHAT I NEED

### 1. Project Structure
Create a clean, modular Flask backend with **two separate API namespaces**:
- `/api/auth/*` and `/api/customers/*` → Staff app (existing)
- `/api/clients/*` → Client app (NEW - this is what you'll build)

### 2. Core Functionality

**Client Authentication Flow:**
1. User enters phone OR email → `POST /api/clients/request-activation`
2. Backend detects identifier type (phone vs email)
3. Backend sends 6-digit code via SMS (phone) or Email (email)
4. User enters code → `POST /api/clients/verify-activation`
5. Backend validates and returns JWT token
6. User accesses protected routes with token

**7 Required Endpoints:**
- `POST /api/clients/request-activation` - Send activation code (SMS or Email)
- `POST /api/clients/verify-activation` - Login with code
- `GET /api/clients/profile` - Get client profile + subscription
- `GET /api/clients/subscription` - Get detailed subscription info
- `GET /api/clients/qr` - Get QR code for gym entry
- `GET /api/clients/entry-history` - View gym entry logs
- `POST /api/clients/refresh` - Refresh access token

---

## 📱 SMART CODE DELIVERY (CRITICAL FEATURE)

The system must automatically detect identifier type and use the appropriate delivery method:

### Detection Logic
```python
def detect_identifier_type(identifier):
    if '@' in identifier and '.' in identifier:
        # It's an email
        return 'email'
    elif identifier.replace('+', '').replace('-', '').replace(' ', '').isdigit():
        # It's a phone number
        return 'phone'
    else:
        return 'invalid'
```

### Delivery Logic
```python
@app.route('/api/clients/request-activation', methods=['POST'])
def request_activation():
    identifier = request.json.get('identifier')
    
    # Detect type
    if is_email(identifier):
        customer = find_by_email(identifier)
        if customer:
            code = generate_6_digit_code()
            send_activation_email(customer.email, code, customer.name)
    
    elif is_phone(identifier):
        customer = find_by_phone(identifier)
        if customer:
            code = generate_6_digit_code()
            send_activation_sms(customer.phone, code)
    
    # Always return success (security)
    return {"status": "success", "message": "Code sent"}
```

---

## 🗄️ DATABASE CHANGES

Add these fields to the existing `Customer` model:

```python
class Customer(db.Model):
    # ...existing fields (id, full_name, phone, email, qr_code, branch_id)...
    
    # NEW FIELDS for client authentication
    activation_code = db.Column(db.String(6), nullable=True)
    activation_code_expires = db.Column(db.DateTime, nullable=True)
    last_activation_request = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def generate_activation_code(self):
        import random
        self.activation_code = f"{random.randint(100000, 999999)}"
        self.activation_code_expires = datetime.utcnow() + timedelta(minutes=10)
        self.last_activation_request = datetime.utcnow()
        return self.activation_code
    
    def verify_activation_code(self, code):
        if not self.activation_code or self.activation_code_expires < datetime.utcnow():
            return False
        return self.activation_code == code
```

---

## 📧 EMAIL SERVICE

Implement email sending for activation codes:

```python
# services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_activation_email(to_email, code, customer_name):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Your Gym Access Code: {code}'
    msg['From'] = 'your-gym@example.com'
    msg['To'] = to_email
    
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>Gym Access Code</h2>
        <p>Hello <strong>{customer_name}</strong>,</p>
        <p>Your activation code is:</p>
        <div style="background: #f5f5f5; padding: 20px; text-align: center; 
                    font-size: 32px; font-weight: bold; letter-spacing: 5px;">
          {code}
        </div>
        <p style="color: #666;">This code expires in <strong>10 minutes</strong>.</p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    # Send via SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-app-password')
        server.send_message(msg)
```

**Configuration:**
```python
# For Gmail, use App Password (not regular password)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'your-gym@example.com'
SENDER_PASSWORD = 'your-app-password'  # Generate from Google Account
```

---

## 📱 SMS SERVICE

Implement SMS sending for activation codes:

```python
# services/sms_service.py
import requests

def send_activation_sms(phone, code):
    """Send activation code via SMS"""
    message = f"Your gym app activation code is: {code}\nValid for 10 minutes."
    
    # Example: Twilio (replace with your SMS provider)
    try:
        response = requests.post(
            'https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json',
            auth=('YOUR_ACCOUNT_SID', 'YOUR_AUTH_TOKEN'),
            data={
                'From': '+1234567890',  # Your Twilio number
                'To': phone,
                'Body': message
            }
        )
        
        if response.status_code == 201:
            print(f"✅ SMS sent to {phone}")
            return True
        else:
            raise Exception(f"SMS failed: {response.status_code}")
            
    except Exception as e:
        # For testing: print code instead of failing
        print(f"⚠️ SMS not configured. Code for {phone}: {code}")
        return True  # Don't block testing
```

**SMS Provider Options:**
- **Twilio** (Global, easy to use)
- **Nexmo/Vonage** (Global)
- **Egypt-specific:** VodafoneSMS, OrangeSMS, EgyptSMS

---

## 🔐 SECURITY REQUIREMENTS

Implement these security measures:

1. **Rate Limiting:** Max 3 activation requests per 10 minutes per customer
2. **Code Expiration:** Codes expire after 10 minutes
3. **No Information Leakage:** Never reveal if customer exists (always return success)
4. **JWT Token Type:** Include `{"type": "client"}` in JWT claims to differentiate from staff
5. **Input Validation:** Validate phone/email format before processing

```python
# Rate limiting example
if customer.last_activation_request:
    time_since = datetime.utcnow() - customer.last_activation_request
    if time_since < timedelta(minutes=10):
        return jsonify({
            'status': 'error',
            'message': 'Too many requests. Wait 10 minutes.',
            'code': 'RATE_LIMIT_EXCEEDED'
        }), 429
```

---

## 🧪 TESTING EXAMPLES

### Test 1: Request Code (Phone)
```bash
curl -X POST http://localhost:5000/api/clients/request-activation \
  -H "Content-Type: application/json" \
  -d '{"identifier": "01234567890"}'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Activation code sent to your phone",
  "data": {
    "expires_in": 600,
    "identifier_type": "phone"
  }
}
```

**Backend Console Should Print:**
```
🔑 ACTIVATION CODE for Ahmed Hassan: 523941
   Valid until: 2026-02-11 10:45:00
   Delivery: SMS to 01234567890
```

### Test 2: Request Code (Email)
```bash
curl -X POST http://localhost:5000/api/clients/request-activation \
  -H "Content-Type: application/json" \
  -d '{"identifier": "customer@example.com"}'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Activation code sent to your email",
  "data": {
    "expires_in": 600,
    "identifier_type": "email"
  }
}
```

**Backend Console Should Print:**
```
🔑 ACTIVATION CODE for Ahmed Hassan: 724598
   Valid until: 2026-02-11 10:45:00
   Delivery: Email to customer@example.com
```

### Test 3: Verify Code
```bash
curl -X POST http://localhost:5000/api/clients/verify-activation \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "01234567890",
    "activation_code": "523941"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "client": {
      "id": 123,
      "full_name": "Ahmed Hassan",
      "phone": "01234567890",
      "email": "customer@example.com",
      "qr_code": "GYM-123",
      "branch_name": "Dragon Club",
      "has_active_subscription": true
    }
  }
}
```

---

## 📦 DEPENDENCIES

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
qrcode[pil]==7.4.2
requests==2.31.0
Pillow==10.2.0
```

---

## 🎯 DELIVERABLES

Please provide:

1. **Complete backend code** with:
   - `api/clients/auth.py` - Request & verify activation
   - `api/clients/profile.py` - Client profile endpoints
   - `api/clients/qr_code.py` - QR code generation
   - `services/email_service.py` - Email sending
   - `services/sms_service.py` - SMS sending
   - `models/customer.py` - Enhanced Customer model
   - `app.py` - Main Flask app with all blueprints

2. **Database migration script** to add new columns

3. **Configuration template** for email/SMS credentials

4. **Testing guide** with curl commands

---

## ⚠️ IMPORTANT NOTES

- **For testing:** Print activation codes to console even if SMS/Email fails
- **Security:** Never reveal if customer exists (always return success)
- **JWT Claims:** Must include `{"type": "client"}` to differentiate from staff tokens
- **Rate Limiting:** Enforce 3 requests per 10 minutes
- **Code Expiration:** 10 minutes from generation

---

## ✅ SUCCESS CRITERIA

The implementation is complete when:

1. ✅ User enters phone → SMS sent with code
2. ✅ User enters email → Email sent with code
3. ✅ Code verification works and returns JWT token
4. ✅ Protected endpoints require valid client token
5. ✅ Rate limiting prevents abuse
6. ✅ Codes expire after 10 minutes
7. ✅ Console prints codes for testing (even if SMS/Email fails)

---

## 🚀 READY TO START?

Please implement the complete backend system as described above. Focus on:
1. **Smart identifier detection** (phone vs email)
2. **Automatic delivery routing** (SMS vs Email)
3. **Robust error handling** (don't fail if SMS/Email not configured)
4. **Security features** (rate limiting, expiration, no info leakage)

**Let me know if you need any clarification!** 🎉

