-- Phoenix Digital Bank - Database Schema
-- ========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- USERS TABLE
-- ========================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- ACCOUNTS TABLE
-- ========================================
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('checking', 'savings', 'premium')),
    currency VARCHAR(3) DEFAULT 'AED',
    balance DECIMAL(15, 2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- BENEFICIARIES TABLE
-- ========================================
CREATE TABLE beneficiaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    beneficiary_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    beneficiary_account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
    nickname VARCHAR(100),
    account_number VARCHAR(50) NOT NULL,
    bank_name VARCHAR(100) DEFAULT 'Phoenix Digital Bank',
    is_internal BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, account_number)
);

-- ========================================
-- TRANSACTIONS TABLE
-- ========================================
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('credit', 'debit', 'transfer_in', 'transfer_out')),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'AED',
    category VARCHAR(50),
    description TEXT,
    merchant_name VARCHAR(100),
    reference_number VARCHAR(50),
    related_transaction_id UUID REFERENCES transactions(id),
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- TRANSFER LOG TABLE (for pending approvals)
-- ========================================
CREATE TABLE transfer_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    from_account_id UUID NOT NULL REFERENCES accounts(id),
    to_account_id UUID REFERENCES accounts(id),
    to_beneficiary_id UUID REFERENCES beneficiaries(id),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'AED',
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'completed', 'rejected', 'cancelled', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    executed_at TIMESTAMP,
    rejected_at TIMESTAMP,
    rejection_reason TEXT
);

-- ========================================
-- INSERT 3 USERS
-- ========================================
INSERT INTO users (id, name, email, phone) VALUES
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Alice Ahmed', 'alice.ahmed@email.com', '+971-50-111-1111'),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'Bob Mansour', 'bob.mansour@email.com', '+971-50-222-2222'),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'Carol Ali', 'carol.ali@email.com', '+971-50-333-3333');

-- ========================================
-- INSERT ACCOUNTS FOR EACH USER
-- ========================================
-- Alice's Accounts
INSERT INTO accounts (id, user_id, name, type, balance) VALUES
    ('a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Salary Account', 'checking', 15000.00),
    ('a2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Savings Account', 'savings', 40000.00);

