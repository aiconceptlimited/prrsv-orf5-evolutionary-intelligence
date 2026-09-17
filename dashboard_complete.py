import os
import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta
import numpy as np
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

pio.templates.default = 'plotly_dark'

# ================= DATABASE =================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "prrsv_genomics")

if not DB_USER or not DB_PASSWORD:
    raise RuntimeError(
        "Database configuration missing. "
        "Set DB_USER and DB_PASSWORD in the environment."
    )

DB_URI = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}/{DB_NAME}"
)
engine = create_engine(DB_URI)

# ================= CACHED LOADERS =================
def load_eii_index():
    try:
        return pd.read_sql("""
            SELECT id, eii_value, created_at
            FROM eii_index
            ORDER BY created_at
        """, engine)
    except Exception as e:
        print(f"Error loading eii_index: {e}")
        return pd.DataFrame()

def load_signals():
    try:
        return pd.read_sql("""
            SELECT signal_name, mean_value, created_at
            FROM eii_signals
            ORDER BY created_at DESC
        """, engine)
    except Exception as e:
        print(f"Error loading signals: {e}")
        return pd.DataFrame()

def load_site_eii():
    try:
        return pd.read_sql("""
            SELECT site, site_eii_v2, fel, meme, entropy, selection_score, glyco_frequency, conservation
            FROM site_eii
        """, engine)
    except Exception as e:
        print(f"Error loading site_eii: {e}")
        return pd.DataFrame()

def load_conservation():
    try:
        return pd.read_sql("""
            SELECT site, conservation, entropy
            FROM conservation_entropy
        """, engine)
    except Exception as e:
        print(f"Error loading conservation: {e}")
        return pd.DataFrame()

def load_glyco():
    try:
        return pd.read_sql("""
            SELECT site, glyco_frequency
            FROM glyco_sites
        """, engine)
    except Exception as e:
        print(f"Error loading glyco: {e}")
        return pd.DataFrame()

def load_fel_meme():
    try:
        return pd.read_sql("""
            SELECT site, fel, meme, site_eii_v2, entropy, selection_score, glyco_frequency
            FROM site_eii
        """, engine)
    except Exception as e:
        print(f"Error loading fel_meme: {e}")
        return pd.DataFrame()

def compute_overlap(df):
    if df.empty:
        return df
    df["fel_pos"] = df["fel"] > 0
    df["meme_pos"] = df["meme"] > 0
    df["both"] = df["fel_pos"] & df["meme_pos"]
    return df

def load_ehi():
    try:
        df = pd.read_sql("""
            SELECT site, fel, meme, site_eii_v2, entropy, selection_score, glyco_frequency
            FROM site_eii
        """, engine)
        
        if df.empty:
            return df
        
        for col in ["site_eii_v2","entropy","selection_score","glyco_frequency","fel","meme"]:
            if col in df.columns:
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    df[col] = (df[col] - min_val) / (max_val - min_val + 1e-9)
                else:
                    df[col] = 0
        
        df["EHI"] = (
            0.25 * df["site_eii_v2"] +
            0.20 * df["fel"] +
            0.20 * df["meme"] +
            0.15 * df["entropy"] +
            0.10 * df["glyco_frequency"] +
            0.10 * df["selection_score"]
        )
        
        q95 = df["EHI"].quantile(0.95)
        q80 = df["EHI"].quantile(0.80)
        q50 = df["EHI"].quantile(0.50)
        
        def classify(x):
            if x >= q95:
                return "🔥 Adaptive Hotspot"
            elif x >= q80:
                return "⚡ Emerging Variant Site"
            elif x >= q50:
                return "📈 Moderate Evolution"
            else:
                return "🔒 Conserved"
        
        df["classification"] = df["EHI"].apply(classify)
        return df
    except Exception as e:
        print(f"Error loading EHI: {e}")
        return pd.DataFrame()

def load_hotspots():
    try:
        return pd.read_sql("""
            SELECT
                site,
                site_eii_v2,
                entropy,
                selection_score,
                glyco_frequency
            FROM site_eii
            ORDER BY site_eii_v2 DESC
            LIMIT 25
        """, engine)
    except Exception as e:
        print(f"Error loading hotspots: {e}")
        return pd.DataFrame()

def calculate_trend(data, lookback_days=7):
    try:
        if data.empty or len(data) < 2:
            return 0.0
        cutoff = datetime.now() - timedelta(days=lookback_days)
        recent = data[data['created_at'] >= cutoff]
        if len(recent) < 2:
            recent = data.tail(2)
        if len(recent) >= 2:
            oldest = recent.iloc[0]['eii_value']
            newest = recent.iloc[-1]['eii_value']
            if oldest > 0:
                return round(((newest - oldest) / oldest) * 100, 1)
        return 0.0
    except:
        return 0.0

