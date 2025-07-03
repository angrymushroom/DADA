# Technical Design Document Updates: ETLs

## 1. Introduction
This document details the recent updates and optimizations made to the Extract, Transform, Load (ETL) scripts within the DADA project. The primary goal of these changes is to ensure efficient data ingestion while respecting API rate limits and focusing on delivering core product functionality.

## 2. General Improvements Across ETLs
*   **Dependency Management:** Ensured all necessary imports (e.g., `pycoingecko`, `BlockFrostApi`) are correctly placed and initialized within each script.
*   **Error Handling:** Enhanced `try-except` blocks for API calls to gracefully handle network issues and API errors.
*   **Data Retention:** Confirmed `delete_old_data` function is correctly implemented and called in each ETL for managing historical data.
*   **Pathing:** Corrected import paths (`sys.path.append`) for direct script execution.

## 3. Specific ETL Updates

### 3.1. `token_prices.py`
*   **Objective:** Fetch real-time token prices for key Cardano assets.
*   **Changes:**
    *   Migrated from dummy price values to real-time data fetching using the **CoinGecko API** (`pycoingecko` library).
    *   Updated `COMMON_TOKENS` dictionary to use CoinGecko IDs for accurate price retrieval (e.g., "cardano", "minswap", "indigo-dao-governance-token", "liqwid-finance", "iusd").
    *   Implemented a `TOKEN_ADDRESS_MAP` to associate CoinGecko IDs with their respective policy ID and asset name hex for database insertion.

### 3.1. `apy.py`
*   **Objective:** Collect APY data for lending protocols.
*   **Current Status:** Continues to use dummy APY values.
*   **Reasoning:** Direct real-time APY data from Liqwid's API proved complex and resource-intensive for the current stage. This remains a future enhancement.

### 3.3. `indigo_blockfrost.py`
*   **Objective:** Fetch Total Value Locked (TVL) data for Indigo Protocol.
*   **Changes:**
    *   Implemented **pagination** for `api.asset_addresses` calls to retrieve asset holders in batches, mitigating 504 timeout errors.
    *   Integrated **CoinGecko API** (`pycoingecko` library) to convert ADA collateral values to USD, providing more meaningful TVL figures.
    *   Updated `data_source` to reflect "Blockfrost/CoinGecko" for clarity.

### 3.4. `minswap_blockfrost.py`
*   **Objective:** Fetch Total Value Locked (TVL) data for Minswap.
*   **Changes:**
    *   **Optimized for API Limits:** Replaced the extensive on-chain pool discovery logic (which used `charli3_dendrite` and caused rate limit issues) with a function (`get_minswap_addresses_from_db`) that **retrieves existing Minswap pool addresses directly from the local `tvl_snapshots` database table.**
    *   Limited the number of addresses fetched from the database to 50 to further reduce Blockfrost API calls.
    *   Removed `charli3_dendrite` imports and associated code.
    *   Removed `time.sleep()` calls as the reduced scope of API calls makes them less critical.
    *   Integrated **CoinGecko API** (`pycoingecko` library) for USD conversion of asset values.
    *   Updated `data_source` to "Blockfrost/CoinGecko".

### 3.5. `risk_metrics.py`
*   **Objective:** Calculate and insert risk metrics (TVL volatility, whale concentration).
*   **Changes:**
    *   Modified `compute_risk_metrics` to **gracefully handle cases where top wallet data for a specific protocol (e.g., ADA) might be unavailable** in the `top_wallets` table. It now checks for the presence of data before attempting calculations.
    *   Ensured `sys` module is imported for correct path handling.

### 3.6. `tvl.py`
*   **Objective:** Aggregate and insert overall TVL data for Minswap, Indigo, and Liqwid.
*   **Changes:**
    *   Migrated all TVL fetching for Minswap, Indigo, and Liqwid to use the **Llama.fi API** (`https://api.llama.fi/tvl/{protocol_id}`). This significantly reduces Blockfrost API calls and improves performance.
    *   Removed direct Blockfrost API calls and related imports from this script.
    *   Updated `data_source` to "DefiLlama" for protocols using this source.
    *   Implemented conditional fetching: if a `llama_id` is not provided for a protocol, a placeholder TVL of 0.0 is used, and the `data_source` is marked as "Manual". This allows for flexible integration of protocols as their Llama.fi IDs become available.

### 3.7. `top_wallets.py`
*   **Objective:** Fetch and insert data for top wallet holders.
*   **Changes:**
    *   **Focused Scope:** Temporarily narrowed the scope to fetch top holders only for `iUSD` (and excluded ADA due to Blockfrost API limitations for native currency top holders).
    *   Implemented **pagination and local sorting** to accurately identify the top 10 holders for tracked assets.
    *   Integrated **CoinGecko API** (`pycoingecko` library) for USD conversion of balances.
    *   Ensured `protocol_name` is consistently "Indigo" for iUSD entries.
    *   Added `sys.path` for correct import handling.

## 4. Next Steps
With these ETLs updated and optimized for the current stage, the next steps involve:
*   **Verification:** Thoroughly testing all ETLs to ensure data is accurately and consistently populating the database.
*   **Scheduling:** Implementing a robust scheduling mechanism for periodic execution of these ETLs.
*   **Frontend Integration:** Proceeding with integrating the collected data into the frontend dashboard.
*   **Future Enhancements:** Re-evaluating the need for more granular on-chain data for Indigo and Liqwid TVL, and exploring star schema and orchestration for data warehousing in later phases.
