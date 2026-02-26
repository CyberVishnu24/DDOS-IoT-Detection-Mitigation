#!/usr/bin/env python3
"""
Enhanced Security Dashboard with Real Mitigation Tracking
"""
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import psutil
import time
import os

# Configuration
LOG_FILE = "traffic_fast.csv"
MITIGATION_LOG = "mitigation_events.csv"
REFRESH_INTERVAL_MS = 1000
MAX_PPS_LIMIT = 5000
MAX_SYN_LIMIT = 50
TARGET_PORT = 8080

# History lists
cpu_history = [0] * 60
mem_history = [0] * 60
syn_history = [0] * 60
blocked_history = [0] * 60
attack_timeline = []

app = dash.Dash(__name__)

def get_traffic_data():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame({'pps': [0]*60, 'bps': [0]*60, 'syn': [0]*60, 'established': [0]*60, 'blocked': [0]*60})
    try:
        df = pd.read_csv(LOG_FILE)
        return df.iloc[-60:] if len(df) >= 60 else df
    except:
        return pd.DataFrame({'pps': [0]*60, 'bps': [0]*60, 'syn': [0]*60, 'established': [0]*60, 'blocked': [0]*60})

def get_mitigation_events():
    """Get recent mitigation events"""
    if not os.path.exists(MITIGATION_LOG):
        return []
    try:
        df = pd.read_csv(MITIGATION_LOG)
        return df.tail(5).to_dict('records')
    except:
        return []

def get_system_metrics():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    syn_count = 0
    
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr and conn.laddr.port == TARGET_PORT and conn.status == 'SYN_RECV':
                syn_count += 1
    except:
        pass
    
    cpu_history.append(cpu)
    mem_history.append(mem)
    syn_history.append(syn_count)
    
    return cpu, mem, syn_count

def get_stable_layout(title, y_label, y_range):
    return {
        'title': {'text': title, 'font': {'color': 'white', 'size': 14, 'family': 'monospace'}},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'margin': dict(l=40, r=20, t=40, b=30),
        'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
        'yaxis': {'gridcolor': '#333', 'zeroline': False, 'range': y_range, 'fixedrange': True},
        'font': {'color': 'white'},
        'showlegend': True,
        'legend': {'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
    }

# Layout
app.layout = html.Div(
    style={'backgroundColor': '#0a0e1a', 'minHeight': '100vh', 'padding': '20px', 'fontFamily': 'monospace'},
    children=[
        html.H1("🛡️ IoT DDoS DEFENSE COMMAND CENTER", 
                style={'textAlign': 'center', 'color': '#00ff88', 'letterSpacing': '3px', 'textShadow': '0 0 10px #00ff88'}),
        
        dcc.Interval(id='refresh-timer', interval=REFRESH_INTERVAL_MS, n_intervals=0),
        
        # Status Banner
        html.Div(id='status-banner', style={
            'textAlign': 'center', 'padding': '15px', 'marginBottom': '20px',
            'borderRadius': '10px', 'fontSize': '24px', 'fontWeight': 'bold'
        }),
        
        # Stats Cards
        html.Div(style={'display': 'flex', 'gap': '15px', 'marginBottom': '20px'}, children=[
            html.Div(id='card-pps', style={'flex': 1, 'backgroundColor': '#161b22', 'padding': '20px', 'borderRadius': '10px', 'borderLeft': '5px solid #00d4ff'}),
            html.Div(id='card-syn', style={'flex': 1, 'backgroundColor': '#161b22', 'padding': '20px', 'borderRadius': '10px', 'borderLeft': '5px solid #ffcc00'}),
            html.Div(id='card-blocked', style={'flex': 1, 'backgroundColor': '#161b22', 'padding': '20px', 'borderRadius': '10px', 'borderLeft': '5px solid #ff3e3e'}),
            html.Div(id='card-mitigation', style={'flex': 1, 'backgroundColor': '#161b22', 'padding': '20px', 'borderRadius': '10px', 'borderLeft': '5px solid #00ff88'}),
        ]),
        
        # Graphs
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div([dcc.Graph(id='traffic-graph', config={'displayModeBar': False})], 
                    style={'backgroundColor': '#161b22', 'borderRadius': '10px'}),
            html.Div([dcc.Graph(id='resource-graph', config={'displayModeBar': False})], 
                    style={'backgroundColor': '#161b22', 'borderRadius': '10px'}),
        ]),
        
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
            html.Div([dcc.Graph(id='syn-graph', config={'displayModeBar': False})], 
                    style={'backgroundColor': '#161b22', 'borderRadius': '10px'}),
            html.Div([dcc.Graph(id='blocked-graph', config={'displayModeBar': False})], 
                    style={'backgroundColor': '#161b22', 'borderRadius': '10px'}),
        ]),
        
        # Mitigation Events Log
        html.Div(id='events-log', style={
            'backgroundColor': '#161b22', 'padding': '20px', 'borderRadius': '10px',
            'marginTop': '20px', 'maxHeight': '200px', 'overflowY': 'auto'
        })
    ]
)

