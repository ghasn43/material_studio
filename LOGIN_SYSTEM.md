# Login System Documentation

## Overview
The Materials Science AI app now includes a secure login system with two user roles: **Admin** and **User**.

## Features

✅ **Dual Role System**
- Admin accounts for system administration
- User accounts for regular access

✅ **Clean UI Design**
- No explicit "username/password" labels on login page
- Input fields use placeholders only (e.g., "Enter identifier", "Enter code")
- Professional UI with tabs for Sign In / Create Account

✅ **Session Management**
- User login state persists during session
- Logout functionality in sidebar
- User role displayed with icon (👑 for admin, 👤 for user)

✅ **Account Management**
- Create new accounts (both admin and user)
- Password validation (minimum 6 characters)
- Duplicate username prevention

## Demo Credentials

### Admin Login
- **Identifier:** `admin`
- **Code:** `admin123`

### User Logins
- **User 1** - Identifier: `user1` | Code: `pass123`
- **User 2** - Identifier: `user2` | Code: `demo456`

## File Structure

### New Files Created

1. **auth.py** - Authentication module
   - Credential management
   - Session state handling
   - Login verification functions
   - User registration logic

2. **login.py** - Login UI module
   - Clean login page display
   - Sign In / Create Account tabs
   - Demo credential display
   - Role-based selection (Admin/User)

3. **credentials.json** - Credential storage
   - Stores admin and user credentials
   - Auto-created with demo data on first run
   - Can be manually edited to add/remove users

### Modified Files

1. **app.py** - Main application
   - Added authentication imports
   - Added login check before main content
   - Added user info + logout button in sidebar
   - Now requires successful login to access material analysis

## Usage Flow

### First-Time User

1. **Open the app** → Presented with login page
2. **Select role** → Choose "👤 User" or "⚙️ Administrator"
3. **Sign In** → Use demo credentials or create account
4. **Access granted** → Redirected to main material analysis interface

### Logged-In User

1. **Main interface** → User info in sidebar (name + role)
2. **Logout button** → Single click logout (🚪 icon in sidebar)
3. **Session persistence** → Stays logged in during session

### Creating New Account

1. **On login page** → Click "Create Account" tab
2. **Choose role** → Select Admin or User first
3. **Enter details** → Identifier and code (no labels shown)
4. **Create** → Account saved to credentials.json
5. **Sign In** → Use new credentials immediately

## Customization

### Add New Users

**Option 1: Via UI**
- Use "Create Account" tab on login page
- Set role and enter credentials
- Account saved automatically

**Option 2: Manual Edit**
- Edit `credentials.json` directly
- Add new entry under "admins" or "users" section
- Format: `"username": "password"`
- Restart app to reload

Example `credentials.json`:
```json
{
  "admins": {
    "admin": "admin123",
    "john_admin": "secure_pass_456"
  },
  "users": {
    "user1": "pass123",
    "user2": "demo456",
    "alice": "alice_password_789"
  }
}
```

### Hide Demo Credentials

Edit **login.py** line ~100, remove:
```python
st.info("📝 Demo Credentials:\n\n" + ...)
```

### Customize UI Text

**Login page title** - Edit `login.py` line ~25
**Sidebar user info** - Edit `app.py` line ~1374-1380
**Placeholder text** - Edit `login.py` lines ~85, ~90, ~110, ~115

## Security Notes

⚠️ **For Production Use:**

1. **Hash passwords** in credentials.json
   - Current demo stores plain text
   - Replace with bcrypt/argon2 hashing

2. **Use environment variables** for sensitive data
   - Store credentials in environment, not JSON files
   - Use secure secret management system

3. **Add database** instead of JSON file
   - PostgreSQL, MongoDB, or similar
   - Better for scaling and security

4. **Implement HTTPS** for Streamlit Cloud
   - Default Streamlit Cloud uses HTTPS
   - Enable SSL for self-hosted deployments

5. **Add rate limiting** on login attempts
   - Prevent brute force attacks
   - Consider failed attempt logging

## Troubleshooting

### Login Page Not Showing

**Issue:** App goes straight to main interface
- **Solution:** Clear Streamlit cache: Delete `.streamlit/cache/` folder and restart

### "Invalid credentials" Error

**Issue:** Correct credentials show error
- **Solution:** 
  1. Check `credentials.json` exists in app directory
  2. Verify exact spelling and case sensitivity
  3. Ensure no extra spaces in JSON file

### Can't Create Account

**Issue:** "User already exists" when creating new user
- **Solution:** Use different username, or delete user from `credentials.json`

### Lost in Demo Credentials

**Issue:** Can't remember demo accounts
- **Solution:** Check credentials.json or this documentation file

## API Reference

### auth.py Functions

```python
# Check if user is logged in
is_authenticated() → bool

# Check if logged-in user is admin
is_admin() → bool

# Get current username
get_username() → str

# Get current user role (admin/user)
get_user_role() → str

# Log out current user
logout() → None

# Verify login credentials
verify_credentials(identifier: str, password: str, role: str) → bool

# Register new user
register_user(identifier: str, password: str, role: str) → dict
```

### login.py Functions

```python
# Display login page UI
show_login_page() → None
```

## Future Enhancements

🔮 **Potential Improvements:**

1. Role-based features
   - Admins: See analytics, user management
   - Users: Access limited to own analysis

2. User profiles
   - Save favorite materials
   - History of analyses
   - Preset configurations

3. Advanced security
   - Two-factor authentication (2FA)
   - OAuth integration (Google, GitHub)
   - IP whitelisting for admins

4. Audit logging
   - Track user actions
   - Log login/logout events
   - Monitor analysis history

5. Permission system
   - Granular access control
   - Feature-level permissions
   - API key management per user

## Support

For issues or questions:
1. Check this documentation
2. Review credentials.json format
3. Check app.py and login.py for integration
4. Clear Streamlit cache and restart

---

**Last Updated:** 2026-06-05
**Version:** 1.0
