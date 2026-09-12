import os
import json
import sqlite3
import time
import hashlib
import secrets
from typing import Dict, Any, List, Tuple, Optional


# Optional MySQL imports
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


def get_db_config() -> Dict[str, Any]:
    """
    Retrieves MySQL credentials from environment variables or data/config.json.
    """
    config = {
        "host": os.environ.get("MYSQL_HOST", "").strip(),
        "user": os.environ.get("MYSQL_USER", "").strip(),
        "password": os.environ.get("MYSQL_PASSWORD", "").strip(),
        "database": os.environ.get("MYSQL_DATABASE", "salary_predictor_db").strip(),
        "port": int(os.environ.get("MYSQL_PORT", 3306))
    }

    if not config["host"] or not config["user"]:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "data", "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if cfg.get("MYSQL_HOST") and cfg.get("MYSQL_USER"):
                        config["host"] = cfg.get("MYSQL_HOST", "").strip()
                        config["user"] = cfg.get("MYSQL_USER", "").strip()
                        config["password"] = cfg.get("MYSQL_PASSWORD", "").strip()
                        config["database"] = cfg.get("MYSQL_DATABASE", "salary_predictor_db").strip()
                        config["port"] = int(cfg.get("MYSQL_PORT", 3306))
            except Exception:
                pass

    return config


def get_sqlite_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "app_database.db")


def get_connection() -> Tuple[Any, str]:
    """
    Attempts to connect to MySQL if configured and available.
    Falls back seamlessly to local SQLite if MySQL is unreachable or not configured.
    Returns (connection, db_type) where db_type is 'mysql' or 'sqlite'.
    """
    cfg = get_db_config()
    if MYSQL_AVAILABLE and cfg["host"] and cfg["user"]:
        try:
            conn = mysql.connector.connect(
                host=cfg["host"],
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                port=cfg["port"],
                connect_timeout=3
            )
            return conn, "mysql"
        except Exception:
            pass  # Fall back to SQLite if MySQL connection fails

    # SQLite fallback
    db_path = get_sqlite_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


def init_db() -> str:
    """
    Initializes SQL tables for Users and Predictions if they do not exist.
    """
    conn, db_type = get_connection()
    cursor = conn.cursor()

    if db_type == "mysql":
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255),
            password_hash VARCHAR(255),
            salt VARCHAR(255),
            auth_type VARCHAR(50) DEFAULT 'email',
            picture TEXT,
            created_at DOUBLE
        );
        """
        predictions_table_sql = """
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100),
            years_of_experience FLOAT,
            job_title VARCHAR(100),
            education_level VARCHAR(100),
            location VARCHAR(100),
            company_size VARCHAR(50),
            predicted_salary_lpa FLOAT,
            created_at DOUBLE
        );
        """
        otps_table_sql = """
        CREATE TABLE IF NOT EXISTS otps (
            email VARCHAR(255) PRIMARY KEY,
            otp_hash VARCHAR(255) NOT NULL,
            salt VARCHAR(255) NOT NULL,
            expires_at DOUBLE NOT NULL,
            last_requested_at DOUBLE NOT NULL,
            attempts INT DEFAULT 0
        );
        """
    else:
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            password_hash TEXT,
            salt TEXT,
            auth_type TEXT DEFAULT 'email',
            picture TEXT,
            created_at REAL
        );
        """
        predictions_table_sql = """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            years_of_experience REAL,
            job_title TEXT,
            education_level TEXT,
            location TEXT,
            company_size TEXT,
            predicted_salary_lpa REAL,
            created_at REAL
        );
        """
        otps_table_sql = """
        CREATE TABLE IF NOT EXISTS otps (
            email TEXT PRIMARY KEY,
            otp_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            expires_at REAL NOT NULL,
            last_requested_at REAL NOT NULL,
            attempts INTEGER DEFAULT 0
        );
        """

    cursor.execute(users_table_sql)
    cursor.execute(predictions_table_sql)
    cursor.execute(otps_table_sql)
    conn.commit()

    cursor.close()
    conn.close()


    # Migrate any existing users from users.json into the DB
    migrate_json_users()

    return db_type