def get_real_metrics():
    """Get all real metrics from database"""
    try:
        site_eii_df = load_site_eii()
        eii_df = load_eii_index()
        signals_df = load_signals()
        
        if site_eii_df.empty or eii_df.empty:
            return {
                'current_eii': 0,
                'total_records': 0,
                'eii_trend': 0,
                'eii_change': 0,
                'dominant_signal': 'No Data',
                'trend_status': 'Unknown',
                'data_freshness': 'Unknown',
                'total_signal': 0,
                'signal_change': 0,
                'signal_data': [],
                'last_update': 'Unknown'
            }
        
        current_eii = eii_df['eii_value'].iloc[-1] if not eii_df.empty else 0
        eii_trend = calculate_trend(eii_df, 7)
        
        if len(eii_df) >= 2:
            prev_eii = eii_df['eii_value'].iloc[-2]
            eii_change = ((current_eii - prev_eii) / prev_eii * 100) if prev_eii > 0 else 0
        else:
            eii_change = 0
        
        if not signals_df.empty:
            latest_signals = signals_df.sort_values('created_at', ascending=False)
            latest_signals = latest_signals.drop_duplicates(subset=['signal_name'], keep='first')
            dominant = latest_signals.loc[latest_signals['mean_value'].idxmax(), 'signal_name']
            rename_map = {
                "SelectionPressure": "Selection Pressure",
                "PhylogeneticInstability": "Phylogenetic Instability",
                "GlycosylationDynamics": "Glycosylation Dynamics",
                "DistanceOutliers": "Distance Outliers",
                "EpitopeDrift": "Epitope Drift"
            }
            dominant_signal = rename_map.get(dominant, dominant)
        else:
            dominant_signal = "No Data"
        
        if eii_trend > 5:
            trend_status = "Increasing 📈"
        elif eii_trend < -5:
            trend_status = "Decreasing 📉"
        else:
            trend_status = "Stable ➡️"
        
        if not eii_df.empty:
            last_update = eii_df['created_at'].iloc[-1]
            if isinstance(last_update, str):
                last_update = pd.to_datetime(last_update)
            minutes_ago = (datetime.now() - last_update).total_seconds() / 60
            
            if minutes_ago < 1:
                data_freshness = "Just now"
            elif minutes_ago < 60:
                data_freshness = f"{int(minutes_ago)} min ago"
            elif minutes_ago < 1440:
                hours_ago = int(minutes_ago / 60)
                data_freshness = f"{hours_ago} hour{'s' if hours_ago > 1 else ''} ago"
            else:
                days_ago = int(minutes_ago / 1440)
                data_freshness = f"{days_ago} day{'s' if days_ago > 1 else ''} ago"
        else:
            data_freshness = "Unknown"
        
        if not signals_df.empty:
            latest_signals = signals_df.sort_values('created_at', ascending=False)
            latest_signals = latest_signals.drop_duplicates(subset=['signal_name'], keep='first')
            total_signal = latest_signals['mean_value'].sum()
        else:
            total_signal = 0
        
        signal_change = 0
        
        signal_data = []
        if not signals_df.empty:
            signal_colors = {
                "Selection Pressure": "#8B5CF6",
                "Phylogenetic Instability": "#3B82F6",
                "Glycosylation Dynamics": "#10B981",
                "Distance Outliers": "#F59E0B",
                "Epitope Drift": "#EF4444"
            }
            
            rename_map = {
                "SelectionPressure": "Selection Pressure",
                "PhylogeneticInstability": "Phylogenetic Instability",
                "GlycosylationDynamics": "Glycosylation Dynamics",
                "DistanceOutliers": "Distance Outliers",
                "EpitopeDrift": "Epitope Drift"
            }
            
            latest_signals = signals_df.sort_values('created_at', ascending=False)
            latest_signals = latest_signals.drop_duplicates(subset=['signal_name'], keep='first')
            
            for _, row in latest_signals.iterrows():
                name = rename_map.get(row['signal_name'], row['signal_name'])
                intensity = row['mean_value']
                if intensity > 0.3:
                    impact = "High"
                elif intensity > 0.15:
                    impact = "Medium"
                else:
                    impact = "Low"
                
                color = signal_colors.get(name, "#8B5CF6")
                signal_data.append({
                    'signal': name,
                    'intensity': round(intensity, 4),
                    'impact': impact,
                    'color': color
                })
            signal_data = sorted(signal_data, key=lambda x: x['intensity'], reverse=True)
        
        return {
            'current_eii': round(float(current_eii), 2),
            'total_records': len(site_eii_df),
            'eii_trend': round(eii_trend, 1),
            'eii_change': round(eii_change, 1),
            'dominant_signal': dominant_signal,
            'trend_status': trend_status,
            'data_freshness': data_freshness,
            'total_signal': round(total_signal, 3),
            'signal_change': signal_change,
            'signal_data': signal_data,
            'last_update': last_update.strftime("%Y-%m-%d %H:%M:%S") if not eii_df.empty else "Unknown"
        }
    except Exception as e:
        print(f"Error loading metrics: {e}")
        import traceback
        traceback.print_exc()
        return {
            'current_eii': 0,
            'total_records': 0,
            'eii_trend': 0,
            'eii_change': 0,
            'dominant_signal': 'Error',
            'trend_status': 'Error',
            'data_freshness': 'Error',
            'total_signal': 0,
            'signal_change': 0,
            'signal_data': [],
            'last_update': 'Error'
        }

