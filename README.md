# DADA – Cardano DeFi Analytics Dashboard

DADA (Decentralized Asset Data Analytics) is a project that collects, processes, and visualises key metrics from leading Cardano DeFi protocols.

## 📊 What the Project Does

- **Data Collection**
  - Automatically queries live on-chain data from Cardano DeFi protocols (currently Minswap, Indigo, and Liqwid) using Blockfrost APIs.
  - Extracts Total Value Locked (TVL) and other risk-related metrics to track protocol health and adoption.

- **Data Storage**
  - Stores historical snapshots of TVL and risk indicators in a PostgreSQL database for analysis over time.

- **Backend API**
  - Provides a FastAPI-based REST API to serve the stored data to the frontend.
  - Exposes endpoints for retrieving:
    - Latest TVL per protocol
    - Recent risk metrics
    - Historical time series data

- **Dashboard Frontend**
  - Offers a React + Tailwind CSS interface to visualise:
    - TVL trends across protocols
    - Protocol comparisons
    - Risk metrics evolution
  - Enables DeFi users and researchers to understand protocol performance in near real-time.

DADA aims to be a modular foundation for building richer DeFi analytics tools within the Cardano ecosystem.
