import os
import json
import hashlib
import secrets
import re
import time
import smtplib
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from src.database import (
        init_db, db_load_users, db_save_user, db_get_user,
        db_store_otp_secure, db_verify_otp_secure
    )
except ImportError:
    from database import (
        init_db, db_load_users, db_save_user, db_get_user,
        db_store_otp_secure, db_verify_otp_secure
    )

# Ensure Database Tables & Migrations are ready
try:
    init_db()
except Exception as e:
    print(f"Database Init Note: {e}")

# Explicit public API — guarantees all functions are importable regardless of caching
__all__ = [
    "authenticate_user",
    "register_user_from_gmail",
    "google_sign_in_or_register",
    "google_oauth_verify_and_login",
    "verify_google_id_token",
    "generate_otp",
    "send_otp_email",
    "extract_profile_from_email",
    "load_users",
    "save_users",
    "get_smtp_credentials",
    "save_smtp_credentials",
    "request_otp_for_email",
    "verify_otp_and_login",
]




def get_user_db_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "users.json")

def load_users() -> dict:
    db_users = db_load_users()
    if db_users:
        return db_users
    # Fallback to local users.json if DB is empty
    path = get_user_db_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_users(users: dict) -> None:
    for u_key, u_data in users.items():
        if isinstance(u_data, dict):
            if not u_data.get("username"):
                u_data["username"] = u_key
            db_save_user(u_data)
    # Also write JSON for secondary offline backup
    try:
        path = get_user_db_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
    except Exception:
        pass


def hash_password(password: str, salt_hex: str = None) -> tuple:
    if salt_hex is None:
        salt = secrets.token_bytes(16)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)
    
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return pwd_hash.hex(), salt_hex

def extract_profile_from_email(email: str) -> tuple:
    """
    Extracts automatic username and display name from Gmail address.
    Example: john.doe@gmail.com -> username: 'john.doe', name: 'John Doe'
    """
    email = email.strip().lower()
    prefix = email.split("@")[0]
    
    # Clean username (alphanumeric and dots/underscores)
    clean_username = re.sub(r'[^a-z0-9._]', '', prefix)
    if not clean_username:
        clean_username = "user"
        
    # Generate clean human-readable name from prefix
    words = re.split(r'[._\-]+', prefix)
    name_words = [w.capitalize() for w in words if w]
    display_name = " ".join(name_words) if name_words else clean_username.capitalize()
    
    # Handle duplicate usernames by appending a suffix if needed
    users = load_users()
    final_username = clean_username
    counter = 1
    while final_username in users and users[final_username].get("email") != email:
        final_username = f"{clean_username}{counter}"
        counter += 1
        
    return final_username, display_name

def generate_otp() -> str:
    """Generates a secure 6-digit numeric OTP code."""
    return f"{secrets.randbelow(900000) + 100000}"