# ================= APP =================
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True
)

app.title = "🧬 PRRSV ORF5 Evolution Platform"

# ================= COLOR SYSTEM =================
COLORS = {
    "bg_primary": "#0A0E1A", "bg_secondary": "#111827", "bg_card": "#1A2332",
    "border": "#2A3A52", "text_primary": "#F1F5F9", "text_secondary": "#94A3B8",
    "text_muted": "#64748B", "gradient_1": "#8B5CF6", "gradient_2": "#3B82F6",
    "gradient_3": "#10B981", "gradient_4": "#F59E0B", "gradient_5": "#EF4444",
    "glass": "rgba(255,255,255,0.03)", "glass_border": "rgba(255,255,255,0.06)"
}

SIGNAL_COLORS = {
    "Selection Pressure": "#8B5CF6",
    "Phylogenetic Instability": "#3B82F6",
    "Glycosylation Dynamics": "#10B981",
    "Distance Outliers": "#F59E0B",
    "Epitope Drift": "#EF4444"
}

# ================= HEADER =================
header = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.I(className="fas fa-dna", style={"fontSize": "28px", "color": COLORS["gradient_1"]}),
                    html.H1("PRRSV ORF5 Evolution", style={
                        "fontWeight": "700", "fontSize": "28px", "marginBottom": "4px",
                        "background": f"linear-gradient(135deg, {COLORS['gradient_1']}, {COLORS['gradient_2']})",
                        "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent", "display": "inline-block"
                    })
                ], style={"display": "flex", "alignItems": "center", "gap": "12px"})
            ], md=6),
            dbc.Col([
                html.Div([
                    html.I(className="fas fa-circle", style={"color": "#10B981", "fontSize": "10px"}),
                    html.Span("LIVE", style={"color": "#10B981", "fontSize": "12px", "fontWeight": "600", "marginLeft": "6px"}),
                    html.Span("•", style={"color": COLORS["text_muted"], "margin": "0 8px"}),
                    html.I(className="fas fa-sync-alt", style={"color": COLORS["gradient_3"], "fontSize": "10px"}),
                    html.Span("Auto-refresh: 60s", style={"color": COLORS["text_muted"], "fontSize": "12px", "marginLeft": "6px"}),
                    html.Span("•", style={"color": COLORS["text_muted"], "margin": "0 8px"}),
                    html.Span(id="header-timestamp", style={"color": COLORS["text_muted"], "fontSize": "11px"})
                ], style={"textAlign": "right"})
            ], md=6)
        ])
    ]),
    style={"background": f"linear-gradient(135deg, {COLORS['bg_secondary']}, {COLORS['bg_card']})", "border": f"1px solid {COLORS['border']}", "borderRadius": "16px", "marginBottom": "15px", "padding": "10px 20px"}
)

# ================= STATUS CARDS =================
def status_card_with_trend(icon, title, value_id, color, trend_id=None):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.I(className=f"fas fa-{icon}", style={"fontSize": "16px", "color": color})
                ], style={"marginBottom": "4px"}),
                html.Div(title, style={"color": COLORS["text_muted"], "fontSize": "10px", "fontWeight": "500", "textTransform": "uppercase"}),
                html.Div([
                    html.Span(id=value_id, children="Loading...", style={"color": color, "fontSize": "18px", "fontWeight": "700"}),
                    html.Span(id=trend_id, children="", style={"fontSize": "12px", "marginLeft": "6px", "fontWeight": "600"}) if trend_id else html.Span()
                ], style={"display": "flex", "alignItems": "center", "justifyContent": "center"})
            ], style={"textAlign": "center"})
        ]),
        style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "10px", "padding": "4px 8px"}
    )

