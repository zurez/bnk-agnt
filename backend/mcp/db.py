DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://banking_user:demo_password@postgres:5432/banking_demo")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Reflect tables
metadata.reflect(bind=engine)
users = metadata.tables['users']
accounts = metadata.tables['accounts']
transactions = metadata.tables['transactions']
transfer_log = metadata.tables['transfer_log']