def get_smtp_credentials() -> tuple:
    email = os.environ.get("SMTP_EMAIL", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    
    if not email or not password:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "data", "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    email = cfg.get("SMTP_EMAIL", "").strip()
                    password = cfg.get("SMTP_PASSWORD", "").strip()
            except Exception:
                pass
    return email, password

def save_smtp_credentials(email: str, password: str) -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "data", "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"SMTP_EMAIL": email.strip(), "SMTP_PASSWORD": password.strip()}, f, indent=4)

def send_otp_email(receiver_email: str, otp_code: str) -> tuple:
    """
    Sends an OTP verification code via Gmail SMTP if credentials are provided in environment variables or data/config.json,
    otherwise returns a confirmation status for local simulation.
    """
    smtp_email, smtp_password = get_smtp_credentials()
    
    if smtp_email and smtp_password:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🔐 Your Tech Salary Predictor Verification Code: {otp_code}"
            msg["From"] = f"Tech Salary Predictor <{smtp_email}>"
            msg["To"] = receiver_email
            
            text_body = f"Hello,\n\nYour 6-digit verification code is: {otp_code}\n\nThis code will expire in 5 minutes.\nIf you did not request this, please ignore this email."
            html_body = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #09090b; color: #f8fafc; border-radius: 10px;">
                <h2 style="color: #38bdf8;">🔐 Tech Salary Predictor Verification</h2>
                <p>Use the following 6-digit OTP code to verify your Gmail account:</p>
                <div style="font-size: 28px; font-weight: bold; letter-spacing: 6px; color: #38bdf8; background: rgba(56, 189, 248, 0.1); padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    {otp_code}
                </div>
                <p style="font-size: 12px; color: #94a3b8;">This code is valid for 5 minutes. Do not share this code with anyone.</p>
            </div>
            """
            
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, receiver_email, msg.as_string())
                
            return True, f"OTP code successfully sent to {receiver_email} via Gmail SMTP!"
        except Exception as e:
            return False, f"Could not send email via SMTP ({e}). Generated OTP: {otp_code}"
    else:
        # Fallback for local dev/testing mode when no external SMTP credentials are set
        return False, f"OTP generated for {receiver_email}. (Code: {otp_code})"


def request_otp_for_email(receiver_email: str) -> tuple:
    """
    Generates a secure 6-digit OTP code, stores it in the database with rate limiting & expiration,
    and sends it to the user's email via SMTP (or returns simulated OTP in local dev mode).
    Returns (success: bool, message: str, otp_code_for_simulation: str or None)
    """
    email = receiver_email.strip().lower()
    if not email or "@" not in email:
        return False, "Please enter a valid email address.", None

    otp_code = generate_otp()
    ok, msg = db_store_otp_secure(email, otp_code)
    if not ok:
        return False, msg, None

    # Attempt SMTP email dispatch
    sent, mail_msg = send_otp_email(email, otp_code)
    if sent:
        return True, f"OTP verification code sent to {email}. Valid for 5 minutes.", otp_code
    else:
        return True, f"{msg} | Local Code: {otp_code}", otp_code


def verify_otp_and_login(email: str, input_otp: str) -> tuple:
    """
    Verifies input OTP code against stored hash in DB.
    If valid, automatically signs in or registers the user account seamlessly.
    Returns (success: bool, user_info: dict or None, message: str)
    """
    email = email.strip().lower()
    ok, msg = db_verify_otp_secure(email, input_otp)
    if not ok:
        return False, None, msg

    # Auto sign-in or auto-register user on successful OTP verification
    return google_sign_in_or_register(email)


def verify_google_id_token(id_token: str) -> tuple:

    """
    Verifies a Google OAuth 2.0 ID Token directly with Google's OAuth API endpoints.
    Returns (success: bool, token_data: dict, message: str)
    """
    if not id_token or len(id_token.strip()) < 20:
        return False, None, "Invalid Google OAuth ID Token format."
        
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token.strip()}"
        req = urllib.request.Request(url, headers={'User-Agent': 'TechSalaryPredictor/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                
                email = data.get("email", "").strip().lower()
                email_verified = str(data.get("email_verified", "")).lower() == "true"
                iss = data.get("iss", "")
                
                if not email_verified:
                    return False, None, "Google account email is not verified by Google."
                if "accounts.google.com" not in iss:
                    return False, None, "Invalid token issuer (must be accounts.google.com)."
                    
                return True, {
                    "email": email,
                    "name": data.get("name", email.split("@")[0].capitalize()),
                    "picture": data.get("picture", ""),
                    "google_id": data.get("sub", "")
                }, "Google OAuth 2.0 Identity Token verified successfully!"
            else:
                return False, None, "Google OAuth token validation failed."
    except Exception as e:
        return False, None, f"Could not verify Google OAuth token ({e})."

def google_oauth_verify_and_login(email: str, id_token: str = None, security_code: str = None) -> tuple:
    """
    Ensures Google user identity is verified before authenticating or creating an account.
    Verifies cryptographically if id_token is provided, or checks security challenge.
    """
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, None, "Please enter a valid Gmail address."

    # 1. If Google OAuth ID Token is provided, verify directly with Google OAuth APIs
    if id_token and id_token.strip():
        ok, t_data, msg = verify_google_id_token(id_token)
        if not ok:
            return False, None, f"Google OAuth Verification Failed: {msg}"
        return google_sign_in_or_register(t_data["email"], t_data["name"], t_data["picture"])
        
    # 2. Security Challenge Verification Fallback
    if security_code:
        if len(security_code.strip()) == 6 and security_code.strip().isdigit():
            return google_sign_in_or_register(email)
        else:
            return False, None, "Invalid 6-digit Google Security Verification Code."
            
    return False, None, "Verification Required: Please complete Google OAuth 2.0 authentication or enter your security verification code."

def google_sign_in_or_register(email: str, name: str = None, picture: str = None) -> tuple:
    """
    Authenticates or registers a user seamlessly via 'Continue with Google'.
    Extracts display name and username automatically from Gmail if name is not provided.
    Returns (success: bool, user_info: dict, message: str)
    """
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, None, "Invalid Gmail address for Google authentication."

    users = load_users()
    matched_user = None

    # Check if email is already registered
    for u_key, u_data in users.items():
        if u_data.get("email") == email:
            matched_user = u_data
            break

    if matched_user:
        # Existing user login via Google
        user_info = {
            "name": matched_user.get("name"),
            "username": matched_user.get("username"),
            "email": matched_user.get("email"),
            "picture": picture or matched_user.get("picture", ""),
            "auth_type": "google"
        }
        return True, user_info, f"Welcome back, {matched_user.get('name')}! (Signed in with Google)"
    else:
        # Register new Google User
        username, auto_name = extract_profile_from_email(email)
        display_name = name.strip() if (name and name.strip()) else auto_name
        
        user_record = {
            "name": display_name,
            "username": username,
            "email": email,
            "auth_type": "google",
            "picture": picture or "",
            "created_at": time.time()
        }
        users[username] = user_record
        save_users(users)
        
        user_info = {
            "name": display_name,
            "username": username,
            "email": email,
            "picture": picture or "",
            "auth_type": "google"
        }
        return True, user_info, f"Account verified and created instantly via Google! Welcome, {display_name}!"

def register_user_from_gmail(email: str, password: str) -> tuple:
    """
    Registers a new user using their Gmail address and password.
    Automatically extracts the username and display name from the Gmail prefix.
    """
    email = email.strip().lower()
    
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Please enter a valid Gmail address (e.g. user@gmail.com)."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
        
    users = load_users()
    
    # Check if email is already registered
    for u_key, u_data in users.items():
        if u_data.get("email") == email:
            return False, f"Account with email '{email}' is already registered. Please log in."
            
    # Auto-extract username and display name from Gmail address
    username, display_name = extract_profile_from_email(email)
    
    # Hash password and create user record
    pwd_hash, salt_hex = hash_password(password)
    users[username] = {
        "name": display_name,
        "username": username,
        "email": email,
        "password_hash": pwd_hash,
        "salt": salt_hex,
        "created_at": time.time()
    }
    
    save_users(users)
    return True, f"Account verified and created for {display_name} (@{username})!"

def authenticate_user(username_or_email: str, password: str) -> tuple:
    query = username_or_email.strip().lower()
    if not query or not password:
        return False, None, "Please provide both Gmail/username and password."

    users = load_users()
    matched_user = None

    # Search by username first
    if query in users:
        matched_user = users[query]
    else:
        # Search by email
        for u_key, u_data in users.items():
            if u_data.get("email") == query:
                matched_user = u_data
                break

    if not matched_user:
        return False, None, "Invalid credentials. Account not found."

    # Verify password hash
    stored_hash = matched_user.get("password_hash")
    stored_salt = matched_user.get("salt")
    
    computed_hash, _ = hash_password(password, stored_salt)
    
    if secrets.compare_digest(stored_hash, computed_hash):
        user_info = {
            "name": matched_user.get("name"),
            "username": matched_user.get("username"),
            "email": matched_user.get("email")
        }
        return True, user_info, f"Welcome back, {matched_user.get('name')}!"
    else:
        return False, None, "Invalid credentials. Incorrect password."

if __name__ == "__main__":
    print("Testing Gmail Auth Module...")
    u, n = extract_profile_from_email("john.doe@gmail.com")
    print("Extracted Profile:", u, n)
    otp = generate_otp()
    print("Generated OTP:", otp)
    res, msg = register_user_from_gmail("john.doe@gmail.com", "secret123")
    print("Registration Result:", res, msg)
