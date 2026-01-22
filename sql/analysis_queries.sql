-- ============================================================================
-- SOCCER PLAYER MARKET VALUE - SQL ANALYSIS QUERIES
-- ============================================================================
-- Database: data/processed/player_market_value.db
-- ============================================================================


-- 1. Top 25 Most Valuable Players
SELECT 
    p.name AS player_name,
    p.position,
    CAST((julianday('now') - julianday(p.date_of_birth)) / 365.25 AS INTEGER) AS age,
    p.current_club_name AS club,
    ROUND(p.market_value_in_eur / 1000000.0, 2) AS value_millions,
    p.country_of_citizenship AS nationality
FROM players p
WHERE p.market_value_in_eur > 0
ORDER BY p.market_value_in_eur DESC
LIMIT 25;


-- 2. Player Count and Value by Position
SELECT 
    position,
    COUNT(*) AS player_count,
    ROUND(AVG(market_value_in_eur) / 1000000.0, 2) AS avg_value_millions,
    ROUND(SUM(market_value_in_eur) / 1000000000.0, 2) AS total_value_billions,
    ROUND(MAX(market_value_in_eur) / 1000000.0, 2) AS max_value_millions
FROM players
WHERE market_value_in_eur > 0 AND position IS NOT NULL
GROUP BY position
ORDER BY avg_value_millions DESC;


-- 3. Top 20 Most Valuable Squads
SELECT 
    c.name AS club_name,
    comp.name AS league,
    COUNT(p.player_id) AS squad_size,
    ROUND(SUM(p.market_value_in_eur) / 1000000000.0, 2) AS total_value_billions,
    ROUND(AVG(p.market_value_in_eur) / 1000000.0, 2) AS avg_player_value_millions
FROM clubs c
JOIN players p ON c.club_id = p.current_club_id
LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
WHERE p.market_value_in_eur > 0
GROUP BY c.club_id
ORDER BY SUM(p.market_value_in_eur) DESC
LIMIT 20;


-- 4. Market Value by Age Group
SELECT 
    CASE 
        WHEN age < 21 THEN '1. Under 21'
        WHEN age BETWEEN 21 AND 24 THEN '2. 21-24'
        WHEN age BETWEEN 25 AND 28 THEN '3. 25-28 (Prime)'
        WHEN age BETWEEN 29 AND 32 THEN '4. 29-32'
        ELSE '5. 33+'
    END AS age_group,
    COUNT(*) AS player_count,
    ROUND(AVG(market_value) / 1000000.0, 2) AS avg_value_millions,
    ROUND(MAX(market_value) / 1000000.0, 2) AS max_value_millions
FROM (
    SELECT 
        CAST((julianday('now') - julianday(date_of_birth)) / 365.25 AS INTEGER) AS age,
        market_value_in_eur AS market_value
    FROM players
    WHERE market_value_in_eur > 0 AND date_of_birth IS NOT NULL
)
WHERE age >= 15 AND age <= 45
GROUP BY age_group
ORDER BY age_group;


-- 5. Value Curve by Single Year Age (for plotting)
SELECT 
    age,
    COUNT(*) AS player_count,
    ROUND(AVG(market_value) / 1000000.0, 2) AS avg_value_millions,
    ROUND(MEDIAN(market_value) / 1000000.0, 2) AS median_value_millions
FROM (
    SELECT 
        CAST((julianday('now') - julianday(date_of_birth)) / 365.25 AS INTEGER) AS age,
        market_value_in_eur AS market_value
    FROM players
    WHERE market_value_in_eur > 0 AND date_of_birth IS NOT NULL
)
WHERE age >= 17 AND age <= 40
GROUP BY age
HAVING player_count >= 30
ORDER BY age;

-- 6. Top Leagues by Total Value
SELECT 
    c.domestic_competition_id AS league_id,
    comp.name AS league_name,
    comp.country_name AS country,
    COUNT(DISTINCT p.player_id) AS total_players,
    ROUND(SUM(p.market_value_in_eur) / 1000000000.0, 2) AS total_value_billions,
    ROUND(AVG(p.market_value_in_eur) / 1000000.0, 2) AS avg_player_value_millions
FROM players p
JOIN clubs c ON p.current_club_id = c.club_id
LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
WHERE p.market_value_in_eur > 0
GROUP BY c.domestic_competition_id
HAVING total_players >= 50
ORDER BY total_value_billions DESC
LIMIT 20;


