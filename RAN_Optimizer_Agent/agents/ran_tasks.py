"""
RAN Network Optimization Tasks
Defines the tasks that agents will perform for network optimization
"""

from crewai import Task
from typing import Dict, List, Any


def create_analysis_task(analyzer_agent, network_state: Dict[str, Any]) -> Task:
    """
    Create a task for the Analyzer Agent to analyze network performance.

    Args:
        analyzer_agent: The analyzer agent instance
        network_state: Current state of the network with cell metrics

    Returns:
        Task: CrewAI task for network analysis
    """

    # Format network state for the prompt
    cells_info = format_network_state(network_state)

    return Task(
        description=f"""
        Analyze the current state of the RAN network and identify cells that need optimization.

        **Current Network State:**
        {cells_info}

        **Your Analysis Should Include:**
        1. Overall network health assessment (score 1-10)
        2. List of problematic cells ranked by severity
        3. Specific issues identified for each problematic cell:
           - Low throughput (threshold: < 100 Mbps is concerning)
           - High drop rate (threshold: > 5% is concerning)
           - High interference (threshold: > 0.3 is concerning)
           - Poor user satisfaction (threshold: < 80% is concerning)
        4. Root cause hypothesis for each issue
        5. Priority ranking for optimization (Critical/High/Medium/Low)

        Provide a structured analysis that the Optimizer Agent can use to recommend changes.
        """,
        expected_output="""
        A detailed analysis report containing:
        - Network health score (1-10)
        - List of cells needing optimization with severity ratings
        - Specific issues and metrics for each cell
        - Root cause analysis
        - Prioritized optimization recommendations
        """,
        agent=analyzer_agent
    )


def create_optimization_task(optimizer_agent, analysis_result: str, network_state: Dict[str, Any]) -> Task:
    """
    Create a task for the Optimizer Agent to recommend parameter changes.

    Args:
        optimizer_agent: The optimizer agent instance
        analysis_result: Output from the analyzer agent
        network_state: Current state of the network

    Returns:
        Task: CrewAI task for optimization recommendations
    """

    cells_info = format_network_state(network_state)

    return Task(
        description=f"""
        Based on the network analysis, recommend specific parameter adjustments to optimize performance.

        **Analysis from Network Analyst:**
        {analysis_result}

        **Current Network State:**
        {cells_info}

        **Available Parameter Adjustments:**
        1. Transmission Power: Can adjust by -3, 0, or +3 dB
           - Range: 10-50 dBm
           - Increasing power: Better coverage, higher interference
           - Decreasing power: Lower interference, reduced coverage

        2. Antenna Tilt: Can adjust by -2, 0, or +2 degrees
           - Range: 0-10 degrees
           - Increasing tilt: Smaller cell footprint, less interference to neighbors
           - Decreasing tilt: Larger coverage, potential overlap issues

        3. Handover Threshold: Can adjust by -5, 0, or +5
           - Range: 50-90
           - Lower threshold: Faster handovers, fewer drops, more signaling
           - Higher threshold: Delayed handovers, potential drops at cell edge

        **Your Recommendations Should Include:**
        For each cell requiring optimization:
        1. Cell ID and current metrics
        2. Recommended parameter changes (power, tilt, handover)
        3. Expected improvement (quantified if possible)
        4. Rationale for each change
        5. Risk assessment (Low/Medium/High)

        Be conservative - prefer smaller changes that can be verified before larger adjustments.
        """,
        expected_output="""
        A structured optimization plan containing:
        - List of cells with recommended changes
        - Specific parameter adjustments (power_change, tilt_change, handover_change)
        - Expected outcomes for each change
        - Risk assessment per recommendation
        - Implementation priority order
        """,
        agent=optimizer_agent
    )


