# DADA – Cardano DeFi Analytics Dashboard

DADA (Decentralized Asset Data Analytics) is a project that collects, processes, and visualises key metrics from leading Cardano DeFi protocols.

## 📊 What the Project Does

- **Data Collection & ETL (Extract, Transform, Load)**
  - Automatically queries live on-chain data from Cardano DeFi protocols (Minswap, Indigo, and Liqwid) using Blockfrost APIs.
  - **Dynamic TVL Fetching:**
    - **Minswap:** Dynamically discovers liquidity pool addresses by querying LP token policies via `charli3-dendrite` and Blockfrost.
    - **Indigo:** Dynamically discovers Collateralized Debt Position (CDP) addresses by querying iUSD asset holders via Blockfrost.
    - **Liqwid:** Dynamically discovers lending pool addresses by querying qADA token policy via Blockfrost.
  - **Token Prices:** Fetches prices for common Cardano tokens (e.g., ADA, MIN, iUSD, LQ) using Blockfrost.
  - **Top Wallets:** Identifies and tracks top wallet holders for specific assets.
  - **Risk Metrics:** Calculates and stores key risk indicators like TVL volatility and whale concentration.
  - **APY Snapshots:** (Simplified) Calculates and stores estimated Supply and Borrow APY for Liqwid lending pools.

- **Data Storage**
  - Stores historical snapshots of TVL, APY, token prices, top wallets, and risk indicators in a PostgreSQL database for analysis over time.
  - **Configurable Data Retention:** ETL scripts now include a configurable data retention policy, allowing you to specify how long granular data is kept to manage storage growth.

- **Backend API**
  - Provides a FastAPI-based REST API to serve the stored data to the frontend (future development).
  - Exposes endpoints for retrieving:
    - Latest TVL per protocol
    - Recent risk metrics
    - Historical time series data

- **Dashboard Frontend**
  - Offers a React + Tailwind CSS interface to visualise data (future development).
  - Enables DeFi users and researchers to understand protocol performance in near real-time.

DADA aims to be a modular foundation for building richer DeFi analytics tools within the Cardano ecosystem.

## 🚀 Getting Started

### Prerequisites

- **PostgreSQL:** Ensure you have a PostgreSQL database instance running.
- **Blockfrost API Key:** Obtain a project ID from [Blockfrost.io](https://blockfrost.io).
- **Python 3.x:** (Recommended: Python 3.7 to 3.10 for full compatibility with all libraries).

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/DADA.git
    cd DADA
    ```

2.  **Set up Python Virtual Environment:**
    ```bash
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    Create a `.env` file in the root directory of the project based on `.env.example`:
    ```
    BLOCKFROST_API_KEY=your_blockfrost_api_key_here
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432
    DATA_RETENTION_DAYS=30 # Optional: Number of days to retain granular data. Set to 0 to disable.
    ```

4.  **Database Schema Setup:**
    Apply the database schema. This will create all necessary tables.
    ```bash
    source env/bin/activate
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f scripts/create_tables.sql
    ```

### Running ETLs

To collect data, run the individual ETL scripts. For production, these should be scheduled using a tool like `cron`.

```bash
source env/bin/activate
python3 backend/etl/minswap_blockfrost.py
python3 backend/etl/indigo_blockfrost.py
python3 backend/etl/liqwid_blockfrost.py
python3 backend/etl/token_prices.py
python3 backend/etl/top_wallets.py
python3 backend/etl/risk_metrics.py
python3 backend/etl/apy.py
```

## 📈 Data Visualization

For now, data can be visualized using tools like Metabase by connecting it to your PostgreSQL database.