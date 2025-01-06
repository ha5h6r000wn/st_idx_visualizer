import altair as alt
import streamlit as st

from config import param_cls
from config.config import CHART_NUM_FORMAT
from data_preparation.data_processor import append_signal_column, reshape_wide_df_into_long_form
from utils import divide_by_100


def get_custom_dt_with_slider(trade_dt, config: param_cls.DtSliderParam):
    selected_dt = [dt for dt in trade_dt if dt >= config.start_dt]
    return st.select_slider(
        config.name,
        options=selected_dt,
        value=(
            selected_dt[-config.default_start_offset],
            selected_dt[-config.default_end_offset],
        ),
        key=config.key,
    )


def get_custom_dt_with_select_slider(trade_dt, config: param_cls.SelectSliderParam):
    keys = list(config.default_select_offset.keys())
    selected_key = st.select_slider(
        config.name,
        options=keys,
        value=(keys[0]),
    )

    return trade_dt[-config.default_select_offset[selected_key]]


def draw_grouped_bars(grouped_df, group_name_df, config: param_cls.BaseBarParam):
    reindex_grouped_df = grouped_df.stack().reset_index()
    reindex_grouped_df.columns = list(config.axis_names.values())

    selection = alt.selection_point(fields=[config.axis_names['LEGEND']], bind='legend')
    order_name = group_name_df.iloc[:, 0].tolist()
    order_group = grouped_df.columns.tolist()
    bar = (
        alt.Chart(
            reindex_grouped_df,
            height=config.height,
            title=alt.TitleParams(
                text=config.title,
                offset=100,
            ),
            # padding={'top': 50},
        )
        .mark_bar()
        .encode(
            x=alt.X(f'{config.axis_names['X']}:{config.axis_types['X']}', sort=order_name),
            xOffset=alt.X(
                f'{config.axis_names['LEGEND']}:{config.axis_types['LEGEND']}',
                sort=order_group,
            ),
            y=alt.Y(
                f'{config.axis_names['Y']}:{config.axis_types['Y']}',
                axis=alt.Axis(format=config.y_axis_format),
            ),
            color=alt.Color(
                f'{config.axis_names['LEGEND']}:{config.axis_types['LEGEND']}',
                sort=order_group,
                legend=alt.Legend(
                    orient='none',
                    legendX=-80,
                    legendY=-80,
                    columns=2,
                ),
            ),
            opacity=alt.condition(selection, alt.value(1), alt.value(0)),
        )
        .add_params(selection)
    )
    st.altair_chart(bar, theme='streamlit', use_container_width=True)


def draw_grouped_lines(wide_df, config: param_cls.IdxLineParam):
    trade_dt = wide_df.index
    if config.dt_slider_param is not None:
        custom_dt = get_custom_dt_with_slider(trade_dt=trade_dt, config=config.dt_slider_param)
        selected_df = wide_df.loc[custom_dt[0] : custom_dt[1]]
    else:
        selected_df = wide_df
    # st.write(selected_df)

    order_group = selected_df.columns.tolist()
    long_df = reshape_wide_df_into_long_form(
        selected_df,
        config.data_col_param.dt_col,
        config.data_col_param.name_col,
        config.data_col_param.price_col,
    )
    # st.write(long_df)
    long_df.columns = list(config.axis_names.values())
    selection = alt.selection_point(fields=[config.axis_names['LEGEND']], bind='legend')
    lines = (
        alt.Chart(
            long_df,
            height=config.height,
            title=alt.TitleParams(
                text=config.title,
                offset=100,
            ),
        )
        .mark_line()
        .encode(
            x=alt.X(config.axis_names['X']),
            y=alt.Y(
                config.axis_names['Y'],
                scale=alt.Scale(
                    domain=(
                        long_df[config.axis_names['Y']].min() - config.y_limit_extra,
                        long_df[config.axis_names['Y']].max() + config.y_limit_extra,
                    )
                ),
                axis=alt.Axis(format=config.y_axis_format),
            ),
            color=alt.Color(
                config.axis_names['LEGEND'],
                sort=order_group,
                legend=alt.Legend(
                    orient='none',
                    legendX=-80,
                    legendY=-80,
                    columns=2,
                ),
            ),
            strokeDash=alt.StrokeDash(config.axis_names['LEGEND'], sort=order_group, legend=None),
            opacity=alt.condition(selection, alt.value(1), alt.value(0)),
        )
        .add_params(selection)
    )

    st.altair_chart(lines, theme='streamlit', use_container_width=True)