-- 7. Top 5 Leagues Detailed Comparison
SELECT 
    CASE c.domestic_competition_id
        WHEN 'GB1' THEN 'Premier League'
        WHEN 'ES1' THEN 'La Liga'
        WHEN 'IT1' THEN 'Serie A'
        WHEN 'L1' THEN 'Bundesliga'
        WHEN 'FR1' THEN 'Ligue 1'
    END AS league,
    COUNT(DISTINCT c.club_id) AS clubs,
    COUNT(p.player_id) AS players,
    ROUND(AVG(p.market_value_in_eur) / 1000000.0, 2) AS avg_value_millions,
    ROUND(SUM(p.market_value_in_eur) / 1000000000.0, 2) AS total_billions
FROM players p
JOIN clubs c ON p.current_club_id = c.club_id
WHERE p.market_value_in_eur > 0
  AND c.domestic_competition_id IN ('GB1', 'ES1', 'IT1', 'L1', 'FR1')
GROUP BY c.domestic_competition_id
ORDER BY total_billions DESC;

-- 8. Top Nationalities by Total Player Value
SELECT 
    country_of_citizenship AS nationality,
    COUNT(*) AS player_count,
    ROUND(SUM(market_value_in_eur) / 1000000000.0, 2) AS total_value_billions,
    ROUND(AVG(market_value_in_eur) / 1000000.0, 2) AS avg_value_millions,
    ROUND(MAX(market_value_in_eur) / 1000000.0, 2) AS most_valuable_millions
FROM players
WHERE market_value_in_eur > 0 AND country_of_citizenship IS NOT NULL
GROUP BY country_of_citizenship
HAVING player_count >= 20
ORDER BY total_value_billions DESC
LIMIT 20;

-- 9. Top Scorers with Market Value
SELECT 
    p.name AS player_name,
    p.position,
    p.current_club_name AS club,
    stats.total_goals,
    stats.total_assists,
    stats.appearances,
    ROUND(stats.total_goals * 90.0 / NULLIF(stats.total_minutes, 0), 2) AS goals_per_90,
    ROUND(p.market_value_in_eur / 1000000.0, 2) AS value_millions
FROM players p
JOIN (
    SELECT 
        player_id,
        COUNT(*) AS appearances,
        SUM(goals) AS total_goals,
        SUM(assists) AS total_assists,
        SUM(minutes_played) AS total_minutes
    FROM appearances
    GROUP BY player_id
) stats ON p.player_id = stats.player_id
WHERE p.market_value_in_eur > 0 AND stats.total_goals > 20
ORDER BY stats.total_goals DESC
LIMIT 25;


-- 10. Goals per 90 Leaders (min 2000 minutes)
SELECT 
    p.name AS player_name,
    p.position,
    stats.appearances,
    stats.total_minutes,
    stats.total_goals,
    ROUND(stats.total_goals * 90.0 / stats.total_minutes, 2) AS goals_per_90,
    ROUND(p.market_value_in_eur / 1000000.0, 2) AS value_millions
FROM players p
JOIN (
    SELECT 
        player_id,
        COUNT(*) AS appearances,
        SUM(goals) AS total_goals,
        SUM(minutes_played) AS total_minutes
    FROM appearances
    GROUP BY player_id
) stats ON p.player_id = stats.player_id
WHERE stats.total_minutes >= 2000 AND p.market_value_in_eur > 0
ORDER BY goals_per_90 DESC
LIMIT 25;


-- 11. Market Value Trends by Year
SELECT 
    strftime('%Y', date) AS year,
    COUNT(*) AS total_valuations,
    ROUND(AVG(market_value_in_eur) / 1000000.0, 2) AS avg_value_millions,
    ROUND(MAX(market_value_in_eur) / 1000000.0, 2) AS max_value_millions,
    COUNT(DISTINCT player_id) AS unique_players
FROM player_valuations
WHERE market_value_in_eur > 0
GROUP BY year
HAVING total_valuations >= 500
ORDER BY year;


-- 12. Players with Biggest Value Increase
SELECT 
    p.name AS player_name,
    p.position,
    ROUND(first_val.market_value / 1000000.0, 2) AS first_value_millions,
    ROUND(latest_val.market_value / 1000000.0, 2) AS latest_value_millions,
    ROUND((latest_val.market_value - first_val.market_value) / 1000000.0, 2) AS value_increase_millions,
    ROUND(((latest_val.market_value - first_val.market_value) / first_val.market_value) * 100, 1) AS increase_percent
