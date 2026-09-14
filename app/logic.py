"""
Построение комбинированного графика (area + bar + spline + line)
в стиле CleanShot-скриншота: Cost (area), CPA (bar), ROI confirmed
(spline), Conversions (line с маркерами), с общим tooltip по дате.
"""

from datetime import date, timedelta
from typing import Sequence

import plotly.graph_objects as go

COLORS = {
    "cost": "#f2d675",  # жёлтый — area
    "cpa": "#4a90e2",  # синий — bar
    "roi_confirmed": "#2e7d32",  # зелёный — spline
    "conversions": "#a020f0",  # фиолетовый — line
}


def _axis_range(values: Sequence[float], pad_ratio: float = 0.1) -> list[float]:
    """Диапазон оси с небольшим отступом, низ всегда 0 (как на гифке)."""
    top = max(values) * (1 + pad_ratio)
    return [0, top if top > 0 else 1]


def build_chart(
        dates: Sequence[date | str],
        cost: Sequence[float],
        cpa: Sequence[float],
        roi_confirmed: Sequence[float],
        conversions: Sequence[float],
) -> go.Figure:
    """
    Строит комбинированный график с 4 сериями поверх общей оси X (даты).
    Каждая серия — на своей независимой оси Y (как на гифке), иначе
    ROI confirmed (до ~600) визуально "сплющивает" остальные серии.

    Все 5 последовательностей должны быть одинаковой длины.
    """
    lengths = {len(dates), len(cost), len(cpa), len(roi_confirmed), len(conversions)}
    if len(lengths) != 1:
        raise ValueError(f"Все серии должны быть одной длины, получено: {lengths}")

    fig = go.Figure()

    # Cost — area (заливка снизу), своя ось y (y1)
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=cost,
            name="Cost",
            mode="lines",
            fill="tozeroy",
            line=dict(color=COLORS["cost"], width=1),
            fillcolor="rgba(242, 214, 117, 0.45)",
            hovertemplate="Cost: <b>%{y:.2f}</b><extra></extra>",
            yaxis="y1",
        )
    )

    # CPA — bar (мелкие столбики внизу), своя ось y2
    # ширина в мс: для оси с датами width задаётся в миллисекундах,
    # иначе Plotly рисует бар как вертикальную линию на всю высоту
    one_day_ms = 24 * 60 * 60 * 1000
    fig.add_trace(
        go.Bar(
            x=dates,
            y=cpa,
            name="CPA",
            marker=dict(color=COLORS["cpa"], cornerradius=6),
            width=one_day_ms * 0.15,
            hovertemplate="CPA: <b>%{y:.2f}</b><extra></extra>",
            yaxis="y2",
        )
    )

    # ROI confirmed — spline, своя ось y3
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=roi_confirmed,
            name="ROI confirmed",
            mode="lines",
            line=dict(color=COLORS["roi_confirmed"], width=2.5, shape="spline"),
            hovertemplate="ROI confirmed: <b>%{y:.2f}</b><extra></extra>",
            yaxis="y3",
        )
    )

    # Conversions — line с квадратными маркерами, своя ось y4
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=conversions,
            name="Conversions",
            mode="lines+markers",
            line=dict(color=COLORS["conversions"], width=4),
            marker=dict(symbol="square", size=14, color=COLORS["conversions"]),
            hovertemplate="Conversions: <b>%{y}</b><extra></extra>",
            yaxis="y4",
        )
    )

    hidden_axis = dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        showline=False,
        overlaying="y",
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        plot_bgcolor="rgba(255, 214, 224, 0.35)",
        paper_bgcolor="rgba(255, 214, 224, 0.35)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            showline=True,
            linecolor="#c9c9c9",
            mirror=True,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            showline=True,
            linecolor="#c9c9c9",
            mirror=True,
            range=_axis_range(cost),
        ),
        yaxis2=dict(**hidden_axis, range=_axis_range(cpa, pad_ratio=40.0)),
        yaxis3=dict(**hidden_axis, range=_axis_range(roi_confirmed)),
        yaxis4=dict(**hidden_axis, range=_axis_range(conversions)),
        barmode="overlay",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="white",
            font=dict(size=16, color="#222"),
            align="left",
        ),
        hoverdistance=100,
    )
    # Убираем вертикальную spike-линию под курсором, как на гифке её нет
    fig.update_xaxes(showspikes=False)

    return fig


def build_chart_html(
        dates: Sequence[date | str],
        cost: Sequence[float],
        cpa: Sequence[float],
        roi_confirmed: Sequence[float],
        conversions: Sequence[float],
        full_html: bool = True,
) -> str:
    """Возвращает готовый HTML графика (строка), без бокового блока."""
    fig = build_chart(dates, cost, cpa, roi_confirmed, conversions)
    return fig.to_html(full_html=full_html, include_plotlyjs="cdn")


def build_page_html(
        dates: Sequence[date | str],
        cost: Sequence[float],
        cpa: Sequence[float],
        roi_confirmed: Sequence[float],
        conversions: Sequence[float],
) -> str:
    """
    Полная страница как на гифке: слева декоративная KPI-панель
    (Tdy / 0% / $0 / $0 / 0 / 0 / —), справа сам график.
    """
    chart_div = build_chart_html(
        dates, cost, cpa, roi_confirmed, conversions, full_html=False
    )

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
  html, body {{ height: 100%; margin: 0; }}
  body {{
    display: flex;
    background: rgba(255, 214, 224, 0.35);
    font-family: -apple-system, Arial, sans-serif;
  }}
  .sidebar {{
    width: 90px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
  }}
  .sidebar .cell {{
    display: flex;
    align-items: center;
    justify-content: center;
    height: 60px;
    background: white;
    border-bottom: 1px solid #eee;
    font-weight: 600;
    font-size: 15px;
    color: #333;
  }}
  .sidebar .cell:first-child {{ font-weight: 700; font-size: 16px; }}
  .chart-wrap {{
    width: 900px;
    height: 500px;
    margin: 24px;
  }}
</style>
</head>
<body>
  <div class="sidebar">
    <div class="cell">Tdy</div>
    <div class="cell">0%</div>
    <div class="cell">$0</div>
    <div class="cell">$0</div>
    <div class="cell">0</div>
    <div class="cell">0</div>
    <div class="cell">&mdash;</div>
  </div>
  <div class="chart-wrap">{chart_div}</div>
</body>
</html>"""


def get_demo_data():
    dates = [
        date(2026, 6, 10),
        date(2026, 6, 11),
        date(2026, 6, 12),
        date(2026, 6, 13),
        date(2026, 6, 14),
    ]
    cost = [2.04, 25.85, 44.36, 55.65, 63.75]
    cpa = [0.68, 0.86, 1.23, 0.79, 0.71]
    roi_confirmed = [610.78, 180.50, 161.47, 56.33, 357.25]
    conversions = [3, 30, 36, 70, 90]
    return dates, cost, cpa, roi_confirmed, conversions