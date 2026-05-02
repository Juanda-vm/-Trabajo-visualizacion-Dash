import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import os

# ── Data Loading ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "ecommerce.csv"), encoding="latin-1", sep=";")
df["Order_Date"] = pd.to_datetime(df["Order_Date"], dayfirst=True)
df["Month"]      = df["Order_Date"].dt.month
df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
df["Year"]       = df["Order_Date"].dt.year
df["Profit_Margin"] = (df["Profit"] / df["Total_Sales"] * 100).round(2)

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
CATEGORIES = sorted(df["Product_Category"].unique())
COUNTRIES  = sorted(df["Country"].unique())
REGIONS    = sorted(df["Region"].unique())
SEGMENTS   = sorted(df["Customer_Segment"].unique())

# ── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    "bg":       "#F4F6FB",
    "card":     "#FFFFFF",
    "primary":  "#1B3A6B",
    "accent":   "#2563EB",
    "green":    "#16A34A",
    "amber":    "#D97706",
    "red":      "#DC2626",
    "text":     "#1E293B",
    "muted":    "#64748B",
    "border":   "#E2E8F0",
    "cat_colors": ["#1B3A6B", "#2563EB", "#16A34A", "#D97706"],
}

CAT_COLOR_MAP = {c: COLORS["cat_colors"][i] for i, c in enumerate(CATEGORIES)}

CARD_STYLE = {
    "backgroundColor": COLORS["card"],
    "borderRadius": "14px",
    "padding": "20px",
    "boxShadow": "0 2px 12px rgba(0,0,0,0.07)",
    "border": f"1px solid {COLORS['border']}",
}

# ── App Init ──────────────────────────────────────────────────────────────────
app = Dash(__name__, title="Global Ecommerce Sales")
server = app.server  # expose for gunicorn