def create_validation_task(validator_agent, optimization_plan: str, network_state: Dict[str, Any]) -> Task:
    """
    Create a task for the Validator Agent to validate proposed changes.

    Args:
        validator_agent: The validator agent instance
        optimization_plan: Output from the optimizer agent
        network_state: Current state of the network

    Returns:
        Task: CrewAI task for validation
    """

    cells_info = format_network_state(network_state)

    return Task(
        description=f"""
        Validate the proposed optimization changes to ensure they are safe and compliant.

        **Proposed Optimization Plan:**
        {optimization_plan}

        **Current Network State:**
        {cells_info}

        **Validation Rules:**
        1. **Power Limits:**
           - Maximum single change: ±6 dB
           - Absolute range: 10-50 dBm
           - Adjacent cells should not have >10 dB difference

        2. **Tilt Limits:**
           - Maximum single change: ±4 degrees
           - Absolute range: 0-10 degrees

        3. **Handover Limits:**
           - Maximum single change: ±10
           - Absolute range: 50-90

        4. **Safety Checks:**
           - No changes that could cause coverage holes
           - No changes that would overload adjacent cells
           - Verify no conflicting changes between neighbors

        **Your Validation Report Should Include:**
        1. For each proposed change: APPROVED / REJECTED / MODIFIED
        2. If rejected: Specific reason and rule violated
        3. If modified: Suggested safe alternative
        4. Overall risk score for the change set (1-10)
        5. Any additional precautions recommended

        Be thorough - you are the last check before changes go live.
        """,
        expected_output="""
        A validation report containing:
        - Approval status for each proposed change (APPROVED/REJECTED/MODIFIED)
        - Reasons for any rejections
        - Modified recommendations if applicable
        - Overall risk score (1-10)
        - Final list of approved changes ready for implementation
        """,
        agent=validator_agent
    )


def create_coordination_task(coordinator_agent, analysis: str, optimization: str, validation: str) -> Task:
    """
    Create a task for the Coordinator Agent to make final decisions.

    Args:
        coordinator_agent: The coordinator agent instance
        analysis: Output from analyzer agent
        optimization: Output from optimizer agent
        validation: Output from validator agent

    Returns:
        Task: CrewAI task for coordination
    """

    return Task(
        description=f"""
        Review all inputs and make final decisions on the network optimization actions.

        **Network Analysis Report:**
        {analysis}

        **Optimization Recommendations:**
        {optimization}

        **Validation Report:**
        {validation}

        **Your Responsibilities:**
        1. Review the complete optimization workflow
        2. Make final GO/NO-GO decision for each change
        3. Prioritize the order of implementation
        4. Identify any concerns not addressed by other agents
        5. Provide executive summary for stakeholders

        **Decision Framework:**
        - If validation passed and risk is Low/Medium: Approve
        - If validation passed but risk is High: Approve with monitoring
        - If validation failed: Reject and request revision
        - If conflicting recommendations: Use business judgment

        **Output Format:**
        Provide a final action plan with:
        1. Executive summary (2-3 sentences)
        2. Approved changes with implementation order
        3. Rejected changes with reasons
        4. Monitoring recommendations
        5. Next review cycle timing
        """,
        expected_output="""
        An executive decision report containing:
        - Executive summary of the optimization cycle
        - Final approved changes in implementation order
        - Rejected changes with clear reasons
        - Risk mitigation and monitoring plan
        - Recommendations for next optimization cycle

        Also provide a structured JSON-like output with the final actions:
        FINAL_ACTIONS:
        - cell_id: X, power_change: Y, tilt_change: Z, handover_change: W, status: APPROVED/REJECTED
        """,
        agent=coordinator_agent
    )