# ================= TABS =================
tabs = dbc.Tabs(
    [
        dbc.Tab(
            label="📊 Executive",
            tab_id="tab-executive",
            children=[
                dbc.Row([
                    dbc.Col(status_card_with_trend("chart-line", "Current EII", "current-eii-value", COLORS["gradient_1"], "current-eii-trend"), md=2),
                    dbc.Col(status_card_with_trend("wave-square", "Dominant Signal", "dominant-signal-value", COLORS["gradient_4"], None), md=2),
                    dbc.Col(status_card_with_trend("arrow-trend-up", "Trend Status", "trend-status-value", COLORS["gradient_3"], None), md=2),
                    dbc.Col(status_card_with_trend("clock", "Data Freshness", "freshness-value", COLORS["text_muted"], None), md=2),
                    dbc.Col(status_card_with_trend("signal", "Total Signal", "total-signal-value", COLORS["gradient_2"], "total-signal-trend"), md=2),
                    dbc.Col(status_card_with_trend("database", "Records", "records-value", COLORS["gradient_1"], None), md=2),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("📈 Evolutionary Trajectory", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("EII evolution with 7-day moving average", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="eii-trend", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=12
                    )
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("🎯 Signal Composition", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Current evolutionary signal distribution", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="signals-donut", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=6
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("📊 Signal Intelligence Matrix", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Detailed evolutionary signal analysis with risk assessment", style={"color": "#94A3B8", "fontSize": "11px"}),
                                html.Div(id="signal-matrix")
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=6
                    )
                ])
            ]
        ),
        
        dbc.Tab(
            label="🧬 Sites",
            tab_id="tab-sites",
            children=[
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("🏆 Top 25 Evolutionary Sites", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Highest EII scores across ORF5 positions", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="sites", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=12
                    )
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("🧬 FEL Selection Landscape", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Fixed Effects Likelihood selection pressures", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="fel", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=6
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("🧬 MEME Selection Landscape", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Mixed Effects Model of Evolution", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="meme", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=6
                    )
                ]),
                
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("🔄 FEL-MEME Convergence", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Sites with both FEL and MEME positive selection", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="convergence", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=12
                    )
                ])
            ]
        ),
        
        dbc.Tab(
            label="📈 Evolution",
            tab_id="tab-evolution",
            children=[
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("🧬 Conservation Landscape", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Sequence conservation across ORF5", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="conservation", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=6
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("🔄 Entropy Landscape", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Shannon entropy diversity measure", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="entropy", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=6
                    )
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("🧬 Glycosylation Landscape", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("N-X-S/T glycosylation motif frequency", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="glyco", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=12
                    )
                ])
            ]
        ),
        
        dbc.Tab(
            label="🔥 Hotspots",
            tab_id="tab-hotspots",
            children=[
                dbc.Row([
                    dbc.Col([
                        html.H5("🔥 Evolutionary Hotspot Intelligence", style={"color": "white", "marginBottom": "15px", "fontSize": "16px"}),
                        dbc.Spinner(
                            dash_table.DataTable(
                                id="ehi-table",
                                page_size=15,
                                sort_action="native",
                                style_header={
                                    "backgroundColor": COLORS["bg_secondary"],
                                    "color": COLORS["text_primary"],
                                    "fontWeight": "600",
                                    "border": "none",
                                    "padding": "10px"
                                },
                                style_data={
                                    "backgroundColor": COLORS["bg_card"],
                                    "color": COLORS["text_secondary"],
                                    "border": "none",
                                    "padding": "8px"
                                },
                                style_data_conditional=[
                                    {"if": {"row_index": "odd"}, "backgroundColor": COLORS["bg_secondary"]},
                                    {"if": {"filter_query": "{classification} contains 'Adaptive'"}, "backgroundColor": "rgba(239, 68, 68, 0.15)", "color": COLORS["gradient_5"]},
                                    {"if": {"filter_query": "{classification} contains 'Emerging'"}, "backgroundColor": "rgba(245, 158, 11, 0.15)", "color": COLORS["gradient_4"]}
                                ],
                                style_cell={
                                    "textAlign": "center",
                                    "padding": "8px",
                                    "fontFamily": "Inter, sans-serif",
                                    "fontSize": "13px"
                                },
                                style_table={
                                    "overflowX": "auto",
                                    "borderRadius": "12px",
                                    "border": f"1px solid {COLORS['border']}"
                                }
                            ),
                            color=COLORS["gradient_1"]
                        )
                    ], md=12)
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        html.H5("📊 Top Hotspot Features", style={"color": "white", "marginBottom": "15px", "fontSize": "16px"}),
                        dbc.Spinner(
                            dash_table.DataTable(
                                id="hotspots-table",
                                page_size=15,
                                sort_action="native",
                                style_header={
                                    "backgroundColor": COLORS["bg_secondary"],
                                    "color": COLORS["text_primary"],
                                    "fontWeight": "600",
                                    "border": "none",
                                    "padding": "10px"
                                },
                                style_data={
                                    "backgroundColor": COLORS["bg_card"],
                                    "color": COLORS["text_secondary"],
                                    "border": "none",
                                    "padding": "8px"
                                },
                                style_data_conditional=[
                                    {"if": {"row_index": "odd"}, "backgroundColor": COLORS["bg_secondary"]}
                                ],
                                style_cell={
                                    "textAlign": "center",
                                    "padding": "8px",
                                    "fontFamily": "Inter, sans-serif",
                                    "fontSize": "13px"
                                },
                                style_table={
                                    "overflowX": "auto",
                                    "borderRadius": "12px",
                                    "border": f"1px solid {COLORS['border']}"
                                }
                            ),
                            color=COLORS["gradient_1"]
                        )
                    ], md=12)
                ])
            ]
        ),
        
        # ================= HISTORICAL TRENDS TAB =================
        dbc.Tab(
            label="📈 History",
            tab_id="tab-history",
            children=[
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("📊 EII Evolution Over Time", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Complete EII history with 30-day moving average", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="history-eii", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=12
                    )
                ], className="mb-3"),
                
                                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("📊 Signal Evolution Over Time", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("How each evolutionary signal has changed over time (REAL DATA)", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="history-signals", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=12
                    )
                ], className="mb-3"),