# ── Helper: KPI Card ──────────────────────────────────────────────────────────
def kpi_card(title, value, delta=None, color=None):
    color = color or COLORS["primary"]
    delta_el = html.Span(delta, style={"fontSize":"13px","color":COLORS["green"],"marginLeft":"6px"}) if delta else None
    return html.Div([
        html.P(title, style={"margin":"0","fontSize":"12px","color":COLORS["muted"],"fontWeight":"600","letterSpacing":"0.05em","textTransform":"uppercase"}),
        html.Div([
            html.H3(value, style={"margin":"4px 0 0","fontSize":"26px","fontWeight":"800","color":color}),
            delta_el or html.Span(),
        ], style={"display":"flex","alignItems":"center"}),
    ], style={**CARD_STYLE, "flex":"1","minWidth":"160px"})

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(style={"backgroundColor":COLORS["bg"],"minHeight":"100vh","fontFamily":"'Segoe UI', system-ui, sans-serif","color":COLORS["text"]}, children=[

    # ── Header
    html.Div([
        html.Div([
            html.H1("Global Ecommerce Sales", style={"margin":"0","fontSize":"24px","fontWeight":"800","color":COLORS["primary"]}),
            html.P("Interactive performance dashboard", style={"margin":"2px 0 0","fontSize":"13px","color":COLORS["muted"]}),
        ]),
        # Nav tabs
        html.Div([
            dcc.Tabs(id="tab-nav", value="overview", children=[
                dcc.Tab(label="Overview",            value="overview"),
                dcc.Tab(label="Operations",          value="operations"),
                dcc.Tab(label="Financial Overview",  value="financial"),
                dcc.Tab(label="Dispersion",          value="dispersion"),
            ], style={"border":"none"}, colors={"border":"transparent","primary":COLORS["accent"],"background":"transparent"}),
        ]),
    ], style={"backgroundColor":COLORS["card"],"padding":"16px 28px","display":"flex","alignItems":"center","justifyContent":"space-between","boxShadow":"0 2px 8px rgba(0,0,0,0.06)","borderBottom":f"1px solid {COLORS['border']}"}),

    # ── Main content area
    html.Div([

        # ── Sidebar Filters
        html.Div([
            html.P("FILTERS", style={"fontSize":"11px","fontWeight":"700","color":COLORS["muted"],"letterSpacing":"0.1em","marginBottom":"16px"}),

            html.Label("Year", style={"fontSize":"12px","fontWeight":"600","color":COLORS["text"]}),
            dcc.Dropdown(
                id="filter-year",
                options=[{"label":"All Years","value":"All"}] + [{"label":str(y),"value":y} for y in sorted(df["Year"].unique())],
                value="All", clearable=False,
                style={"marginBottom":"14px","fontSize":"13px"},
            ),

            html.Label("Region", style={"fontSize":"12px","fontWeight":"600","color":COLORS["text"]}),
            dcc.Dropdown(
                id="filter-region",
                options=[{"label":"All Regions","value":"All"}] + [{"label":r,"value":r} for r in REGIONS],
                value="All", clearable=False,
                style={"marginBottom":"14px","fontSize":"13px"},
            ),

            html.Label("Country", style={"fontSize":"12px","fontWeight":"600","color":COLORS["text"]}),
            dcc.Dropdown(
                id="filter-country",
                options=[{"label":"All Countries","value":"All"}] + [{"label":c,"value":c} for c in COUNTRIES],
                value="All", clearable=False,
                style={"marginBottom":"14px","fontSize":"13px"},
            ),

            html.Label("Category", style={"fontSize":"12px","fontWeight":"600","color":COLORS["text"]}),
            dcc.Dropdown(
                id="filter-category",
                options=[{"label":"All Categories","value":"All"}] + [{"label":c,"value":c} for c in CATEGORIES],
                value="All", clearable=False,
                style={"marginBottom":"14px","fontSize":"13px"},
            ),

            html.Label("Segment", style={"fontSize":"12px","fontWeight":"600","color":COLORS["text"]}),
            dcc.Dropdown(
                id="filter-segment",
                options=[{"label":"All Segments","value":"All"}] + [{"label":s,"value":s} for s in SEGMENTS],
                value="All", clearable=False,
                style={"marginBottom":"14px","fontSize":"13px"},
            ),
        ], style={**CARD_STYLE,"width":"210px","flexShrink":"0","alignSelf":"flex-start","position":"sticky","top":"20px"}),

        # ── Charts Area
        html.Div(id="tab-content", style={"flex":"1","minWidth":"0"}),

    ], style={"display":"flex","gap":"20px","padding":"20px 24px","maxWidth":"1400px","margin":"0 auto"}),
])

# ── Shared Filter Helper ───────────────────────────────────────────────────────
def apply_filters(year, region, country, category, segment):
    d = df.copy()
    if year     != "All": d = d[d["Year"]            == year]
    if region   != "All": d = d[d["Region"]          == region]
    if country  != "All": d = d[d["Country"]         == country]
    if category != "All": d = d[d["Product_Category"]== category]
    if segment  != "All": d = d[d["Customer_Segment"]== segment]
    return d

# ── Chart Theme ───────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Segoe UI, system-ui, sans-serif", color=COLORS["text"], size=12),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor=COLORS["border"], zeroline=False),
)

def fmt_k(n):
    if n >= 1_000_000: return f"${n/1_000_000:.1f}M"
    if n >= 1_000:     return f"${n/1_000:.0f}K"
    return f"${n:.0f}"

