from main import app, db
from sqlalchemy import inspect

def test_db_connection():
    with app.app_context():
        try:
            # Try to connect to the database
            db.engine.connect()
            print('Successfully connected to the database')
            
            # Get table names
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print('Existing tables:', tables)
        except Exception as e:
            print('Error connecting to the database:', str(e))

if __name__ == '__main__':
    test_db_connection()
