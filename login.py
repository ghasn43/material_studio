"""
Login page UI for Materials Science AI app
Clean, minimal login interface with admin and user options
"""

import streamlit as st
from auth import (
    verify_credentials,
    register_user,
    set_authenticated,
    init_session_state,
)


def show_login_page():
    """Display the login page"""
    init_session_state()
    
    # Set page config
    st.set_page_config(
        page_title="Materials Science AI - Login",
        page_icon="🔐",
        layout="centered"
    )
    
    # Remove sidebar for login page
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {
                display: none
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Main container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🧪 Materials Science AI</h1>", 
                   unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Advanced Material Classification System</p>", 
                   unsafe_allow_html=True)
        st.markdown("---")
        
        # Login mode selection
        login_type = st.radio(
            "Access Type",
            ["👤 User", "⚙️ Administrator"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Determine if admin or user
        is_admin_login = login_type == "⚙️ Administrator"
        role = "admin" if is_admin_login else "user"
        
        # Create tabs for login/register
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            st.markdown("### Sign In")
            
            # Input fields - full width for better UX
            identifier = st.text_input(
                label="identifier",
                placeholder="Enter identifier",
                label_visibility="collapsed",
                key=f"login_id_{role}"
            )
            
            password = st.text_input(
                label="password",
                type="password",
                placeholder="Enter code",
                label_visibility="collapsed",
                key=f"login_pass_{role}"
            )
            
            if st.button("🔓 Access System", use_container_width=True, type="primary"):
                if not identifier.strip() or not password.strip():
                    st.error("⚠️ Both fields required")
                else:
                    # Debug: Show what we're checking
                    if verify_credentials(identifier.strip(), password.strip(), role):
                        set_authenticated(identifier.strip(), role)
                        st.success(f"✅ Welcome, {identifier}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Invalid credentials for {role} account")
            
            # Display demo credentials
            st.info("📝 Demo Credentials:\n\n" +
                   ("**Admin:** admin / admin123\n" if is_admin_login else "**User 1:** user1 / pass123\n**User 2:** user2 / demo456\n"))
        
        with tab2:
            st.markdown("### Create Account")
            
            new_identifier = st.text_input(
                label="new_id",
                placeholder="Choose identifier",
                label_visibility="collapsed",
                key=f"reg_id_{role}"
            )
            
            new_password = st.text_input(
                label="new_pass",
                type="password",
                placeholder="Set code (min 6 chars)",
                label_visibility="collapsed",
                key=f"reg_pass_{role}"
            )
            
            if st.button("✨ Create Account", use_container_width=True):
                if not new_identifier.strip() or not new_password.strip():
                    st.error("⚠️ Both fields required")
                else:
                    result = register_user(new_identifier.strip(), new_password.strip(), role)
                    if result["success"]:
                        st.success(f"✅ {result['message']}")
                        st.info("Now try signing in with your new credentials")
                    else:
                        st.error(f"❌ {result['message']}")
        
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; font-size: 12px; color: #999;'>"
            "Materials Science AI • Advanced Classification Engine"
            "</p>",
            unsafe_allow_html=True
        )
