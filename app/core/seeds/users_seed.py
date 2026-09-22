from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.features.users.model import User

FIRST_NAMES = [
    "Muhammad",
    "Ahmed",
    "Ali",
    "Hassan",
    "Hussain",
    "Ibrahim",
    "Ismail",
    "Yusuf",
    "Omar",
    "Usman",
    "Bilal",
    "Hamza",
    "Zain",
    "Ayaan",
    "Rayyan",
    "Abdullah",
    "Abdul Rahman",
    "Abdul Hadi",
    "Adeel",
    "Adnan",
    "Arham",
    "Danish",
    "Ehsan",
    "Fahad",
    "Farhan",
    "Imran",
    "Junaid",
    "Kashif",
    "Muneeb",
    "Noman",
    "Qasim",
    "Rashid",
    "Saad",
    "Salman",
    "Sameer",
    "Shahzaib",
    "Shoaib",
    "Talha",
    "Waleed",
    "Yahya",
    "Aisha",
    "Amina",
    "Amna",
    "Anaya",
    "Arwa",
    "Ayra",
    "Bushra",
    "Fatima",
    "Hafsa",
    "Hania",
    "Hiba",
    "Iqra",
    "Khadija",
    "Maryam",
    "Mariam",
    "Maham",
    "Mehwish",
    "Mishal",
    "Noor",
    "Rida",
    "Saba",
    "Sadia",
    "Sana",
    "Sara",
    "Sobia",
    "Sumaya",
    "Sundas",
    "Uzma",
    "Yasmeen",
    "Zainab",
    "Zara",
]

LAST_NAMES = [
    "Khan",
    "Ahmed",
    "Malik",
    "Qureshi",
    "Siddiqui",
    "Hussain",
    "Raza",
    "Farooq",
    "Iqbal",
    "Chaudhry",
    "Sheikh",
    "Butt",
    "Mirza",
    "Mahmood",
    "Javed",
]


def build_users(count: int = 1000) -> list[User]:
    password_hash = hash_password("admin@123")
    users = []

    for index in range(count):
        first_name = FIRST_NAMES[index % len(FIRST_NAMES)]
        last_name = LAST_NAMES[index // len(FIRST_NAMES)]
        sequence = index + 1
        users.append(
            User(
                username=f"dummy_user_{sequence:04d}",
                email=f"dummy.user{sequence:04d}@example.com",
                full_name=f"{first_name} {last_name}",
                password=password_hash,
                role="user",
                is_verified=True,
            )
        )

    return users


def seed_users(count: int = 1000) -> int:
    db: Session = SessionLocal()

    try:
        users = build_users(count)
        usernames = [user.username for user in users]
        existing_usernames = {
            username
            for (username,) in db.query(User.username)
            .filter(User.username.in_(usernames))
            .all()
        }
        new_users = [user for user in users if user.username not in existing_usernames]

        db.add_all(new_users)
        db.commit()
        print(f"Created {len(new_users)} dummy users. Shared password: admin@123")
        return len(new_users)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