def db_load_users() -> Dict[str, Dict[str, Any]]:
    """
    Loads all users from the active database into a dictionary keyed by username.
    """
    conn, db_type = get_connection()
    cursor = conn.cursor()

    users_dict = {}
    try:
        cursor.execute("SELECT username, email, name, password_hash, salt, auth_type, picture, created_at FROM users")
        rows = cursor.fetchall()

        for row in rows:
            if db_type == "sqlite":
                u_data = dict(row)
            else:
                u_data = {
                    "username": row[0],
                    "email": row[1],
                    "name": row[2],
                    "password_hash": row[3],
                    "salt": row[4],
                    "auth_type": row[5],
                    "picture": row[6],
                    "created_at": row[7]
                }
            users_dict[u_data["username"]] = u_data
    except Exception as e:
        print(f"Error loading users from database: {e}")
    finally:
        cursor.close()
        conn.close()

    return users_dict


def db_save_user(user_data: Dict[str, Any]) -> bool:
    """
    Inserts or updates a user record in the SQL database.
    """
    conn, db_type = get_connection()
    cursor = conn.cursor()

    username = user_data.get("username")
    email = user_data.get("email")
    name = user_data.get("name", "")
    password_hash = user_data.get("password_hash", "")
    salt = user_data.get("salt", "")
    auth_type = user_data.get("auth_type", "email")
    picture = user_data.get("picture", "")
    created_at = user_data.get("created_at", time.time())

    try:
        if db_type == "mysql":
            sql = """
            INSERT INTO users (username, email, name, password_hash, salt, auth_type, picture, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                email = VALUES(email),
                name = VALUES(name),
                password_hash = VALUES(password_hash),
                salt = VALUES(salt),
                auth_type = VALUES(auth_type),
                picture = VALUES(picture);
            """
            cursor.execute(sql, (username, email, name, password_hash, salt, auth_type, picture, created_at))
        else:
            sql = """
            INSERT INTO users (username, email, name, password_hash, salt, auth_type, picture, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                email = excluded.email,
                name = excluded.name,
                password_hash = excluded.password_hash,
                salt = excluded.salt,
                auth_type = excluded.auth_type,
                picture = excluded.picture;
            """
            cursor.execute(sql, (username, email, name, password_hash, salt, auth_type, picture, created_at))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving user to DB: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def db_get_user(username_or_email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single user by username or email.
    """
    conn, db_type = get_connection()
    cursor = conn.cursor()
    query = username_or_email.strip().lower()

    try:
        placeholder = "%s" if db_type == "mysql" else "?"
        sql = f"""
        SELECT username, email, name, password_hash, salt, auth_type, picture, created_at 
        FROM users 
        WHERE LOWER(username) = {placeholder} OR LOWER(email) = {placeholder}
        LIMIT 1
        """
        cursor.execute(sql, (query, query))
        row = cursor.fetchone()

        if row:
            if db_type == "sqlite":
                return dict(row)
            else:
                return {
                    "username": row[0],
                    "email": row[1],
                    "name": row[2],
                    "password_hash": row[3],
                    "salt": row[4],
                    "auth_type": row[5],
                    "picture": row[6],
                    "created_at": row[7]
                }
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def db_save_prediction(username: str, pred_data: Dict[str, Any]) -> bool:
    """
    Logs a prediction query into the predictions database table.
    """
    conn, db_type = get_connection()
    cursor = conn.cursor()

    placeholder = "%s" if db_type == "mysql" else "?"
    sql = f"""
    INSERT INTO predictions 
    (username, years_of_experience, job_title, education_level, location, company_size, predicted_salary_lpa, created_at)
    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """
    vals = (
        username,
        float(pred_data.get("years_of_experience", 0)),
        str(pred_data.get("job_title", "")),
        str(pred_data.get("education_level", "")),
        str(pred_data.get("location", "")),
        str(pred_data.get("company_size", "")),
        float(pred_data.get("predicted_salary_lpa", 0)),
        time.time()
    )

    try:
        cursor.execute(sql, vals)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving prediction to DB: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def db_get_user_predictions(username: str) -> List[Dict[str, Any]]:
    """
    Retrieves past predictions made by a specific user.
    """
    conn, db_type = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if db_type == "mysql" else "?"

    sql = f"""
    SELECT years_of_experience, job_title, education_level, location, company_size, predicted_salary_lpa, created_at
    FROM predictions
    WHERE username = {placeholder}
    ORDER BY created_at DESC
    """

    results = []
    try:
        cursor.execute(sql, (username,))
        rows = cursor.fetchall()
        for row in rows:
            if db_type == "sqlite":
                results.append(dict(row))
            else:
                results.append({
                    "years_of_experience": row[0],
                    "job_title": row[1],
                    "education_level": row[2],
                    "location": row[3],
                    "company_size": row[4],
                    "predicted_salary_lpa": row[5],
                    "created_at": row[6]
                })
    except Exception as e:
        print(f"Error fetching user predictions: {e}")
    finally:
        cursor.close()
        conn.close()

    return results


def migrate_json_users() -> None:
    """
    Reads existing users from data/users.json and inserts them into the SQL database.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "data", "users.json")

    if not os.path.exists(json_path):
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            users_json = json.load(f)

        if not isinstance(users_json, dict):
            return

        for username, u_data in users_json.items():
            if isinstance(u_data, dict):
                if not u_data.get("username"):
                    u_data["username"] = username
                db_save_user(u_data)
    except Exception as e:
        print(f"Migration note: Could not migrate users.json to DB ({e})")


