# app/core/seeds/admin_seed.py

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.features.users.model import User
from app.features.auth.utils import hash_password


def create_admin():
    db: Session = SessionLocal()

    try:
        # 1. check if admin already exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()

        if admin:
            print("Admin already exists")
            return

        # 2. create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="System Admin",
            password=hash_password("admin@123"),
            role="admin",
        )

        db.add(admin_user)
        db.commit()

        print("Admin created successfully")

    except Exception as e:
        db.rollback()
        print("Error creating admin:", str(e))

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