dbc.Row([
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H5("📊 Monthly EII Statistics", style={"color": "white", "marginBottom": "5px", "fontSize": "16px"}),
                                html.P("Average EII by month with min/max range", style={"color": "#94A3B8", "fontSize": "11px"}),
                                dcc.Graph(id="history-monthly", config={"displayModeBar": False})
                            ]),
                            style={"background": COLORS["glass"], "border": f"1px solid {COLORS['glass_border']}", "borderRadius": "16px"}
                        ),
                        md=12
                    )
                ])
            ]
        )
    ],
    active_tab="tab-executive",
    style={"marginBottom": "15px"}
)

# ================= LAYOUT =================
app.layout = dbc.Container([
    header,
    tabs,
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),
    html.Hr(style={"borderColor": COLORS["border"], "margin": "15px 0"}),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.I(className="fas fa-dna", style={"color": COLORS["gradient_1"], "fontSize": "14px"}),
                html.H6("PRRSV ORF5 Evolutionary Intelligence Platform", style={"color": COLORS["text_primary"], "fontWeight": "600", "margin": "0", "display": "inline-block", "marginLeft": "8px", "fontSize": "13px"})
            ], style={"display": "flex", "alignItems": "center"}),
            html.P("EII • FEL • MEME • Conservation • Glycosylation", style={"color": COLORS["text_muted"], "fontSize": "10px", "margin": "2px 0 0 0"}),
            html.Small("v3.0 • Real-time evolutionary monitoring • Data refreshes every 60 seconds", style={"color": COLORS["text_muted"], "fontSize": "9px"})
        ], md=8),
        dbc.Col([
            html.Div([
                html.A(html.I(className="fab fa-github", style={"fontSize": "14px"}), href="#", style={"color": COLORS["text_muted"], "marginRight": "10px"}),
                html.A(html.I(className="fab fa-twitter", style={"fontSize": "14px"}), href="#", style={"color": COLORS["text_muted"], "marginRight": "10px"}),
                html.A(html.I(className="fab fa-linkedin", style={"fontSize": "14px"}), href="#", style={"color": COLORS["text_muted"]})
            ], style={"textAlign": "right", "paddingTop": "5px"})
        ], md=4)
    ], style={"padding": "5px 0"})
], fluid=True, style={"padding": "10px 15px", "background": COLORS["bg_primary"], "minHeight": "100vh"})

# ================= CALLBACKS =================

