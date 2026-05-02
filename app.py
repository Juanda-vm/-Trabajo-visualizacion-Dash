import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import os

# ── Data Loading ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "ecommerce.csv"), encoding="latin-1", sep=";")
df["Order_Date"]    = pd.to_datetime(df["Order_Date"], dayfirst=True)
df["Month"]         = df["Order_Date"].dt.month
df["Month_Name"]    = df["Order_Date"].dt.strftime("%b")
df["Year"]          = df["Order_Date"].dt.year
df["Profit_Margin"] = (df["Profit"] / df["Total_Sales"] * 100).round(2)

CATEGORIES = sorted(df["Product_Category"].unique())
COUNTRIES  = sorted(df["Country"].unique())
REGIONS    = sorted(df["Region"].unique())
SEGMENTS   = sorted(df["Customer_Segment"].unique())

COLORS = {
    "bg":         "#F0F4FA",
    "card":       "#FFFFFF",
    "primary":    "#1B3A6B",
    "accent":     "#2563EB",
    "green":      "#16A34A",
    "amber":      "#D97706",
    "text":       "#1E293B",
    "muted":      "#64748B",
    "border":     "#E2E8F0",
    "cat_colors": ["#1B3A6B", "#2563EB", "#16A34A", "#D97706"],
}
CAT_COLOR_MAP = {c: COLORS["cat_colors"][i] for i, c in enumerate(CATEGORIES)}

CARD_STYLE = {
    "backgroundColor": COLORS["card"],
    "borderRadius":    "14px",
    "padding":         "20px",
    "boxShadow":       "0 2px 12px rgba(0,0,0,0.07)",
    "border":          f"1px solid {COLORS['border']}",
}

def base_layout(**kwargs):
    """Aplica el tema base y permite sobrescribir cualquier propiedad."""
    defaults = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Segoe UI', system-ui, sans-serif", color=COLORS["text"], size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=COLORS["border"], zeroline=False),
    )
    defaults.update(kwargs)
    return defaults

def fmt_k(n):
    if n >= 1_000_000: return f"${n/1_000_000:.1f}M"
    if n >= 1_000:     return f"${n/1_000:.0f}K"
    return f"${n:.0f}"

def apply_filters(region, country, category, segments):
    d = df.copy()
    if region and region != "All":
        d = d[d["Region"] == region]
    if country and country != "All":
        d = d[d["Country"] == country]
    if category and category != "All":
        d = d[d["Product_Category"] == category]
    if segments:
        segs = segments if isinstance(segments, list) else [segments]
        if segs:
            d = d[d["Customer_Segment"].isin(segs)]
    return d

def filtered(region, country, category, segments):
    segs = segments if segments else SEGMENTS
    return apply_filters(region, country, category, segs)

def kpi_card(title, value, color):
    return dbc.Card(dbc.CardBody([
        html.P(title, style={"margin": "0", "fontSize": "11px", "fontWeight": "700",
                             "color": COLORS["muted"], "letterSpacing": "0.08em", "textTransform": "uppercase"}),
        html.H3(value, style={"margin": "4px 0 0", "fontSize": "26px", "fontWeight": "800", "color": color}),
    ]), style=CARD_STYLE)

