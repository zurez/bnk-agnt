-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    name VARCHAR(255) NOT NULL,
    label VARCHAR(1) CHECK (label IN ('A', 'B', 'C')), -- For demo
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Accounts table
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    user_id UUID REFERENCES users (id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL, -- e.g., "Salary Account"
    type VARCHAR(50), -- e.g., "checking", "savings"
    currency VARCHAR(3) DEFAULT 'AED',
    balance DECIMAL(15, 2) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Transactions table
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    account_id UUID REFERENCES accounts (id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    merchant VARCHAR(255),
    category VARCHAR(100), -- "groceries", "restaurants", etc.
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transfer log (for money transfers)
CREATE TABLE transfer_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    user_id UUID REFERENCES users (id),
    from_account_id UUID REFERENCES accounts (id),
    to_account_id UUID REFERENCES accounts (id),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'AED',
    status VARCHAR(20) CHECK (
        status IN (
            'pending',
            'completed',
            'rejected'
        )
    ),
    created_at TIMESTAMP DEFAULT NOW(),
    executed_at TIMESTAMP
);

-- Conversation history (optional, for demo persistence)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    user_id UUID REFERENCES users (id),
    model VARCHAR(50),
    messages JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_transactions_account_id ON transactions (account_id);

CREATE INDEX idx_transactions_timestamp ON transactions (timestamp);

CREATE INDEX idx_transactions_category ON transactions (category);

CREATE INDEX idx_transfer_log_user_id ON transfer_log (user_id);

CREATE INDEX idx_transfer_log_status ON transfer_log (status);

-- Seed Data

-- User A - "Salary + Savings"
INSERT INTO
    users (id, name, label, email)
VALUES (
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        'Alice Ahmed',
        'A',
        'alice@demo.com'
    );

INSERT INTO accounts (id, user_id, name, type, balance) VALUES
('a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Salary Account', 'checking', 15000.00),
('a2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Savings Account', 'savings', 40000.00);

-- Transactions for User A
INSERT INTO
    transactions (
        account_id,
        timestamp,
        amount,
        merchant,
        category,
        description
    )
VALUES (
        'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        '2024-11-01 09:00:00',
        20000.00,
        'Employer Inc.',
        'salary',
        'Monthly salary'
    ),
    (
        'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        '2024-11-02 14:30:00',
        -87.50,
        'Carrefour',
        'groceries',
        'Weekly groceries'
    ),
    (
        'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        '2024-11-05 19:00:00',
        -45.00,
        'Shell Gas Station',
        'transportation',
        'Fuel'
    ),
    (
        'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        '2024-11-07 20:00:00',
        -120.00,
        'Nandos',
        'restaurants',
        'Dinner with friends'
    ),
    (
        'a1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        '2024-11-10 10:00:00',
        -200.00,
        'DEWA',
        'utilities',
        'Electricity bill'
    );

-- User B - "High Spender"
INSERT INTO
    users (id, name, label, email)
VALUES (
        'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
        'Bob Mansour',
        'B',
        'bob@demo.com'
    );

INSERT INTO
    accounts (
        id,
        user_id,
        name,
        type,
        balance
    )
VALUES (
        'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
        'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
        'Main Account',
        'checking',
        5000.00
    ),
    (
        'b2eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
        'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
        'Credit Card',
        'credit',
        -3500.00
    );

-- Transactions for User B
INSERT INTO
    transactions (
        account_id,
        timestamp,
        amount,
        merchant,
        category,
        description
    )
VALUES (
        'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
        '2024-11-01 12:00:00',
        -350.00,
        'Zara',
        'shopping',
        'Clothes'
    ),
    (
        'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
        '2024-11-03 19:30:00',
        -450.00,
        'Zuma',
        'restaurants',
        'Fancy dinner'
    ),
    (
        'b2eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
        '2024-11-05 15:00:00',
        -1200.00,
        'Emirates',
        'travel',
        'Flight ticket'
    ),
    (
        'b2eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
        '2024-11-08 11:00:00',
        -150.00,
        'Starbucks',
        'restaurants',
        'Coffee run'
    );

-- User C - "Low Activity"
INSERT INTO
    users (id, name, label, email)
VALUES (
        'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33',
        'Carol Ali',
        'C',
        'carol@demo.com'
    );

INSERT INTO
    accounts (
        id,
        user_id,
        name,
        type,
        balance
    )
VALUES (
        'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33',
        'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c33',
        'Checking Account',
        'checking',
        2000.00
    );

-- Transactions for User C
INSERT INTO
    transactions (
        account_id,
        timestamp,
        amount,
        merchant,
        category,
        description
    )
VALUES (
        'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33',
        '2024-11-01 09:00:00',
        500.00,
        'Freelance',
        'income',
        'Project payment'
    ),
    (
        'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380c33',
        '2024-11-15 10:00:00',
        -50.00,
        'Etisalat',
        'utilities',
        'Phone bill'
    );