"""
Simplified dashboard with better Windows compatibility
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from ran_environment import RANEnvironment
from agent import RANOptimizationAgent

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go


# Create environment and agent
print("Loading environment and agent...")
env = RANEnvironment(num_cells=10)
state_size = env.observation_space.shape[0]
action_size = env.action_space.n
agent = RANOptimizationAgent(state_size, action_size)

# Load trained model if available
results_dir = '../results'
model_path = None
if os.path.exists(results_dir):
    models = [f for f in os.listdir(results_dir) if f.endswith('.pth')]
    if models:
        models.sort()
        model_path = os.path.join(results_dir, models[-1])
        print(f"Loading model: {model_path}")
        agent.load(model_path)
        is_trained = True
    else:
        is_trained = False
        print("No trained model found - using random actions")
else:
    is_trained = False
    print("No trained model found - using random actions")

# Live data storage
live_data = {
    'timestamps': [],
    'throughput': [],
    'drop_rate': [],
    'satisfaction': [],
    'power': []
}

# Create Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("RAN Network Optimizer - Live Dashboard",
            style={'textAlign': 'center', 'color': '#2c3e50', 'padding': '20px'}),

    html.Div([
        html.H3(f"Status: {'Trained Agent Active' if is_trained else 'Random Actions (No Model)'}",
                style={'textAlign': 'center', 'color': 'green' if is_trained else 'orange'})
    ]),

    # KPI Cards
    html.Div(id='kpi-cards', style={'textAlign': 'center', 'padding': '20px'}),

    # Graphs
    html.Div([
        html.Div([dcc.Graph(id='throughput-graph')], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='drop-rate-graph')], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='satisfaction-graph')], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='power-graph')], style={'width': '50%', 'display': 'inline-block'}),
    ]),

    # Auto-refresh every 2 seconds
    dcc.Interval(id='interval', interval=2000, n_intervals=0)
])


@app.callback(
    [Output('kpi-cards', 'children'),
     Output('throughput-graph', 'figure'),
     Output('drop-rate-graph', 'figure'),
     Output('satisfaction-graph', 'figure'),
     Output('power-graph', 'figure')],
    [Input('interval', 'n_intervals')]
)
def update_dashboard(n):
    global live_data

    # Reset environment on first call
    if n == 0:
        env.reset()

    # Get state and take action
    state = env._get_state()
    if is_trained:
        action = agent.act(state, training=False)
    else:
        action = env.action_space.sample()

    env.step(action)

    # Get statistics
    stats = env.get_network_stats()

    # Store data
    live_data['timestamps'].append(n)
    live_data['throughput'].append(stats['avg_throughput'])
    live_data['drop_rate'].append(stats['avg_drop_rate'] * 100)
    live_data['satisfaction'].append(stats['avg_satisfaction'])
    live_data['power'].append(stats['total_power'])

    # Keep only last 50 points
    if len(live_data['timestamps']) > 50:
        for key in live_data:
            live_data[key] = live_data[key][-50:]

    # KPI Cards
    kpi_cards = html.Div([
        html.Div([
            html.H2(f"{stats['avg_throughput']:.1f} Mbps", style={'color': '#3498db'}),
            html.P("Average Throughput")
        ], style={'display': 'inline-block', 'margin': '20px', 'padding': '20px',
                 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        html.Div([
            html.H2(f"{stats['avg_drop_rate']*100:.2f}%", style={'color': '#e74c3c'}),
            html.P("Drop Rate")
        ], style={'display': 'inline-block', 'margin': '20px', 'padding': '20px',
                 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        html.Div([
            html.H2(f"{stats['avg_satisfaction']:.1f}/100", style={'color': '#2ecc71'}),
            html.P("User Satisfaction")
        ], style={'display': 'inline-block', 'margin': '20px', 'padding': '20px',
                 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        html.Div([
            html.H2(f"{stats['total_power']:.0f}W", style={'color': '#f39c12'}),
            html.P("Total Power")
        ], style={'display': 'inline-block', 'margin': '20px', 'padding': '20px',
                 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    ])

    # Throughput graph
    throughput_fig = go.Figure()
    throughput_fig.add_trace(go.Scatter(
        x=live_data['timestamps'],
        y=live_data['throughput'],
        mode='lines+markers',
        name='Throughput',
        line=dict(color='#3498db', width=2)
    ))
    throughput_fig.update_layout(
        title='Average Throughput (Mbps)',
        xaxis_title='Time Step',
        yaxis_title='Mbps',
        height=300
    )

    # Drop rate graph
    drop_fig = go.Figure()
    drop_fig.add_trace(go.Scatter(
        x=live_data['timestamps'],
        y=live_data['drop_rate'],
        mode='lines+markers',
        name='Drop Rate',
        line=dict(color='#e74c3c', width=2),
        fill='tozeroy'
    ))
    drop_fig.update_layout(
        title='Call Drop Rate (%)',
        xaxis_title='Time Step',
        yaxis_title='%',
        height=300
    )

    # Satisfaction graph
    sat_fig = go.Figure()
    sat_fig.add_trace(go.Scatter(
        x=live_data['timestamps'],
        y=live_data['satisfaction'],
        mode='lines+markers',
        name='Satisfaction',
        line=dict(color='#2ecc71', width=2)
    ))
    sat_fig.update_layout(
        title='User Satisfaction',
        xaxis_title='Time Step',
        yaxis_title='Score (0-100)',
        height=300
    )

    # Power graph
    power_fig = go.Figure()
    power_fig.add_trace(go.Scatter(
        x=live_data['timestamps'],
        y=live_data['power'],
        mode='lines+markers',
        name='Power',
        line=dict(color='#f39c12', width=2)
    ))
    power_fig.update_layout(
        title='Total Power Consumption',
        xaxis_title='Time Step',
        yaxis_title='Watts',
        height=300
    )

    return kpi_cards, throughput_fig, drop_fig, sat_fig, power_fig


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting RAN Optimizer Dashboard")
    print("="*60)
    print("\nDashboard will open in your browser automatically...")
    print("\nIf it doesn't open, go to one of these URLs:")
    print("  http://localhost:8050")
    print("  http://127.0.0.1:8050")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")

    # Run with settings optimized for Windows
    app.run(
        debug=False,
        host='127.0.0.1',  # Only localhost
        port=8050,
        use_reloader=False  # Disable reloader for Windows
    )
