import os
import sys

# Add project root to sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from src.database import init_db, db_load_users, get_connection, get_db_config

def main():
    print("=" * 60)
    print(" DATABASE INITIALIZATION UTILITY - TECH SALARY PREDICTOR")
    print("=" * 60)


    cfg = get_db_config()
    if cfg.get("host") and cfg.get("user"):
        print(f"[+] MySQL Configuration Found:")
        print(f"   Host:     {cfg['host']}")
        print(f"   Port:     {cfg['port']}")
        print(f"   Database: {cfg['database']}")
        print(f"   User:     {cfg['user']}")
    else:
        print("[i] No MySQL configuration found in ENV or data/config.json.")
        print("   Defaulting to local embedded SQLite database.")

    print("\nInitializing database tables and running data migrations...")
    db_type = init_db()
    print(f"[+] Success! Active Database Engine: {db_type.upper()}")

    users = db_load_users()
    print(f"[*] Total Registered Users in Database: {len(users)}")
    for username, udata in users.items():
        print(f"   - @{username} ({udata.get('email')}) | Auth: {udata.get('auth_type', 'email')}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