app = Dash(__name__, title="Global Ecommerce Sales", external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div(
    style={"backgroundColor": COLORS["bg"], "minHeight": "100vh",
           "fontFamily": "'Segoe UI', system-ui, sans-serif"},
    children=[

        # HEADER
        html.Div([
            dbc.Container([
                dbc.Row([dbc.Col([
                    html.H1("🌐 Global Ecommerce Sales",
                            style={"margin": "0", "fontSize": "26px", "fontWeight": "800", "color": "white"}),
                    html.P("Tablero interactivo de rendimiento comercial",
                           style={"margin": "2px 0 0", "fontSize": "13px", "color": "rgba(255,255,255,0.75)"}),
                ])])
            ], fluid=True)
        ], style={
            "background": f"linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%)",
            "padding": "18px 24px",
            "boxShadow": "0 4px 16px rgba(0,0,0,0.15)",
        }),

        dbc.Container([

            # FILTROS
            dbc.Row([dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.P("FILTROS Y CONTROLES", style={
                        "fontSize": "11px", "fontWeight": "700", "color": COLORS["muted"],
                        "letterSpacing": "0.1em", "marginBottom": "16px",
                    }),
                    dbc.Row([
                        dbc.Col([
                            html.Label("📍 Región", style={"fontSize": "12px", "fontWeight": "600",
                                                           "color": COLORS["text"], "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="filter-region",
                                options=[{"label": "Todas las Regiones", "value": "All"}]
                                       + [{"label": r, "value": r} for r in REGIONS],
                                value="All", clearable=False, style={"fontSize": "13px"},
                            ),
                        ], md=3),
                        dbc.Col([
                            html.Label("🌍 País", style={"fontSize": "12px", "fontWeight": "600",
                                                         "color": COLORS["text"], "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="filter-country",
                                options=[{"label": "Todos los Países", "value": "All"}]
                                       + [{"label": c, "value": c} for c in COUNTRIES],
                                value="All", clearable=False, style={"fontSize": "13px"},
                            ),
                        ], md=3),
                        dbc.Col([
                            html.Label("📦 Categoría de Producto", style={"fontSize": "12px", "fontWeight": "600",
                                                                           "color": COLORS["text"], "marginBottom": "4px"}),
                            dcc.RadioItems(
                                id="filter-category",
                                options=[{"label": "  Todas", "value": "All"}]
                                       + [{"label": f"  {c}", "value": c} for c in CATEGORIES],
                                value="All",
                                style={"fontSize": "12px", "color": COLORS["text"], "lineHeight": "1.8"},
                                inputStyle={"marginRight": "6px", "accentColor": COLORS["accent"]},
                            ),
                        ], md=3),
                        dbc.Col([
                            html.Label("👥 Segmento de Cliente", style={"fontSize": "12px", "fontWeight": "600",
                                                                         "color": COLORS["text"], "marginBottom": "4px"}),
                            dcc.Checklist(
                                id="filter-segment",
                                options=[{"label": f"  {s}", "value": s} for s in SEGMENTS],
                                value=SEGMENTS,
                                style={"fontSize": "12px", "color": COLORS["text"], "lineHeight": "1.8"},
                                inputStyle={"marginRight": "6px", "accentColor": COLORS["accent"]},
                            ),
                        ], md=3),
                    ], className="g-3"),
                ]), style=CARD_STYLE)
            ])], className="mt-3 mb-3"),

            # KPIs
            dbc.Row(id="kpi-row", className="mb-3 g-3"),

            # FILA 1
            dbc.Row([
                dbc.Col([
                    dbc.Card(dbc.CardBody([
                        html.H5("📈 Tendencia de Ventas Mensuales",
                                style={"fontWeight": "700", "color": COLORS["primary"], "marginBottom": "2px"}),
                        html.P("Evolución de ventas por categoría | Selector: 1M · 6M · 1A · Todo",
                               style={"fontSize": "11px", "color": COLORS["muted"], "marginBottom": "8px"}),
                        dcc.Graph(id="graph-line", config={"displayModeBar": False}, style={"height": "370px"}),
                    ]), style=CARD_STYLE)
                ], md=6),
                dbc.Col([
                    dbc.Card(dbc.CardBody([
                        html.H5("📊 Ventas y Ganancias por País (Top 10)",
                                style={"fontWeight": "700", "color": COLORS["primary"], "marginBottom": "2px"}),
                        html.P("Cambia el fondo del gráfico con los botones:",
                               style={"fontSize": "11px", "color": COLORS["muted"], "marginBottom": "6px"}),
                        dbc.ButtonGroup([
                            dbc.Button("☀️ Claro",  id="btn-light", color="secondary", outline=True, size="sm", n_clicks=0),
                            dbc.Button("🌙 Oscuro", id="btn-dark",  color="dark",      outline=True, size="sm", n_clicks=0),
                            dbc.Button("🟦 Azul",   id="btn-blue",  color="primary",   outline=True, size="sm", n_clicks=0),
                        ], className="mb-2"),
                        dcc.Graph(id="graph-bar-country", config={"displayModeBar": False}, style={"height": "330px"}),
                    ]), style=CARD_STYLE)
                ], md=6),
            ], className="mb-3 g-3"),

            # FILA 2
            dbc.Row([
                dbc.Col([
                    dbc.Card(dbc.CardBody([
                        html.H5("🍩 Distribución de Ventas por Categoría",
                                style={"fontWeight": "700", "color": COLORS["primary"], "marginBottom": "2px"}),
                        html.P("Participación porcentual de cada categoría en el total de ventas",
                               style={"fontSize": "11px", "color": COLORS["muted"], "marginBottom": "8px"}),
                        dcc.Graph(id="graph-donut", config={"displayModeBar": False}, style={"height": "360px"}),
                    ]), style=CARD_STYLE)
                ], md=6),
                dbc.Col([
                    dbc.Card(dbc.CardBody([
                        html.H5("🔵 Dispersión: Ventas vs Ganancia",
                                style={"fontWeight": "700", "color": COLORS["primary"], "marginBottom": "2px"}),
                        html.P("Cada punto es una transacción; tamaño proporcional a la cantidad vendida",
                               style={"fontSize": "11px", "color": COLORS["muted"], "marginBottom": "8px"}),
                        dcc.Graph(id="graph-scatter", config={"displayModeBar": False}, style={"height": "360px"}),
                    ]), style=CARD_STYLE)
                ], md=6),
            ], className="mb-4 g-3"),

        ], fluid=True),
    ]
)