@app.callback(
    [Output("current-eii-value", "children"),
     Output("current-eii-trend", "children"),
     Output("dominant-signal-value", "children"),
     Output("trend-status-value", "children"),
     Output("freshness-value", "children"),
     Output("total-signal-value", "children"),
     Output("total-signal-trend", "children"),
     Output("records-value", "children"),
     Output("header-timestamp", "children"),
     Output("signal-matrix", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_status(n_intervals):
    metrics = get_real_metrics()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    eii_trend = metrics['eii_change']
    if eii_trend > 0:
        eii_trend_text = f"↑ {eii_trend:.1f}%"
        eii_trend_color = "#10B981"
    elif eii_trend < 0:
        eii_trend_text = f"↓ {abs(eii_trend):.1f}%"
        eii_trend_color = "#EF4444"
    else:
        eii_trend_text = "→ 0%"
        eii_trend_color = "#94A3B8"
    
    signal_trend = metrics.get('signal_change', 0)
    if signal_trend > 0:
        signal_trend_text = f"↑ {signal_trend:.1f}%"
        signal_trend_color = "#10B981"
    elif signal_trend < 0:
        signal_trend_text = f"↓ {abs(signal_trend):.1f}%"
        signal_trend_color = "#EF4444"
    else:
        signal_trend_text = "→ 0%"
        signal_trend_color = "#94A3B8"
    
    matrix_rows = []
    if metrics['signal_data']:
        for sig in metrics['signal_data']:
            if sig['impact'] == "High":
                impact_color = "#EF4444"
                bg_color = "rgba(239, 68, 68, 0.15)"
            elif sig['impact'] == "Medium":
                impact_color = "#F59E0B"
                bg_color = "rgba(245, 158, 11, 0.15)"
            else:
                impact_color = "#10B981"
                bg_color = "rgba(16, 185, 129, 0.15)"
            
            matrix_rows.append(
                html.Tr([
                    html.Td([
                        html.Span(style={
                            "display": "inline-block",
                            "width": "10px",
                            "height": "10px",
                            "backgroundColor": sig['color'],
                            "borderRadius": "50%",
                            "marginRight": "8px"
                        }),
                        sig['signal']
                    ], style={"color": "white", "padding": "5px 8px", "borderBottom": f"1px solid {COLORS['border']}", "fontSize": "13px"}),
                    html.Td(str(sig['intensity']), style={"color": "#94A3B8", "padding": "5px 8px", "borderBottom": f"1px solid {COLORS['border']}", "fontSize": "13px"}),
                    html.Td(
                        html.Span(sig['impact'], style={
                            "background": bg_color,
                            "color": impact_color,
                            "padding": "2px 10px",
                            "borderRadius": "12px",
                            "fontSize": "11px",
                            "fontWeight": "600"
                        }),
                        style={"padding": "5px 8px", "borderBottom": f"1px solid {COLORS['border']}"}
                    )
                ])
            )
    
    signal_matrix = html.Table([
        html.Thead(html.Tr([
            html.Th("Evolutionary Signal", style={"color": "#94A3B8", "textAlign": "left", "padding": "5px 8px", "fontSize": "11px"}),
            html.Th("Intensity", style={"color": "#94A3B8", "textAlign": "left", "padding": "5px 8px", "fontSize": "11px"}),
            html.Th("Impact", style={"color": "#94A3B8", "textAlign": "left", "padding": "5px 8px", "fontSize": "11px"})
        ])),
        html.Tbody(matrix_rows)
    ], style={"width": "100%", "borderCollapse": "collapse"})
    
    return (
        str(metrics['current_eii']),
        html.Span(eii_trend_text, style={"color": eii_trend_color}),
        metrics['dominant_signal'],
        metrics['trend_status'],
        metrics['data_freshness'],
        str(metrics['total_signal']),
        html.Span(signal_trend_text, style={"color": signal_trend_color}),
        str(metrics['total_records']),
        f"Updated: {timestamp}",
        signal_matrix
    )

@app.callback(Output("eii-trend", "figure"), Input("interval-component", "n_intervals"))
def update_eii(_):
    df = load_eii_index()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_secondary"]),
            height=300,
            annotations=[{"text": "No EII Data Available", "x": 0.5, "y": 0.5, "showarrow": False}]
        )
        return fig
    
    fig = px.line(df, x="created_at", y="eii_value")
    fig.update_traces(line=dict(width=2.5, color=COLORS["gradient_1"]), hovertemplate="<b>Time:</b> %{x}<br><b>EII:</b> %{y:.2f}<extra></extra>")
    
    if not df.empty:
        mean_value = df["eii_value"].mean()
        fig.add_hline(y=mean_value, line_dash="dash", line_color=COLORS["gradient_3"], annotation_text=f"Mean: {mean_value:.2f}", annotation_font_color=COLORS["gradient_3"])
        df['ma_7'] = df['eii_value'].rolling(window=7).mean()
        fig.add_trace(go.Scatter(x=df['created_at'], y=df['ma_7'], mode='lines', name='7-Day MA', line=dict(color=COLORS["gradient_4"], width=2, dash='dot')))
        std_value = df["eii_value"].std()
        fig.add_hrect(y0=mean_value - std_value, y1=mean_value + std_value, fillcolor="rgba(16, 185, 129, 0.08)", line_width=0)
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_secondary"]),
        height=300,
        margin=dict(l=40, r=20, t=10, b=40),
        xaxis_title="Date",
        yaxis_title="EII Value",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

@app.callback(Output("signals-donut", "figure"), Input("interval-component", "n_intervals"))
def update_signals_donut(_):
    df = load_signals()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280,
            annotations=[{"text": "No Signal Data Available", "x": 0.5, "y": 0.5, "showarrow": False}]
        )
        return fig
    
    latest_signals = df.sort_values('created_at', ascending=False)
    latest_signals = latest_signals.drop_duplicates(subset=['signal_name'], keep='first')
    
    rename_map = {
        "SelectionPressure": "Selection Pressure",
        "PhylogeneticInstability": "Phylogenetic Instability",
        "GlycosylationDynamics": "Glycosylation Dynamics",
        "DistanceOutliers": "Distance Outliers",
        "EpitopeDrift": "Epitope Drift"
    }
    latest_signals["signal_name"] = latest_signals["signal_name"].replace(rename_map)
    latest_signals = latest_signals.sort_values("mean_value", ascending=False)
    
    total = latest_signals['mean_value'].sum()
    latest_signals['percentage'] = (latest_signals['mean_value'] / total * 100).round(1) if total > 0 else 0
    colors = [SIGNAL_COLORS.get(name, "#8B5CF6") for name in latest_signals['signal_name']]
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=latest_signals['signal_name'],
        values=latest_signals['mean_value'],
        hole=0.4,
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text_primary"]),
        marker=dict(colors=colors, line=dict(color=COLORS["bg_primary"], width=2)),
        hoverinfo="label+value+percent",
        hovertemplate="<b>%{label}</b><br>Strength: %{value:.3f}<br>Percentage: %{percent}<extra></extra>",
        showlegend=False
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=15, r=15, t=10, b=15),
        annotations=[dict(text=f"<b>Total</b><br><span style='font-size:16px;color:#F1F5F9;'>{total:.3f}</span>", x=0.5, y=0.5, showarrow=False, font=dict(size=12, color="#94A3B8"), align="center")]
    )
    return fig

def style_chart(fig, height=280):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_secondary"]),
        height=height,
        margin=dict(l=40, r=20, t=10, b=40),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False, showline=True, linewidth=1, linecolor=COLORS["border"])
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False, showline=True, linewidth=1, linecolor=COLORS["border"])
    return fig

