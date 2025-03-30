SELECT
    TRADE_DT AS 交易日期,
    S_INFO_WINDCODE AS 证券代码,
    B_INFO_RATE AS 利率,
    B_INFO_TERM AS 期限
FROM
    wind.ShiborPrices
WHERE
    TRADE_DT BETWEEN :start_date AND :end_date
ORDER BY
    TRADE_DT,
    S_INFO_WINDCODE,
    B_INFO_TERM