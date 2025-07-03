# Technical Design Document: Data Ingestion & API Interaction

## 1. Introduction
This document outlines the technical design for the data ingestion and API interaction components of the DADA project. The primary goal is to reliably fetch, process, and store various DeFi-related metrics from external data sources into our PostgreSQL database.

## 2. Scope
This document covers:
*   Interaction with external APIs (e.g., CoinGecko, Blockfrost).
*   Data parsing and transformation.
*   Database insertion and updates.
*   Error handling and retry mechanisms for API calls.
*   Data retention policies.

## 3. Architecture Overview
The data ingestion process is primarily handled by Python ETL (Extract, Transform, Load) scripts located in `backend/etl/`. These scripts are designed to be run periodically (e.g., via cron jobs) to collect snapshots of data.

```
[External APIs (CoinGecko, Blockfrost)] <--- HTTP/API Calls ---> [Python ETL Scripts] <--- PostgreSQL (psycopg2) ---> [DADA Database]
```

## 4. Data Sources & API Interactions

### 4.1. CoinGecko API (for Token Prices)
*   **Purpose:** Fetch real-time and historical price data for various tokens in USD.
*   **Library:** `pycoingecko` Python library.
*   **Endpoint Example:** `cg.get_price(ids='cardano,minswap', vs_currencies='usd')`
*   **Data Points:** `token_symbol`, `price_usd`.
*   **Error Handling:**
    *   API rate limits: `pycoingecko` handles basic rate limiting. Implement exponential backoff for repeated failures.
    *   Network errors: Implement `try-except` blocks to catch `requests.exceptions.RequestException`.
    *   Invalid token IDs: Log errors for tokens not found on CoinGecko.
*   **Configuration:** No API key required for basic `get_price` endpoint.

### 4.2. Blockfrost API (for TVL, Wallets, Risk Metrics)
*   **Purpose:** Fetch on-chain data related to TVL, top wallets, and other blockchain-specific metrics.
*   **Library:** `blockfrost-python` library.
*   **Authentication:** Requires `BLOCKFROST_API_KEY` environment variable.
*   **Key Endpoints (Examples):**
    *   `api.asset_transactions(asset_id)`: For dynamic TVL discovery.
    *   `api.address_utxos(address)`: For wallet balances.
    *   `api.pool_history(pool_id)`: For historical pool data (if applicable for risk).
*   **Data Points:** Varies by ETL script (e.g., `protocol_name`, `tvl_usd`, `wallet_address`, `balance`, `risk_score`).
*   **Error Handling:**
    *   `ApiError` from `blockfrost-python`: Catch specific API errors (e.g., 404 Not Found, 400 Bad Request).
    *   Rate limits: Blockfrost has rate limits; implement retry logic with delays.
    *   Network issues: Standard network error handling.
*   **Configuration:** `BLOCKFROST_API_KEY` and `ApiUrls.mainnet.value` (or testnet/preprod as needed).

## 5. Data Processing & Transformation

*   **ETL Scripts:** Each metric (token prices, TVL, APY, top wallets, risk metrics) has a dedicated Python script in `backend/etl/`.
*   **Data Normalization:** Ensure consistent data types and formats before insertion into the database.
*   **Timestamping:** All snapshot data will include a `snapshot_time` (UTC) to track historical values.
*   **Protocol Identification:** Data will be tagged with `protocol_name` (e.g., 'Minswap', 'Indigo', 'Liqwid') and `chain` ('Cardano').

## 6. Database Interaction

*   **Database:** PostgreSQL.
*   **Library:** `psycopg2` for Python-PostgreSQL connectivity.
*   **Connection:** Database credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) are loaded from environment variables.
*   **Schema:** Refer to `scripts/create_tables.sql` for the latest database schema.
*   **Insertion Strategy:** `ON CONFLICT DO NOTHING` is used for idempotent insertions, preventing duplicate entries for the same `(token_symbol, token_address, snapshot_time)` or similar unique constraints.
*   **Error Handling:** Catch `psycopg2.Error` for database-related issues (e.g., connection errors, constraint violations).

## 7. Data Retention Policy

*   **Mechanism:** A `delete_old_data` function is implemented in each ETL script.
*   **Configuration:** `DATA_RETENTION_DAYS` environment variable (integer, default 0 for no retention).
*   **Execution:** The `delete_old_data` function is called after new data insertion to prune old records.
*   **Impact:** Ensures database size is managed, especially for granular snapshot data.

## 8. Deployment & Scheduling

*   **Execution Environment:** Python virtual environment (`env/`).
*   **Scheduling:** ETL scripts are designed to be run periodically using external schedulers (e.g., `cron` on Linux/macOS, Windows Task Scheduler, or a dedicated job orchestrator like Apache Airflow for more complex pipelines).
*   **Environment Variables:** All sensitive information (API keys, database credentials) and configurable parameters (data retention) are managed via environment variables (`.env` file for local development).

## 9. Future Considerations

*   **Centralized Error Logging:** Implement a more robust logging system (e.g., ELK stack, Sentry) for better monitoring of ETL failures.
*   **Monitoring & Alerting:** Set up alerts for ETL script failures or data anomalies.
*   **Data Validation:** Add more comprehensive data validation checks after fetching and before insertion.
*   **Asynchronous API Calls:** For performance, consider asynchronous API calls if fetching large volumes of data concurrently.
*   **Data Lake/Warehouse:** For long-term historical data and complex analytics, consider integrating with a data lake or data warehouse solution.