@app.callback(Output("sites", "figure"), Input("interval-component", "n_intervals"))
def update_sites(_):
    df = load_site_eii()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(height=280, annotations=[{"text": "No Data", "x": 0.5, "y": 0.5, "showarrow": False}])
        return style_chart(fig)
    
    top_df = df.nlargest(25, "site_eii_v2")
    fig = px.bar(top_df, x="site", y="site_eii_v2", color="site_eii_v2", color_continuous_scale="blues")
    fig.update_traces(hovertemplate="<b>Site %{x}</b><br>EII: %{y:.3f}<extra></extra>")
    fig.add_hline(y=0.5, line_dash="dash", line_color=COLORS["gradient_4"], annotation_text="🔥 Hotspot Threshold", annotation_font_color=COLORS["gradient_4"])
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Amino Acid Position", yaxis_title="EII Score")
    return style_chart(fig)

@app.callback(Output("fel", "figure"), Input("interval-component", "n_intervals"))
def update_fel(_):
    df = load_site_eii()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(height=280, annotations=[{"text": "No Data", "x": 0.5, "y": 0.5, "showarrow": False}])
        return style_chart(fig)
    fig = px.bar(df, x="site", y="fel", color="fel", color_continuous_scale="plasma")
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Amino Acid Position", yaxis_title="FEL Score")
    return style_chart(fig)

@app.callback(Output("meme", "figure"), Input("interval-component", "n_intervals"))
def update_meme(_):
    df = load_site_eii()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(height=280, annotations=[{"text": "No Data", "x": 0.5, "y": 0.5, "showarrow": False}])
        return style_chart(fig)
    fig = px.bar(df, x="site", y="meme", color="meme", color_continuous_scale="plasma")
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Amino Acid Position", yaxis_title="MEME Score")
    return style_chart(fig)

@app.callback(Output("convergence", "figure"), Input("interval-component", "n_intervals"))
def update_convergence(_):
    df = load_fel_meme()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(height=280, annotations=[{"text": "No Data", "x": 0.5, "y": 0.5, "showarrow": False}])
        return style_chart(fig)
    df = compute_overlap(df)
    fig = px.scatter(df, x="fel", y="meme", color="both", color_discrete_map={True: COLORS["gradient_3"], False: COLORS["gradient_5"]}, hover_data=["site"])
    fig.update_traces(marker=dict(size=8, opacity=0.8), hovertemplate="<b>Site %{customdata[0]}</b><br>FEL: %{x:.3f}<br>MEME: %{y:.3f}<extra></extra>")
    fig.update_layout(xaxis_title="FEL Score", yaxis_title="MEME Score", legend_title="Both Positive")
    return style_chart(fig)

@app.callback(Output("conservation", "figure"), Input("interval-component", "n_intervals"))
def update_conservation(_):
    df = load_conservation()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(height=280, annotations=[{"text": "No Data", "x": 0.5, "y": 0.5, "showarrow": False}])
        return style_chart(fig)
    fig = px.line(df, x="site", y="conservation")
    fig.update_traces(line=dict(width=2.5, color=COLORS["gradient_2"]), fill="tozeroy", fillcolor="rgba(59, 130, 246, 0.1)", hovertemplate="<b>Site %{x}</b><br>Conservation: %{y:.2f}<extra></extra>")
    fig.update_layout(xaxis_title="Amino Acid Position", yaxis_title="Conservation Score")
    return style_chart(fig)

@app.callback(Output("entropy", "figure"), Input("interval-component", "n_intervals"))
def update_entropy(_):
    df = load_conservation()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(height=280, annotations=[{"text": "No Data", "x": 0.5, "y": 0.5, "showarrow": False}])
        return style_chart(fig)
    fig = px.line(df, x="site", y="entropy")
    fig.update_traces(line=dict(width=2.5, color=COLORS["gradient_4"]), fill="tozeroy", fillcolor="rgba(245, 158, 11, 0.1)", hovertemplate="<b>Site %{x}</b><br>Entropy: %{y:.2f}<extra></extra>")
    fig.add_hline(y=1.0, line_dash="dash", line_color=COLORS["gradient_5"], annotation_text="High Diversity Threshold", annotation_font_color=COLORS["gradient_5"])
    fig.update_layout(xaxis_title="Amino Acid Position", yaxis_title="Entropy Score")
    return style_chart(fig)

@app.callback(Output("glyco", "figure"), Input("interval-component", "n_intervals"))
def update_glyco(_):
    df = load_glyco()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(height=280, annotations=[{"text": "No Data", "x": 0.5, "y": 0.5, "showarrow": False}])
        return style_chart(fig)
    fig = px.line(df, x="site", y="glyco_frequency")
    fig.update_traces(line=dict(width=2.5, color=COLORS["gradient_1"]), fill="tozeroy", fillcolor="rgba(139, 92, 246, 0.1)", hovertemplate="<b>Site %{x}</b><br>Glycosylation: %{y:.2f}<extra></extra>")
    fig.update_layout(xaxis_title="Amino Acid Position", yaxis_title="Glycosylation Frequency")
    return style_chart(fig)

