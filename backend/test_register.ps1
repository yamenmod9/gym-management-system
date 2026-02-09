# Test Customer Registration Endpoint

# Step 1: Login as reception1
$loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/auth/login" -Method Post -Body (@{
    username = "reception1"
    password = "reception123"
} | ConvertTo-Json) -ContentType "application/json"

$token = $loginResponse.access_token
Write-Host "✅ Login successful" -ForegroundColor Green
Write-Host "Token: $token`n" -ForegroundColor Gray

# Step 2: Register a new customer
$customerData = @{
    full_name = "Ahmed Test Customer"
    phone = "01234567890"
    email = "ahmed.test@example.com"
    national_id = "30012251234567"
    age = 24
    gender = "male"
    address = "123 Test Street, Cairo"
    height = 175.0
    weight = 78.5
    health_notes = "No health issues"
    branch_id = 1
}

Write-Host "Registering customer..." -ForegroundColor Yellow
Write-Host "Request data:" -ForegroundColor Gray
$customerData | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/customers/register" `
        -Method Post `
        -Headers @{ Authorization = "Bearer $token" } `
        -Body ($customerData | ConvertTo-Json) `
        -ContentType "application/json"
    
    Write-Host "`n✅ Customer registered successfully!" -ForegroundColor Green
    Write-Host "`nResponse:" -ForegroundColor Gray
    $registerResponse | ConvertTo-Json -Depth 3
    
    Write-Host "`nKey Fields:" -ForegroundColor Cyan
    Write-Host "  ID: $($registerResponse.id)" -ForegroundColor White
    Write-Host "  QR Code: $($registerResponse.qr_code)" -ForegroundColor White
    Write-Host "  Age: $($registerResponse.age)" -ForegroundColor White
    Write-Host "  BMI: $($registerResponse.bmi)" -ForegroundColor White
    Write-Host "  BMI Category: $($registerResponse.bmi_category)" -ForegroundColor White
    Write-Host "  BMR: $($registerResponse.bmr)" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ Registration failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
