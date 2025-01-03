SELECT
    TDATE AS 交易日期,
    F2_4112 AS 指标代码,
    F3_4112 AS 指标名称,
    F4_4112 AS 指标单位,
    CASE
        WHEN F5_4112 = '1' THEN '日'
        WHEN F5_4112 = '2' THEN '周'
        WHEN F5_4112 = '3' THEN '月'
        WHEN F5_4112 = '4' THEN '季'
        WHEN F5_4112 = '5' THEN '半年'
        WHEN F5_4112 = '6' THEN '年'
    END AS 指标频率,
    INDICATOR_NUM AS 指标数值
FROM
    wind.GFZQEDB
WHERE
    F2_4112 IN ({})
    AND F3_4112 NOT LIKE '%停止%'
    AND TDATE BETWEEN :start_date AND :end_date
ORDER BY
    TDATE