def db_store_otp_secure(email: str, otp_code: str) -> Tuple[bool, str]:
    """
    Stores an OTP code securely:
    - Enforces a 60-second request rate-limit per email.
    - Hashes the OTP using PBKDF2 HMAC SHA-256 with a random salt.
    - Sets an expiration of exactly 5 minutes (300 seconds).
    - Resets attempts counter to 0.
    """
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Invalid email address format."

    conn, db_type = get_connection()
    cursor = conn.cursor()
    now = time.time()
    placeholder = "%s" if db_type == "mysql" else "?"

    try:
        # 1. Rate Limit Check (60 seconds)
        sql_check = f"SELECT last_requested_at FROM otps WHERE email = {placeholder}"
        cursor.execute(sql_check, (email,))
        row = cursor.fetchone()

        if row:
            last_req = row[0] if db_type == "mysql" else (dict(row).get("last_requested_at", 0) if isinstance(row, sqlite3.Row) else row[0])
            elapsed = now - float(last_req)
            if elapsed < 60:
                cooldown_remaining = int(60 - elapsed)
                return False, f"Rate limit reached. Please wait {cooldown_remaining}s before requesting a new code."

        # 2. Hash OTP with Salt
        salt = secrets.token_bytes(16)
        salt_hex = salt.hex()
        otp_hash = hashlib.pbkdf2_hmac(
            'sha256',
            otp_code.encode('utf-8'),
            salt,
            100000
        ).hex()

        expires_at = now + 300.0  # 5 minutes

        # 3. Store/Upsert in otps table
        if db_type == "mysql":
            sql_upsert = """
            INSERT INTO otps (email, otp_hash, salt, expires_at, last_requested_at, attempts)
            VALUES (%s, %s, %s, %s, %s, 0)
            ON DUPLICATE KEY UPDATE
                otp_hash = VALUES(otp_hash),
                salt = VALUES(salt),
                expires_at = VALUES(expires_at),
                last_requested_at = VALUES(last_requested_at),
                attempts = 0;
            """
            cursor.execute(sql_upsert, (email, otp_hash, salt_hex, expires_at, now))
        else:
            sql_upsert = """
            INSERT INTO otps (email, otp_hash, salt, expires_at, last_requested_at, attempts)
            VALUES (?, ?, ?, ?, ?, 0)
            ON CONFLICT(email) DO UPDATE SET
                otp_hash = excluded.otp_hash,
                salt = excluded.salt,
                expires_at = excluded.expires_at,
                last_requested_at = excluded.last_requested_at,
                attempts = 0;
            """
            cursor.execute(sql_upsert, (email, otp_hash, salt_hex, expires_at, now))

        conn.commit()
        return True, "Verification code generated and sent! (Valid for 5 minutes)"
    except Exception as e:
        print(f"Error storing OTP: {e}")
        return False, f"Database error storing OTP: {e}"
    finally:
        cursor.close()
        conn.close()


