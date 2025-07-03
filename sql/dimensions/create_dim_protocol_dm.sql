-- sql/dimensions/create_dim_protocol_dm.sql
-- Description: Creates the dim_protocol_dm dimension table.
-- This table stores information about different DeFi protocols.

CREATE TABLE IF NOT EXISTS dim_protocol_dm (
    protocol_id SERIAL PRIMARY KEY,
    protocol_name VARCHAR(255) NOT NULL UNIQUE,
    protocol_segment VARCHAR(255), -- e.g., 'DEX', 'Lending Pool', 'CDP'
    chain VARCHAR(255) -- e.g., 'Cardano'
);
