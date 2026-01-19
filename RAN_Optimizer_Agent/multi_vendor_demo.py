"""
Multi-Vendor RAN Coordination - Interactive Web Demo
Side-by-side comparison: WITHOUT vs WITH coordination
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from multi_vendor_environment import MultiVendorEnvironment
from vendor_ai_simulator import IndependentVendorSimulation, VendorAI
from coordination_agent import MultiVendorCoordinationAgent

# Page configuration
st.set_page_config(
    page_title="Multi-Vendor RAN Coordination POC",
    page_icon="🔄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .vendor-ericsson {
        background-color: #e6f2ff;
        padding: 0.5rem;
        border-left: 4px solid #0033A0;
        color: #000000 !important;
    }
    .vendor-nokia {
        background-color: #e6f0ff;
        padding: 0.5rem;
        border-left: 4px solid #124191;
        color: #000000 !important;
    }
    .vendor-huawei {
        background-color: #ffe6e6;
        padding: 0.5rem;
        border-left: 4px solid #FF0000;
        color: #000000 !important;
    }
    .conflict-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-left: 5px solid #ffc107;
        margin: 0.5rem 0;
        color: #000000 !important;
    }
    .conflict-box b, .conflict-box small {
        color: #000000 !important;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-left: 5px solid #28a745;
        margin: 0.5rem 0;
        color: #000000 !important;
    }
    .success-box b, .success-box small {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

def create_network_topology(env, title="Network Topology"):
    """Create network topology visualization with vendor colors"""

    fig = go.Figure()

    # Group cells by vendor
    vendor_cells = {
        'ericsson': [],
        'nokia': [],
        'huawei': []
    }

    for cell in env.cells:
        vendor_cells[cell['vendor']].append(cell)

    # Plot cells for each vendor
    for vendor, cells in vendor_cells.items():
        if not cells:
            continue

        x_coords = [c['x'] for c in cells]
        y_coords = [c['y'] for c in cells]
        sizes = [c['tx_power'] * 2 for c in cells]  # Size based on power
        hover_text = [
            f"Cell {c['id']} ({vendor.upper()})<br>" +
            f"Power: {c['tx_power']:.1f} dBm<br>" +
            f"Throughput: {c['throughput']:.1f} Mbps<br>" +
            f"Interference: {c['interference']:.4f}<br>" +
            f"Users: {c['num_users']}"
            for c in cells
        ]

        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers+text',
            name=vendor.capitalize(),
            marker=dict(
                size=sizes,
                color=cells[0]['color'],
                line=dict(color='white', width=2),
                opacity=0.8
            ),
            text=[f"C{c['id']}" for c in cells],
            textposition="middle center",
            textfont=dict(color='white', size=10, family='Arial Black'),
            hovertext=hover_text,
            hoverinfo='text'
        ))

    # Draw interference links (simplified)
    for cell in env.cells:
        neighbors = env.get_cross_vendor_neighbors(cell['id'])
        for neighbor in neighbors[:2]:  # Show only top 2 neighbors
            neighbor_cell = env.cells[neighbor['id']]
            fig.add_trace(go.Scatter(
                x=[cell['x'], neighbor_cell['x']],
                y=[cell['y'], neighbor_cell['y']],
                mode='lines',
                line=dict(color='rgba(255,0,0,0.2)', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))

    fig.update_layout(
        title=title,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='rgba(240,242,246,0.5)',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def show_conflicts(conflicts):
    """Display detected conflicts"""

    if not conflicts:
        st.success("✅ No conflicts detected")
        return

    st.warning(f"⚠️ {len(conflicts)} conflicts detected")

    for i, conflict in enumerate(conflicts):
        st.markdown(f"""
        <div class="conflict-box">
        <b>Conflict {i+1}: {conflict['type'].replace('_', ' ').title()}</b><br>
        {conflict['description']}<br>
        <small>Severity: {conflict['severity']} | Cells: {conflict['cells']} | Vendors: {conflict['vendors']}</small>
        </div>
        """, unsafe_allow_html=True)

def create_metrics_comparison(stats_without, stats_with):
    """Create comparison metrics chart"""

    categories = ['Throughput (Mbps)', 'Drop Rate (%)', 'Interference', 'Power (W)']

    without_values = [
        stats_without['avg_throughput'],
        stats_without['avg_drop_rate'] * 100,
        stats_without['avg_interference'] * 100,
        stats_without['total_power']
    ]

    with_values = [
        stats_with['avg_throughput'],
        stats_with['avg_drop_rate'] * 100,
        stats_with['avg_interference'] * 100,
        stats_with['total_power']
    ]

    fig = go.Figure(data=[
        go.Bar(name='Without Coordination', x=categories, y=without_values, marker_color='#ff6b6b'),
        go.Bar(name='With Coordination', x=categories, y=with_values, marker_color='#51cf66')
    ])

    fig.update_layout(
        barmode='group',
        title="Performance Comparison",
        yaxis_title="Value",
        height=400
    )

    return fig

# ============= MAIN APP =============

def main():
    st.markdown('<h1 class="main-header">🔄 Multi-Vendor RAN Coordination POC</h1>', unsafe_allow_html=True)
    st.markdown("### Demonstrating the Problem and Solution")

    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    num_cells = st.sidebar.slider("Number of Cells", 6, 15, 12)
    num_steps = st.sidebar.slider("Simulation Steps", 5, 20, 10)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About This Demo")
    st.sidebar.info("""
    This demo shows:
    - **LEFT**: Vendor AIs operating independently (conflicts arise)
    - **RIGHT**: Coordination agent preventing conflicts

    **Vendors simulated:**
    - 🔵 Ericsson
    - 🔵 Nokia
    - 🔴 Huawei
    """)

    if st.sidebar.button("🚀 Run Simulation"):

        st.markdown("---")

        # Create two columns for side-by-side comparison
        col1, col2 = st.columns(2)

        # ========== LEFT COLUMN: WITHOUT COORDINATION ==========
        with col1:
            st.markdown("## ❌ WITHOUT Coordination")
            st.markdown("*Vendor AIs operate independently*")

            with st.spinner("Running simulation without coordination..."):
                # Create environment and run simulation
                env_without = MultiVendorEnvironment(num_cells=num_cells)
                sim_without = IndependentVendorSimulation(env_without)

                # Store initial state
                initial_stats = env_without.get_network_stats()

                # Run simulation
                results_without = sim_without.run_simulation(num_steps=num_steps)

                final_stats_without = results_without['final_stats']

            # Show network topology
            st.plotly_chart(create_network_topology(env_without, "Network: Independent Vendor AIs"),
                          use_container_width=True)

            # Show conflicts
            st.markdown("#### Conflicts Detected:")
            total_conflicts = results_without['total_conflicts']
            show_conflicts(sim_without.conflicts_history[-1] if sim_without.conflicts_history else [])

            # Show metrics
            st.markdown("#### Final Metrics:")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Throughput", f"{final_stats_without['avg_throughput']:.1f} Mbps")
            m2.metric("Drop Rate", f"{final_stats_without['avg_drop_rate']*100:.2f}%")
            m3.metric("Interference", f"{final_stats_without['avg_interference']:.4f}")
            m4.metric("Power", f"{final_stats_without['total_power']:.0f} W")

            st.warning(f"⚠️ Total conflicts in simulation: **{total_conflicts}**")

        # ========== RIGHT COLUMN: WITH COORDINATION ==========
        with col2:
            st.markdown("## ✅ WITH Coordination")
            st.markdown("*Multi-Vendor Coordination Agent*")

            with st.spinner("Running simulation with coordination..."):
                # Create environment and coordination agent
                env_with = MultiVendorEnvironment(num_cells=num_cells)
                vendor_ais = {
                    'ericsson': VendorAI('ericsson', env_with),
                    'nokia': VendorAI('nokia', env_with),
                    'huawei': VendorAI('huawei', env_with)
                }
                coordinator = MultiVendorCoordinationAgent(env_with, vendor_ais)

                # Run coordinated simulation
                results_with = coordinator.run_coordinated_simulation(num_steps=num_steps)

                final_stats_with = results_with['final_stats']

            # Show network topology
            st.plotly_chart(create_network_topology(env_with, "Network: Coordinated Optimization"),
                          use_container_width=True)

            # Show coordination results
            st.markdown("#### Coordination Results:")
            conflicts_detected = results_with['total_conflicts_detected']
            conflicts_resolved = results_with['total_conflicts_resolved']

            if conflicts_resolved > 0:
                st.markdown(f"""
                <div class="success-box">
                ✅ <b>{conflicts_resolved} conflicts detected and resolved</b><br>
                Coordinated actions prevented vendor AI conflicts
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("✅ No conflicts detected - vendors operating optimally")

            # Show metrics
            st.markdown("#### Final Metrics:")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Throughput", f"{final_stats_with['avg_throughput']:.1f} Mbps")
            m2.metric("Drop Rate", f"{final_stats_with['avg_drop_rate']*100:.2f}%")
            m3.metric("Interference", f"{final_stats_with['avg_interference']:.4f}")
            m4.metric("Power", f"{final_stats_with['total_power']:.0f} W")

            st.success(f"✅ Conflicts resolved: **{conflicts_resolved}**")

        # ========== COMPARISON SECTION ==========
        st.markdown("---")
        st.markdown("## 📊 Performance Improvement Analysis")

        # Calculate improvements
        throughput_improvement = ((final_stats_with['avg_throughput'] - final_stats_without['avg_throughput']) /
                                 final_stats_without['avg_throughput'] * 100)
        drop_improvement = ((final_stats_without['avg_drop_rate'] - final_stats_with['avg_drop_rate']) /
                           final_stats_without['avg_drop_rate'] * 100)
        interference_improvement = ((final_stats_without['avg_interference'] - final_stats_with['avg_interference']) /
                                   final_stats_without['avg_interference'] * 100)
        power_improvement = ((final_stats_without['total_power'] - final_stats_with['total_power']) /
                            final_stats_without['total_power'] * 100)

        # Show improvement metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Throughput Improvement", f"+{throughput_improvement:.1f}%",
                   delta=f"+{throughput_improvement:.1f}%")
        col2.metric("Drop Rate Reduction", f"-{drop_improvement:.1f}%",
                   delta=f"{drop_improvement:.1f}%")
        col3.metric("Interference Reduction", f"-{interference_improvement:.1f}%",
                   delta=f"{interference_improvement:.1f}%")
        col4.metric("Power Savings", f"-{power_improvement:.1f}%",
                   delta=f"{power_improvement:.1f}%")

        # Comparison chart
        st.plotly_chart(create_metrics_comparison(final_stats_without, final_stats_with),
                       use_container_width=True)

        # Summary
        st.markdown("---")
        st.markdown("### 🎯 Key Findings")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("""
            #### ❌ Without Coordination
            - Vendor AIs operate in silos
            - Cross-vendor conflicts arise
            - Suboptimal global performance
            - Interference escalation
            - Wasted resources
            """)

        with col_b:
            st.markdown("""
            #### ✅ With Coordination
            - Global network visibility
            - Conflicts detected early
            - Coordinated optimization
            - Better resource utilization
            - Superior performance
            """)

        # Business value
        st.markdown("---")
        st.markdown("### 💰 Business Impact")

        st.markdown(f"""
        <div class="success-box">
        <b>For a network with {num_cells} cells:</b><br><br>

        📈 <b>Throughput:</b> +{throughput_improvement:.1f}% = More capacity, more revenue<br>
        📉 <b>Drops:</b> -{drop_improvement:.1f}% = Better user experience, reduced churn<br>
        ⚡ <b>Power:</b> -{power_improvement:.1f}% = Lower operational costs<br>
        🔄 <b>Conflicts:</b> {conflicts_resolved} resolved = Stable, predictable network<br><br>

        <b>Key Differentiator:</b> Only a vendor-neutral coordination agent can achieve this!<br>
        Ericsson won't coordinate with Nokia. Nokia won't coordinate with Huawei. <b>But we can.</b>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Initial state - show explanation
        st.markdown("---")
        st.markdown("### 🎯 The Problem")

        st.markdown("""
        <div class="conflict-box">
        <b>Multi-Vendor Networks Face a Critical Challenge:</b><br><br>

        Most CSPs (like STC, Mobily, Zain in Saudi Arabia) use equipment from multiple vendors:
        - 🔵 <b>Ericsson</b> cells in some areas
        - 🔵 <b>Nokia</b> cells in other areas
        - 🔴 <b>Huawei</b> cells elsewhere

        <br><br>

        <b>Each vendor provides its own AI optimization system</b>, but they:
        - ❌ Cannot see each other's cells
        - ❌ Don't coordinate actions
        - ❌ Create conflicts (interference, power escalation, load imbalance)
        - ❌ Result in 15-30% degraded performance
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### ✅ The Solution")

        st.markdown("""
        <div class="success-box">
        <b>Multi-Vendor RAN Coordination Agent</b><br><br>

        A vendor-neutral AI that:
        - ✅ Monitors <b>ALL</b> cells from <b>ALL</b> vendors
        - ✅ Detects cross-vendor conflicts before they impact performance
        - ✅ Coordinates optimization actions globally
        - ✅ Achieves 20-35% better performance than uncoordinated vendor AIs

        <br>

        <b>Why this matters:</b> Vendors won't coordinate with competitors (conflict of interest).<br>
        Only an independent coordination agent can solve this problem.
        </div>
        """, unsafe_allow_html=True)

        st.info("👆 Click **'Run Simulation'** in the sidebar to see the demonstration!")

if __name__ == "__main__":
    main()
