-- Stage 1
CREATE TABLE IF NOT EXISTS trade_log (
    trade_id        VARCHAR PRIMARY KEY,
    ts              TIMESTAMP,
    symbol          VARCHAR,
    sector          VARCHAR,
    entry_price     DOUBLE,
    stop_price      DOUBLE,
    target_price    DOUBLE,
    signal          VARCHAR,
    rsi14           DOUBLE,
    macd            DOUBLE,
    macd_signal     DOUBLE,
    bb_position     DOUBLE,
    volatility_20   DOUBLE,
    volume_ratio    DOUBLE,
    golden_cross    DOUBLE,
    d1              VARCHAR,
    d2              VARCHAR,
    year_pillar     VARCHAR,
    month_pillar    VARCHAR,
    day_pillar      VARCHAR,
    year_pillar_hanja   VARCHAR,
    month_pillar_hanja  VARCHAR,
    day_pillar_hanja    VARCHAR,
    year_pillar_english   VARCHAR,
    month_pillar_english  VARCHAR,
    day_pillar_english    VARCHAR,
    jieqi_zone      VARCHAR,
    month_progress  DOUBLE,
    month_hidden_wood_weight   DOUBLE,
    month_hidden_fire_weight   DOUBLE,
    month_hidden_earth_weight  DOUBLE,
    month_hidden_metal_weight  DOUBLE,
    month_hidden_water_weight  DOUBLE,
    sim_return_t5   DOUBLE,
    applied_rules   VARCHAR,
    suppressed_by   VARCHAR
);

ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS signal VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS year_pillar VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS month_pillar VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS day_pillar VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS year_pillar_hanja VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS month_pillar_hanja VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS day_pillar_hanja VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS year_pillar_english VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS month_pillar_english VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS day_pillar_english VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS jieqi_zone VARCHAR;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS month_progress DOUBLE;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS month_hidden_wood_weight DOUBLE;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS month_hidden_fire_weight DOUBLE;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS month_hidden_earth_weight DOUBLE;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS month_hidden_metal_weight DOUBLE;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS month_hidden_water_weight DOUBLE;
ALTER TABLE trade_log ADD COLUMN IF NOT EXISTS sim_return_t5 DOUBLE;

-- Stage 2
CREATE TABLE IF NOT EXISTS failure_cases (
    trade_id        VARCHAR PRIMARY KEY,
    outcome         VARCHAR,
    return_pct      DOUBLE,
    holding_days    INTEGER,
    tagged_at       TIMESTAMP,
    FOREIGN KEY (trade_id) REFERENCES trade_log(trade_id)
);

-- Stage 5
CREATE TABLE IF NOT EXISTS rule_deployments (
    rule_id         VARCHAR PRIMARY KEY,
    status          VARCHAR,
    spawned_from    VARCHAR,
    backtest_stats  VARCHAR,
    created_at      TIMESTAMP,
    file_path       VARCHAR
);
