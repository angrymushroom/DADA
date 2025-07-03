-- sql/dws/create_dws_risk_metrics_dm.sql
-- Description: Creates the dws_risk_metrics_dm fact table.
-- This table stores detailed risk metrics snapshots.

CREATE TABLE IF NOT EXISTS dws_risk_metrics_dm (
    risk_metric_id SERIAL PRIMARY KEY,
    protocol_id INT NOT NULL, -- FK to dim_protocol_dm
    time_id INT NOT NULL, -- FK to dim_time_dm
    metric_name VARCHAR(255) NOT NULL,
    metric_value NUMERIC(20, 8) NOT NULL,
    data_source VARCHAR(255),
    
    CONSTRAINT fk_protocol
        FOREIGN KEY(protocol_id)
        REFERENCES dim_protocol_dm(protocol_id),
    CONSTRAINT fk_time
        FOREIGN KEY(time_id)
        REFERENCES dim_time_dm(time_id),
    UNIQUE (protocol_id, time_id, metric_name)
);