FROM players p
JOIN (
    SELECT player_id, market_value_in_eur AS market_value, date,
           ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY date ASC) AS rn
    FROM player_valuations
    WHERE market_value_in_eur > 0
) first_val ON p.player_id = first_val.player_id AND first_val.rn = 1
JOIN (
    SELECT player_id, market_value_in_eur AS market_value, date,
           ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY date DESC) AS rn
    FROM player_valuations
    WHERE market_value_in_eur > 0
) latest_val ON p.player_id = latest_val.player_id AND latest_val.rn = 1
WHERE first_val.market_value >= 500000  -- Min €500K starting value
ORDER BY (latest_val.market_value - first_val.market_value) DESC
LIMIT 25;

-- 13. Value Efficiency: Goals per Million Euro Value
SELECT 
    p.name AS player_name,
    p.position,
    p.current_club_name AS club,
    stats.total_goals,
    ROUND(p.market_value_in_eur / 1000000.0, 2) AS value_millions,
    ROUND(stats.total_goals / (p.market_value_in_eur / 1000000.0), 2) AS goals_per_million
FROM players p
JOIN (
    SELECT player_id, SUM(goals) AS total_goals
    FROM appearances
    GROUP BY player_id
) stats ON p.player_id = stats.player_id
WHERE p.market_value_in_eur >= 5000000  -- Min €5M value
  AND stats.total_goals >= 10
ORDER BY goals_per_million DESC
LIMIT 25;


-- 14. Undervalued Young Players (High performance, lower value)
SELECT 
    p.name AS player_name,
    CAST((julianday('now') - julianday(p.date_of_birth)) / 365.25 AS INTEGER) AS age,
    p.position,
    p.current_club_name AS club,
    stats.appearances,
    stats.total_goals,
    ROUND(stats.total_goals * 90.0 / NULLIF(stats.total_minutes, 0), 2) AS goals_per_90,
    ROUND(p.market_value_in_eur / 1000000.0, 2) AS value_millions
FROM players p
JOIN (
    SELECT 
        player_id,
        COUNT(*) AS appearances,
        SUM(goals) AS total_goals,
        SUM(minutes_played) AS total_minutes
    FROM appearances
    GROUP BY player_id
) stats ON p.player_id = stats.player_id
WHERE CAST((julianday('now') - julianday(p.date_of_birth)) / 365.25 AS INTEGER) < 25
  AND p.market_value_in_eur BETWEEN 1000000 AND 20000000
  AND stats.appearances >= 30
  AND stats.total_goals >= 5
ORDER BY (stats.total_goals * 90.0 / NULLIF(stats.total_minutes, 0)) DESC
LIMIT 25;


-- 15. Position-Age Analysis: Peak Ages by Position
SELECT 
    position,
    age,
    ROUND(AVG(market_value) / 1000000.0, 2) AS avg_value_millions,
    COUNT(*) AS players
FROM (
    SELECT 
        position,
        CAST((julianday('now') - julianday(date_of_birth)) / 365.25 AS INTEGER) AS age,
        market_value_in_eur AS market_value
    FROM players
    WHERE market_value_in_eur > 0 
      AND date_of_birth IS NOT NULL
      AND position IS NOT NULL
)
WHERE age BETWEEN 18 AND 38
GROUP BY position, age
HAVING players >= 10
ORDER BY position, age;

-- 16. Dataset Summary
SELECT 
    'Total Players with Value' AS metric,
    CAST(COUNT(*) AS TEXT) AS value
FROM players WHERE market_value_in_eur > 0
UNION ALL
SELECT 'Total Clubs', CAST(COUNT(*) AS TEXT) FROM clubs
UNION ALL
SELECT 'Total Competitions', CAST(COUNT(*) AS TEXT) FROM competitions
UNION ALL
SELECT 'Total Games', CAST(COUNT(*) AS TEXT) FROM games
UNION ALL
SELECT 'Total Appearances', CAST(COUNT(*) AS TEXT) FROM appearances
UNION ALL
SELECT 'Total Valuations', CAST(COUNT(*) AS TEXT) FROM player_valuations
UNION ALL
SELECT 'Total Market Value (€B)', 
       CAST(ROUND(SUM(market_value_in_eur) / 1000000000.0, 2) AS TEXT) 
FROM players WHERE market_value_in_eur > 0
UNION ALL
SELECT 'Average Player Value (€M)', 
       CAST(ROUND(AVG(market_value_in_eur) / 1000000.0, 2) AS TEXT) 
FROM players WHERE market_value_in_eur > 0
UNION ALL
SELECT 'Median Player Value (€M)', 
       CAST(ROUND(
           (SELECT market_value_in_eur FROM players WHERE market_value_in_eur > 0 
            ORDER BY market_value_in_eur LIMIT 1 
            OFFSET (SELECT COUNT(*)/2 FROM players WHERE market_value_in_eur > 0)
           ) / 1000000.0, 2) AS TEXT);
