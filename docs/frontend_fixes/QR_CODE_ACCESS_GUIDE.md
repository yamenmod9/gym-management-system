# QR Code Access Guide

## 📱 How to Access Customer QR Codes

### Step-by-Step Process

#### 1. Register a Customer
```
Reception Dashboard
  └─ Click "Register Customer" button
      └─ Fill in customer details:
          • Full Name (required)
          • Phone (optional)
          • Email (optional)
          • Gender (required)
          • Age (required)
          • Weight in kg (required)
          • Height in cm (required)
      └─ Click "Register"
      └─ Wait for success message
```

#### 2. Find the Customer
```
Reception Dashboard
  └─ Scroll to "Recent Customers" section
      └─ Look for the newly registered customer
      └─ Or use search/filter to find customer
```

#### 3. View Customer Details
```
Recent Customers List
  └─ Tap on customer card
      └─ Opens Customer Detail Screen
          └─ Shows customer information
          └─ Shows subscription status
          └─ Shows health metrics
```

#### 4. Access QR Code
```
Customer Detail Screen
  └─ Scroll down to "Health Report" section
      OR
  └─ Look for QR Code display area
      └─ QR Code is automatically generated
      └─ Format: GYM_CUSTOMER_{customer_id}
      └─ Can be scanned immediately
```

---

## 🔧 QR Code Technical Details

### Generation Method
```dart
// In customer_qr_code_widget.dart
final qrData = 'GYM_CUSTOMER_$customerId';

// Example output:
// GYM_CUSTOMER_123
// GYM_CUSTOMER_456
```

### Display Widget
```dart
QrImageView(
  data: 'GYM_CUSTOMER_${customer.id}',
  version: QrVersions.auto,
  size: 200,
  backgroundColor: Colors.white,
)
```

### QR Code Format
- **Prefix:** `GYM_CUSTOMER_`
- **Suffix:** Customer's unique database ID
- **Example:** `GYM_CUSTOMER_123`
- **Type:** Text-based QR code
- **Scannable:** Yes, with any QR scanner

---

## 📍 File Locations

### QR Code Widget
**File:** `lib/features/reception/widgets/customer_qr_code_widget.dart`
- Generates QR code from customer ID
- Displays in dialog with customer info
- Includes customer name and ID

### Health Report Screen
**File:** `lib/features/reception/screens/health_report_screen.dart`
- Shows customer health metrics
- Displays QR code inline
- Calculates BMI, BMR, daily calories

### Customer Detail Screen
**File:** `lib/features/reception/screens/customer_detail_screen.dart`
- Main customer information screen
- Links to health report
- Shows subscription status

---

## 🎨 QR Code Customization

### Change QR Code Format
```dart
// In customer_qr_code_widget.dart (line 17)

// Current format
final qrData = 'GYM_CUSTOMER_$customerId';

// Alternative formats:
final qrData = 'GYM-$customerId';                    // GYM-123
final qrData = 'CUSTOMER_$customerId';                // CUSTOMER_123
final qrData = '${branchId}_$customerId';             // 1_123
final qrData = 'GYM_${branchId}_$customerId';         // GYM_1_123
```

### Change QR Code Size
```dart
// In health_report_screen.dart (line 103)

// Current size
QrImageView(
  data: qrData,
  size: 200, // Change this value
  ...
)

// Larger
size: 300,

// Smaller
size: 150,
```

### Change QR Code Color
```dart
QrImageView(
  data: qrData,
  size: 200,
  backgroundColor: Colors.white,
  foregroundColor: Colors.black, // Add this line
)

// Or match theme
foregroundColor: Theme.of(context).colorScheme.primary, // Red
backgroundColor: Theme.of(context).colorScheme.surface,  // Dark grey
```

---

## 🔐 QR Code Usage Scenarios

### 1. **Entry Check-In**
```
Customer arrives at gym
  └─ Receptionist scans QR code
      └─ System extracts customer ID
      └─ Verifies active subscription
      └─ Grants access
```

### 2. **Service Consumption**
```
Customer wants to use paid service
  └─ Staff scans QR code
      └─ System shows available coins
      └─ Deducts coins for service
      └─ Updates customer balance
```

### 3. **Quick Lookup**
```
Staff needs customer info
  └─ Scan QR code
      └─ Instantly shows customer details
      └─ No need to search by name
      └─ Faster service
```

---

## 🛠️ Troubleshooting

### QR Code Not Showing
**Possible Causes:**
1. Customer ID is null (not saved properly)
2. Navigation to wrong screen
3. Widget not rendered