def db_verify_otp_secure(email: str, input_otp: str) -> Tuple[bool, str]:
    """
    Verifies an input OTP code securely:
    - Enforces 5-minute expiration window.
    - Enforces 3-strike lockout policy (invalidates code on 3rd wrong attempt).
    - Uses constant-time hash comparison (secrets.compare_digest).
    - Deletes code immediately upon successful verification (single-use).
    """
    email = email.strip().lower()
    input_otp = input_otp.strip()

    if not email or "@" not in email:
        return False, "Invalid email address format."
    if not input_otp or len(input_otp) != 6 or not input_otp.isdigit():
        return False, "Verification code must be a 6-digit number."

    conn, db_type = get_connection()
    cursor = conn.cursor()
    now = time.time()
    placeholder = "%s" if db_type == "mysql" else "?"

    try:
        sql_select = f"SELECT otp_hash, salt, expires_at, attempts FROM otps WHERE email = {placeholder}"
        cursor.execute(sql_select, (email,))
        row = cursor.fetchone()

        if not row:
            return False, "No verification code requested for this email. Please request a new one."

        if db_type == "sqlite":
            record = dict(row)
            stored_hash = record["otp_hash"]
            stored_salt_hex = record["salt"]
            expires_at = float(record["expires_at"])
            attempts = int(record["attempts"])
        else:
            stored_hash = row[0]
            stored_salt_hex = row[1]
            expires_at = float(row[2])
            attempts = int(row[3])

        # 1. Expiration check (5 minutes)
        if now > expires_at:
            sql_del = f"DELETE FROM otps WHERE email = {placeholder}"
            cursor.execute(sql_del, (email,))
            conn.commit()
            return False, "Verification code has expired (valid for 5 minutes). Please request a new code."

        # 2. Lockout check (3 strikes)
        if attempts >= 3:
            sql_del = f"DELETE FROM otps WHERE email = {placeholder}"
            cursor.execute(sql_del, (email,))
            conn.commit()
            return False, "Too many failed attempts (3-strike limit reached). Code invalidated. Please request a new code."

        # 3. Hash computation & verification
        salt_bytes = bytes.fromhex(stored_salt_hex)
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            input_otp.encode('utf-8'),
            salt_bytes,
            100000
        ).hex()

        if secrets.compare_digest(stored_hash, computed_hash):
            # Success! Delete OTP (single use)
            sql_del = f"DELETE FROM otps WHERE email = {placeholder}"
            cursor.execute(sql_del, (email,))
            conn.commit()
            return True, "Verification successful!"
        else:
            # Failed attempt - increment strikes
            new_attempts = attempts + 1
            if new_attempts >= 3:
                sql_del = f"DELETE FROM otps WHERE email = {placeholder}"
                cursor.execute(sql_del, (email,))
                conn.commit()
                return False, "Incorrect verification code. Maximum 3 failed attempts reached. Code has been invalidated."
            else:
                sql_upd = f"UPDATE otps SET attempts = {placeholder} WHERE email = {placeholder}"
                cursor.execute(sql_upd, (new_attempts, email))
                conn.commit()
                remaining = 3 - new_attempts
                return False, f"Incorrect verification code. {remaining} attempt(s) remaining."

    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return False, f"Database error verifying OTP: {e}"
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    db_type = init_db()
    print(f"Database initialized successfully! Active DB type: {db_type.upper()}")

