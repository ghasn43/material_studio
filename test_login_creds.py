from auth import verify_credentials, load_credentials
import json

# Load and display credentials
print("Current credentials in file:")
creds = load_credentials()
print(json.dumps(creds, indent=2))

print("\n" + "="*50)
print("Testing credentials...\n")

# Test admin
result = verify_credentials("admin", "admin123", "admin")
print(f"Admin login (admin/admin123): {result}")

# Test user1
result = verify_credentials("user1", "pass123", "user")
print(f"User1 login (user1/pass123): {result}")

# Test user2
result = verify_credentials("user2", "demo456", "user")
print(f"User2 login (user2/demo456): {result}")

# Test invalid
result = verify_credentials("admin", "wrongpass", "admin")
print(f"Invalid password: {result}")
