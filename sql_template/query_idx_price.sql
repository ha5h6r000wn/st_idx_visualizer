SELECT
    s1.TRADE_DT,
    s1.S_INFO_WINDCODE,
    s2.S_INFO_NAME,
    s1.S_DQ_CLOSE
FROM
    (
        SELECT
            S_INFO_WINDCODE,
            TRADE_DT,
            S_DQ_CLOSE
        FROM
            wind.AIndexEODPrices
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