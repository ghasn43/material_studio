# Login Credentials Troubleshooting Guide

## ✅ Verified Working Credentials

All demo credentials are confirmed working:

```
Admin:    admin / admin123 ✓
User 1:   user1 / pass123  ✓
User 2:   user2 / demo456  ✓
```

## 🔧 Common Issues and Fixes

### Issue 1: "Invalid credentials" Error

**Possible Causes:**
1. Extra spaces in input fields
2. Wrong role selected (Admin vs User)
3. Credentials.json file corrupted or missing

**Solutions:**
- **Ensure no spaces**: Trim spaces from identifier and password
- **Select correct role**: Admin credentials only work with "⚙️ Administrator" selected
- **Verify credentials.json exists**: Check `d:\material_studio_1\credentials.json`

**Credentials.json Format:**
```json
{
  "admins": {
    "admin": "admin123"
  },
  "users": {
    "user1": "pass123",
    "user2": "demo456"
  }
}
```

### Issue 2: Login Page Not Showing

**Possible Causes:**
1. Streamlit cache issue
2. Session state corrupted
3. Import error in auth.py

**Solutions:**
```bash
# Clear Streamlit cache
rm -r .streamlit/cache/
# OR on Windows
rmdir /s .streamlit\cache

# Restart the app
streamlit run app.py
```

### Issue 3: After Login, Stays on Login Page

**Possible Causes:**
1. `st.rerun()` happening too quickly
2. Session state not persisting
3. Authentication check failing on reload

**Solution:**
- Try hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Clear browser cookies for localhost:8501
- Restart Streamlit entirely

### Issue 4: Can't Create New Account

**Possible Causes:**
1. User already exists
2. Password too short (minimum 6 characters)
3. Credentials.json has permission issues

**Solutions:**
- Use different username
- Ensure password is at least 6 characters
- Check file permissions on credentials.json

## 🧪 Testing the Login System

### Quick Test
```bash
python test_login_creds.py
```

Expected output:
```
Admin login (admin/admin123): True
User1 login (user1/pass123): True
User2 login (user2/demo456): True
Invalid password: False
```

### Manual Testing Steps

1. **Start the app:**
   ```bash
   streamlit run app.py
   ```

2. **Select role:**
   - Choose "👤 User" or "⚙️ Administrator"

3. **Test login:**
   - Enter demo credentials
   - Click "🔓 Access System"
   - Should see success message and redirect

4. **Test invalid credentials:**
   - Enter wrong password
   - Click button
   - Should see "Invalid credentials for [role] account"

5. **Test account creation:**
   - Click "Create Account" tab
   - Enter new username and password (>= 6 chars)
   - Click "✨ Create Account"
   - Try logging in with new account

## 🔑 Adding More Credentials

### Option 1: Via UI
1. Login page → Create Account tab
2. Select role (Admin or User)
3. Enter identifier and code
4. Click "✨ Create Account"

### Option 2: Manual Edit
Edit `credentials.json`:
```json
{
  "admins": {
    "admin": "admin123",
    "john_admin": "secret_pass"
  },
  "users": {
    "user1": "pass123",
    "user2": "demo456",
    "alice": "alice_password"
  }
}
```

Then restart the app.

## 📊 Debug Information

### Check Credentials Load
```python
from auth import load_credentials
creds = load_credentials()
print(creds)
```

### Verify Authentication
```python
from auth import verify_credentials
result = verify_credentials("admin", "admin123", "admin")
print(f"Login result: {result}")  # Should print: True
```

### Check Session State
In Streamlit sidebar, look for user info display:
- Shows username and role if logged in
- Shows 🚪 logout button if logged in
- Shows login page if not authenticated

## 🚀 Fresh Start (Nuclear Option)

If nothing works, start fresh:

```bash
# 1. Clear all cache and temp files
rmdir /s .streamlit\cache
rmdir /s __pycache__

# 2. Delete and regenerate credentials.json
del credentials.json

# 3. Restart app (will recreate defaults)
streamlit run app.py
```

The app will automatically create `credentials.json` with demo credentials.

## ✨ Latest Changes (Fixed)

**Version 2.0 - Input Handling Fixes:**
- ✅ Removed column layout (was causing input issues)
- ✅ Added `.strip()` to remove whitespace
- ✅ Improved error messages with role indication
- ✅ Better validation before credential check
- ✅ Full-width input fields for better UX

## 📞 Getting Help

1. Run `test_login_creds.py` to verify credentials work
2. Check console output for error messages
3. Clear cache and restart
4. Verify credentials.json format
5. Check browser console for JavaScript errors (F12)

---

**Last Updated:** 2026-06-05
**Version:** 2.0 - Fixed Input Handling
