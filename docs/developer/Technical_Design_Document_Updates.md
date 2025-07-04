# Technical Design Document Updates: ETLs

## 1. Introduction
This document details the recent updates and optimizations made to the Extract, Transform, Load (ETL) scripts within the DADA project. The primary goal of these changes is to ensure efficient data ingestion while respecting API rate limits and focusing on delivering core product functionality.

## 2. Star Schema Implementation
To improve data organization, scalability, and analytical capabilities, a star schema has been implemented for the DADA project's database. This involves a clear separation of fact and dimension tables, adhering to a consistent naming convention.

### 2.1. Naming Conventions
*   **Dimension Tables (DIM):** `dim_purpose_frequency` (e.g., `dim_time_dm`, `dim_protocol_dm`, `dim_asset_dm`).
*   **ODS (Operational Data Store) Tables:** `ods_source_entity_frequency` (raw, landing data).
*   **DWS (Detailed Data Warehouse) Tables:** `dws_entity_detail_frequency` (transformed, integrated detailed data).
*   **ADS (Aggregated Data Store) Tables:** `ads_aggregation_type_entity_frequency` (summarized data for analytics).
*   **Frequency Suffixes:** `_dm` (daily), `_wm` (weekly), `_mm` (monthly), `_hm` (hourly), `_minm` (per minute).

### 2.2. New Tables Created
*   **Dimension Tables:**
    *   `dim_time_dm`: Stores time-related attributes.
    *   `dim_protocol_dm`: Stores information about DeFi protocols.
    *   `dim_asset_dm`: Stores information about assets (tokens).
*   **ODS Tables:**
    *   `ods_coingecko_prices_hm`: Landing zone for raw CoinGecko price data.
*   **DWS Fact Tables:**
    *   `dws_tvl_snapshots_dm`: Detailed TVL snapshots.
    *   `dws_token_prices_dm`: Detailed token price snapshots.
    *   `dws_apy_snapshots_dm`: Detailed APY snapshots.
    *   `dws_top_wallets_dm`: Detailed top wallet snapshots.
    *   `dws_risk_metrics_dm`: Detailed risk metrics snapshots.

## 3. General Improvements Across ETLs
*   **Dependency Management:** Ensured all necessary imports (e.g., `pycoingecko`, `BlockFrostApi`) are correctly placed and initialized within each script.
*   **Error Handling:** Enhanced `try-except` blocks for API calls to gracefully handle network issues and API errors.
*   **Data Retention:** Confirmed `delete_old_data` function is correctly implemented and called in each ETL for managing historical data.
*   **Pathing:** Corrected import paths (`sys.path.append`) for direct script execution.
*   **Helper Functions:** Implemented `get_or_create_time_id`, `get_or_create_protocol_id`, and `get_or_create_asset_id` to manage dimension table population and retrieve foreign keys.

## 4. Specific ETL Updates

### 4.1. `token_prices.py`
*   **Objective:** Fetch real-time token prices for key Cardano assets.
*   **Changes:**
    *   Migrated from dummy price values to real-time data fetching using the **CoinGecko API** (`pycoingecko` library).
    *   Updated `COMMON_TOKENS` dictionary to use CoinGecko IDs for accurate price retrieval.
    *   Data is now inserted into `ods_coingecko_prices_hm` (raw data) and `dws_token_prices_dm` (processed data).
    *   `dim_time_dm` and `dim_asset_dm` are populated via helper functions.
    *   `ON CONFLICT` clause for `dws_token_prices_dm` is set to `DO UPDATE SET` to handle multiple runs within the same day.

### 4.2. `apy.py`
*   **Objective:** Collect APY data for lending protocols.
*   **Changes:**
    *   Integrated with the new star schema, inserting data into `dws_apy_snapshots_dm`.
    *   `dim_time_dm`, `dim_protocol_dm`, and `dim_asset_dm` are populated via helper functions.
*   **Current Status:** Continues to use dummy APY values.
*   **Reasoning:** Direct real-time APY data from Liqwid's API proved complex and resource-intensive for the current stage. This remains a future enhancement.

### 4.3. `indigo_blockfrost.py`
*   **Objective:** Fetch Total Value Locked (TVL) data for Indigo Protocol.
*   **Changes:**
    *   Integrated with the new star schema, inserting data into `dws_tvl_snapshots_dm`.
    *   `dim_time_dm`, `dim_protocol_dm`, and `dim_asset_dm` are populated via helper functions.
    *   Implemented **pagination** for `api.asset_addresses` calls to retrieve asset holders in batches, mitigating 504 timeout errors.
    *   Integrated **CoinGecko API** (`pycoingecko` library) to convert ADA collateral values to USD.