@app.callback(
    [Output('status-banner', 'children'), Output('status-banner', 'style'),
     Output('card-pps', 'children'), Output('card-syn', 'children'), 
     Output('card-blocked', 'children'), Output('card-mitigation', 'children'),
     Output('traffic-graph', 'figure'), Output('resource-graph', 'figure'),
     Output('syn-graph', 'figure'), Output('blocked-graph', 'figure'),
     Output('events-log', 'children')],
    [Input('refresh-timer', 'n_intervals')]
)
def update_ui(n):
    df = get_traffic_data()
    cpu, mem, syn = get_system_metrics()
    events = get_mitigation_events()
    
    curr_pps = int(df['pps'].iloc[-1]) if not df.empty else 0
    curr_blocked = int(df['blocked'].iloc[-1]) if not df.empty and 'blocked' in df.columns else 0
    total_blocked = int(df['blocked'].sum()) if not df.empty and 'blocked' in df.columns else 0
    
    blocked_history.append(curr_blocked)
    
    # Attack detection
    is_attack = curr_pps > (MAX_PPS_LIMIT * 0.7) or syn > MAX_SYN_LIMIT
    
    # Status Banner
    if is_attack:
        banner_text = "🚨 ATTACK DETECTED - MITIGATION ACTIVE"
        banner_style = {
            'textAlign': 'center', 'padding': '15px', 'marginBottom': '20px',
            'borderRadius': '10px', 'fontSize': '24px', 'fontWeight': 'bold',
            'backgroundColor': '#ff3e3e', 'color': 'black', 'animation': 'blink 1s infinite'
        }
    else:
        banner_text = "✅ SYSTEM SECURE - ALL TRAFFIC NORMAL"
        banner_style = {
            'textAlign': 'center', 'padding': '15px', 'marginBottom': '20px',
            'borderRadius': '10px', 'fontSize': '24px', 'fontWeight': 'bold',
            'backgroundColor': '#00ff88', 'color': 'black'
        }
    
    # Cards
    card_pps = [html.Small("PACKETS/SEC", style={'color': '#888'}), 
                html.H2(f"{curr_pps:,}", style={'color': '#00d4ff', 'margin': 0})]
    
    card_syn = [html.Small("HALF-OPEN (SYN)", style={'color': '#888'}), 
                html.H2(f"{syn}", style={'color': '#ffcc00', 'margin': 0})]
    
    card_blocked = [html.Small("BLOCKED NOW", style={'color': '#888'}), 
                    html.H2(f"{curr_blocked}", style={'color': '#ff3e3e', 'margin': 0})]
    
    card_mitigation = [html.Small("TOTAL BLOCKED", style={'color': '#888'}), 
                       html.H2(f"{total_blocked:,}", style={'color': '#00ff88', 'margin': 0})]
    
    # Traffic Graph
    fig_traffic = go.Figure()
    fig_traffic.add_trace(go.Scatter(
        y=df['pps'], name="PPS", 
        line=dict(color='#00d4ff', width=2), 
        fill='tozeroy', fillcolor='rgba(0, 212, 255, 0.1)'
    ))
    fig_traffic.add_hline(y=MAX_PPS_LIMIT*0.7, line_dash="dash", line_color="#ff3e3e", 
                          annotation_text="Alert Threshold")
    fig_traffic.update_layout(**get_stable_layout("Network Traffic", "PPS", [0, MAX_PPS_LIMIT]))
    
    # Resource Graph
    fig_res = go.Figure()
    fig_res.add_trace(go.Scatter(y=cpu_history[-60:], name="CPU %", line=dict(color='#ff3e3e', width=2)))
    fig_res.add_trace(go.Scatter(y=mem_history[-60:], name="RAM %", line=dict(color='#ffcc00', width=2)))
    fig_res.update_layout(**get_stable_layout("System Resources", "%", [0, 100]))
    
    # SYN Graph
    fig_syn = go.Figure()
    fig_syn.add_trace(go.Scatter(
        y=syn_history[-60:], name="SYN_RECV", 
        line=dict(color='#ffcc00', width=2, shape='spline'),
        fill='tozeroy', fillcolor='rgba(255, 204, 0, 0.1)'
    ))
    fig_syn.add_hline(y=MAX_SYN_LIMIT, line_dash="dash", line_color="#ff3e3e")
    fig_syn.update_layout(**get_stable_layout("SYN Flood Detection", "Count", [0, 100]))
    
    # Blocked Requests Graph
    fig_blocked = go.Figure()
    fig_blocked.add_trace(go.Scatter(
        y=blocked_history[-60:], name="Blocked", 
        line=dict(color='#ff3e3e', width=2),
        fill='tozeroy', fillcolor='rgba(255, 62, 62, 0.1)'
    ))
    fig_blocked.update_layout(**get_stable_layout("Mitigation Actions", "Blocked/s", [0, max(blocked_history[-60:] or [10]) + 10]))
    
    # Events Log
    events_content = [html.H4("🔒 Recent Mitigation Events", style={'color': '#00ff88', 'marginBottom': '10px'})]
    if events:
        for event in reversed(events):
            events_content.append(html.Div([
                html.Span(f"[{event['timestamp']}] ", style={'color': '#888'}),
                html.Span(f"{event['event_type']}: ", style={'color': '#00d4ff', 'fontWeight': 'bold'}),
                html.Span(f"{event['details']} → {event['action_taken']}", style={'color': '#fff'})
            ], style={'marginBottom': '5px', 'fontSize': '12px'}))
    else:
        events_content.append(html.P("No mitigation events recorded yet", style={'color': '#888', 'fontSize': '12px'}))
    
    return (banner_text, banner_style, card_pps, card_syn, card_blocked, card_mitigation,
            fig_traffic, fig_res, fig_syn, fig_blocked, events_content)

if __name__ == '__main__':
    print("🚀 Starting Enhanced Security Dashboard on http://localhost:8050")
    app.run(debug=False, host='0.0.0.0', port=8050)
