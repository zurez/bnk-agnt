from datetime import datetime
import os
from typing import List
from sqlalchemy import create_engine, select, text, MetaData, insert, update
import uuid 


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://zurez@127.0.0.1:5432/banking_demo")
DATABASE_URL="postgresql://zurez@127.0.0.1:5432/banking_demo"
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Reflect tables
metadata.reflect(bind=engine)
users = metadata.tables['users']
accounts = metadata.tables['accounts']
transactions = metadata.tables['transactions']
transfer_log = metadata.tables['transfer_log']



class BankingMCPServer:
    """
    This is not like a real MCP. Just simlates it 
    """
    
    async def get_balance(self, user_id: str) -> List[dict]:
        with engine.connect() as conn:
            result = conn.execute(
                select(accounts).where(accounts.c.user_id == user_id)
            )
            rows = []
            for row in result:
                d = dict(row._mapping)
                d['id'] = str(d['id'])
                d['user_id'] = str(d['user_id'])
                rows.append(d)
            return rows
    
    async def get_transactions(
        self, 
        user_id: str,
        from_date: str = None,
        to_date: str = None,
        category: str = None,
        limit: int = 10
    ) -> List[dict]:
        query = select(transactions).where(
            transactions.c.account_id.in_(
                select(accounts.c.id).where(accounts.c.user_id == user_id)
            )
        )
        
        if from_date:
            query = query.where(transactions.c.timestamp >= from_date)
        if to_date:
            query = query.where(transactions.c.timestamp <= to_date)
        if category:
            query = query.where(transactions.c.category == category)
        
        query = query.limit(limit).order_by(transactions.c.timestamp.desc())
        
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = []
            for row in result:
                d = dict(row._mapping)
                d['id'] = str(d['id'])
                d['account_id'] = str(d['account_id'])
                d['timestamp'] = d['timestamp'].isoformat()
                d['created_at'] = d['created_at'].isoformat()
                rows.append(d)
            return rows
    
    async def get_spend_by_category(
        self,
        user_id: str,
        from_date: str = None,
        to_date: str = None
    ) -> List[dict]:
      
        query = select(
            transactions.c.category,
            text("SUM(amount) as total")
        ).where(
            transactions.c.account_id.in_(
                select(accounts.c.id).where(accounts.c.user_id == user_id)
            )
        ).group_by(transactions.c.category)

        if from_date:
            query = query.where(transactions.c.timestamp >= from_date)
        if to_date:
            query = query.where(transactions.c.timestamp <= to_date)
            
        with engine.connect() as conn:
            result = conn.execute(query)
            return [{"category": row.category, "total": float(row.total)} for row in result]
    
    async def propose_transfer(
        self,
        user_id: str,
        from_account_name: str,
        to_account_name: str,
        amount: float,
        currency: str = "AED"
    ) -> dict:
        """
        Does NOT execute the transfer yet, may add human in middlke here.
        """
        with engine.begin() as conn:
            # Helper to find account
            def find_account(name_part):
                stmt = select(accounts).where(
                    accounts.c.user_id == user_id,
                    accounts.c.name.ilike(f"%{name_part}%")
                )
                return conn.execute(stmt).first()

            from_account = find_account(from_account_name)
            to_account = find_account(to_account_name)

            if not from_account:
                return {"success": False, "error": f"Source account '{from_account_name}' not found"}
            if not to_account:
                return {"success": False, "error": f"Destination account '{to_account_name}' not found"}
            
            if from_account.balance < amount:
                return {
                    "success": False,
                    "error": f"Insufficient funds in {from_account.name}. Balance: {from_account.balance}"
                }
            proposal_id = str(uuid.uuid4())
            conn.execute(
                insert(transfer_log).values(
                    id=proposal_id,
                    user_id=user_id,
                    from_account_id=from_account.id,
                    to_account_id=to_account.id,
                    amount=amount,
                    currency=currency,
                    status='pending',
                    created_at=datetime.utcnow()
                )
            )
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "from_account": from_account.name,
                "to_account": to_account.name,
                "amount": amount,
                "currency": currency,
                "message": "Transfer proposal created. Awaiting approval."
            }
    
    async def execute_transfer(self, proposal_id: str) -> dict:
     
        with engine.begin() as conn:
            proposal = conn.execute(
                select(transfer_log).where(
                    transfer_log.c.id == proposal_id,
                    transfer_log.c.status == 'pending'
                )
            ).first()
            
            if not proposal:
                return {"success": False, "error": "Proposal not found or already processed"}
            
         
            conn.execute(
                update(accounts)
                .where(accounts.c.id == proposal.from_account_id)
                .values(balance=accounts.c.balance - proposal.amount)
            )
            
            conn.execute(
                update(accounts)
                .where(accounts.c.id == proposal.to_account_id)
                .values(balance=accounts.c.balance + proposal.amount)
            )
            
            conn.execute(
                update(transfer_log)
                .where(transfer_log.c.id == proposal_id)
                .values(status='completed', executed_at=datetime.utcnow())
            )
            
            return {
                "success": True,
                "message": f"Transfer of {proposal.amount} {proposal.currency} completed"
            }
