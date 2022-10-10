BEGIN;
    CREATE SCHEMA stock;
COMMIT;
BEGIN;
    CREATE TABLE IF NOT EXISTS stock.ticker (
      id SERIAL PRIMARY KEY,
      name varchar(250) NOT NULL
    );
COMMIT;
BEGIN;
    CREATE TABLE IF NOT EXISTS stock.analysis_configuration (
        id SERIAL PRIMARY KEY,
        sht INT NOT NULL,
        lng INT NOT NULL
    );
COMMIT;
BEGIN;
    CREATE TABLE IF NOT EXISTS stock.performances (
      id SERIAL PRIMARY KEY,
      ticker_id INT NOT NULL,
      update_at TIMESTAMP NOT NULL DEFAULT NOW(),
      index VARCHAR(200) NOT NULL,
      parameters VARCHAR(200) NOT NULL,
      final_return NUMERIC NOT NULL,
      annual_rate_percent NUMERIC NOT NULL,
      month_rate_percent NUMERIC NOT NULL,
      rsi NUMERIC NOT NULL,
      CONSTRAINT fk_performances_tickers
        FOREIGN KEY(ticker_id)
      REFERENCES stock.ticker(id)
    );
COMMIT;
BEGIN;
    CREATE TABLE IF NOT EXISTS stock.analysis (
        ticker_id INT NOT NULL,
        configuration_id INT NOT NULL,
        adj_close NUMERIC NOT NULL,
        stop_loss NUMERIC NOT NULL,
        lng  NUMERIC NOT NULL,
        sht  NUMERIC NOT NULL,
        image_url VARCHAR(200) NOT NULL,
        CONSTRAINT fk_analysis_tickers
            FOREIGN KEY(ticker_id)
        REFERENCES stock.ticker(id),
        CONSTRAINT fk_configuration_analysis
            FOREIGN KEY(configuration_id)
        REFERENCES stock.analysis_configuration(id)
    );
COMMIT;