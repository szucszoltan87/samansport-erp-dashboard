"""
Plotly chart builders for SamanSport ERP Dashboard.
"""

import copy

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from theme import C, FONT_FAMILY, PLOTLY_BASE_LAYOUT, PLOTLY_NO_MODEBAR, hu_thousands


def _base_layout(**overrides) -> dict:
    """Return a deep copy of PLOTLY_BASE_LAYOUT merged with overrides."""
    layout = copy.deepcopy(PLOTLY_BASE_LAYOUT)
    layout.update(overrides)
    return layout


def _empty_chart_placeholder(fig: go.Figure, height: int = 380) -> None:
    """Render a chart with a centered 'Nincs adat' annotation."""
    fig.add_annotation(
        text="Nincs adat",
        xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=18, color="#9ca3af", family=FONT_FAMILY),
    )
    fig.update_layout(
        **_base_layout(
            height=height,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_NO_MODEBAR)


def chart_style(fig: go.Figure, height: int = 380, title: str = "") -> None:
    fig.update_layout(
        **_base_layout(
            title=dict(text=title, font=dict(size=13, color="#374151", family=FONT_FAMILY), x=0) if title else dict(text=""),
            height=height,
            margin=dict(l=0, r=0, t=40 if title else 10, b=0),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_NO_MODEBAR)


def hbar_chart(labels, values, color: str, height: int = 300) -> None:
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=color, opacity=0.85),
        hovertemplate="%{y}<br><b>%{x:,.0f}</b><extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(
            height=height,
            margin=dict(l=0, r=16, t=0, b=0),
            yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(color="#374151", size=10), automargin=True),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_NO_MODEBAR)


def revenue_trend_chart(monthly: pd.DataFrame) -> None:
    """Area line chart for revenue trend (Bruttó forgalom)."""
    if monthly.empty:
        return _empty_chart_placeholder(go.Figure(), height=260)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Periódus"], y=monthly["Bruttó érték"],
        mode="lines", name="Bruttó forgalom",
        line=dict(color=C["coral"], width=2.5),
        fill="tozeroy", fillcolor="rgba(231,76,60,0.08)",
        hovertemplate="%{x}<br><b>%{y:,.0f} HUF</b><extra></extra>",
    ))
    chart_style(fig, height=260)


def quantity_bar_chart(mq: pd.DataFrame) -> None:
    """Bar chart for sold quantities per period."""
    if mq.empty:
        return _empty_chart_placeholder(go.Figure(), height=230)
    fig = go.Figure(go.Bar(
        x=mq["Periódus"], y=mq["Mennyiség"],
        marker=dict(color=C["charcoal"], opacity=0.8),
        hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>",
    ))
    chart_style(fig, height=230)


def top10_products_chart(grp: pd.DataFrame) -> None:
    """Horizontal bar chart for top 10 products by revenue."""
    if grp.empty:
        return _empty_chart_placeholder(go.Figure(), height=300)
    max_val = grp["Forgalom"].max()
    fig = go.Figure(go.Bar(
        x=grp["Forgalom"], y=grp["Label"].tolist(), orientation="h",
        marker=dict(color=C["coral"], opacity=0.85),
        text=grp.apply(lambda r: f"  {hu_thousands(r['Forgalom'])} Ft  ({r['Pct']:.1f}%)", axis=1),
        textposition="outside",
        textfont=dict(size=11, color="#374151"),
        hovertemplate="%{y}<br><b>%{x:,.0f} Ft</b><br>Arány: %{customdata:.1f}%<extra></extra>",
        customdata=grp["Pct"],
        cliponaxis=False,
    ))
    fig.update_layout(
        **_base_layout(
            height=max(400, len(grp) * 42),
            margin=dict(l=0, r=20, t=0, b=30),
            xaxis=dict(range=[0, max_val * 1.35], gridcolor="#f1f5f9",
                       tickfont=dict(color="#9ca3af", size=10),
                       tickformat=",.0f", separatethousands=True,
                       title=dict(text="Bruttó forgalom (HUF)", font=dict(size=11, color="#9ca3af"))),
            yaxis=dict(type="category", gridcolor="#f1f5f9",
                       tickfont=dict(color="#374151", size=10),
                       automargin=True, title=None),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_NO_MODEBAR)


def metric_chart(grouped: pd.DataFrame, col_name: str, metric: str,
                 unit: str, ytitle: str, chart_type: str) -> None:
    """Bar or line chart for a single analytics metric."""
    if grouped.empty:
        return _empty_chart_placeholder(go.Figure(), height=380)
    fig = go.Figure()
    ht = f"%{{x}}<br><b>%{{y:,.0f}} {unit}</b><extra></extra>"
    if chart_type == "Oszlop":
        fig.add_trace(go.Bar(
            x=grouped["Periódus"], y=grouped[col_name],
            marker_color=C["coral"], name=metric, hovertemplate=ht,
        ))
    else:
        fig.add_trace(go.Scatter(
            x=grouped["Periódus"], y=grouped[col_name],
            mode="lines+markers", name=metric,
            line=dict(color=C["coral"], width=2.5),
            marker=dict(size=6, color=C["coral"]),
            fill="tozeroy", fillcolor="rgba(231,76,60,0.07)",
            hovertemplate=ht,
        ))
    fig.update_layout(yaxis_title=ytitle)
    chart_style(fig, height=380)


def movements_chart(all_p: list, be_v: list, ki_v: list,
                    chart_type: str) -> None:
    """Bar or line chart for warehouse movements (incoming vs outgoing)."""
    if not all_p:
        return _empty_chart_placeholder(go.Figure(), height=380)
    fig = go.Figure()
    if chart_type == "Oszlop":
        fig.add_trace(go.Bar(x=all_p, y=be_v, name="Beérkező", marker_color=C["coral"],
                             hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>"))
        fig.add_trace(go.Bar(x=all_p, y=ki_v, name="Kiadó",    marker_color=C["charcoal"],
                             hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>"))
        fig.update_layout(barmode="group")
    else:
        fig.add_trace(go.Scatter(x=all_p, y=be_v, name="Beérkező",
                                 mode="lines+markers", line=dict(color=C["coral"], width=2.5),
                                 marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=all_p, y=ki_v, name="Kiadó",
                                 mode="lines+markers", line=dict(color=C["charcoal"], width=2.5),
                                 marker=dict(size=6)))
    chart_style(fig, height=380)
