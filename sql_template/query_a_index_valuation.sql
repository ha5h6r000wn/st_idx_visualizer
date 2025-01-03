SELECT
    s1.TRADE_DT AS 交易日期,
    s1.S_INFO_WINDCODE AS 证券代码,
    s2.S_INFO_NAME AS 证券简称,
    s1.TURNOVER AS 日换手率,
    s1.PE_TTM AS 市盈率
FROM
    (
        SELECT
            S_INFO_WINDCODE,
            TRADE_DT,
            TURNOVER,
            PE_TTM
        FROM
            wind.AIndexValuation
        WHERE
            S_INFO_WINDCODE IN ({})
            AND TRADE_DT BETWEEN :start_date AND :end_date
        ORDER BY
            S_INFO_WINDCODE,
            TRADE_DT
    ) s1
    LEFT JOIN (
        SELECT
            S_INFO_WINDCODE,
            S_INFO_NAME
        FROM
            wind.AIndexDescription
        WHERE
            S_INFO_WINDCODE IN ({})
        ORDER BY
            S_INFO_WINDCODE
    ) s2 ON s1.S_INFO_WINDCODE = s2.S_INFO_WINDCODE