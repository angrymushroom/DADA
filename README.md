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

## 🚀 Getting Started with Docker

This project is fully dockerized, which makes it easy to set up and run all the services with a single command. The `docker-compose.yml` file orchestrates the following services:

-   `postgres`: The PostgreSQL database for storing all the data.
-   `airflow-webserver`: The Airflow web interface for managing and monitoring ETL pipelines.
-   `airflow-scheduler`: The Airflow scheduler that triggers the ETL jobs.
-   `metabase`: A business intelligence tool for data visualization.
-   `backend`: The FastAPI backend application.

### Prerequisites

-   **Docker and Docker Compose:** Ensure you have Docker and Docker Compose installed on your system.
-   **Blockfrost API Key:** Obtain a project ID from [Blockfrost.io](https://blockfrost.io).

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/DADA.git
    cd DADA
    ```

2.  **Environment Variables:**
    Create a `.env` file in the root directory of the project based on `.env.example`. You only need to set the `BLOCKFROST_API_KEY`. The rest of the variables are pre-configured for the Docker environment.
    ```
    BLOCKFROST_API_KEY=your_blockfrost_api_key_here
    ```

3.  **Build and Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images and start all the services.

### Accessing the Services

-   **Airflow UI:** Open your browser and go to `http://localhost:8080`. The default username and password are `airflow`.
-   **Metabase UI:** Open your browser and go to `http://localhost:3000`. You will need to set up a new user and connect to the PostgreSQL database. The database connection details are:
    -   **Database Type:** PostgreSQL
    -   **Host:** `postgres`
    -   **Port:** `5432`
    -   **Database Name:** `cardano_dada`
    -   **Username:** `gaobotao`
    -   **Password:** `yourpassword`
-   **FastAPI Backend:** The API is available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

## 📈 Running ETLs with Airflow

The ETL pipelines are defined as Airflow DAGs in the `dags` directory. Once you start the services with `docker-compose`, the Airflow scheduler will automatically start triggering the DAGs based on their schedules.

You can also manually trigger the DAGs from the Airflow UI.

## 📈 Data Visualization with Metabase

Once the ETLs have run and populated the database, you can use Metabase to create dashboards and visualize the data. Connect Metabase to the PostgreSQL database as described in the "Accessing the Services" section.
