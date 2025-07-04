-- sql/dimensions/create_dim_time_dm.sql
-- Description: Creates the dim_time_dm dimension table.
-- This table stores time-related attributes for analytical purposes.

CREATE TABLE IF NOT EXISTS dim_time_dm (
    time_id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    day SMALLINT NOT NULL,
    day_of_week SMALLINT NOT NULL,
    day_name VARCHAR(9) NOT NULL,
    month_name VARCHAR(9) NOT NULL,
    quarter SMALLINT NOT NULL,
    week_of_year SMALLINT NOT NULL
);