*   **Current Status:** Temporarily uses dummy TVL data.
*   **Reasoning:** Blockfrost API rate limits and performance issues prevent reliable real-time data fetching for this ETL at this stage. Real-time integration will be addressed in future iterations or with increased API capacity.

### 4.4. `minswap_blockfrost.py`
*   **Objective:** Fetch Total Value Locked (TVL) data for Minswap.
*   **Changes:**
    *   Integrated with the new star schema, inserting data into `dws_tvl_snapshots_dm`.
    *   `dim_time_dm`, `dim_protocol_dm`, and `dim_asset_dm` are populated via helper functions.
    *   **Optimized for API Limits:** Replaced the extensive on-chain pool discovery logic with a function (`get_minswap_addresses_from_db`) that retrieves existing Minswap pool addresses directly from the local `tvl_snapshots` database table (now `dws_tvl_snapshots_dm`).
    *   Limited the number of addresses fetched from the database to 50 to further reduce Blockfrost API calls.
    *   Removed `charli3_dendrite` imports and associated code.
    *   Removed `time.sleep()` calls as the reduced scope of API calls makes them less critical.
    *   Integrated **CoinGecko API** (`pycoingecko` library) for USD conversion of asset values.
*   **Current Status:** Temporarily uses dummy TVL data.
*   **Reasoning:** Blockfrost API rate limits and performance issues prevent reliable real-time data fetching for this ETL at this stage. Real-time integration will be addressed in future iterations or with increased API capacity.

### 4.5. `risk_metrics.py`
*   **Objective:** Calculate and insert risk metrics (TVL volatility, whale concentration).
*   **Changes:**
    *   Integrated with the new star schema, inserting data into `dws_risk_metrics_dm`.
    *   `dim_time_dm` and `dim_protocol_dm` are populated via helper functions.
    *   Modified `compute_risk_metrics` to gracefully handle cases where underlying data (from `dws_tvl_snapshots_dm` and `dws_top_wallets_dm`) might be unavailable or null, returning 0.0 for calculations.

### 4.6. `tvl.py`
*   **Objective:** Aggregate and insert overall TVL data for Minswap, Indigo, and Liqwid.
*   **Changes:**
    *   Integrated with the new star schema, inserting data into `dws_tvl_snapshots_dm`.
    *   `dim_time_dm` and `dim_protocol_dm` are populated via helper functions.
    *   Migrated all TVL fetching for Minswap, Indigo, and Liqwid to use the **Llama.fi API** (`https://api.llama.fi/tvl/{protocol_id}`).
    *   Removed direct Blockfrost API calls and related imports from this script.
    *   Implemented conditional fetching: if a `llama_id` is not provided for a protocol, a placeholder TVL of 0.0 is used, and the `data_source` is marked as "Manual".

### 4.7. `top_wallets.py`
*   **Objective:** Fetch and insert data for top wallet holders.
*   **Changes:**
    *   Integrated with the new star schema, inserting data into `dws_top_wallets_dm`.
    *   `dim_time_dm`, `dim_protocol_dm`, and `dim_asset_dm` are populated via helper functions.
    *   **Focused Scope:** Temporarily narrowed the scope to fetch top holders only for `iUSD` (and excluded ADA due to Blockfrost API limitations for native currency top holders).
    *   Implemented **pagination and local sorting** to accurately identify the top 10 holders for tracked assets.
    *   Integrated **CoinGecko API** (`pycoingecko` library) for USD conversion of balances.
*   **Current Status:** Temporarily uses dummy top wallet data.
*   **Reasoning:** Blockfrost API rate limits and performance issues prevent reliable real-time data fetching for this ETL at this stage. Real-time integration will be addressed in future iterations or with increased API capacity.

## 5. Next Steps
With these ETLs updated and optimized for the current stage, the next steps involve:
*   **Verification:** Thoroughly testing all ETLs to ensure data is accurately and consistently populating the database.
*   **Scheduling:** Implementing a robust scheduling mechanism for periodic execution of these ETLs.
*   **Frontend Integration:** Proceeding with integrating the collected data into the frontend dashboard.
*   **Future Enhancements:** Re-evaluating the need for more granular on-chain data for Indigo and Liqwid TVL, and exploring star schema and orchestration for data warehousing in later phases.

