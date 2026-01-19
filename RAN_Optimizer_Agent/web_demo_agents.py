"""
AI Agents Web Demo for RAN Network Optimization
Multi-Agent System using CrewAI and Groq
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
import time
from datetime import datetime

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from src.ran_environment import RANEnvironment
from src.data_loader import NetworkDataLoader

# Page configuration
st.set_page_config(
    page_title="RAN Network Optimizer - AI Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
    }
    .agent-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .status-running {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-complete {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-error {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .thought-bubble {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #6c757d;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'crew' not in st.session_state:
    st.session_state.crew = None
if 'env' not in st.session_state:
    st.session_state.env = None
if 'optimization_result' not in st.session_state:
    st.session_state.optimization_result = None
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False


def create_agent_cards():
    """Display agent information cards"""
    agents_info = {
        'analyzer': {
            'name': 'Network Performance Analyst',
            'icon': '📊',
            'description': 'Analyzes KPIs, detects anomalies, identifies problem cells',
            'color': '#3498db'
        },
        'optimizer': {
            'name': 'RF Optimization Engineer',
            'icon': '⚡',
            'description': 'Recommends power, tilt, and handover adjustments',
            'color': '#e74c3c'
        },
        'validator': {
            'name': 'Quality Assurance Engineer',
            'icon': '✅',
            'description': 'Validates changes, checks conflicts, ensures safety',
            'color': '#2ecc71'
        },
        'coordinator': {
            'name': 'Network Operations Manager',
            'icon': '🎯',
            'description': 'Makes final decisions, prioritizes actions',
            'color': '#9b59b6'
        }
    }

    cols = st.columns(4)
    for i, (key, agent) in enumerate(agents_info.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {agent['color']} 0%, {agent['color']}99 100%);
                        padding: 1rem; border-radius: 10px; color: white; text-align: center; height: 180px;">
                <div style="font-size: 2rem;">{agent['icon']}</div>
                <div style="font-weight: bold; margin: 0.5rem 0;">{agent['name']}</div>
                <div style="font-size: 0.8rem; opacity: 0.9;">{agent['description']}</div>
            </div>
            """, unsafe_allow_html=True)


