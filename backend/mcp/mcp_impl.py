import os
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, select, text, MetaData, insert, update, and_

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://zurez@127.0.0.1:5432/banking_demo")
DATABASE_URL = "postgresql://zurez@127.0.0.1:5432/banking_demo"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

users = metadata.tables['users']
accounts = metadata.tables['accounts']
transactions = metadata.tables['transactions']
beneficiaries = metadata.tables['beneficiaries']
transfer_log = metadata.tables['transfer_log']


class BankingMCPServer:
    """This is not like a real MCP. Just simlates it """
    
    async def get_balance(self, user_id: str) -> List[dict]:
        """Get all account balances for a user."""
        with engine.connect() as conn:
            result = conn.execute(
                select(accounts).where(
                    and_(accounts.c.user_id == user_id, accounts.c.is_active == True)
                )
            )
            return [self._row_to_dict(row) for row in result]

    async def get_transactions(
        self,
        user_id: str,
        from_date: str = None,
        to_date: str = None,
        category: str = None,
        limit: int = 10
    ) -> List[dict]:
        """Get transaction history with optional filters."""
        # Join with accounts to include account name in results
        query = select(
            transactions,
            accounts.c.name.label('account_name')
        ).select_from(
            transactions.join(accounts, transactions.c.account_id == accounts.c.id)
        ).where(
            accounts.c.user_id == user_id
        )
        
        if from_date:
            query = query.where(transactions.c.timestamp >= from_date)
        if to_date:
            query = query.where(transactions.c.timestamp <= to_date)
        if category:
            query = query.where(transactions.c.category == category)
        
        query = query.order_by(transactions.c.timestamp.desc()).limit(limit)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            return [dict(row._mapping) for row in result]

    async def get_spend_by_category(
        self,
        user_id: str,
        from_date: str = None,
        to_date: str = None
    ) -> List[dict]:
        """Get spending aggregated by category with optional date filters."""
        # Build conditions list to apply filters before GROUP BY
        conditions = [
            transactions.c.account_id.in_(
                select(accounts.c.id).where(accounts.c.user_id == user_id)
            ),
            transactions.c.type.in_(['debit', 'transfer_out'])
        ]
        
        # Add date filters to WHERE clause (before GROUP BY)
        if from_date:
            conditions.append(transactions.c.timestamp >= from_date)
        if to_date:
            conditions.append(transactions.c.timestamp <= to_date)
        
        query = select(
            transactions.c.category,
            text("SUM(amount) as total")
        ).where(
            and_(*conditions)
        ).group_by(transactions.c.category)
            
        with engine.connect() as conn:
            result = conn.execute(query)
            return [{"category": row.category, "total": float(row.total)} for row in result]


    async def get_beneficiaries(self, user_id: str) -> List[dict]:
        query = select(
            beneficiaries.c.id,
            beneficiaries.c.nickname,
            beneficiaries.c.account_number,
            beneficiaries.c.bank_name,
            beneficiaries.c.is_internal,
            users.c.name.label('beneficiary_name')
        ).select_from(
            beneficiaries.outerjoin(users, beneficiaries.c.beneficiary_user_id == users.c.id)
        ).where(
            and_(beneficiaries.c.user_id == user_id, beneficiaries.c.is_active == True)
        )
        
        with engine.connect() as conn:
            result = conn.execute(query)
            return [dict(row._mapping) for row in result]

    async def add_beneficiary(
        self,
        user_id: str,
        account_number: str,
        nickname: str
    ) -> dict:
      
        account_map = {
            'PDB-ALICE-001': ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
            'PDB-BOB-001': ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22'),
            'PDB-CAROL-001': ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33'),
        }
        
        if account_number not in account_map:
            return {"success": False, "error": f"Account {account_number} not found. Valid accounts: PDB-ALICE-001, PDB-BOB-001, PDB-CAROL-001"}
        
        beneficiary_user_id, beneficiary_account_id = account_map[account_number]
        
        if beneficiary_user_id == user_id:
            return {"success": False, "error": "Cannot add yourself as a beneficiary"}
        
        with engine.begin() as conn:
            existing = conn.execute(
                select(beneficiaries).where(
                    and_(
                        beneficiaries.c.user_id == user_id,
                        beneficiaries.c.account_number == account_number
                    )
                )
            ).first()
            
            if existing and existing.is_active:
                return {"success": False, "error": f"Beneficiary '{existing.nickname}' already exists"}
            
            if existing and not existing.is_active:
                conn.execute(
                    update(beneficiaries)
                    .where(beneficiaries.c.id == existing.id)
                    .values(
                        is_active=True,
                        nickname=nickname,
                        updated_at=datetime.utcnow()
                    )
                )
                return {"success": True, "beneficiary_id": str(existing.id), "message": f"Beneficiary '{nickname}' reactivated successfully"}
            
            new_id = str(uuid.uuid4())
            conn.execute(
                insert(beneficiaries).values(
                    id=new_id,
                    user_id=user_id,
                    beneficiary_user_id=beneficiary_user_id,
                    beneficiary_account_id=beneficiary_account_id,
                    nickname=nickname,
                    account_number=account_number,
                    bank_name='Phoenix Digital Bank',
                    is_internal=True
                )
            )
            
            return {"success": True, "beneficiary_id": new_id, "message": f"Beneficiary '{nickname}' added successfully"}


    async def remove_beneficiary(self, user_id: str, beneficiary_id: str) -> dict:
        """Soft delete a beneficiary."""
        with engine.begin() as conn:
            result = conn.execute(
                update(beneficiaries)
                .where(and_(beneficiaries.c.id == beneficiary_id, beneficiaries.c.user_id == user_id))
                .values(is_active=False, updated_at=datetime.utcnow())
            )
            
            if result.rowcount == 0:
                return {"success": False, "error": "Beneficiary not found"}
            
            return {"success": True, "message": "Beneficiary removed successfully"}

 

    async def propose_transfer(
        self,
        user_id: str,
        from_account_name: str,
        to_beneficiary_nickname: str,
        amount: float,
        description: str = ""
    ) -> dict:
        with engine.begin() as conn:
            from_account = conn.execute(
                select(accounts).where(
                    and_(
                        accounts.c.user_id == user_id,
                        accounts.c.name.ilike(f"%{from_account_name}%"),
                        accounts.c.is_active == True
                    )
                )
            ).first()
            
            if not from_account:
                return {"success": False, "error": f"Account '{from_account_name}' not found"}
            
            if from_account.balance < amount:
                return {"success": False, "error": f"Insufficient funds. Balance: AED {from_account.balance}"}
            
            beneficiary = conn.execute(
                select(beneficiaries).where(
                    and_(
                        beneficiaries.c.user_id == user_id,
                        beneficiaries.c.nickname.ilike(f"%{to_beneficiary_nickname}%"),
                        beneficiaries.c.is_active == True
                    )
                )
            ).first()
            
            if not beneficiary:
                return {"success": False, "error": f"Beneficiary '{to_beneficiary_nickname}' not found"}
            
            # Validate currency consistency
            to_account = conn.execute(
                select(accounts).where(accounts.c.id == beneficiary.beneficiary_account_id)
            ).first()
            
            if not to_account:
                return {"success": False, "error": "Beneficiary account not found"}
            
            if from_account.currency != to_account.currency:
                return {
                    "success": False, 
                    "error": f"Currency mismatch: source account is {from_account.currency} but destination is {to_account.currency}"
                }
      
            proposal_id = str(uuid.uuid4())
            conn.execute(
                insert(transfer_log).values(
                    id=proposal_id,
                    user_id=user_id,
                    from_account_id=from_account.id,
                    to_account_id=beneficiary.beneficiary_account_id,
                    to_beneficiary_id=beneficiary.id,
                    amount=amount,
                    description=description or f"Transfer to {beneficiary.nickname}",
                    status='pending'
                )
            )
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "from_account": from_account.name,
                "to_beneficiary": beneficiary.nickname,
                "amount": amount,
                "currency": "AED",
                "message": "Transfer proposal created. Please approve to execute."
            }

    async def propose_internal_transfer(
        self,
        user_id: str,
        from_account_name: str,
        to_account_name: str,
        amount: float,
        description: str = ""
    ) -> dict:
        with engine.begin() as conn:
            from_account = conn.execute(
                select(accounts).where(
                    and_(
                        accounts.c.user_id == user_id,
                        accounts.c.name.ilike(f"%{from_account_name}%")
                    )
                )
            ).first()
            
            if not from_account:
                return {"success": False, "error": f"Source account '{from_account_name}' not found"}
            
            to_account = conn.execute(
                select(accounts).where(
                    and_(
                        accounts.c.user_id == user_id,
                        accounts.c.name.ilike(f"%{to_account_name}%")
                    )
                )
            ).first()
            
            if not to_account:
                return {"success": False, "error": f"Destination account '{to_account_name}' not found"}
            
            if from_account.id == to_account.id:
                return {"success": False, "error": "Cannot transfer to the same account"}
            
            # Validate currency consistency
            if from_account.currency != to_account.currency:
                return {
                    "success": False,
                    "error": f"Currency mismatch: {from_account.name} is {from_account.currency} but {to_account.name} is {to_account.currency}"
                }
            
            if from_account.balance < amount:
                return {"success": False, "error": f"Insufficient funds. Balance: {from_account.currency} {from_account.balance}"}
            
            proposal_id = str(uuid.uuid4())
            conn.execute(
                insert(transfer_log).values(
                    id=proposal_id,
                    user_id=user_id,
                    from_account_id=from_account.id,
                    to_account_id=to_account.id,
                    amount=amount,
                    description=description or f"Internal transfer",
                    status='pending'
                )
            )
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "from_account": from_account.name,
                "to_account": to_account.name,
                "amount": amount,
                "currency": "AED",
                "message": "Transfer proposal created. Please approve to execute."
            }

    async def approve_transfer(self, user_id: str, transfer_id: str) -> dict:
        with engine.begin() as conn:
            transfer = conn.execute(
                select(transfer_log).where(
                    and_(
                        transfer_log.c.id == transfer_id,
                        transfer_log.c.user_id == user_id,
                        transfer_log.c.status == 'pending'
                    )
                )
            ).first()
            
            if not transfer:
                return {"success": False, "error": "Transfer not found or already processed"}
            
            from_account = conn.execute(
                select(accounts).where(accounts.c.id == transfer.from_account_id)
            ).first()
            
            to_account = conn.execute(
                select(accounts).where(accounts.c.id == transfer.to_account_id)
            ).first()
            
            # Validate currency consistency
            if to_account and from_account.currency != to_account.currency:
                conn.execute(
                    update(transfer_log)
                    .where(transfer_log.c.id == transfer_id)
                    .values(
                        status='failed',
                        rejection_reason=f'Currency mismatch: {from_account.currency} vs {to_account.currency}'
                    )
                )
                return {
                    "success": False,
                    "error": f"Currency mismatch: source is {from_account.currency} but destination is {to_account.currency}"
                }
            
            if from_account.balance < transfer.amount:
                conn.execute(
                    update(transfer_log)
                    .where(transfer_log.c.id == transfer_id)
                    .values(status='failed', rejection_reason='Insufficient funds')
                )
                return {"success": False, "error": "Insufficient funds"}
            
            conn.execute(
                update(accounts)
                .where(accounts.c.id == transfer.from_account_id)
                .values(
                    balance=accounts.c.balance - transfer.amount,
                    updated_at=datetime.utcnow()
                )
            )
            
            conn.execute(
                update(accounts)
                .where(accounts.c.id == transfer.to_account_id)
                .values(
                    balance=accounts.c.balance + transfer.amount,
                    updated_at=datetime.utcnow()
                )
            )
            
            ref_number = f"TRF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            conn.execute(
                insert(transactions).values(
                    account_id=transfer.from_account_id,
                    type='transfer_out',
                    amount=transfer.amount,
                    category='transfer',
                    description=transfer.description,
                    reference_number=ref_number,
                    status='completed'
                )
            )
            
            conn.execute(
                insert(transactions).values(
                    account_id=transfer.to_account_id,
                    type='transfer_in',
                    amount=transfer.amount,
                    category='transfer',
                    description=transfer.description,
                    reference_number=ref_number,
                    status='completed'
                )
            )
            
            conn.execute(
                update(transfer_log)
                .where(transfer_log.c.id == transfer_id)
                .values(
                    status='completed',
                    approved_at=datetime.utcnow(),
                    executed_at=datetime.utcnow()
                )
            )
            
            return {
                "success": True,
                "message": f"Transfer of AED {transfer.amount} completed successfully",
                "reference_number": ref_number
            }

    async def reject_transfer(self, user_id: str, transfer_id: str, reason: str = "") -> dict:
        with engine.begin() as conn:
            result = conn.execute(
                update(transfer_log)
                .where(
                    and_(
                        transfer_log.c.id == transfer_id,
                        transfer_log.c.user_id == user_id,
                        transfer_log.c.status == 'pending'
                    )
                )
                .values(
                    status='rejected',
                    rejected_at=datetime.utcnow(),
                    rejection_reason=reason or "Rejected by user"
                )
            )
            
            if result.rowcount == 0:
                return {"success": False, "error": "Transfer not found or already processed"}
            
            return {"success": True, "message": "Transfer rejected"}

    async def get_pending_transfers(self, user_id: str) -> List[dict]:
        query = text("""
            SELECT 
                t.id, t.amount, t.currency, t.description, t.created_at,
                fa.name as from_account,
                COALESCE(ta.name, b.nickname) as to_destination
            FROM transfer_log t
            JOIN accounts fa ON t.from_account_id = fa.id
            LEFT JOIN accounts ta ON t.to_account_id = ta.id
            LEFT JOIN beneficiaries b ON t.to_beneficiary_id = b.id
            WHERE t.user_id = :user_id AND t.status = 'pending'
            ORDER BY t.created_at DESC
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            return [dict(row._mapping) for row in result]

    async def get_transfer_history(self, user_id: str, limit: int = 10) -> List[dict]:
        query = text("""
            SELECT 
                t.id, t.amount, t.currency, t.description, t.status,
                t.created_at, t.executed_at,
                fa.name as from_account,
                COALESCE(ta.name, b.nickname) as to_destination
            FROM transfer_log t
            JOIN accounts fa ON t.from_account_id = fa.id
            LEFT JOIN accounts ta ON t.to_account_id = ta.id
            LEFT JOIN beneficiaries b ON t.to_beneficiary_id = b.id
            WHERE t.user_id = :user_id
            ORDER BY t.created_at DESC
            LIMIT :limit
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id, "limit": limit})
            return [dict(row._mapping) for row in result]

    
    
    @staticmethod
    def _row_to_dict(row) -> dict:
        """Convert a SQLAlchemy row to dict with proper type handling."""
        d = dict(row._mapping)
        for key, value in d.items():
            if isinstance(value, uuid.UUID):
                d[key] = str(value)
            elif isinstance(value, datetime):
                d[key] = value.isoformat()
        return d