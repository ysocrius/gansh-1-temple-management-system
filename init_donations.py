from database import donations_collection, donations_list
from datetime import datetime, timedelta

def init_donations_data():
    # Clear existing data
    donations_list.delete_many({})
    donations_collection.delete_many({})
    
    # Insert donation types
    donation_types = [
        {
            "id": "general",
            "name": "General Donation",
            "description": "Support the temple's daily activities and maintenance",
            "min_amount": 100
        },
        {
            "id": "development",
            "name": "Temple Development",
            "description": "Contribute to temple expansion and improvement projects",
            "min_amount": 1000
        },
        {
            "id": "annadanam",
            "name": "Annadanam",
            "description": "Sponsor food for devotees and the needy",
            "min_amount": 500
        },
        {
            "id": "festival",
            "name": "Festival Sponsorship",
            "description": "Support temple festivals and special events",
            "min_amount": 2000
        }
    ]
    donations_list.insert_many(donation_types)
    
    # Insert sample recent donations
    current_date = datetime.now()
    recent_donations = [
        {
            "donor_name": "Ramesh Kumar",
            "amount": 1000,
            "type": "General Donation",
            "date": current_date - timedelta(days=1)
        },
        {
            "donor_name": "Priya Sharma",
            "amount": 5000,
            "type": "Temple Development",
            "date": current_date - timedelta(days=2)
        },
        {
            "donor_name": "Anonymous",
            "amount": 750,
            "type": "Annadanam",
            "date": current_date - timedelta(days=3)
        },
        {
            "donor_name": "Suresh Patel",
            "amount": 2500,
            "type": "Festival Sponsorship",
            "date": current_date - timedelta(days=4)
        },
        {
            "donor_name": "Anonymous",
            "amount": 200,
            "type": "General Donation",
            "date": current_date - timedelta(days=5)
        }
    ]
    donations_collection.insert_many(recent_donations)
    
    print("Sample donations data initialized successfully!")

if __name__ == "__main__":
    init_donations_data() 