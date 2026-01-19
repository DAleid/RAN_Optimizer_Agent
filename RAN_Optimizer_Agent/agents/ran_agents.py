"""
RAN Network Optimization Agents
Defines the 4 specialized agents for network optimization using CrewAI and Groq
"""

import os
from crewai import Agent
from langchain_groq import ChatGroq

def get_groq_llm(model_name: str = "llama-3.1-70b-versatile"):
    """
    Initialize Groq LLM for the agents.

    Available Groq models:
    - llama-3.1-70b-versatile (recommended - best quality)
    - llama-3.1-8b-instant (faster, good for simple tasks)
    - mixtral-8x7b-32768 (good balance)
    - gemma2-9b-it (lightweight)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please set it in your environment or .env file.\n"
            "Get your free API key at: https://console.groq.com/keys"
        )

    return ChatGroq(
        api_key=api_key,
        model_name=model_name,
        temperature=0.3,  # Lower temperature for more consistent outputs
        max_tokens=2048
    )


def create_agents(llm=None):
    """
    Create the 4 specialized agents for RAN network optimization.

    Returns:
        dict: Dictionary containing all 4 agents
    """

    if llm is None:
        llm = get_groq_llm()

    # ============================================
    # AGENT 1: Network Performance Analyzer
    # ============================================
    analyzer_agent = Agent(
        role="Network Performance Analyst",
        goal="""Analyze cellular network performance metrics and identify cells
        that need optimization. Detect anomalies, performance degradation, and
        potential issues before they impact users.""",
        backstory="""You are a senior network performance analyst with 15 years
        of experience in telecommunications. You specialize in analyzing KPIs
        (Key Performance Indicators) for RAN (Radio Access Networks) including
        4G LTE and 5G networks. You have deep expertise in:
        - Throughput analysis and capacity planning
        - Call drop rate investigation
        - Interference detection and root cause analysis
        - User experience metrics and QoS monitoring

        You are known for your ability to quickly identify problematic cells
        and prioritize them based on business impact.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # ============================================
    # AGENT 2: RF Optimization Engineer
    # ============================================
    optimizer_agent = Agent(
        role="RF Optimization Engineer",
        goal="""Recommend optimal parameter adjustments for cellular network cells
        to improve throughput, reduce drop rates, minimize interference, and
        optimize power consumption while maintaining network stability.""",
        backstory="""You are an expert RF (Radio Frequency) optimization engineer
        with extensive experience in cellular network optimization. You have
        worked with all major vendors (Ericsson, Nokia, Huawei) and understand
        the intricacies of:
        - Transmission power optimization (typical range: 10-50 dBm)
        - Antenna tilt adjustments (electrical and mechanical, 0-10 degrees)
        - Handover parameter tuning (thresholds, hysteresis, time-to-trigger)
        - Load balancing between cells

        You always consider the trade-offs:
        - Increasing power improves coverage but increases interference
        - Adjusting tilt affects coverage footprint and neighbor relations
        - Handover parameters affect user mobility and drop rates

        Your recommendations are always data-driven and conservative to avoid
        network instability.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # ============================================
    # AGENT 3: Quality Assurance Validator
    # ============================================
    validator_agent = Agent(
        role="Quality Assurance Engineer",
        goal="""Validate proposed network parameter changes to ensure they are
        safe, won't cause service degradation, and comply with operational
        guidelines. Identify potential conflicts and risks before implementation.""",
        backstory="""You are a meticulous QA engineer specializing in network
        change validation. You have prevented countless network outages by
        catching risky changes before they were implemented. Your expertise includes:
        - Change impact assessment
        - Conflict detection between neighboring cells
        - Compliance checking against operational limits
        - Risk scoring and mitigation recommendations

        You follow strict validation rules:
        - Power changes should not exceed ±6 dB in a single change window
        - Tilt changes should not exceed ±4 degrees at once
        - Handover threshold changes should be gradual (±10 max)
        - Adjacent cells should not have conflicting configurations

        You are the last line of defense before changes go live.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # ============================================
    # AGENT 4: Network Operations Coordinator
    # ============================================
    coordinator_agent = Agent(
        role="Network Operations Manager",
        goal="""Coordinate the optimization workflow, prioritize actions based on
        business impact, make final decisions on parameter changes, and ensure
        smooth execution of the optimization strategy.""",
        backstory="""You are the head of Network Operations with responsibility
        for maintaining optimal network performance across the entire RAN. You
        coordinate between different teams and make executive decisions on:
        - Which cells to prioritize for optimization
        - Whether to approve or reject proposed changes
        - Scheduling of optimization activities
        - Escalation of critical issues

        You have a holistic view of the network and understand business priorities:
        - High-traffic areas (malls, stadiums) get priority
        - Revenue-generating enterprise customers are critical
        - Regulatory compliance is non-negotiable
        - Network stability trumps marginal improvements

        You synthesize inputs from analysts, engineers, and QA to make
        informed decisions that balance performance with risk.""",
        verbose=True,
        allow_delegation=True,  # Coordinator can delegate to other agents
        llm=llm
    )

    return {
        'analyzer': analyzer_agent,
        'optimizer': optimizer_agent,
        'validator': validator_agent,
        'coordinator': coordinator_agent
    }


# Agent descriptions for display in UI
AGENT_DESCRIPTIONS = {
    'analyzer': {
        'name': 'Network Performance Analyst',
        'icon': '📊',
        'color': '#3498db',
        'responsibilities': [
            'Analyze network KPIs and metrics',
            'Detect anomalies and performance issues',
            'Identify cells requiring optimization',
            'Prioritize based on impact'
        ]
    },
    'optimizer': {
        'name': 'RF Optimization Engineer',
        'icon': '⚡',
        'color': '#e74c3c',
        'responsibilities': [
            'Recommend TX power adjustments',
            'Suggest antenna tilt changes',
            'Optimize handover parameters',
            'Balance throughput vs interference'
        ]
    },
    'validator': {
        'name': 'Quality Assurance Engineer',
        'icon': '✅',
        'color': '#2ecc71',
        'responsibilities': [
            'Validate proposed changes',
            'Check for conflicts',
            'Assess risks',
            'Ensure compliance with limits'
        ]
    },
    'coordinator': {
        'name': 'Network Operations Manager',
        'icon': '🎯',
        'color': '#9b59b6',
        'responsibilities': [
            'Orchestrate optimization workflow',
            'Make final decisions',
            'Prioritize actions',
            'Manage overall strategy'
        ]
    }
}


if __name__ == "__main__":
    # Test agent creation
    print("Testing agent creation...")
    print("Note: Requires GROQ_API_KEY environment variable")

    try:
        agents = create_agents()
        print(f"\n✅ Successfully created {len(agents)} agents:")
        for name, agent in agents.items():
            print(f"   - {name}: {agent.role}")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo test, set your GROQ_API_KEY:")
        print("  export GROQ_API_KEY='your-api-key-here'")
