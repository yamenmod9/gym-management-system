"""
Test page route - for testing APIs with interactive health checks
"""
from flask import Blueprint, render_template_string

test_bp = Blueprint('test', __name__)

TEST_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gym Management API - Interactive Test & Health Check</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .auth-panel {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .auth-status {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff4444;
        }
        .status-indicator.active {
            background: #00ff00;
            box-shadow: 0 0 10px #00ff00;
        }
        .auth-controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        select, button, input {
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
        }
        select {
            background: white;
            color: #333;
        }
        button {
            background: white;
            color: #667eea;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .health-check {
            background: #f0f0f0;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .health-results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .health-item {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #ddd;
        }
        .health-item.healthy {
            border-color: #4CAF50;
        }
        .health-item.unhealthy {
            border-color: #f44336;
        }
        .health-item.pending {
            border-color: #ff9800;
        }
        .section {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .endpoint {
            margin: 15px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 6px;
            border-left: 4px solid #4CAF50;
        }
        .endpoint-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .method {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            margin-right: 10px;
        }
        .get { background: #61affe; color: white; }
        .post { background: #49cc90; color: white; }
        .put { background: #fca130; color: white; }
        .delete { background: #f93e3e; color: white; }
        .test-btn {
            padding: 6px 12px;
            font-size: 12px;
            background: #667eea;
            color: white;
        }
        code, pre {
            background: #272822;
            color: #f8f8f2;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 10px 0;
            font-size: 13px;
        }
        .response-box {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 6px;
            margin-top: 10px;
            display: none;
            max-height: 300px;
            overflow-y: auto;
        }
        .response-box.show {
            display: block;
        }
        .response-box.success {
            border-left: 4px solid #4CAF50;
        }
        .response-box.error {
            border-left: 4px solid #f44336;
        }
        .test-accounts {
            background: #fff9e6;
            padding: 15px;
            border-left: 4px solid #ffc107;
            border-radius: 6px;
        }
        .loading {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .stats {
            display: flex;
            gap: 20px;
            margin-top: 15px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏋️ Gym Management System - API Test & Health Check</h1>
        <p class="subtitle">Interactive endpoint testing and system health monitoring</p>
        
        <!-- Authentication Panel -->
        <div class="auth-panel">
            <div class="auth-status">
                <div class="status-indicator" id="authIndicator"></div>
                <div>
                    <strong id="authStatusText">Not Authenticated</strong>
                    <div id="authUser" style="font-size: 12px; opacity: 0.9;"></div>
                </div>
            </div>
            <div class="auth-controls">
                <select id="testAccount">
                    <option value="owner:owner123">Owner (Full Access)</option>
                    <option value="manager1:manager123">Branch Manager</option>
                    <option value="reception1:reception123">Front Desk</option>
                    <option value="accountant1:accountant123">Accountant</option>
                </select>
                <button onclick="quickLogin()">🔑 Quick Login</button>
                <button onclick="logout()">🚪 Logout</button>
                <button onclick="copyToken()">📋 Copy Token</button>
            </div>
        </div>

        <!-- Health Check Panel -->
        <div class="health-check">
            <h2>🏥 System Health Check</h2>
            <button onclick="runHealthCheck()" style="margin-bottom: 15px;">🔍 Run Full Health Check</button>
            <div id="healthResults" class="health-results"></div>
            <div class="stats" id="statsContainer" style="display: none;">
                <div class="stat-item">
                    <div class="stat-value" id="healthyCount">0</div>
                    <div class="stat-label">Healthy</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="unhealthyCount" style="color: #f44336;">0</div>
                    <div class="stat-label">Unhealthy</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="totalCount">0</div>
                    <div class="stat-label">Total Endpoints</div>
                </div>
            </div>
        </div>
    
    <div class="section">
        <h2>🔐 Test Accounts</h2>
        <div class="test-accounts">
            <h3>Owner Account</h3>
            <p><strong>Username:</strong> owner<br>
            <strong>Password:</strong> owner123</p>
            
            <h3>Branch Manager Account</h3>
            <p><strong>Username:</strong> manager1<br>
            <strong>Password:</strong> manager123</p>
            
            <h3>Receptionist Account</h3>
            <p><strong>Username:</strong> reception1<br>
            <strong>Password:</strong> reception123</p>
            
            <h3>Accountant Account</h3>
            <p><strong>Username:</strong> accountant1<br>
            <strong>Password:</strong> accountant123</p>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>🚀 Authentication</h2>
            <button class="test-btn" onclick="testSection('auth')">Test All Auth Endpoints</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method post">POST</span> <strong>/api/auth/login</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('login')">Test</button>
            </div>
            <p>Login and get JWT token</p>
            <code>
{
  "username": "owner",
  "password": "owner123"
}
            </code>
            <div id="response-login" class="response-box"></div>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/auth/me</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('me')">Test</button>
            </div>
            <p>Get current user info (requires JWT)</p>
            <div id="response-me" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>🏢 Branches</h2>
            <button class="test-btn" onclick="testSection('branches')">Test All Branch Endpoints</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/branches</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('branches-list')">Test</button>
            </div>
            <p>Get all branches</p>
            <div id="response-branches-list" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>👥 Customers</h2>
            <button class="test-btn" onclick="testSection('customers')">Test All Customer Endpoints</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/customers</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('customers-list')">Test</button>
            </div>
            <p>Get all customers (paginated, filtered by branch)</p>
            <div id="response-customers-list" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>🎟️ Services</h2>
            <button class="test-btn" onclick="testSection('services')">Test All Service Endpoints</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/services</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('services-list')">Test</button>
            </div>
            <p>Get all services</p>
            <div id="response-services-list" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>🏋️ Subscriptions</h2>
            <button class="test-btn" onclick="testSection('subscriptions')">Test All Subscription Endpoints</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/subscriptions</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('subscriptions-list')">Test</button>
            </div>
            <p>Get all subscriptions</p>
            <div id="response-subscriptions-list" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>💰 Transactions</h2>
            <button class="test-btn" onclick="testSection('transactions')">Test All Transaction Endpoints</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/transactions</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('transactions-list')">Test</button>
            </div>
            <p>Get all transactions</p>
            <div id="response-transactions-list" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>💸 Expenses</h2>
            <button class="test-btn" onclick="testSection('expenses')">Test All Expense Endpoints</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/expenses</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('expenses-list')">Test</button>
            </div>
            <p>Get all expenses</p>
            <div id="response-expenses-list" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>📞 Complaints</h2>
            <button class="test-btn" onclick="testSection('complaints')">Test All Complaint Endpoints</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/complaints</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('complaints-list')">Test</button>
            </div>
            <p>Get all complaints</p>
            <div id="response-complaints-list" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>🧬 Fingerprint Access</h2>
            <button class="test-btn" onclick="testSection('fingerprints')">Test Fingerprint System</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/fingerprints</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('fingerprints-list')">Test</button>
            </div>
            <p>Get all registered fingerprints</p>
            <div id="response-fingerprints-list" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <div class="section-header">
            <h2>📊 Dashboards</h2>
            <button class="test-btn" onclick="testSection('dashboards')">Test All Dashboards</button>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/dashboards/owner</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('dashboard-owner')">Test</button>
            </div>
            <p>Owner dashboard with smart alerts</p>
            <div id="response-dashboard-owner" class="response-box"></div>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/dashboards/accountant</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('dashboard-accountant')">Test</button>
            </div>
            <p>Accountant dashboard with financial summary</p>
            <div id="response-dashboard-accountant" class="response-box"></div>
        </div>
        
        <div class="endpoint">
            <div class="endpoint-header">
                <div>
                    <span class="method get">GET</span> <strong>/api/dashboards/branch-manager</strong>
                </div>
                <button class="test-btn" onclick="testEndpoint('dashboard-branch')">Test</button>
            </div>
            <p>Branch manager dashboard</p>
            <div id="response-dashboard-branch" class="response-box"></div>
        </div>
    </div>

    <div class="section">
        <h2>💡 Testing Notes</h2>
    <div class="section">
        <h2>💡 Testing Notes</h2>
        <ul>
            <li>Click <strong>"Quick Login"</strong> to authenticate with a test account</li>
            <li>Use <strong>"Run Full Health Check"</strong> to test all endpoints at once</li>
            <li>Click individual <strong>"Test"</strong> buttons to test specific endpoints</li>
            <li>Authentication token is automatically included in requests</li>
            <li>Green responses = Success (2xx), Red responses = Error (4xx/5xx)</li>
            <li>All API routes are prefixed with <code>/api</code></li>
        </ul>
    </div>
    
    </div>

    <script>
        let authToken = null;
        let currentUser = null;

        // Update auth UI
        function updateAuthUI() {
            const indicator = document.getElementById('authIndicator');
            const statusText = document.getElementById('authStatusText');
            const userText = document.getElementById('authUser');
            
            if (authToken) {
                indicator.classList.add('active');
                statusText.textContent = 'Authenticated';
                userText.textContent = currentUser ? `Logged in as: ${currentUser.username} (${currentUser.role})` : '';
            } else {
                indicator.classList.remove('active');
                statusText.textContent = 'Not Authenticated';
                userText.textContent = '';
            }
        }

        // Quick login function
        async function quickLogin() {
            const accountSelect = document.getElementById('testAccount');
            const [username, password] = accountSelect.value.split(':');
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                
                // API returns {success: true, data: {access_token: ...}, message: ...}
                if (response.ok && data.success && data.data && data.data.access_token) {
                    authToken = data.data.access_token;
                    
                    // Get user info
                    const userResponse = await fetch('/api/auth/me', {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    });
                    
                    if (userResponse.ok) {
                        const userData = await userResponse.json();
                        // Extract user data from response
                        currentUser = userData.data || userData;
                    }
                    
                    updateAuthUI();
                    alert('✅ Login successful!');
                } else {
                    alert('❌ Login failed: ' + (data.error || data.message || 'Unknown error'));
                }
            } catch (error) {
                alert('❌ Login error: ' + error.message);
            }
        }

        // Logout function
        function logout() {
            authToken = null;
            currentUser = null;
            updateAuthUI();
            alert('✅ Logged out successfully');
        }

        // Copy token function
        function copyToken() {
            if (!authToken) {
                alert('⚠️ No token available. Please login first.');
                return;
            }
            
            // Show token details
            const tokenPreview = authToken.substring(0, 50) + '...';
            
            navigator.clipboard.writeText(authToken).then(() => {
                alert(`✅ Token copied to clipboard!\n\nToken preview: ${tokenPreview}\n\nToken length: ${authToken.length} characters`);
            }).catch(() => {
                prompt('Copy this token:', authToken);
            });
        }

        // Test individual endpoint
        async function testEndpoint(endpointId) {
            const responseBox = document.getElementById(`response-${endpointId}`);
            responseBox.className = 'response-box show';
            responseBox.innerHTML = '<div class="loading"></div> Testing...';
            
            const endpoints = {
                'login': { method: 'POST', url: '/api/auth/login', body: { username: 'owner', password: 'owner123' }, noAuth: true },
                'me': { method: 'GET', url: '/api/auth/me' },
                'branches-list': { method: 'GET', url: '/api/branches' },
                'customers-list': { method: 'GET', url: '/api/customers' },
                'services-list': { method: 'GET', url: '/api/services' },
                'subscriptions-list': { method: 'GET', url: '/api/subscriptions' },
                'transactions-list': { method: 'GET', url: '/api/transactions' },
                'expenses-list': { method: 'GET', url: '/api/expenses' },
                'complaints-list': { method: 'GET', url: '/api/complaints' },
                'fingerprints-list': { method: 'GET', url: '/api/fingerprints' },
                'dashboard-owner': { method: 'GET', url: '/api/dashboards/owner' },
                'dashboard-accountant': { method: 'GET', url: '/api/dashboards/accountant' },
                'dashboard-branch': { method: 'GET', url: '/api/dashboards/branch-manager' }
            };
            
            const config = endpoints[endpointId];
            if (!config) {
                responseBox.innerHTML = '❌ Unknown endpoint';
                return;
            }
            
            if (!config.noAuth && !authToken) {
                responseBox.className = 'response-box show error';
                responseBox.innerHTML = '⚠️ Please login first to test this endpoint';
                return;
            }
            
            try {
                const options = {
                    method: config.method,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                };
                
                if (!config.noAuth && authToken) {
                    options.headers['Authorization'] = `Bearer ${authToken}`;
                }
                
                if (config.body) {
                    options.body = JSON.stringify(config.body);
                }
                
                const startTime = performance.now();
                const response = await fetch(config.url, options);
                const endTime = performance.now();
                const responseTime = (endTime - startTime).toFixed(2);
                
                let data;
                try {
                    data = await response.json();
                } catch (e) {
                    data = { error: 'Failed to parse response' };
                }
                
                // For login endpoint, extract the token
                if (endpointId === 'login' && response.ok && data.data && data.data.access_token) {
                    authToken = data.data.access_token;
                    
                    // Get user info
                    const userResponse = await fetch('/api/auth/me', {
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    });
                    
                    if (userResponse.ok) {
                        const userData = await userResponse.json();
                        currentUser = userData.data || userData;
                    }
                    
                    updateAuthUI();
                }
                
                responseBox.className = `response-box show ${response.ok ? 'success' : 'error'}`;
                
                // Show detailed error information for 422 responses
                let errorDetails = '';
                if (response.status === 422) {
                    errorDetails = '<div style="color: #ff9800; margin-top: 10px;"><strong>JWT Error:</strong> Token validation failed. Check token format.</div>';
                }
                
                responseBox.innerHTML = `
                    <div><strong>Status:</strong> ${response.status} ${response.statusText}</div>
                    <div><strong>Response Time:</strong> ${responseTime}ms</div>
                    ${errorDetails}
                    <div><strong>Response:</strong></div>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            } catch (error) {
                responseBox.className = 'response-box show error';
                responseBox.innerHTML = `❌ <strong>Error:</strong> ${error.message}`;
            }
        }

        // Health check for all endpoints
        async function runHealthCheck() {
            const resultsContainer = document.getElementById('healthResults');
            const statsContainer = document.getElementById('statsContainer');
            resultsContainer.innerHTML = '<div class="health-item pending">🔄 Running health checks...</div>';
            statsContainer.style.display = 'none';
            
            if (!authToken) {
                alert('⚠️ Please login first to run health checks');
                resultsContainer.innerHTML = '';
                return;
            }
            
            const endpoints = [
                { name: 'Authentication', url: '/api/auth/me', method: 'GET' },
                { name: 'Branches', url: '/api/branches', method: 'GET' },
                { name: 'Customers', url: '/api/customers', method: 'GET' },
                { name: 'Services', url: '/api/services', method: 'GET' },
                { name: 'Subscriptions', url: '/api/subscriptions', method: 'GET' },
                { name: 'Transactions', url: '/api/transactions', method: 'GET' },
                { name: 'Expenses', url: '/api/expenses', method: 'GET' },
                { name: 'Complaints', url: '/api/complaints', method: 'GET' },
                { name: 'Fingerprints', url: '/api/fingerprints', method: 'GET' },
                { name: 'Owner Dashboard', url: '/api/dashboards/owner', method: 'GET' }
            ];
            
            let results = [];
            let healthyCount = 0;
            let unhealthyCount = 0;
            
            for (const endpoint of endpoints) {
                try {
                    const startTime = performance.now();
                    const response = await fetch(endpoint.url, {
                        method: endpoint.method,
                        headers: {
                            'Authorization': `Bearer ${authToken}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    const endTime = performance.now();
                    const responseTime = (endTime - startTime).toFixed(2);
                    
                    const isHealthy = response.ok;
                    if (isHealthy) healthyCount++;
                    else unhealthyCount++;
                    
                    results.push({
                        name: endpoint.name,
                        status: response.status,
                        healthy: isHealthy,
                        responseTime: responseTime
                    });
                } catch (error) {
                    unhealthyCount++;
                    results.push({
                        name: endpoint.name,
                        status: 0,
                        healthy: false,
                        error: error.message
                    });
                }
            }
            
            // Display results
            resultsContainer.innerHTML = results.map(r => `
                <div class="health-item ${r.healthy ? 'healthy' : 'unhealthy'}">
                    <div><strong>${r.name}</strong></div>
                    <div style="font-size: 12px; margin-top: 5px;">
                        ${r.healthy ? '✅' : '❌'} Status: ${r.status || 'Error'}<br>
                        ${r.responseTime ? `⏱️ ${r.responseTime}ms` : ''}
                        ${r.error ? `<br>Error: ${r.error}` : ''}
                    </div>
                </div>
            `).join('');
            
            // Update stats
            document.getElementById('healthyCount').textContent = healthyCount;
            document.getElementById('unhealthyCount').textContent = unhealthyCount;
            document.getElementById('totalCount').textContent = endpoints.length;
            statsContainer.style.display = 'flex';
        }

        // Initialize on page load
        updateAuthUI();
    </script>
</body>
</html>
"""


@test_bp.route('/test')
def test_page():
    """Interactive test page with API documentation and health checks"""
    return render_template_string(TEST_PAGE_HTML)
