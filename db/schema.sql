-- -------------------------------------
-- Drop existing tables (optional reset)
-- -------------------------------------
DROP TABLE IF EXISTS investment_scores;
DROP TABLE IF EXISTS dividends;
DROP TABLE IF EXISTS ticker_daily;
DROP TABLE IF EXISTS tickers;

-- -------------------------------------
-- Table: tickers
-- -------------------------------------
CREATE TABLE tickers (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    sector VARCHAR(100) DEFAULT 'Unknown',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------
-- Table: ticker_daily
-- -------------------------------------
CREATE TABLE ticker_daily (
    ticker_id INTEGER REFERENCES tickers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    price NUMERIC(10, 4),
    dividend_yield NUMERIC(6, 2),
    moving_avg_5 NUMERIC(10, 4),
    moving_avg_20 NUMERIC(10, 4),
    PRIMARY KEY (ticker_id, date)
);

-- -------------------------------------
-- Table: dividends
-- -------------------------------------
CREATE TABLE dividends (
    id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(id) ON DELETE CASCADE,
    ex_date DATE NOT NULL,
    amount NUMERIC(8, 4) NOT NULL,
    declared_date DATE,
    payment_date DATE,
    yield NUMERIC(6, 2),
    UNIQUE (ticker_id, ex_date)
);

-- -------------------------------------
-- Table: investment_scores
-- -------------------------------------
CREATE TABLE investment_scores (
    id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(id) ON DELETE CASCADE,
    ex_date DATE NOT NULL,
    score NUMERIC(5, 2) CHECK (score >= 0 AND score <= 100),
    grade VARCHAR(3),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (ticker_id, ex_date)
);

-- -------------------------------------
-- Optional: Indexes for performance
-- -------------------------------------
CREATE INDEX idx_ticker_symbol ON tickers(symbol);
CREATE INDEX idx_dividends_ex_date ON dividends(ex_date);
CREATE INDEX idx_scores_ex_date ON investment_scores(ex_date);
CREATE INDEX idx_daily_date ON ticker_daily(date);