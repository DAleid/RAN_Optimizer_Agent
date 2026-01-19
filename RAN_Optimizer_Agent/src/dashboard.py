"""
Interactive dashboard for monitoring and analyzing agent performance
Uses Dash and Plotly to create a web interface
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
import json

# Dash and Plotly
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px

# Add path
sys.path.append(os.path.dirname(__file__))

from ran_environment import RANEnvironment
from agent import RANOptimizationAgent


class RANDashboard:
    """Dashboard for network monitoring"""

    def __init__(self, model_path=None):
        """
        Args:
            model_path: Path to trained model (optional)
        """

        # Create environment and agent
        self.env = RANEnvironment(num_cells=10)
        state_size = self.env.observation_space.shape[0]
        action_size = self.env.action_space.n
        self.agent = RANOptimizationAgent(state_size, action_size)

        # Load model if it exists
        if model_path and os.path.exists(model_path):
            self.agent.load(model_path)
            self.is_trained = True
        else:
            self.is_trained = False

        # Live data
        self.live_data = {
            'timestamps': [],
            'avg_throughput': [],
            'avg_drop_rate': [],
            'avg_satisfaction': [],
            'total_power': []
        }

        # Create app
        self.app = dash.Dash(__name__)
        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self):
        """Setup dashboard layout"""

        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("RAN Network Optimizer Dashboard",
                       style={'textAlign': 'center', 'color': '#2c3e50'}),
                html.P("Real-time monitoring and analysis of intelligent agent performance",
                      style={'textAlign': 'center', 'color': '#7f8c8d'})
            ], style={'padding': '20px', 'backgroundColor': '#ecf0f1'}),

            # Status
            html.Div([
                html.Div([
                    html.H4("System Status"),
                    html.P(f"Agent: {'Trained OK' if self.is_trained else 'Not Trained WARNING'}"),
                    html.P(f"Number of Cells: {self.env.num_cells}")
                ], style={'padding': '20px', 'backgroundColor': 'white',
                         'borderRadius': '10px', 'margin': '10px'}),
            ]),

            # Key Performance Indicators
            html.Div([
                html.H3("Key Performance Indicators", style={'textAlign': 'center'}),
                html.Div(id='kpi-cards', children=[])
            ], style={'padding': '20px'}),

            # Charts
            html.Div([
                # Performance over time
                html.Div([
                    dcc.Graph(id='live-throughput-graph')
                ], style={'width': '50%', 'display': 'inline-block'}),

                html.Div([
                    dcc.Graph(id='live-drop-rate-graph')
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),

            html.Div([
                # User satisfaction
                html.Div([
                    dcc.Graph(id='satisfaction-gauge')
                ], style={'width': '50%', 'display': 'inline-block'}),

                # Power consumption
                html.Div([
                    dcc.Graph(id='power-bar-chart')
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),

            # Cell details table
            html.Div([
                html.H3("Cell Details", style={'textAlign': 'center'}),
                html.Div(id='cells-table')
            ], style={'padding': '20px'}),

            # Auto-refresh
            dcc.Interval(
                id='interval-component',
                interval=2*1000,  # Update every 2 seconds
                n_intervals=0
            )
        ])

    def _setup_callbacks(self):
        """Setup interactions"""

        @self.app.callback(
            [Output('kpi-cards', 'children'),
             Output('live-throughput-graph', 'figure'),
             Output('live-drop-rate-graph', 'figure'),
             Output('satisfaction-gauge', 'figure'),
             Output('power-bar-chart', 'figure'),
             Output('cells-table', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_dashboard(n):
            """Update dashboard"""

            # Execute step in environment
            if n == 0:
                self.env.reset()

            state = self.env._get_state()

            if self.is_trained:
                action = self.agent.act(state, training=False)
            else:
                action = self.env.action_space.sample()

            self.env.step(action)

            # Get statistics
            stats = self.env.get_network_stats()

            # Save live data
            self.live_data['timestamps'].append(datetime.now())
            self.live_data['avg_throughput'].append(stats['avg_throughput'])
            self.live_data['avg_drop_rate'].append(stats['avg_drop_rate'] * 100)
            self.live_data['avg_satisfaction'].append(stats['avg_satisfaction'])
            self.live_data['total_power'].append(stats['total_power'])

            # Keep only last 50 points
            for key in self.live_data:
                if len(self.live_data[key]) > 50:
                    self.live_data[key] = self.live_data[key][-50:]

            # 1. KPI cards
            kpi_cards = self._create_kpi_cards(stats)

            # 2. Throughput graph
            throughput_fig = go.Figure()
            throughput_fig.add_trace(go.Scatter(
                x=list(range(len(self.live_data['avg_throughput']))),
                y=self.live_data['avg_throughput'],
                mode='lines+markers',
                name='Throughput',
                line=dict(color='#3498db', width=2)
            ))
            throughput_fig.update_layout(
                title='Average Throughput (Mbps)',
                xaxis_title='Time',
                yaxis_title='Mbps',
                height=300
            )

            # 3. Drop rate graph
            drop_rate_fig = go.Figure()
            drop_rate_fig.add_trace(go.Scatter(
                x=list(range(len(self.live_data['avg_drop_rate']))),
                y=self.live_data['avg_drop_rate'],
                mode='lines+markers',
                name='Drop Rate',
                line=dict(color='#e74c3c', width=2),
                fill='tozeroy'
            ))
            drop_rate_fig.update_layout(
                title='Average Call Drop Rate (%)',
                xaxis_title='Time',
                yaxis_title='%',
                height=300
            )

            # 4. Satisfaction gauge
            satisfaction_fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=stats['avg_satisfaction'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "User Satisfaction"},
                delta={'reference': 70},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "yellow"},
                        {'range': [75, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            satisfaction_fig.update_layout(height=300)

            # 5. Power consumption by cell
            cell_ids = [f"Cell {c['id']}" for c in self.env.cells[:5]]
            power_values = [c['power_consumption'] for c in self.env.cells[:5]]

            power_fig = go.Figure(data=[
                go.Bar(
                    x=cell_ids,
                    y=power_values,
                    marker_color='#f39c12'
                )
            ])
            power_fig.update_layout(
                title='Power Consumption (First 5 Cells)',
                xaxis_title='Cell',
                yaxis_title='Watts',
                height=300
            )

            # 6. Cell details table
            cells_table = self._create_cells_table()

            return kpi_cards, throughput_fig, drop_rate_fig, satisfaction_fig, power_fig, cells_table

    def _create_kpi_cards(self, stats):
        """Create KPI cards"""

        cards = html.Div([
            # Throughput
            html.Div([
                html.H2(f"{stats['avg_throughput']:.1f}", style={'color': '#3498db'}),
                html.P("Mbps", style={'fontSize': '12px'}),
                html.P("Avg Throughput", style={'fontSize': '14px'})
            ], style={
                'padding': '20px',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'display': 'inline-block',
                'width': '200px'
            }),

            # Drop rate
            html.Div([
                html.H2(f"{stats['avg_drop_rate']*100:.2f}%", style={'color': '#e74c3c'}),
                html.P("Drop Rate", style={'fontSize': '12px'}),
                html.P("Call Drops", style={'fontSize': '14px'})
            ], style={
                'padding': '20px',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'display': 'inline-block',
                'width': '200px'
            }),

            # Satisfaction
            html.Div([
                html.H2(f"{stats['avg_satisfaction']:.1f}", style={'color': '#2ecc71'}),
                html.P("out of 100", style={'fontSize': '12px'}),
                html.P("User Satisfaction", style={'fontSize': '14px'})
            ], style={
                'padding': '20px',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'display': 'inline-block',
                'width': '200px'
            }),

            # Power
            html.Div([
                html.H2(f"{stats['total_power']:.0f}", style={'color': '#f39c12'}),
                html.P("Watts", style={'fontSize': '12px'}),
                html.P("Power Consumption", style={'fontSize': '14px'})
            ], style={
                'padding': '20px',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'display': 'inline-block',
                'width': '200px'
            }),
        ], style={'textAlign': 'center'})

        return cards

    def _create_cells_table(self):
        """Create table with cell details"""

        # Table data
        data = []
        for cell in self.env.cells[:5]:  # First 5 cells
            satisfaction = self.env._calculate_satisfaction(cell)
            data.append({
                'Cell': f"Cell {cell['id']}",
                'Users': cell['num_users'],
                'Throughput (Mbps)': f"{cell['throughput']:.1f}",
                'Drop Rate (%)': f"{cell['drop_rate']*100:.2f}",
                'Power (dBm)': f"{cell['tx_power']:.1f}",
                'Antenna Tilt': f"{cell['antenna_tilt']:.1f} deg",
                'Satisfaction': f"{satisfaction:.0f}/100"
            })

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Create HTML table
        table = html.Table([
            html.Thead(
                html.Tr([html.Th(col) for col in df.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(df.iloc[i][col]) for col in df.columns
                ]) for i in range(len(df))
            ])
        ], style={
            'width': '100%',
            'textAlign': 'center',
            'backgroundColor': 'white',
            'borderRadius': '10px',
            'padding': '10px'
        })

        return table

    def run(self, port=8050):
        """Run dashboard"""
        print(f"\nStarting dashboard...")
        print(f"Open browser at: http://localhost:{port}")
        print("Press Ctrl+C to stop")
        self.app.run(debug=False, port=port)


def main():
    """Main program"""

    # Search for last trained model
    results_dir = '../results'
    model_path = None

    if os.path.exists(results_dir):
        models = [f for f in os.listdir(results_dir) if f.endswith('.pth')]
        if models:
            # Select last model
            models.sort()
            model_path = os.path.join(results_dir, models[-1])
            print(f"Found model: {model_path}")

    # Create and run dashboard
    dashboard = RANDashboard(model_path=model_path)
    dashboard.run()


if __name__ == "__main__":
    main()