**Solution:**
```dart
// Check customer ID exists
if (customer.id != null) {
  // Display QR code
  QrImageView(data: 'GYM_CUSTOMER_${customer.id}')
} else {
  // Show error message
  Text('Customer ID not available')
}
```

### QR Code Not Scannable
**Possible Causes:**
1. QR code too small
2. Poor contrast
3. Invalid data format

**Solution:**
- Increase size (300px minimum)
- Use white background, black foreground
- Ensure data format is plain text

### QR Code Shows Wrong Customer
**Possible Causes:**
1. Customer ID mismatch
2. Cache issue
3. Wrong customer object

**Solution:**
```dart
// Add debug logging
print('Generating QR for customer ID: ${customer.id}');
print('QR Data: GYM_CUSTOMER_${customer.id}');
```

---

## 📊 QR Code Data Structure

### What's Encoded
```
Format: GYM_CUSTOMER_123
         │      │      │
         │      │      └─ Customer Database ID
         │      └─ Separator
         └─ Gym identifier prefix
```

### How to Parse (Backend/Scanner)
```dart
// Dart/Flutter example
String scannedData = 'GYM_CUSTOMER_123';
List<String> parts = scannedData.split('_');

if (parts.length == 3 && parts[0] == 'GYM' && parts[1] == 'CUSTOMER') {
  int customerId = int.parse(parts[2]); // 123
  // Look up customer in database
}
```

```python
# Python example
scanned_data = 'GYM_CUSTOMER_123'
parts = scanned_data.split('_')

if len(parts) == 3 and parts[0] == 'GYM' and parts[1] == 'CUSTOMER':
    customer_id = int(parts[2])  # 123
    # Look up customer in database
```

---

## 🎯 Best Practices

### For Staff
1. **Always verify QR code is visible** before scanning
2. **Ensure good lighting** for QR code scanning
3. **Keep QR codes clean** (no damage, dirt, or obstruction)
4. **Test scanner regularly** to ensure it works

### For Developers
1. **Use consistent format** across all QR codes
2. **Include validation** when parsing QR data
3. **Log QR scans** for audit trail
4. **Handle errors gracefully** if QR is invalid
5. **Consider adding branch ID** to QR format for multi-branch

### For Users (Customers)
1. **Screenshot QR code** for easy access
2. **Save customer ID** as backup
3. **Keep profile updated** for accurate QR generation
4. **Report issues immediately** if QR doesn't work

---

## 🔄 Alternative Access Methods

### If QR Code Fails

#### Method 1: Manual ID Entry
```
Staff enters customer ID manually
  └─ System looks up customer
      └─ Shows customer details
      └─ Proceeds with service
```

#### Method 2: Phone Number Lookup
```
Staff enters customer phone
  └─ System searches database
      └─ Shows matching customers
      └─ Staff selects correct one
```

#### Method 3: Name Search
```
Staff enters customer name
  └─ System shows list of matches
      └─ Staff verifies and selects
      └─ Proceeds with service
```

---

## 📱 Mobile QR Code App Integration

### For Customers (Future Enhancement)
```
Mobile App
  └─ Customer logs in
      └─ Dashboard shows QR code
      └─ Always accessible
      └─ No need for staff
```

### Implementation Ideas
```dart
// Customer mobile app
class CustomerQRScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final customerId = context.watch<AuthProvider>().customerId;
    
    return Scaffold(
      appBar: AppBar(title: Text('My QR Code')),
      body: Center(
        child: QrImageView(
          data: 'GYM_CUSTOMER_$customerId',
          size: 300,
        ),
      ),
    );
  }
}
```

---

## ✅ Checklist

### For Reception Staff
- [ ] Register customer with all required details
- [ ] Wait for success confirmation
- [ ] Navigate to customer detail screen
- [ ] Verify QR code is displayed
- [ ] Test QR code with scanner
- [ ] Confirm customer can check in

### For Developers
- [ ] QR code generates from customer ID
- [ ] QR code displays correctly
- [ ] QR code is scannable
- [ ] Data format is consistent
- [ ] Error handling is in place
- [ ] Logging is implemented

### For Management
- [ ] Staff trained on QR code usage
- [ ] Scanners are working
- [ ] Backup procedures in place
- [ ] System is tested
- [ ] Customers are informed

---

## 📞 Support

### Need Help?
1. **QR code not generating:** Check customer has valid ID
2. **QR code not scanning:** Verify scanner compatibility
3. **Wrong customer showing:** Clear cache and regenerate
4. **Format issues:** Verify QR data string is correct

### Contact
- Technical issues: Check console logs
- Usage questions: Refer to this guide
- Feature requests: Update ticket system

---

**QR Code System: ✅ Fully Operational**

All customers get unique QR codes automatically generated from their database ID. No manual generation needed!
