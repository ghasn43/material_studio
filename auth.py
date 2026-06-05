"""
Authentication module for Materials Science AI app
Handles user login, admin access, and session management
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st

# Credentials storage file
CREDENTIALS_FILE = Path("credentials.json")

# Default admin and user credentials (hardcoded for demo)
DEFAULT_CREDENTIALS = {
    "admins": {
        "admin": "admin123",  # username: password (hash in production)
    },
    "users": {
        "user1": "pass123",
        "user2": "demo456",
    }
}


def load_credentials():
    """Load credentials from file or create default ones"""
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    else:
        # Save default credentials
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(DEFAULT_CREDENTIALS, f, indent=2)
        return DEFAULT_CREDENTIALS


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_credentials(identifier: str, password: str, role: str = "user") -> bool:
    """
    Verify user credentials
    
    Args:
        identifier: Username or email
        password: Password to verify
        role: 'admin' or 'user'
    
    Returns:
        True if credentials are valid, False otherwise
    """
    credentials = load_credentials()
    
    if role == "admin":
        users = credentials.get("admins", {})
    else:
        users = credentials.get("users", {})
    
    # For demo: plain text comparison (use hashing in production)
    return users.get(identifier) == password


def register_user(identifier: str, password: str, role: str = "user") -> dict:
    """
    Register a new user
    
    Args:
        identifier: Username
        password: Password
        role: 'admin' or 'user'
    
    Returns:
        Dict with status and message
    """
    credentials = load_credentials()
    
    if role == "admin":
        users = credentials.get("admins", {})
    else:
        users = credentials.get("users", {})
    
    if identifier in users:
        return {"success": False, "message": "User already exists"}
    
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters"}
    
    users[identifier] = password
    credentials[f"{'admins' if role == 'admin' else 'users'}"] = users
    
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=2)
    
    return {"success": True, "message": "User registered successfully"}


def init_session_state():
    """Initialize session state for authentication"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "login_time" not in st.session_state:
        st.session_state.login_time = None


def set_authenticated(username: str, role: str):
    """Set user as authenticated"""
    st.session_state.authenticated = True
    st.session_state.user_role = role
    st.session_state.username = username
    st.session_state.login_time = datetime.now()


def logout():
    """Log out current user"""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.login_time = None


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)


def is_admin() -> bool:
    """Check if logged-in user is admin"""
    return st.session_state.get("user_role") == "admin"


def get_username() -> str:
    """Get current username"""
    return st.session_state.get("username", "Guest")


def get_user_role() -> str:
    """Get current user role"""
    return st.session_state.get("user_role", "guest")