-- Bob's Accounts
INSERT INTO accounts (id, user_id, name, type, balance) VALUES
    ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'Main Account', 'checking', 25000.00),
    ('b2eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'Savings Account', 'savings', 60000.00);

-- Carol's Accounts
INSERT INTO accounts (id, user_id, name, type, balance) VALUES
    ('c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'Current Account', 'checking', 18000.00),
    ('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'Premium Savings', 'premium', 100000.00);

-- ========================================
-- INSERT BENEFICIARIES (Each user has the other 2 as beneficiaries)
-- ========================================
-- Alice's Beneficiaries (Bob and Carol)
INSERT INTO beneficiaries (user_id, beneficiary_user_id, beneficiary_account_id, nickname, account_number, bank_name, is_internal) VALUES
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'Bob - Main', 'PDB-BOB-001', 'Phoenix Digital Bank', TRUE),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'Carol - Current', 'PDB-CAROL-001', 'Phoenix Digital Bank', TRUE);

-- Bob's Beneficiaries (Alice and Carol)
INSERT INTO beneficiaries (user_id, beneficiary_user_id, beneficiary_account_id, nickname, account_number, bank_name, is_internal) VALUES
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Alice - Salary', 'PDB-ALICE-001', 'Phoenix Digital Bank', TRUE),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'Carol - Current', 'PDB-CAROL-001', 'Phoenix Digital Bank', TRUE);

-- Carol's Beneficiaries (Alice and Bob)
INSERT INTO beneficiaries (user_id, beneficiary_user_id, beneficiary_account_id, nickname, account_number, bank_name, is_internal) VALUES
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Alice - Salary', 'PDB-ALICE-001', 'Phoenix Digital Bank', TRUE),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'Bob - Main', 'PDB-BOB-001', 'Phoenix Digital Bank', TRUE);

-- ========================================
-- INSERT SAMPLE TRANSACTIONS
-- ========================================
-- Alice's Transactions
INSERT INTO transactions (account_id, type, amount, category, description, merchant_name, status, timestamp) VALUES
    ('a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'credit', 15000.00, 'salary', 'Monthly Salary', 'TechCorp LLC', 'completed', NOW() - INTERVAL '5 days'),
    ('a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'debit', 500.00, 'groceries', 'Weekly groceries', 'Carrefour', 'completed', NOW() - INTERVAL '4 days'),
    ('a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'debit', 200.00, 'restaurants', 'Dinner with friends', 'Zuma Dubai', 'completed', NOW() - INTERVAL '3 days'),
    ('a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'debit', 1500.00, 'utilities', 'Electricity bill', 'DEWA', 'completed', NOW() - INTERVAL '2 days'),
    ('a2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'credit', 5000.00, 'transfer', 'Transfer from checking', 'Internal Transfer', 'completed', NOW() - INTERVAL '1 day');

-- Bob's Transactions
INSERT INTO transactions (account_id, type, amount, category, description, merchant_name, status, timestamp) VALUES
    ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'credit', 25000.00, 'salary', 'Monthly Salary', 'Finance Corp', 'completed', NOW() - INTERVAL '6 days'),
    ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'debit', 800.00, 'shopping', 'Electronics purchase', 'Sharaf DG', 'completed', NOW() - INTERVAL '4 days'),
    ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'debit', 350.00, 'entertainment', 'Cinema and dinner', 'VOX Cinemas', 'completed', NOW() - INTERVAL '2 days'),
    ('b2eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'credit', 10000.00, 'transfer', 'Monthly savings', 'Internal Transfer', 'completed', NOW() - INTERVAL '1 day');

-- Carol's Transactions
INSERT INTO transactions (account_id, type, amount, category, description, merchant_name, status, timestamp) VALUES
    ('c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'credit', 20000.00, 'salary', 'Monthly Salary', 'Design Studio', 'completed', NOW() - INTERVAL '7 days'),
    ('c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'debit', 2000.00, 'shopping', 'Fashion shopping', 'Dubai Mall', 'completed', NOW() - INTERVAL '5 days'),
    ('c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'debit', 150.00, 'transport', 'Taxi rides', 'Careem', 'completed', NOW() - INTERVAL '3 days'),
    ('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'credit', 50000.00, 'investment', 'Investment returns', 'Phoenix Investments', 'completed', NOW() - INTERVAL '2 days');

-- ========================================
-- SAMPLE TRANSFER BETWEEN USERS
-- ========================================
-- Alice sent 1000 AED to Bob (completed transfer)
INSERT INTO transfer_log (user_id, from_account_id, to_account_id, amount, description, status, created_at, approved_at, executed_at) VALUES
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 1000.00, 'Payment for dinner', 'completed', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days');

-- Record the transactions for the above transfer
INSERT INTO transactions (account_id, type, amount, category, description, merchant_name, status, timestamp) VALUES
    ('a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'transfer_out', 1000.00, 'transfer', 'Transfer to Bob Mansour', 'Phoenix Digital Bank', 'completed', NOW() - INTERVAL '10 days'),
    ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'transfer_in', 1000.00, 'transfer', 'Transfer from Alice Ahmed', 'Phoenix Digital Bank', 'completed', NOW() - INTERVAL '10 days');

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_beneficiaries_user_id ON beneficiaries(user_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transfer_log_user_id ON transfer_log(user_id);
CREATE INDEX idx_transfer_log_status ON transfer_log(status);

-- ========================================
-- HELPFUL VIEWS
-- ========================================
CREATE VIEW user_account_summary AS
SELECT 
    u.id as user_id,
    u.name as user_name,
    a.id as account_id,
    a.name as account_name,
    a.type as account_type,
    a.balance,
    a.currency
FROM users u
JOIN accounts a ON u.id = a.user_id
WHERE a.is_active = TRUE;

CREATE VIEW user_beneficiaries_view AS
SELECT 
    b.id as beneficiary_id,
    b.user_id,
    u1.name as owner_name,
    b.nickname,
    b.account_number,
    b.bank_name,
    b.is_internal,
    u2.name as beneficiary_name,
    a.name as beneficiary_account_name
FROM beneficiaries b
JOIN users u1 ON b.user_id = u1.id
LEFT JOIN users u2 ON b.beneficiary_user_id = u2.id
LEFT JOIN accounts a ON b.beneficiary_account_id = a.id
WHERE b.is_active = TRUE;

CREATE VIEW pending_transfers_view AS
SELECT 
    t.id as transfer_id,
    t.user_id,
    u.name as user_name,
    fa.name as from_account,
    ta.name as to_account,
    COALESCE(bu.name, b.nickname) as beneficiary_name,
    t.amount,
    t.currency,
    t.description,
    t.status,
    t.created_at
FROM transfer_log t
JOIN users u ON t.user_id = u.id
JOIN accounts fa ON t.from_account_id = fa.id
LEFT JOIN accounts ta ON t.to_account_id = ta.id
LEFT JOIN beneficiaries b ON t.to_beneficiary_id = b.id
LEFT JOIN users bu ON b.beneficiary_user_id = bu.id
WHERE t.status = 'pending';