def draw_heatmap(wide_df, config: param_cls.HeatmapParam):
    long_df = reshape_wide_df_into_long_form(
        wide_df.rename_axis(config.axis_names['X']),
        config.axis_names['X'],
        config.axis_names['Y'],
        config.axis_names['LEGEND'],
    )
    heatmap = (
        alt.Chart(long_df, height=config.height, title=config.title)
        .mark_rect()
        .encode(
            x=alt.X(
                f'{config.axis_names['X']}:{config.col_types['X']}',
                sort=long_df.columns.tolist(),
            ),
            y=alt.Y(
                f'{config.axis_names['Y']}:{config.col_types['Y']}',
                sort=long_df.columns.tolist(),
            ),
            color=alt.Color(
                f'{config.axis_names['LEGEND']}:{config.col_types['LEGEND']}',
                legend=alt.Legend(format=config.legend_format),
            ),
        )
    )
    st.altair_chart(heatmap, theme='streamlit', use_container_width=True)


def add_altair_bar_with_highlighted_signal(df, config: param_cls.SignalBarParam):
    if config.signal_order is not None:
        signal_order = config.signal_order
    elif config.no_signal is None:
        signal_order = [config.false_signal, config.true_signal]
    else:
        signal_order = [config.false_signal, config.true_signal, config.no_signal]

    return (
        alt.Chart(
            df,
            title=alt.TitleParams(
                text=config.title,
                offset=100,
            ),
            height=config.height,
        )
        .mark_bar(clip=True)
        .encode(
            x=alt.X(
                f'{config.axis_names['X']}:{config.axis_types['X']}',
                axis=alt.Axis(labelAngle=-45),
            ),
            y=alt.Y(
                f'{config.axis_names['Y']}:{config.axis_types['Y']}',
                axis=alt.Axis(format=config.y_axis_format),
            ).scale(
                domain=(
                    df[config.axis_names['Y']].min() - abs(df[config.axis_names['Y']].min()) * 0.2,
                    df[config.axis_names['Y']].max() + abs(df[config.axis_names['Y']].max()) * 0.05,
                )
            ),
            color=alt.Color(
                f'{config.axis_names['LEGEND']}:{config.axis_types['LEGEND']}',  # 使用新的数据列来编码颜色
                scale=alt.Scale(
                    domain=signal_order,
                    # range=['steelblue', 'skyblue'],
                ),  # 设置颜色范围
                legend=alt.Legend(
                    orient='none',
                    legendX=-80,
                    legendY=-80,
                    columns=2,
                ),
            ),
        )
    )


def add_altair_line_with_stroke_dash(df, config: param_cls.LineParam):
    if config.compared_cols is not None:
        new_df = df[[config.axis_names['X']] + config.compared_cols].melt(
            id_vars=config.axis_names['X'],
            var_name=config.axis_names['LEGEND'],
            value_name=config.axis_names['Y'],
        )
        order_group = config.compared_cols
    else:
        new_df = df
        order_group = 'ascending'
    return (
        alt.Chart(new_df)
        .mark_line(strokeDash=config.stroke_dash)
        .encode(
            x=alt.X(
                f'{config.axis_names['X']}:{config.axis_types['X']}',
                axis=alt.Axis(labelAngle=-45),
            ),
            y=alt.Y(
                f'{config.axis_names['Y']}:{config.axis_types['Y']}',
                axis=alt.Axis(format=config.y_axis_format),
                # scale=alt.Scale(
                #     domain=(
                #         new_df[config.axis_names['Y']].min(),
                #         new_df[config.axis_names['Y']].max(),
                #     )
                # ),
            ).scale(
                domain=(
                    new_df[config.axis_names['Y']].min() - abs(new_df[config.axis_names['Y']].min()) * 0.2,
                    new_df[config.axis_names['Y']].max() * 1,
                )
            ),
            color=alt.Color(
                f'{config.axis_names['LEGEND']}:{config.axis_types['LEGEND']}',  # 使用新的数据列来编码颜色
                scale=alt.Scale(
                    # domain=[config.axis_names['Y']],
                    range=['red', 'black'],
                ),
                sort=order_group,
                # 设置颜色范围
                # legend=alt.Legend(title='比较基准'),  # 设置图例的标题
                legend=alt.Legend(
                    orient='none',
                    legendX=120,
                    legendY=-80,
                    columns=1,
                ),
            ),
            # tooltip=[
            #     alt.Tooltip('交易日期'),
            #     alt.Tooltip(style_config.TERM_SPREAD_CONFIG['MEAN_COL']),
            # ],
        )
    )