def create_network_topology(env):
    """Create network topology visualization"""
    if env is None or not env.cells:
        return None

    num_cells = len(env.cells)
    positions = []
    for i in range(num_cells):
        row = i // 4
        col = i % 4
        x = col * 1.5 + (row % 2) * 0.75
        y = row * 1.3
        positions.append((x, y))

    fig = go.Figure()

    # Cell colors based on satisfaction
    colors = [env._calculate_satisfaction(cell) for cell in env.cells]

    # Plot hexagonal coverage areas
    for i, (x, y) in enumerate(positions):
        hex_angles = np.linspace(0, 2*np.pi, 7)
        hex_x = x + 0.5 * np.cos(hex_angles)
        hex_y = y + 0.5 * np.sin(hex_angles)

        fig.add_trace(go.Scatter(
            x=hex_x, y=hex_y,
            fill='toself',
            fillcolor=f'rgba(102, 126, 234, {0.2 + colors[i]/200})',
            line=dict(color='rgb(102, 126, 234)', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Plot cell markers
    cell_types = [cell.get('cell_type', 'Unknown') for cell in env.cells]
    hover_text = [
        f"<b>Cell {cell['id']}</b> ({cell.get('cell_type', 'Unknown')})<br>" +
        f"Users: {cell['num_users']}<br>" +
        f"Throughput: {cell['throughput']:.1f} Mbps<br>" +
        f"Drop Rate: {cell['drop_rate']*100:.2f}%<br>" +
        f"TX Power: {cell['tx_power']:.1f} dBm<br>" +
        f"Satisfaction: {env._calculate_satisfaction(cell):.1f}/100"
        for cell in env.cells
    ]

    fig.add_trace(go.Scatter(
        x=[p[0] for p in positions],
        y=[p[1] for p in positions],
        mode='markers+text',
        marker=dict(
            size=40,
            color=colors,
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Satisfaction"),
            line=dict(color='white', width=2)
        ),
        text=[f"C{i}" for i in range(num_cells)],
        textposition="middle center",
        textfont=dict(color='white', size=10, family='Arial Black'),
        hovertext=hover_text,
        hoverinfo='text',
        showlegend=False
    ))

    fig.update_layout(
        title="Network Topology - Cell Performance Map",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='rgba(248, 249, 250, 0.5)',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig


def display_agent_output(agent_name: str, icon: str, output: str, status: str = "complete"):
    """Display agent output in a styled container"""
    status_class = f"status-{status}"
    st.markdown(f"""
    <div class="{status_class}">
        <strong>{icon} {agent_name}</strong>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"View {agent_name} Output", expanded=False):
        st.markdown(output)


def run_optimization_with_ui(crew, network_state):
    """Run optimization with real-time UI updates"""

    results = {
        'analysis': None,
        'optimization': None,
        'validation': None,
        'coordination': None,
        'success': True,
        'error': None
    }

    # Agent progress display
    progress_container = st.container()

    with progress_container:
        st.markdown("### 🤖 Agent Workflow Progress")

        # Step 1: Analyzer
        with st.status("📊 Network Performance Analyst analyzing...", expanded=True) as status:
            st.write("Analyzing network KPIs and identifying problem cells...")
            time.sleep(0.5)  # Simulate processing

            try:
                from agents.ran_tasks import create_analysis_task, format_network_state
                from crewai import Crew, Process

                analysis_task = create_analysis_task(crew.agents['analyzer'], network_state)
                analysis_crew = Crew(
                    agents=[crew.agents['analyzer']],
                    tasks=[analysis_task],
                    process=Process.sequential,
                    verbose=False
                )
                analysis_result = analysis_crew.kickoff()
                results['analysis'] = str(analysis_result)
                status.update(label="📊 Analysis Complete!", state="complete")
                st.success("Identified cells requiring optimization")
            except Exception as e:
                results['success'] = False
                results['error'] = str(e)
                status.update(label="📊 Analysis Failed", state="error")
                st.error(f"Error: {e}")
                return results

        # Step 2: Optimizer
        with st.status("⚡ RF Optimization Engineer planning...", expanded=True) as status:
            st.write("Calculating optimal parameter adjustments...")
            time.sleep(0.5)

            try:
                from agents.ran_tasks import create_optimization_task

                optimization_task = create_optimization_task(
                    crew.agents['optimizer'],
                    results['analysis'],
                    network_state
                )
                optimization_crew = Crew(
                    agents=[crew.agents['optimizer']],
                    tasks=[optimization_task],
                    process=Process.sequential,
                    verbose=False
                )
                optimization_result = optimization_crew.kickoff()
                results['optimization'] = str(optimization_result)
                status.update(label="⚡ Optimization Plan Ready!", state="complete")
                st.success("Generated parameter adjustment recommendations")
            except Exception as e:
                results['success'] = False
                results['error'] = str(e)
                status.update(label="⚡ Optimization Failed", state="error")
                st.error(f"Error: {e}")
                return results

        # Step 3: Validator
        with st.status("✅ Quality Assurance Engineer validating...", expanded=True) as status:
            st.write("Checking for conflicts and validating safety...")
            time.sleep(0.5)

            try:
                from agents.ran_tasks import create_validation_task

                validation_task = create_validation_task(
                    crew.agents['validator'],
                    results['optimization'],
                    network_state
                )
                validation_crew = Crew(
                    agents=[crew.agents['validator']],
                    tasks=[validation_task],
                    process=Process.sequential,
                    verbose=False
                )
                validation_result = validation_crew.kickoff()
                results['validation'] = str(validation_result)
                status.update(label="✅ Validation Complete!", state="complete")
                st.success("Changes validated and approved")
            except Exception as e:
                results['success'] = False
                results['error'] = str(e)
                status.update(label="✅ Validation Failed", state="error")
                st.error(f"Error: {e}")
                return results

        # Step 4: Coordinator
        with st.status("🎯 Network Operations Manager deciding...", expanded=True) as status:
            st.write("Making final decisions on approved changes...")
            time.sleep(0.5)

            try:
                from agents.ran_tasks import create_coordination_task, parse_final_actions

                coordination_task = create_coordination_task(
                    crew.agents['coordinator'],
                    results['analysis'],
                    results['optimization'],
                    results['validation']
                )
                coordination_crew = Crew(
                    agents=[crew.agents['coordinator']],
                    tasks=[coordination_task],
                    process=Process.sequential,
                    verbose=False
                )
                coordination_result = coordination_crew.kickoff()
                results['coordination'] = str(coordination_result)
                results['final_actions'] = parse_final_actions(str(coordination_result))
                status.update(label="🎯 Final Decision Made!", state="complete")
                st.success(f"Approved {len(results.get('final_actions', []))} optimization actions")
            except Exception as e:
                results['success'] = False
                results['error'] = str(e)
                status.update(label="🎯 Coordination Failed", state="error")
                st.error(f"Error: {e}")
                return results

    return results


# ============= MAIN APPLICATION =============

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Agents for RAN Network Optimization</h1>', unsafe_allow_html=True)
    st.markdown("### Multi-Agent System powered by CrewAI & Groq")

    # Sidebar
    st.sidebar.header("⚙️ Configuration")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Overview", "🔑 Setup API Key", "🎯 Run Optimization", "📊 Results Analysis"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Network Settings")
    num_cells = st.sidebar.slider("Number of Cells", 5, 15, 10)
    use_real_data = st.sidebar.checkbox("Use Real Data (CSV)", value=True)

    # ============= PAGE: OVERVIEW =============
    if page == "🏠 Overview":
        st.header("Multi-Agent Architecture")

        st.markdown("""
        This system uses **4 specialized AI agents** working together to optimize
        your RAN network. Each agent has a specific role and expertise.
        """)

        create_agent_cards()

        st.markdown("---")

        # Workflow diagram
        st.markdown("### 🔄 Optimization Workflow")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
            **Step 1: Analysis**
            ```
            📊 Analyzer Agent
            ├─ Collect metrics
            ├─ Detect anomalies
            └─ Identify issues
            ```
            """)

        with col2:
            st.markdown("""
            **Step 2: Optimization**
            ```
            ⚡ Optimizer Agent
            ├─ Calculate changes
            ├─ Consider trade-offs
            └─ Recommend actions
            ```
            """)

        with col3:
            st.markdown("""
            **Step 3: Validation**
            ```
            ✅ Validator Agent
            ├─ Check safety
            ├─ Detect conflicts
            └─ Approve/Reject
            ```
            """)

        with col4:
            st.markdown("""
            **Step 4: Coordination**
            ```
            🎯 Coordinator Agent
            ├─ Final decision
            ├─ Prioritize actions
            └─ Execute plan
            ```
            """)

        st.markdown("---")

        st.markdown("### 🚀 Key Features")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            - **Intelligent Decision Making**: LLM-powered agents that understand network context
            - **Explainable AI**: Every decision comes with reasoning
            - **Safety First**: Validation agent ensures changes are safe
            - **Real Data Support**: Works with actual 6G HetNet dataset
            """)

        with col2:
            st.markdown("""
            - **Multi-Vendor Compatible**: Works with any RAN infrastructure
            - **Scalable**: Handle networks of any size
            - **Fast Inference**: Powered by Groq's ultra-fast LLM API
            - **Free Tier Available**: Get started with Groq's free API
            """)

    # ============= PAGE: SETUP API KEY =============
    elif page == "🔑 Setup API Key":
        st.header("Setup Groq API Key")

        st.markdown("""
        This application uses **Groq** for fast LLM inference. Groq offers a generous free tier.

        ### Get Your Free API Key:
        1. Go to [console.groq.com](https://console.groq.com)
        2. Sign up for a free account
        3. Navigate to "API Keys"
        4. Create a new API key
        5. Paste it below
        """)

        api_key = st.text_input(
            "Enter your Groq API Key",
            type="password",
            placeholder="gsk_xxxxxxxxxxxxxxxxxxxx"
        )

        if st.button("✅ Save API Key"):
            if api_key and api_key.startswith("gsk_"):
                os.environ["GROQ_API_KEY"] = api_key
                st.session_state.api_key_set = True

                # Initialize the crew
                try:
                    from agents.ran_crew import RANOptimizationCrew
                    st.session_state.crew = RANOptimizationCrew(groq_api_key=api_key)

                    if st.session_state.crew.is_ready():
                        st.success("✅ API Key saved and agents initialized!")
                        st.balloons()
                    else:
                        st.error("Failed to initialize agents")
                except Exception as e:
                    st.error(f"Error initializing agents: {e}")
            else:
                st.error("Please enter a valid Groq API key (starts with 'gsk_')")

        if st.session_state.api_key_set:
            st.success("✅ API Key is configured!")

        st.markdown("---")

        st.markdown("""
        ### For Streamlit Cloud Deployment

        Add your API key to **Secrets** in the Streamlit Cloud dashboard:

        ```toml
        GROQ_API_KEY = "gsk_your_api_key_here"
        ```
        """)

        # Check if key is in environment (for Streamlit Cloud)
        if os.getenv("GROQ_API_KEY"):
            st.info("🔐 GROQ_API_KEY found in environment variables")
            if not st.session_state.api_key_set:
                try:
                    from agents.ran_crew import RANOptimizationCrew
                    st.session_state.crew = RANOptimizationCrew()
                    st.session_state.api_key_set = st.session_state.crew.is_ready()
                except Exception as e:
                    st.error(f"Error: {e}")

    # ============= PAGE: RUN OPTIMIZATION =============
    elif page == "🎯 Run Optimization":
        st.header("Run Network Optimization")

        if not st.session_state.api_key_set:
            st.warning("⚠️ Please configure your Groq API key first!")
            st.page_link("🔑 Setup API Key", label="Go to Setup")
            return

        # Initialize environment
        if st.session_state.env is None or st.button("🔄 Reset Network"):
            with st.spinner("Initializing network environment..."):
                st.session_state.env = RANEnvironment(
                    num_cells=num_cells,
                    use_real_data=use_real_data
                )
                st.success(f"✅ Network initialized with {num_cells} cells")

        # Display current network
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### Current Network State")
            if st.session_state.env:
                fig = create_network_topology(st.session_state.env)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Network Metrics")
            if st.session_state.env:
                stats = st.session_state.env.get_network_stats()
                st.metric("Avg Throughput", f"{stats['avg_throughput']:.1f} Mbps")
                st.metric("Avg Drop Rate", f"{stats['avg_drop_rate']*100:.2f}%")
                st.metric("Total Power", f"{stats['total_power']:.1f} W")
                st.metric("Avg Satisfaction", f"{stats['avg_satisfaction']:.1f}/100")

        st.markdown("---")

        # Run optimization button
        if st.button("🚀 Run AI Optimization", type="primary", use_container_width=True):
            if st.session_state.crew and st.session_state.env:
                # Prepare network state
                network_state = {
                    'cells': st.session_state.env.cells,
                    'stats': st.session_state.env.get_network_stats()
                }

                # Run optimization
                results = run_optimization_with_ui(st.session_state.crew, network_state)
                st.session_state.optimization_result = results

                if results['success']:
                    st.success("🎉 Optimization Complete!")
                    st.balloons()
                else:
                    st.error(f"Optimization failed: {results.get('error', 'Unknown error')}")

    # ============= PAGE: RESULTS ANALYSIS =============
    elif page == "📊 Results Analysis":
        st.header("Optimization Results Analysis")

        if st.session_state.optimization_result is None:
            st.info("Run an optimization first to see results here")
            return

        results = st.session_state.optimization_result

        if not results['success']:
            st.error(f"Last optimization failed: {results.get('error', 'Unknown error')}")
            return

        # Display agent outputs
        st.markdown("### 🤖 Agent Reports")

        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Analysis", "⚡ Optimization", "✅ Validation", "🎯 Coordination"
        ])

        with tab1:
            st.markdown("#### Network Performance Analyst Report")
            if results.get('analysis'):
                st.markdown(results['analysis'])

        with tab2:
            st.markdown("#### RF Optimization Engineer Report")
            if results.get('optimization'):
                st.markdown(results['optimization'])

        with tab3:
            st.markdown("#### Quality Assurance Engineer Report")
            if results.get('validation'):
                st.markdown(results['validation'])

        with tab4:
            st.markdown("#### Network Operations Manager Report")
            if results.get('coordination'):
                st.markdown(results['coordination'])

        # Final actions
        st.markdown("---")
        st.markdown("### 📋 Approved Actions")

        final_actions = results.get('final_actions', [])

        if final_actions:
            actions_df = pd.DataFrame(final_actions)
            st.dataframe(actions_df, use_container_width=True)

            # Apply actions button
            if st.button("✅ Apply Approved Actions to Network"):
                if st.session_state.env and st.session_state.crew:
                    before_after = st.session_state.crew.apply_actions(
                        st.session_state.env,
                        final_actions
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Before:**")
                        st.json(before_after['before'])

                    with col2:
                        st.markdown("**After:**")
                        st.json(before_after['after'])

                    st.success(f"✅ Applied {before_after['actions_applied']} actions!")
        else:
            st.info("No actions were approved in this optimization cycle")


if __name__ == "__main__":
    main()