@app.callback([Output("ehi-table", "data"), Output("ehi-table", "columns")], Input("interval-component", "n_intervals"))
def update_ehi_table(_):
    df = load_ehi()
    if df.empty:
        return [], []
    df = df.sort_values("EHI", ascending=False).head(25)
    return df.to_dict("records"), [{"name": c, "id": c} for c in df.columns]

@app.callback([Output("hotspots-table", "data"), Output("hotspots-table", "columns")], Input("interval-component", "n_intervals"))
def update_hotspots_table(_):
    df = load_hotspots()
    if df.empty:
        return [], []
    return df.to_dict("records"), [{"name": c, "id": c} for c in df.columns]

# ================= HISTORICAL CALLBACKS =================

@app.callback(Output("history-eii", "figure"), Input("interval-component", "n_intervals"))
def update_history_eii(_):
    df = load_eii_index()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No EII Data Available", height=350)
        return fig
    
    fig = px.line(df, x="created_at", y="eii_value", title=f"EII History ({len(df)} data points)")
    fig.update_traces(line=dict(width=2.5, color=COLORS["gradient_1"]))
    
    # Add 30-day moving average
    df['ma_30'] = df['eii_value'].rolling(window=30).mean()
    fig.add_trace(go.Scatter(
        x=df['created_at'], 
        y=df['ma_30'], 
        mode='lines', 
        name='30-Day MA',
        line=dict(color=COLORS["gradient_4"], width=2, dash='dot')
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_secondary"]),
        height=350,
        xaxis_title="Date",
        yaxis_title="EII Value",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

@app.callback(Output("history-monthly", "figure"), Input("interval-component", "n_intervals"))
def update_history_monthly(_):
    df = load_eii_index()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No Data Available", height=350)
        return fig
    
    # Group by month
    df['month'] = df['created_at'].dt.to_period('M')
    monthly = df.groupby('month')['eii_value'].agg(['mean', 'min', 'max', 'std']).reset_index()
    monthly['month_str'] = monthly['month'].astype(str)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly['month_str'],
        y=monthly['mean'],
        mode='lines+markers',
        name='Average EII',
        line=dict(color=COLORS["gradient_1"], width=2.5),
        marker=dict(size=8)
    ))
    
    # Add min/max range
    fig.add_trace(go.Scatter(
        x=monthly['month_str'],
        y=monthly['max'],
        mode='lines',
        name='Max',
        line=dict(color=COLORS["gradient_5"], width=1, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=monthly['month_str'],
        y=monthly['min'],
        mode='lines',
        name='Min',
        line=dict(color=COLORS["gradient_3"], width=1, dash='dot'),
        fill='tonexty',
        fillcolor='rgba(139, 92, 246, 0.1)'
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_secondary"]),
        height=350,
        xaxis_title="Month",
        yaxis_title="EII Value",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig



@app.callback(Output("history-signals", "figure"), Input("interval-component", "n_intervals"))
def update_history_signals(_):
    # Load signal history from database
    df = pd.read_sql("""
        SELECT signal_name, mean_value, created_at
        FROM eii_signals
        ORDER BY created_at
    """, engine)
    
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No Signal History Data Available", height=350)
        return fig
    
    # Rename signals for display
    rename_map = {
        "SelectionPressure": "Selection Pressure",
        "PhylogeneticInstability": "Phylogenetic Instability",
        "GlycosylationDynamics": "Glycosylation Dynamics",
        "DistanceOutliers": "Distance Outliers",
        "EpitopeDrift": "Epitope Drift"
    }
    df["signal_name"] = df["signal_name"].replace(rename_map)
    
    # Create line chart
    fig = px.line(df, x="created_at", y="mean_value", color="signal_name",
                  title=f"Signal Evolution Over Time ({len(df)} data points)",
                  color_discrete_map=SIGNAL_COLORS)
    
    fig.update_traces(line=dict(width=2))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_secondary"]),
        height=350,
        xaxis_title="Date",
        yaxis_title="Signal Intensity",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧬 PRRSV ORF5 Evolutionary Intelligence Platform v3.0")
    print("="*70)
    print("📊 Database: prrsv_genomics")
    print("📍 Access the dashboard at:")
    print("   - http://127.0.0.1:8056 (Local)")
    print("   - Public dashboard: https://prrsv-orf5.aiconceptlimited.com.ng/")
    print("="*70)
    print("✅ Features:")
    print("   - Status cards with trend arrows (↑/↓)")
    print("   - Real-time data freshness (minutes/hours ago)")
    print("   - EII trend with 7-day moving average")
    print("   - Signal composition donut chart")
    print("   - Signal intelligence matrix with risk assessment")
    print("   - Historical trends (EII history, monthly statistics)")
    print("   - Auto-refresh every 60 seconds")
    print("="*70)
    print("⚠️  Press CTRL+C to stop the server")
    print("="*70 + "\n")
    
    app.run(
        host="0.0.0.0",
        port=8056,
        debug=False
    )
