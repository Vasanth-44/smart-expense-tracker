"""
Database migration script to add new SaaS columns
"""

import sqlite3

def migrate_database():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    try:
        # Add is_admin column to users table
        print("Adding is_admin column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        print("✅ Added is_admin column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️  is_admin column already exists")
        else:
            print(f"❌ Error adding is_admin: {e}")
    
    try:
        # Add created_at column to users table
        print("Adding created_at column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN created_at DATETIME")
        print("✅ Added created_at column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️  created_at column already exists")
        else:
            print(f"❌ Error adding created_at: {e}")
    
    try:
        # Add group_id column to expenses table
        print("Adding group_id column to expenses table...")
        cursor.execute("ALTER TABLE expenses ADD COLUMN group_id INTEGER")
        print("✅ Added group_id column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️  group_id column already exists")
        else:
            print(f"❌ Error adding group_id: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Database migration completed!")
    print("="*60)
    print("\nNow creating new SaaS tables...")
    
    # Create new tables using SQLAlchemy
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    print("✅ All SaaS tables created!")
    print("\nYou can now run: python create_test_users.py")

if __name__ == "__main__":
    print("\n🔧 Migrating Database for SaaS Features...\n")
    migrate_database()
