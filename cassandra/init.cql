-- Keyspace lưu trữ dữ liệu thống kê bóng đá
CREATE KEYSPACE IF NOT EXISTS football_stats
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};

USE football_stats;

-- Bảng `matches`: lưu một trận đấu (một hàng = một trận)
-- Các trường:
--   season: mùa giải (ví dụ "2019/2020")
--   div: hạng đấu / giải (ví dụ "E0" cho Premier League)
--   date: ngày thi đấu
--   hometeam / awayteam: tên đội chủ / đội khách
--   fthg / ftag: full-time goals home / away (bàn thắng đầy đủ thời gian)
--   ftr: full-time result (Kết quả: H = home win, D = draw, A = away win)
--   hthg / htag: half-time goals home / away
--   htr: half-time result (H/D/A tương tự)
--   hs / as: tổng số cú sút (home / away)
--   hst / ast: số cú sút trúng đích (home / away)
--   hf / af: fouls (phạm lỗi) home / away
--   hc / ac: corners (phạt góc) home / away
--   hy / ay: yellow cards home / away
--   hr / ar: red cards home / away
--   psh / psd / psa: xác suất (probability) từ nhà cái: p(home)/p(draw)/p(away)
--   match_id: UUID duy nhất cho mỗi trận (dùng để tránh trùng lặp khi cùng ngày)
-- PRIMARY KEY phân vùng theo (season, div) để lấy theo mùa/giải; clustering theo date và match_id
CREATE TABLE IF NOT EXISTS matches (
    season TEXT,
    div TEXT,
    date DATE,
    hometeam TEXT,
    awayteam TEXT,

    fthg INT,
    ftag INT,
    ftr TEXT,

    hthg INT,
    htag INT,
    htr TEXT,

    hs INT,
    as INT,
    hst INT,
    ast INT,

    hf INT,
    af INT,
    hc INT,
    ac INT,
    hy INT,
    ay INT,
    hr INT,
    ar INT,

    psh FLOAT,
    psd FLOAT,
    psa FLOAT,

    match_id UUID,

    PRIMARY KEY ((season, div), date, match_id)
) WITH CLUSTERING ORDER BY (date DESC)
AND default_time_to_live = 31536000; -- TTL 1 năm (tuỳ chỉnh)

-- Bảng `team_metrics`: chỉ số tổng hợp theo đội và ngày
-- Các trường:
--   team: tên đội
--   date: mốc thời gian cho chỉ số (thường là ngày sau trận đấu)
--   season: mùa giải tương ứng
--   total_goals_for / total_goals_against: tổng bàn thắng ghi được / thủng lưới đến ngày đó
--   wins / draws / losses: số trận thắng/hòa/thua đến mốc
--   shots / shots_on_target: tổng cú sút / cú sút trúng đích
--   fouls / corners / yellow / red: số lỗi, phạt góc, thẻ vàng, thẻ đỏ
CREATE TABLE IF NOT EXISTS team_metrics (
    team TEXT,
    date DATE,
    season TEXT,
    total_goals_for INT,
    total_goals_against INT,
    wins INT,
    draws INT,
    losses INT,
    shots INT,
    shots_on_target INT,
    fouls INT,
    corners INT,
    yellow INT,
    red INT,
    PRIMARY KEY ((team), date)
) WITH CLUSTERING ORDER BY (date DESC);

-- Bảng `season_metrics`: số liệu tổng hợp theo mùa và giải
-- Các trường:
--   season / div: khóa phân vùng (mùa giải và hạng)
--   total_matches: tổng số trận đã đấu trong mùa
--   total_goals: tổng số bàn thắng cả mùa
--   avg_goals: trung bình bàn/trận
--   home_wins / away_wins / draws: số trận thắng sân nhà / sân khách / hòa
CREATE TABLE IF NOT EXISTS season_metrics (
    season TEXT,
    div TEXT,
    total_matches INT,
    total_goals INT,
    avg_goals FLOAT,
    home_wins INT,
    away_wins INT,
    draws INT,
    PRIMARY KEY ((season, div))
);

-- Bảng `odds_metrics`: lưu tỷ lệ nhà cái trung bình theo ngày cho một mùa/giải
-- Các trường:
--   avg_psh / avg_psd / avg_psa: trung bình odds cho home/draw/away
CREATE TABLE IF NOT EXISTS odds_metrics (
    season TEXT,
    div TEXT,
    date DATE,
    avg_psh FLOAT,
    avg_psd FLOAT,
    avg_psa FLOAT,
    PRIMARY KEY ((season, div), date)
) WITH CLUSTERING ORDER BY (date DESC);