def draw_bar_line_chart_with_highlighted_signal(dt_indexed_df, config: param_cls.BarLineWithSignalParam):
    trade_dt = dt_indexed_df.index
    st.write(trade_dt[-1])
    if config.dt_slider_param is not None:
        custom_dt = get_custom_dt_with_slider(trade_dt=trade_dt, config=config.dt_slider_param)
        selected_df = dt_indexed_df.loc[custom_dt[0] : custom_dt[1]].reset_index()
    else:
        selected_df = dt_indexed_df

    # 创建一个新的数据列，用于编码颜色
    if not config.isSignalAssigned:
        if config.bar_param.no_signal is None:
            selected_df[config.bar_param.axis_names['LEGEND']] = (
                selected_df[config.bar_param.axis_names['Y']] >= selected_df[config.line_param.axis_names['Y']]
            ).replace(
                {
                    True: config.bar_param.true_signal,
                    False: config.bar_param.false_signal,
                }
            )
        else:
            selected_df = append_signal_column(
                df=selected_df,
                signal_col=config.bar_param.axis_names['LEGEND'],
                target_col=config.bar_param.axis_names['Y'],
                upper_bound_col=config.line_param.compared_cols[0],
                lower_bound_col=config.line_param.compared_cols[1],
                top_signal=config.bar_param.true_signal,
                bottom_signal=config.bar_param.false_signal,
                middle_signal=config.bar_param.no_signal,
            )

    selected_df[config.line_param.axis_names['LEGEND']] = config.line_param.axis_names['Y']
    if config.isConvertedToPct:
        selected_df = selected_df.apply(divide_by_100)
        config.bar_param.y_axis_format = CHART_NUM_FORMAT['pct']
        config.line_param.y_axis_format = CHART_NUM_FORMAT['pct']

    # st.write(selected_df)

    # 创建条形图
    bar = add_altair_bar_with_highlighted_signal(selected_df, config.bar_param)

    if config.isLineDrawn:
        # 创建线图
        line = add_altair_line_with_stroke_dash(selected_df, config.line_param)

        # 显示图表
        st.altair_chart(
            (bar + line).resolve_scale(color='independent'),
            theme='streamlit',
            use_container_width=True,
        )
    else:
        st.altair_chart(
            bar,
            theme='streamlit',
            use_container_width=True,
        )


def draw_test(dt_indexed_df, config: param_cls.BarLineWithSignalParam):
    config.dt_slider_param.key = 'TEST_SLIDER'
    trade_dt = dt_indexed_df.index
    # st.write(trade_dt)
    if config.dt_slider_param is not None:
        custom_dt = get_custom_dt_with_slider(trade_dt=trade_dt, config=config.dt_slider_param)
        selected_df = dt_indexed_df.loc[custom_dt[0] : custom_dt[1]].reset_index()
    else:
        selected_df = dt_indexed_df
    st.write(dt_indexed_df)
    st.write(selected_df)

    # 创建一个新的数据列，用于编码颜色
    if config.bar_param.no_signal is None:
        selected_df[config.bar_param.axis_names['LEGEND']] = (
            selected_df[config.bar_param.axis_names['Y']] >= selected_df[config.line_param.axis_names['Y']]
        ).replace(
            {
                True: config.bar_param.true_signal,
                False: config.bar_param.false_signal,
            }
        )
    else:
        selected_df = append_signal_column(
            df=selected_df,
            signal_col=config.bar_param.axis_names['LEGEND'],
            target_col=config.bar_param.axis_names['Y'],
            upper_bound_col=config.line_param.compared_cols[0],
            lower_bound_col=config.line_param.compared_cols[1],
            top_signal=config.bar_param.true_signal,
            bottom_signal=config.bar_param.false_signal,
            middle_signal=config.bar_param.no_signal,
        )

    selected_df[config.line_param.axis_names['LEGEND']] = config.line_param.axis_names['Y']
    if config.isConvertedToPct:
        selected_df = selected_df.apply(divide_by_100)
        config.bar_param.y_axis_format = CHART_NUM_FORMAT['pct']
        config.line_param.y_axis_format = CHART_NUM_FORMAT['pct']

    st.write(selected_df)

    # 创建条形图
    bar = add_altair_bar_with_highlighted_signal(selected_df, config.bar_param)

    if config.isLineDrawn:
        # 创建线图
        line = add_altair_line_with_stroke_dash(selected_df, config.line_param)

        # 显示图表
        st.altair_chart(
            (bar + line).resolve_scale(color='independent'),
            theme='streamlit',
            use_container_width=True,
        )
    else:
        st.altair_chart(
            bar,
            theme='streamlit',
            use_container_width=True,
        )
