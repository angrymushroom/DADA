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

-- Optional: Function to populate dim_time_dm for a given date range
-- This function can be called from an ETL to ensure the dimension is up-to-date.
CREATE OR REPLACE FUNCTION populate_dim_time_dm(start_date DATE, end_date DATE)
RETURNS VOID AS $$
DECLARE
    _current_date DATE := start_date;
BEGIN
    WHILE _current_date <= end_date LOOP
        INSERT INTO dim_time_dm (
            date, year, month, day, day_of_week, day_name, month_name, quarter, week_of_year
        )
        VALUES (
            _current_date,
            EXTRACT(YEAR FROM _current_date),
            EXTRACT(MONTH FROM _current_date),
            EXTRACT(DAY FROM _current_date),
            EXTRACT(DOW FROM _current_date),
            TRIM(TO_CHAR(_current_date, 'Day')),
            TRIM(TO_CHAR(_current_date, 'Month')),
            EXTRACT(QUARTER FROM _current_date),
            EXTRACT(WEEK FROM _current_date)
        )
        ON CONFLICT (date) DO NOTHING; -- Avoid inserting duplicates
        
        _current_date := _current_date + INTERVAL '1 day';
    END LOOP;
END;
$$ LANGUAGE plpgsql;