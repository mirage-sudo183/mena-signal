"""
Seed script to create demo user and trigger initial ingestion.
Run with: python seed.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_context
from app.models import User
from app.auth import get_password_hash
from app.services.ingestion import load_sources_from_yaml, ingest_all_sources


def seed_demo_user():
    """Create a demo user if not exists."""
    with get_db_context() as db:
        existing = db.query(User).filter(User.email == "demo@menasignal.com").first()
        if existing:
            print("Demo user already exists")
            return
        
        user = User(
            email="demo@menasignal.com",
            password_hash=get_password_hash("demo123"),
        )
        db.add(user)
        db.commit()
        print("Created demo user: demo@menasignal.com / demo123")


def main():
    print("=" * 50)
    print("MENA Signal - Seed Script")
    print("=" * 50)
    
    # Load sources from YAML
    print("\n1. Loading sources from YAML...")
    load_sources_from_yaml()
    print("   Sources loaded successfully")
    
    # Create demo user
    print("\n2. Creating demo user...")
    seed_demo_user()
    
    # Run initial ingestion
    print("\n3. Running initial ingestion...")
    print("   This may take a minute...")
    results = ingest_all_sources()
    
    total_items = 0
    for source_id, result in results.items():
        if isinstance(result, dict) and result.get('status') == 'success':
            items = result.get('items_added', 0)
            total_items += items
            print(f"   Source {source_id}: {items} items added")
        else:
            print(f"   Source {source_id}: {result}")
    
    print(f"\n   Total items ingested: {total_items}")
    
    print("\n" + "=" * 50)
    print("Seed completed!")
    print("=" * 50)
    print("\nYou can now login with:")
    print("  Email: demo@menasignal.com")
    print("  Password: demo123")


if __name__ == "__main__":
    main()

