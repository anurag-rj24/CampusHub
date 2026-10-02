from database.connection import create_connection
from utils.password import hash_password

def setup():
    conn = create_connection()
    cur = conn.cursor(dictionary=True)
    h = hash_password('test123')

    # Update admin
    cur.execute("UPDATE users SET password_hash = %s WHERE email = %s", (h, 'admin@campushub.com'))

    # Check super head
    cur.execute("SELECT * FROM users WHERE role = 'SUPER_HEAD'")
    sh = cur.fetchone()
    if not sh:
        cur.execute(
            "INSERT INTO users (first_name, last_name, email, phone, password_hash, role, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            ('Dr. Rajesh', 'Verma', 'director@campushub.com', '+91 9876543210', h, 'SUPER_HEAD', 'ACTIVE')
        )
        uid = cur.lastrowid
        cur.execute(
            """INSERT INTO super_head (user_id, designation, date_of_birth, gender, qualification, joining_date, salary, address, city, state, pincode)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (uid, 'Director & Super Head', '1975-08-15', 'MALE', 'Ph.D. in Computer Science', '2015-01-01', 250000.0, 'Campus Administrative Block 1', 'New Delhi', 'Delhi', '110001')
        )
    conn.commit()
    cur.close()
    conn.close()
    print("All demo credentials synchronized with password: test123")

if __name__ == "__main__":
    setup()
