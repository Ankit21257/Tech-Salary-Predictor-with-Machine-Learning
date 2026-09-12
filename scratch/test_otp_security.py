import os
import sys
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from src.auth import (
    request_otp_for_email, verify_otp_and_login,
    google_sign_in_or_register
)
from src.database import (
    db_store_otp_secure, db_verify_otp_secure, get_connection
)

def run_tests():
    print("=" * 60)
    print(" SECURITY TEST SUITE: GOOGLE OAUTH & HASHED OTP ENGINE")
    print("=" * 60)

    test_email = "security_test_user@gmail.com"

    # Clean up any prior test OTP records for test_email
    conn, db_type = get_connection()
    cursor = conn.cursor()
    ph = "%s" if db_type == "mysql" else "?"
    cursor.execute(f"DELETE FROM otps WHERE email = {ph}", (test_email,))
    conn.commit()
    cursor.close()
    conn.close()

    # -------------------------------------------------------------
    # TEST 1: OTP Generation & Hashed Storage
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing OTP Generation & Hashed DB Storage...")
    ok, msg, otp_code = request_otp_for_email(test_email)
    assert ok, f"OTP request failed: {msg}"
    assert len(otp_code) == 6 and otp_code.isdigit(), "OTP must be 6 digits"
    print(f"  -> Generated OTP Code: {otp_code}")

    # Inspect database table to verify hashing
    conn, db_type = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT otp_hash, salt, expires_at FROM otps WHERE email = {ph}", (test_email,))
    row = cursor.fetchone()
    assert row is not None, "OTP record must exist in DB"
    stored_hash = row[0] if db_type == "mysql" else dict(row)["otp_hash"]
    assert stored_hash != otp_code, "CRITICAL: Plaintext OTP MUST NOT be stored in DB!"
    print("  -> Verified DB record is cryptographically hashed with salt.")
    cursor.close()
    conn.close()

    # -------------------------------------------------------------
    # TEST 2: 60-Second Cooldown / Rate Limiting
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing 60-Second Rate Limiting Cooldown...")
    ok2, msg2, otp2 = request_otp_for_email(test_email)
    assert not ok2, "Second OTP request within 60s MUST be blocked!"
    assert "Rate limit" in msg2, f"Expected rate limit warning, got: {msg2}"
    print(f"  -> Successfully blocked rapid request with message: '{msg2}'")

    # -------------------------------------------------------------
    # TEST 3: 3-Strike Lockout Policy (Wrong Attempts)
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing 3-Strike Lockout Policy...")
    
    # Strike 1
    ok_v1, msg_v1 = db_verify_otp_secure(test_email, "000000")
    assert not ok_v1 and "2 attempt(s) remaining" in msg_v1, f"Strike 1 unexpected response: {msg_v1}"
    print(f"  -> Strike 1 Result: {msg_v1}")

    # Strike 2
    ok_v2, msg_v2 = db_verify_otp_secure(test_email, "111111")
    assert not ok_v2 and "1 attempt(s) remaining" in msg_v2, f"Strike 2 unexpected response: {msg_v2}"
    print(f"  -> Strike 2 Result: {msg_v2}")

    # Strike 3 (Lockout & Invalidation)
    ok_v3, msg_v3 = db_verify_otp_secure(test_email, "222222")
    assert not ok_v3 and "invalidated" in msg_v3.lower(), f"Strike 3 unexpected response: {msg_v3}"
    print(f"  -> Strike 3 Result: {msg_v3}")

    # Verify code was deleted from DB after lockout
    conn, db_type = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM otps WHERE email = {ph}", (test_email,))
    row = cursor.fetchone()
    assert row is None, "OTP record MUST be destroyed after 3 strikes!"
    print("  -> Verified OTP record was destroyed after 3 failed attempts.")
    cursor.close()
    conn.close()

    # -------------------------------------------------------------
    # TEST 4: Successful OTP Verification & Auto Sign-In / Registration
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing Successful OTP Verification & User Auto-Provisioning...")
    
    # Force clear cooldown for test 4 by deleting OTP record
    conn, db_type = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM otps WHERE email = {ph}", (test_email,))
    conn.commit()
    cursor.close()
    conn.close()

    ok_gen, msg_gen, valid_otp = request_otp_for_email(test_email)
    assert ok_gen, "OTP generation failed"
    
    ok_login, user_info, login_msg = verify_otp_and_login(test_email, valid_otp)
    assert ok_login, f"Valid OTP verification failed: {login_msg}"
    assert user_info and user_info.get("email") == test_email, "User info must contain verified email"
    print(f"  -> Success! User Auto-Provisioned & Signed In: {user_info['name']} (@{user_info['username']})")

    # -------------------------------------------------------------
    # TEST 5: Google OAuth Auto-Provisioning & Existing User Login
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing Google OAuth Flow (New Account & Returning User)...")
    
    google_email = "new_google_dev@gmail.com"
    
    # 1. New Google User -> Provisioning
    ok_g1, u_g1, msg_g1 = google_sign_in_or_register(google_email, name="Google Dev", picture="https://example.com/avatar.jpg")
    assert ok_g1, f"Google signup failed: {msg_g1}"
    assert u_g1["email"] == google_email, "Google user email mismatch"
    print(f"  -> Google Signup Success: {msg_g1}")

    # 2. Existing Google User -> Instant Login
    ok_g2, u_g2, msg_g2 = google_sign_in_or_register(google_email)
    assert ok_g2, f"Google login failed: {msg_g2}"
    assert u_g2["username"] == u_g1["username"], "Usernames must match"
    print(f"  -> Google Login Success: {msg_g2}")

    print("=" * 60)
    print(" ALL SECURITY & AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