def format_network_state(network_state: Dict[str, Any]) -> str:
    """
    Format network state dictionary into a readable string for prompts.

    Args:
        network_state: Dictionary with network metrics

    Returns:
        str: Formatted string representation
    """

    if 'cells' in network_state:
        cells = network_state['cells']
    else:
        cells = network_state.get('cell_metrics', [])

    if not cells:
        return "No cell data available"

    lines = []
    lines.append(f"Total Cells: {len(cells)}")
    lines.append("-" * 60)

    for cell in cells:
        cell_id = cell.get('id', 'Unknown')
        cell_type = cell.get('cell_type', 'Unknown')
        lines.append(f"\nCell {cell_id} ({cell_type}):")
        lines.append(f"  - Users: {cell.get('num_users', 'N/A')}")
        lines.append(f"  - Throughput: {cell.get('throughput', 0):.1f} Mbps")
        lines.append(f"  - Drop Rate: {cell.get('drop_rate', 0)*100:.2f}%")
        lines.append(f"  - TX Power: {cell.get('tx_power', 0):.1f} dBm")
        lines.append(f"  - Antenna Tilt: {cell.get('antenna_tilt', 0):.1f} degrees")
        lines.append(f"  - Interference: {cell.get('interference', 0):.3f}")
        lines.append(f"  - Power Consumption: {cell.get('power_consumption', 0):.1f} W")

        if 'qos_satisfaction' in cell:
            lines.append(f"  - QoS Satisfaction: {cell.get('qos_satisfaction', 0):.1f}%")

        if 'optimized_action' in cell:
            lines.append(f"  - Recommended Action: {cell.get('optimized_action', 'N/A')}")

    # Add summary stats if available
    if 'stats' in network_state:
        stats = network_state['stats']
        lines.append("\n" + "=" * 60)
        lines.append("NETWORK SUMMARY:")
        lines.append(f"  - Avg Throughput: {stats.get('avg_throughput', 0):.1f} Mbps")
        lines.append(f"  - Avg Drop Rate: {stats.get('avg_drop_rate', 0)*100:.2f}%")
        lines.append(f"  - Total Power: {stats.get('total_power', 0):.1f} W")
        lines.append(f"  - Avg Satisfaction: {stats.get('avg_satisfaction', 0):.1f}/100")

    return "\n".join(lines)


def parse_final_actions(coordinator_output: str) -> List[Dict[str, Any]]:
    """
    Parse the coordinator's output to extract final actions.

    Args:
        coordinator_output: Raw output from coordinator agent

    Returns:
        List of action dictionaries
    """

    actions = []

    # Look for FINAL_ACTIONS section
    if "FINAL_ACTIONS:" in coordinator_output:
        lines = coordinator_output.split("FINAL_ACTIONS:")[1].strip().split("\n")

        for line in lines:
            if "cell_id:" in line.lower():
                action = {}
                parts = line.split(",")

                for part in parts:
                    part = part.strip().strip("-").strip()
                    if ":" in part:
                        key, value = part.split(":", 1)
                        key = key.strip().lower().replace(" ", "_")
                        value = value.strip()

                        # Convert numeric values
                        if key in ['cell_id', 'power_change', 'tilt_change', 'handover_change']:
                            try:
                                value = int(value)
                            except ValueError:
                                try:
                                    value = float(value)
                                except ValueError:
                                    pass

                        action[key] = value

                if action:
                    actions.append(action)

    return actions


if __name__ == "__main__":
    # Test task creation with sample data
    print("Testing task creation...")

    sample_network_state = {
        'cells': [
            {
                'id': 0,
                'cell_type': 'Macro',
                'num_users': 150,
                'throughput': 85.5,
                'drop_rate': 0.03,
                'tx_power': 43.0,
                'antenna_tilt': 5.0,
                'interference': 0.15,
                'power_consumption': 21.5,
                'qos_satisfaction': 82.0
            },
            {
                'id': 1,
                'cell_type': 'Micro',
                'num_users': 80,
                'throughput': 45.2,
                'drop_rate': 0.08,
                'tx_power': 35.0,
                'antenna_tilt': 3.0,
                'interference': 0.35,
                'power_consumption': 17.5,
                'qos_satisfaction': 65.0
            }
        ],
        'stats': {
            'avg_throughput': 65.35,
            'avg_drop_rate': 0.055,
            'total_power': 39.0,
            'avg_satisfaction': 73.5
        }
    }

    formatted = format_network_state(sample_network_state)
    print("\nFormatted Network State:")
    print(formatted)
