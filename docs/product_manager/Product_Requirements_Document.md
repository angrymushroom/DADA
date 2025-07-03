# Product Requirements Document (PRD) - DADA Project

## 1. Introduction
This Product Requirements Document (PRD) outlines the features, functionalities, and overall scope of the DADA (Decentralized Analytics for DeFi on Cardano) project. It serves as a guiding document for both product and development teams, ensuring alignment on what needs to be built and why.

## 2. Product Overview
DADA aims to provide a comprehensive analytics dashboard for various DeFi protocols on the Cardano blockchain. It will offer users insights into key metrics such as Total Value Locked (TVL), token prices, Annual Percentage Yields (APY), and risk metrics, enabling informed decision-making within the Cardano DeFi ecosystem.

## 3. User Stories (Examples)
*   As a DeFi investor, I want to see the current TVL of major Cardano protocols so I can understand market liquidity.
*   As a token holder, I want to view real-time prices of my assets so I can track my portfolio value.
*   As a yield farmer, I want to compare APYs across different lending pools so I can optimize my returns.
*   As a risk-averse user, I want to see risk metrics associated with protocols so I can assess potential vulnerabilities.

## 4. Key Features (Current & Planned)

### 4.1. Data Ingestion & Processing
*   **Real-time Token Price Fetching:** Integration with CoinGecko API for accurate token prices (ADA, MIN, LQ, iUSD).
*   **Dynamic TVL Calculation:** Fetching and aggregating TVL data from various Cardano DeFi protocols (Minswap, Indigo, Liqwid).
*   **APY Data Collection:** Gathering APY data for lending and staking pools.
*   **Risk Metrics Calculation:** Aggregating data to derive risk scores and other relevant metrics.
*   **Data Storage:** Persistent storage of historical data in a PostgreSQL database.
*   **Data Retention Policy:** Configurable policies for managing historical data to optimize storage.

### 4.2. Frontend Dashboard (Planned)
*   Interactive charts and graphs for visualizing historical trends.
*   Summary dashboards for quick overviews of key metrics.
*   Detailed views for individual protocols and assets.
*   User-friendly interface for easy navigation and data exploration.

## 5. Technical Considerations
*   **Backend:** Python-based ETLs, FastAPI for API.
*   **Database:** PostgreSQL.
*   **Frontend:** React (as per project structure).
*   **APIs:** CoinGecko, Blockfrost (for on-chain data).

## 6. Unfinished Tasks / To-Do List (Coding Progress)

### 6.1. ETL Development & Refinement
*   **`apy.py`:** Integrate real-time APY data fetching for Liqwid (currently using dummy values). This may require deeper investigation into Liqwid's specific API or alternative data sources.
*   **`indigo_blockfrost.py`:**
    *   Continue debugging the Blockfrost API calls for fetching asset holders, specifically addressing the 504 timeout errors with robust pagination and error handling.
    *   Implement accurate USD conversion for all collateral assets, not just ADA. This will require fetching prices for other assets (e.g., using CoinGecko or other reliable sources).
*   **`liqwid_blockfrost.py`:** Review and update to fetch real-time TVL data, similar to the approach taken for `indigo_blockfrost.py`.
*   **`minswap_blockfrost.py`:** Review and update to fetch real-time TVL data.
*   **`risk_metrics.py`:** Implement logic to calculate actual risk metrics based on collected TVL, APY, and other relevant data.
*   **`top_wallets.py`:** Implement logic to fetch and process data for top wallets.
*   **`tvl.py`:** Ensure this script correctly aggregates and processes TVL data from all relevant protocols.

### 6.2. Data Validation & Quality
*   Implement comprehensive data validation checks for all incoming data to ensure accuracy and consistency.
*   Set up monitoring and alerting for ETL failures or data anomalies.

### 6.3. Infrastructure & Deployment
*   Establish a robust scheduling mechanism for all ETL scripts (e.g., cron jobs, Airflow).
*   Refine environment variable management for production deployments.

## 7. Future Enhancements (Beyond Current Scope)
*   Historical data visualization and charting in the frontend.
*   User authentication and personalized dashboards.
*   Integration with more DeFi protocols and chains.
*   Advanced predictive analytics.
