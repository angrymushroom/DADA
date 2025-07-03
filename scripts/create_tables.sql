-- scripts/create_tables.sql
-- Description: This script creates all necessary tables for the DADA project.
-- It drops existing tables to ensure a clean slate for schema migration.

-- Drop existing tables (order matters due to foreign key constraints)
DROP TABLE IF EXISTS dws_tvl_snapshots_dm CASCADE;
DROP TABLE IF EXISTS dws_token_prices_dm CASCADE;
DROP TABLE IF EXISTS dws_apy_snapshots_dm CASCADE;
DROP TABLE IF EXISTS dws_top_wallets_dm CASCADE;
DROP TABLE IF EXISTS dws_risk_metrics_dm CASCADE;
DROP TABLE IF EXISTS ods_coingecko_prices_hm CASCADE;

DROP TABLE IF EXISTS apy_snapshots CASCADE;
DROP TABLE IF EXISTS risk_metrics CASCADE;
DROP TABLE IF EXISTS token_prices CASCADE;
DROP TABLE IF EXISTS top_wallets CASCADE;
DROP TABLE IF EXISTS tvl_snapshots CASCADE;

DROP TABLE IF EXISTS dim_protocol_dm CASCADE;
DROP TABLE IF EXISTS dim_asset_dm CASCADE;
DROP TABLE IF EXISTS dim_time_dm CASCADE;

-- Create Dimension Tables
\i sql/dimensions/create_dim_time_dm.sql
\i sql/dimensions/create_dim_protocol_dm.sql
\i sql/dimensions/create_dim_asset_dm.sql

-- Create ODS Tables
\i sql/ods/create_ods_coingecko_prices_hm.sql

-- Create DWS Fact Tables
\i sql/dws/create_dws_tvl_snapshots_dm.sql
\i sql/dws/create_dws_token_prices_dm.sql
\i sql/dws/create_dws_apy_snapshots_dm.sql
\i sql/dws/create_dws_top_wallets_dm.sql
\i sql/dws/create_dws_risk_metrics_dm.sql