FILTER_INPUTS = [
    Input("filter-region",   "value"),
    Input("filter-country",  "value"),
    Input("filter-category", "value"),
    Input("filter-segment",  "value"),
]

@app.callback(Output("kpi-row", "children"), *FILTER_INPUTS)
def update_kpis(region, country, category, segments):
    d = filtered(region, country, category, segments)
    ts = d["Total_Sales"].sum()
    tp = d["Profit"].sum()
    to = d["Order_ID"].nunique()
    am = (tp / ts * 100) if ts else 0
    return [
        dbc.Col(kpi_card("💰 Total Ventas",    fmt_k(ts),    COLORS["primary"]), md=3),
        dbc.Col(kpi_card("📈 Total Ganancias", fmt_k(tp),    COLORS["green"]),   md=3),
        dbc.Col(kpi_card("🛒 Total Pedidos",   f"{to:,}",    COLORS["accent"]),  md=3),
        dbc.Col(kpi_card("📊 Margen Promedio", f"{am:.1f}%", COLORS["amber"]),   md=3),
    ]

@app.callback(Output("graph-line", "figure"), *FILTER_INPUTS)
def update_line(region, country, category, segments):
    d = filtered(region, country, category, segments).copy()
    d["YM"] = d["Order_Date"].values.astype("datetime64[M]")
    mo = (d.groupby(["YM", "Product_Category"])["Total_Sales"]
           .sum().reset_index().sort_values("YM"))
    fig = go.Figure()
    for cat in CATEGORIES:
        sub = mo[mo["Product_Category"] == cat]
        fig.add_trace(go.Scatter(
            x=sub["YM"], y=sub["Total_Sales"],
            mode="lines+markers", name=cat,
            line=dict(color=CAT_COLOR_MAP[cat], width=2.5),
            marker=dict(size=5),
            hovertemplate="%{x|%b %Y}<br>%{y:$,.0f}<extra>" + cat + "</extra>",
        ))
    fig.update_layout(**base_layout(
        margin=dict(l=10, r=10, t=10, b=65),
        xaxis=dict(
            showgrid=False, zeroline=False, type="date",
            rangeslider=dict(visible=True, thickness=0.07),
            rangeselector=dict(
                buttons=[
                    dict(count=1,  label="1M", step="month", stepmode="backward"),
                    dict(count=6,  label="6M", step="month", stepmode="backward"),
                    dict(count=1,  label="1A", step="year",  stepmode="backward"),
                    dict(step="all", label="Todo"),
                ],
                bgcolor=COLORS["bg"], activecolor=COLORS["accent"],
                font=dict(size=11, color=COLORS["text"]),
            ),
        ),
        yaxis=dict(showgrid=True, gridcolor=COLORS["border"], zeroline=False, tickformat="$,.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.32, xanchor="left", x=0),
    ))
    return fig

@app.callback(
    Output("graph-bar-country", "figure"),
    *FILTER_INPUTS,
    Input("btn-light", "n_clicks"),
    Input("btn-dark",  "n_clicks"),
    Input("btn-blue",  "n_clicks"),
)
def update_bar_country(region, country, category, segments, n_light, n_dark, n_blue):
    d = filtered(region, country, category, segments)
    ctry = (d.groupby("Country")[["Total_Sales", "Profit"]]
             .sum().nlargest(10, "Total_Sales").reset_index())
    # Determinar fondo segun cual boton fue presionado (mayor numero de clicks)
    clicks = {"btn-dark": n_dark or 0, "btn-blue": n_blue or 0, "btn-light": n_light or 0}
    triggered = max(clicks, key=clicks.get) if any(clicks.values()) else "btn-light"
    if triggered == "btn-dark":
        plot_bg, paper_bg, fc, gc = "#1E293B", "#1E293B", "#F8FAFC", "#334155"
    elif triggered == "btn-blue":
        plot_bg, paper_bg, fc, gc = "#EFF6FF", "#EFF6FF", COLORS["text"], "#BFDBFE"
    else:
        plot_bg, paper_bg, fc, gc = "rgba(0,0,0,0)", "rgba(0,0,0,0)", COLORS["text"], COLORS["border"]
    fig = go.Figure([
        go.Bar(name="Ventas Totales", x=ctry["Country"], y=ctry["Total_Sales"],
               marker_color=COLORS["primary"],
               hovertemplate="%{x}: %{y:$,.0f}<extra>Ventas</extra>"),
        go.Bar(name="Ganancias", x=ctry["Country"], y=ctry["Profit"],
               marker_color=COLORS["green"],
               hovertemplate="%{x}: %{y:$,.0f}<extra>Ganancias</extra>"),
    ])
    fig.update_layout(
        barmode="group",
        paper_bgcolor=paper_bg, plot_bgcolor=plot_bg,
        font=dict(family="'Segoe UI', system-ui, sans-serif", color=fc, size=11),
        margin=dict(l=10, r=10, t=10, b=90),
        xaxis=dict(showgrid=False, zeroline=False, tickangle=-40),
        yaxis=dict(showgrid=True, gridcolor=gc, zeroline=False, tickformat="$,.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
    )
    return fig

@app.callback(Output("graph-donut", "figure"), *FILTER_INPUTS)
def update_donut(region, country, category, segments):
    d = filtered(region, country, category, segments)
    cs = d.groupby("Product_Category")["Total_Sales"].sum().reset_index()
    fig = go.Figure(go.Pie(
        labels=cs["Product_Category"],
        values=cs["Total_Sales"],
        hole=0.60,
        marker_colors=[CAT_COLOR_MAP[c] for c in cs["Product_Category"]],
        marker=dict(line=dict(color="white", width=3)),
        # Solo mostrar porcentaje dentro del grafico, etiquetas en la leyenda
        textinfo="percent",
        textposition="inside",
        textfont=dict(size=14, color="white"),
        insidetextorientation="radial",
        hovertemplate="<b>%{label}</b><br>Ventas: %{value:$,.0f}<br>Participacion: %{percent}<extra></extra>",
        pull=[0.03, 0.03, 0.03, 0.03],  # separa ligeramente cada segmento
    ))
    # Texto central con total
    total = cs["Total_Sales"].sum()
    total_str = f"${total/1_000_000:.1f}M" if total >= 1_000_000 else f"${total/1_000:.0f}K"
    fig.update_layout(**base_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        # Leyenda vertical a la derecha con nombres completos y valores
        legend=dict(
            orientation="v",
            yanchor="middle", y=0.5,
            xanchor="left", x=1.02,
            font=dict(size=12),
            itemsizing="constant",
        ),
        annotations=[dict(
            text=f"<b>{total_str}</b><br><span style='font-size:11px'>Total Ventas</span>",
            x=0.5, y=0.5, font=dict(size=15, color=COLORS["primary"]),
            showarrow=False, align="center",
        )],
    ))
    return fig

@app.callback(Output("graph-scatter", "figure"), *FILTER_INPUTS)
def update_scatter(region, country, category, segments):
    d = filtered(region, country, category, segments)
    fig = px.scatter(
        d, x="Total_Sales", y="Profit",
        color="Product_Category",
        color_discrete_map=CAT_COLOR_MAP,
        opacity=0.60,
        size="Quantity", size_max=18,
        hover_data=["Country", "Product_Name", "Customer_Segment"],
        labels={"Total_Sales": "Ventas Totales ($)", "Profit": "Ganancia ($)", "Product_Category": "Categoría"},
    )
    fig.update_layout(**base_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, tickformat="$,.0f"),
        yaxis=dict(showgrid=True, gridcolor=COLORS["border"], zeroline=False, tickformat="$,.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
    ))
    return fig

if __name__ == "__main__":
    app.run(debug=True)