# ── Tab Content Callback ───────────────────────────────────────────────────────
@app.callback(
    Output("tab-content","children"),
    Input("tab-nav","value"),
    Input("filter-year","value"),
    Input("filter-region","value"),
    Input("filter-country","value"),
    Input("filter-category","value"),
    Input("filter-segment","value"),
)
def render_tab(tab, year, region, country, category, segment):
    d = apply_filters(year, region, country, category, segment)

    total_sales  = d["Total_Sales"].sum()
    total_profit = d["Profit"].sum()
    total_orders = d["Order_ID"].nunique()
    avg_margin   = (d["Profit"].sum() / d["Total_Sales"].sum() * 100) if total_sales else 0

    # ── KPI Row (shared across tabs)
    kpis = html.Div([
        kpi_card("Total Sales",    fmt_k(total_sales),  color=COLORS["primary"]),
        kpi_card("Total Profit",   fmt_k(total_profit), color=COLORS["green"]),
        kpi_card("Orders",         f"{total_orders:,}",  color=COLORS["accent"]),
        kpi_card("Avg Margin",     f"{avg_margin:.1f}%", color=COLORS["amber"]),
    ], style={"display":"flex","gap":"14px","flexWrap":"wrap","marginBottom":"18px"})

    # ════════════════════════════════════════════════════════════════
    if tab == "overview":
        # Donut – Sales by category
        cat_sales = d.groupby("Product_Category")["Total_Sales"].sum().reset_index()
        fig_donut = go.Figure(go.Pie(
            labels=cat_sales["Product_Category"], values=cat_sales["Total_Sales"],
            hole=0.55, marker_colors=[CAT_COLOR_MAP[c] for c in cat_sales["Product_Category"]],
            textinfo="percent+label", hovertemplate="%{label}: %{value:,.0f}<extra></extra>",
        ))
        fig_donut.update_layout(title="Sales Distribution by Category", showlegend=True, **CHART_LAYOUT)

        # Bar – Profit Margin by Category
        cat_margin = d.groupby("Product_Category").apply(
            lambda x: x["Profit"].sum() / x["Total_Sales"].sum() * 100 if x["Total_Sales"].sum() else 0
        ).reset_index(name="Margin")
        fig_margin = go.Figure([go.Bar(
            x=cat_margin["Product_Category"], y=cat_margin["Margin"],
            marker_color=[CAT_COLOR_MAP[c] for c in cat_margin["Product_Category"]],
            text=cat_margin["Margin"].apply(lambda v: f"{v:.1f}%"), textposition="outside",
        )])
        fig_margin.update_layout(title="Profit Margin by Category (%)", yaxis_title="Profit Margin %", **CHART_LAYOUT)

        # Grouped Bar – Sales & Profit by Country (top 10)
        ctry = d.groupby("Country")[["Total_Sales","Profit"]].sum().nlargest(10,"Total_Sales").reset_index()
        fig_country = go.Figure([
            go.Bar(name="Total Sales",  x=ctry["Country"], y=ctry["Total_Sales"],  marker_color=COLORS["primary"]),
            go.Bar(name="Total Profit", x=ctry["Country"], y=ctry["Profit"],        marker_color=COLORS["accent"]),
        ])
        fig_country.update_layout(title="Sales and Profit by Country (Top 10)", barmode="group", **CHART_LAYOUT)

        # Line – Profit evolution by category
        monthly = d.groupby(["Month","Month_Name","Product_Category"])["Profit"].sum().reset_index()
        monthly = monthly.sort_values("Month")
        fig_line = go.Figure()
        for cat in CATEGORIES:
            sub = monthly[monthly["Product_Category"]==cat]
            fig_line.add_trace(go.Scatter(
                x=sub["Month_Name"], y=sub["Profit"], mode="lines+markers",
                name=cat, line=dict(color=CAT_COLOR_MAP[cat], width=2),
            ))
        fig_line.update_layout(title="Profit Evolution by Category", yaxis_title="Total Profit", **CHART_LAYOUT)

        return html.Div([kpis,
            html.Div([
                html.Div([dcc.Graph(figure=fig_donut,  config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
                html.Div([dcc.Graph(figure=fig_margin, config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
            ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),
            html.Div([
                html.Div([dcc.Graph(figure=fig_country,config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
                html.Div([dcc.Graph(figure=fig_line,   config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
            ], style={"display":"flex","gap":"16px"}),
        ])

    # ════════════════════════════════════════════════════════════════
    elif tab == "operations":
        # Bar – Orders by region
        reg_orders = d.groupby("Region")["Order_ID"].count().reset_index(name="Orders")
        fig_reg = go.Figure(go.Bar(
            x=reg_orders["Region"], y=reg_orders["Orders"],
            marker_color=COLORS["accent"],
            text=reg_orders["Orders"], textposition="outside",
        ))
        fig_reg.update_layout(title="Orders by Region", **CHART_LAYOUT)

        # Bar – Top 10 Products by Sales
        prod = d.groupby("Product_Name")["Total_Sales"].sum().nlargest(10).reset_index()
        fig_prod = go.Figure(go.Bar(
            y=prod["Product_Name"], x=prod["Total_Sales"],
            orientation="h", marker_color=COLORS["primary"],
            text=prod["Total_Sales"].apply(fmt_k), textposition="outside",
        ))
        fig_prod.update_layout(title="Top 10 Products by Sales", xaxis_title="Total Sales",
                               yaxis=dict(autorange="reversed"), **CHART_LAYOUT)

        # Pie – Payment Method
        pay = d.groupby("Payment_Method")["Order_ID"].count().reset_index(name="Count")
        fig_pay = go.Figure(go.Pie(
            labels=pay["Payment_Method"], values=pay["Count"], hole=0.4,
            marker_colors=[COLORS["primary"],COLORS["accent"],COLORS["green"],COLORS["amber"]],
        ))
        fig_pay.update_layout(title="Orders by Payment Method", **CHART_LAYOUT)

        # Bar – Segment contribution
        seg = d.groupby("Customer_Segment")[["Total_Sales","Profit"]].sum().reset_index()
        fig_seg = go.Figure([
            go.Bar(name="Total Sales",  x=seg["Customer_Segment"], y=seg["Total_Sales"],  marker_color=COLORS["primary"]),
            go.Bar(name="Total Profit", x=seg["Customer_Segment"], y=seg["Profit"],        marker_color=COLORS["green"]),
        ])
        fig_seg.update_layout(title="Sales & Profit by Customer Segment", barmode="group", **CHART_LAYOUT)

        return html.Div([kpis,
            html.Div([
                html.Div([dcc.Graph(figure=fig_reg,  config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
                html.Div([dcc.Graph(figure=fig_pay,  config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
            ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),
            html.Div([
                html.Div([dcc.Graph(figure=fig_prod, config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1.5"}),
                html.Div([dcc.Graph(figure=fig_seg,  config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
            ], style={"display":"flex","gap":"16px"}),
        ])

    # ════════════════════════════════════════════════════════════════
    elif tab == "financial":
        # Line – Monthly Sales trend
        mo_sales = d.groupby(["Month","Month_Name"])["Total_Sales"].sum().reset_index().sort_values("Month")
        fig_trend = go.Figure(go.Scatter(
            x=mo_sales["Month_Name"], y=mo_sales["Total_Sales"],
            mode="lines+markers", fill="tozeroy",
            line=dict(color=COLORS["accent"],width=2.5),
            fillcolor="rgba(37,99,235,0.1)",
        ))
        fig_trend.update_layout(title="Monthly Sales Trend", yaxis_title="Total Sales", **CHART_LAYOUT)

        # Bar – Profit by Country (top 10)
        ctry_p = d.groupby("Country")["Profit"].sum().nlargest(10).reset_index()
        fig_cp = go.Figure(go.Bar(
            x=ctry_p["Country"], y=ctry_p["Profit"],
            marker_color=COLORS["green"],
            text=ctry_p["Profit"].apply(fmt_k), textposition="outside",
        ))
        fig_cp.update_layout(title="Top 10 Countries by Profit", **CHART_LAYOUT)

        # Stacked Bar – Sales by Category per Month
        mo_cat = d.groupby(["Month","Month_Name","Product_Category"])["Total_Sales"].sum().reset_index().sort_values("Month")
        fig_stack = go.Figure()
        for cat in CATEGORIES:
            sub = mo_cat[mo_cat["Product_Category"]==cat]
            fig_stack.add_trace(go.Bar(
                name=cat, x=sub["Month_Name"], y=sub["Total_Sales"],
                marker_color=CAT_COLOR_MAP[cat],
            ))
        fig_stack.update_layout(title="Monthly Sales by Category", barmode="stack", **CHART_LAYOUT)

        # Bar – Avg Discount by Category
        disc = d.groupby("Product_Category")["Discount_Percent"].mean().reset_index()
        disc["Discount_Percent"] = (disc["Discount_Percent"]*100).round(1)
        fig_disc = go.Figure(go.Bar(
            x=disc["Product_Category"], y=disc["Discount_Percent"],
            marker_color=[CAT_COLOR_MAP[c] for c in disc["Product_Category"]],
            text=disc["Discount_Percent"].apply(lambda v:f"{v:.1f}%"), textposition="outside",
        ))
        fig_disc.update_layout(title="Average Discount % by Category", yaxis_title="Avg Discount %", **CHART_LAYOUT)

        return html.Div([kpis,
            html.Div([
                html.Div([dcc.Graph(figure=fig_trend, config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
                html.Div([dcc.Graph(figure=fig_disc,  config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
            ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),
            html.Div([
                html.Div([dcc.Graph(figure=fig_stack, config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1.5"}),
                html.Div([dcc.Graph(figure=fig_cp,    config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
            ], style={"display":"flex","gap":"16px"}),
        ])

    # ════════════════════════════════════════════════════════════════
    elif tab == "dispersion":
        # Scatter – Sales vs Profit colored by Category
        fig_scatter = px.scatter(
            d, x="Total_Sales", y="Profit", color="Product_Category",
            color_discrete_map=CAT_COLOR_MAP, opacity=0.65,
            hover_data=["Country","Product_Name","Customer_Segment"],
            title="Sales vs Profit by Category",
            size="Quantity", size_max=20,
        )
        fig_scatter.update_layout(**CHART_LAYOUT)

        # Scatter – Unit Price vs Profit Margin
        d2 = d.copy()
        d2["Profit_Margin"] = (d2["Profit"]/d2["Total_Sales"]*100).clip(-20,100)
        fig_s2 = px.scatter(
            d2, x="Unit_Price", y="Profit_Margin", color="Product_Category",
            color_discrete_map=CAT_COLOR_MAP, opacity=0.6,
            title="Unit Price vs Profit Margin",
        )
        fig_s2.update_layout(**CHART_LAYOUT)

        # Box – Profit distribution by Category
        fig_box = px.box(
            d, x="Product_Category", y="Profit", color="Product_Category",
            color_discrete_map=CAT_COLOR_MAP,
            title="Profit Distribution by Category",
        )
        fig_box.update_layout(showlegend=False, **CHART_LAYOUT)

        # Histogram – Total Sales distribution
        fig_hist = px.histogram(
            d, x="Total_Sales", nbins=40, color="Product_Category",
            color_discrete_map=CAT_COLOR_MAP,
            title="Sales Distribution Histogram",
            barmode="overlay", opacity=0.7,
        )
        fig_hist.update_layout(**CHART_LAYOUT)

        return html.Div([kpis,
            html.Div([
                html.Div([dcc.Graph(figure=fig_scatter,config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
                html.Div([dcc.Graph(figure=fig_s2,     config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
            ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),
            html.Div([
                html.Div([dcc.Graph(figure=fig_box,    config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
                html.Div([dcc.Graph(figure=fig_hist,   config={"displayModeBar":False})], style={**CARD_STYLE,"flex":"1"}),
            ], style={"display":"flex","gap":"16px"}),
        ])

    return html.Div("Select a tab.")


if __name__ == "__main__":
    app.run(debug=True)