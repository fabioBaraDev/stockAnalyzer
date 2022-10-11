BEGIN;

    CREATE TABLE IF NOT EXISTS ticker (
      id SERIAL PRIMARY KEY,
      name varchar(250) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS analysis_configuration (
        id SERIAL PRIMARY KEY,
        sht INT NOT NULL,
        lng INT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS performances (
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
      REFERENCES ticker(id)
    );

    CREATE TABLE IF NOT EXISTS analysis (
        id SERIAL PRIMARY KEY,
        ticker_id INT NOT NULL,
        configuration_id INT NOT NULL,
        adj_close NUMERIC NOT NULL,
        stop_loss NUMERIC NOT NULL,
        lng  NUMERIC NOT NULL,
        sht  NUMERIC NOT NULL,
        image_url VARCHAR(200) NOT NULL,
        CONSTRAINT fk_analysis_tickers
            FOREIGN KEY(ticker_id)
        REFERENCES ticker(id),
        CONSTRAINT fk_configuration_analysis
            FOREIGN KEY(configuration_id)
        REFERENCES analysis_configuration(id)
    );

    CREATE TABLE IF NOT EXISTS recent_recommendation (
        analysis_id INT NOT NULL,
        update_at TIMESTAMP NOT NULL
        CONSTRAINT fk_recent_recommendation
            FOREIGN KEY(analysis_id)
        REFERENCES analysis(id)
    )

COMMIT;
BEGIN;
 INSERT INTO ticker(name) VALUES
        		('CSNA3.SA'),('LWSA3.SA'),('VALE3.SA'),('IGTI11.SA'),('COGN3.SA'),('DXCO3.SA'),('POSI3.SA'),('CSAN3.SA'),
                ('SOMA3.SA'),('PETR3.SA'),('YDUQ3.SA'),('ELET3.SA'),('PRIO3.SA'),('PCAR3.SA'),('CVCB3.SA'),('GOLL4.SA'),
                ('SULA11.SA'),('VIIA3.SA'),('ELET6.SA'),('BPAN4.SA'),('PETR4.SA'),('RENT3.SA'),('BRAP4.SA'),('BPAC11.SA'),
                ('LREN3.SA'),('ENEV3.SA'),('MRVE3.SA'),('HAPV3.SA'),('JHSF3.SA'),('PETZ3.SA'),('NTCO3.SA'),('ASAI3.SA'),
                ('RDOR3.SA'),('BEEF3.SA'),('CMIN3.SA'),('ALPA4.SA'),('CCRO3.SA'),('RAIL3.SA'),('BRML3.SA'),('GGBR4.SA'),
                ('USIM5.SA'),('GOAU4.SA'),('AZUL4.SA'),('BRKM5.SA'),('EZTC3.SA'),('MRFG3.SA'),('CYRE3.SA'),('ECOR3.SA'),
                ('CIEL3.SA'),('B3SA3.SA'),('AMER3.SA'),('BBAS3.SA'),('SBSP3.SA'),('SANB11.SA'),('ITUB4.SA'),('MULT3.SA'),
                ('UGPA3.SA'),('CRFB3.SA'),('BRFS3.SA'),('ENBR3.SA'),('EMBR3.SA'),('FLRY3.SA'),('BBDC3.SA'),('ITSA4.SA'),
                ('BBDC4.SA'),('VBBR3.SA'),('BBSE3.SA'),('CPFE3.SA'),('MGLU3.SA'),('EQTL3.SA'),('CASH3.SA'),('QUAL3.SA'),
                ('ENGI11.SA'),('RRRP3.SA'),('EGIE3.SA'),('CMIG4.SA'),('IRBR3.SA'),('TAEE11.SA'),('WEGE3.SA'),('KLBN11.SA'),
                ('VIVT3.SA'),('CPLE6.SA'),('RADL3.SA'),('ABEV3.SA'),('HYPE3.SA'),('TOTS3.SA'),('SUZB3.SA'),('JBSS3.SA'),
                ('TIMS3.SA')

    INSERT INTO analysis_configuration(sht, lng) VALUES (10, 50), (10, 60), (10, 90), (20, 50),
                                                        (20, 60), (20, 90), (30, 50), (30, 60), (30, 90)

COMMIT;

