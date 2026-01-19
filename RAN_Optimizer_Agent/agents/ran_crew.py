"""
RAN Network Optimization Crew
Orchestrates the multi-agent system for network optimization using CrewAI
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from crewai import Crew, Process

from .ran_agents import create_agents, get_groq_llm, AGENT_DESCRIPTIONS
from .ran_tasks import (
    create_analysis_task,
    create_optimization_task,
    create_validation_task,
    create_coordination_task,
    format_network_state,
    parse_final_actions
)


@dataclass
class OptimizationResult:
    """Results from an optimization cycle"""
    timestamp: str
    network_state_before: Dict[str, Any]
    analysis_report: str
    optimization_plan: str
    validation_report: str
    coordinator_decision: str
    final_actions: List[Dict[str, Any]]
    execution_log: List[str] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None


class RANOptimizationCrew:
    """
    Main class to orchestrate the RAN optimization multi-agent system.

    This crew consists of 4 specialized agents:
    1. Analyzer Agent - Analyzes network performance
    2. Optimizer Agent - Recommends parameter changes
    3. Validator Agent - Validates proposed changes
    4. Coordinator Agent - Makes final decisions
    """

    def __init__(self, groq_api_key: Optional[str] = None, model_name: str = "llama-3.1-70b-versatile"):
        """
        Initialize the RAN Optimization Crew.

        Args:
            groq_api_key: Groq API key (or set GROQ_API_KEY env variable)
            model_name: Groq model to use
        """
        # Set API key if provided
        if groq_api_key:
            os.environ["GROQ_API_KEY"] = groq_api_key

        self.model_name = model_name
        self.llm = None
        self.agents = None
        self.crew = None
        self.optimization_history: List[OptimizationResult] = []

        # Initialize agents
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all agents with the Groq LLM."""
        try:
            self.llm = get_groq_llm(self.model_name)
            self.agents = create_agents(self.llm)
            print(f"✅ Initialized {len(self.agents)} agents with Groq ({self.model_name})")
        except ValueError as e:
            print(f"⚠️ Agent initialization failed: {e}")
            self.agents = None

    def is_ready(self) -> bool:
        """Check if the crew is ready to operate."""
        return self.agents is not None

    def run_optimization_cycle(self, network_state: Dict[str, Any], verbose: bool = True) -> OptimizationResult:
        """
        Run a complete optimization cycle with all 4 agents.

        Args:
            network_state: Current state of the network with cell metrics
            verbose: Whether to print progress updates

        Returns:
            OptimizationResult: Complete results from the optimization cycle
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execution_log = []

        def log(message: str):
            execution_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
            if verbose:
                print(message)

        log("🚀 Starting RAN Optimization Cycle")
        log(f"   Network: {len(network_state.get('cells', []))} cells")

        if not self.is_ready():
            return OptimizationResult(
                timestamp=timestamp,
                network_state_before=network_state,
                analysis_report="",
                optimization_plan="",
                validation_report="",
                coordinator_decision="",
                final_actions=[],
                execution_log=execution_log,
                success=False,
                error_message="Agents not initialized. Check GROQ_API_KEY."
            )

        try:
            # Step 1: Analysis
            log("\n📊 Step 1: Network Analysis")
            log("   Agent: Network Performance Analyst")
            analysis_task = create_analysis_task(self.agents['analyzer'], network_state)
            analysis_crew = Crew(
                agents=[self.agents['analyzer']],
                tasks=[analysis_task],
                process=Process.sequential,
                verbose=verbose
            )
            analysis_result = analysis_crew.kickoff()
            analysis_report = str(analysis_result)
            log("   ✓ Analysis complete")

            # Step 2: Optimization
            log("\n⚡ Step 2: Optimization Planning")
            log("   Agent: RF Optimization Engineer")
            optimization_task = create_optimization_task(
                self.agents['optimizer'],
                analysis_report,
                network_state
            )
            optimization_crew = Crew(
                agents=[self.agents['optimizer']],
                tasks=[optimization_task],
                process=Process.sequential,
                verbose=verbose
            )
            optimization_result = optimization_crew.kickoff()
            optimization_plan = str(optimization_result)
            log("   ✓ Optimization plan ready")

            # Step 3: Validation
            log("\n✅ Step 3: Change Validation")
            log("   Agent: Quality Assurance Engineer")
            validation_task = create_validation_task(
                self.agents['validator'],
                optimization_plan,
                network_state
            )
            validation_crew = Crew(
                agents=[self.agents['validator']],
                tasks=[validation_task],
                process=Process.sequential,
                verbose=verbose
            )
            validation_result = validation_crew.kickoff()
            validation_report = str(validation_result)
            log("   ✓ Validation complete")

            # Step 4: Coordination
            log("\n🎯 Step 4: Final Decision")
            log("   Agent: Network Operations Manager")
            coordination_task = create_coordination_task(
                self.agents['coordinator'],
                analysis_report,
                optimization_plan,
                validation_report
            )
            coordination_crew = Crew(
                agents=[self.agents['coordinator']],
                tasks=[coordination_task],
                process=Process.sequential,
                verbose=verbose
            )
            coordination_result = coordination_crew.kickoff()
            coordinator_decision = str(coordination_result)
            log("   ✓ Final decision made")

            # Parse final actions
            final_actions = parse_final_actions(coordinator_decision)
            log(f"\n📋 Optimization cycle complete: {len(final_actions)} actions approved")

            result = OptimizationResult(
                timestamp=timestamp,
                network_state_before=network_state,
                analysis_report=analysis_report,
                optimization_plan=optimization_plan,
                validation_report=validation_report,
                coordinator_decision=coordinator_decision,
                final_actions=final_actions,
                execution_log=execution_log,
                success=True
            )

        except Exception as e:
            log(f"\n❌ Error during optimization: {str(e)}")
            result = OptimizationResult(
                timestamp=timestamp,
                network_state_before=network_state,
                analysis_report="",
                optimization_plan="",
                validation_report="",
                coordinator_decision="",
                final_actions=[],
                execution_log=execution_log,
                success=False,
                error_message=str(e)
            )

        # Store in history
        self.optimization_history.append(result)

        return result

    def apply_actions(self, environment, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply the approved actions to the environment.

        Args:
            environment: RANEnvironment instance
            actions: List of actions from the optimization cycle

        Returns:
            Dict with before and after metrics
        """

        before_stats = environment.get_network_stats()

        for action in actions:
            if action.get('status', '').upper() != 'APPROVED':
                continue

            cell_id = action.get('cell_id')
            if cell_id is None or cell_id >= len(environment.cells):
                continue

            cell = environment.cells[cell_id]

            # Apply power change
            power_change = action.get('power_change', 0)
            if power_change:
                cell['tx_power'] = max(10, min(50, cell['tx_power'] + power_change))
                cell['power_consumption'] = cell['tx_power'] * 0.5

            # Apply tilt change
            tilt_change = action.get('tilt_change', 0)
            if tilt_change:
                cell['antenna_tilt'] = max(0, min(10, cell['antenna_tilt'] + tilt_change))

            # Apply handover change
            handover_change = action.get('handover_change', 0)
            if handover_change:
                cell['handover_threshold'] = max(50, min(90, cell['handover_threshold'] + handover_change))

        after_stats = environment.get_network_stats()

        return {
            'before': before_stats,
            'after': after_stats,
            'actions_applied': len([a for a in actions if a.get('status', '').upper() == 'APPROVED'])
        }

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about all agents for display."""
        return AGENT_DESCRIPTIONS

    def export_history(self, filepath: str):
        """Export optimization history to JSON file."""
        history_data = []

        for result in self.optimization_history:
            history_data.append({
                'timestamp': result.timestamp,
                'success': result.success,
                'actions_count': len(result.final_actions),
                'final_actions': result.final_actions,
                'error': result.error_message
            })

        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)

        print(f"✅ History exported to {filepath}")


def run_demo():
    """Run a demo of the optimization crew."""

    print("=" * 60)
    print("  RAN Optimization Crew - Demo")
    print("=" * 60)

    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("\n❌ GROQ_API_KEY not set!")
        print("Get your free API key at: https://console.groq.com/keys")
        print("\nSet it with:")
        print("  export GROQ_API_KEY='your-key-here'")
        return

    # Sample network state
    sample_network = {
        'cells': [
            {
                'id': 0, 'cell_type': 'Macro', 'num_users': 250,
                'throughput': 450.0, 'drop_rate': 0.02, 'tx_power': 40.0,
                'antenna_tilt': 5.0, 'interference': 0.15, 'power_consumption': 20.0,
                'qos_satisfaction': 88.0
            },
            {
                'id': 1, 'cell_type': 'Micro', 'num_users': 120,
                'throughput': 180.0, 'drop_rate': 0.09, 'tx_power': 30.0,
                'antenna_tilt': 3.0, 'interference': 0.45, 'power_consumption': 15.0,
                'qos_satisfaction': 62.0
            },
            {
                'id': 2, 'cell_type': 'Femto', 'num_users': 45,
                'throughput': 95.0, 'drop_rate': 0.12, 'tx_power': 20.0,
                'antenna_tilt': 2.0, 'interference': 0.55, 'power_consumption': 10.0,
                'qos_satisfaction': 55.0
            }
        ],
        'stats': {
            'avg_throughput': 241.67,
            'avg_drop_rate': 0.077,
            'total_power': 45.0,
            'avg_satisfaction': 68.3
        }
    }

    # Initialize crew
    print("\n🤖 Initializing AI Agents...")
    crew = RANOptimizationCrew()

    if not crew.is_ready():
        print("Failed to initialize agents")
        return

    # Run optimization
    print("\n" + "=" * 60)
    result = crew.run_optimization_cycle(sample_network)

    # Show results
    print("\n" + "=" * 60)
    print("  OPTIMIZATION RESULTS")
    print("=" * 60)

    if result.success:
        print(f"\n✅ Optimization completed successfully!")
        print(f"   Actions approved: {len(result.final_actions)}")

        if result.final_actions:
            print("\n📋 Approved Actions:")
            for action in result.final_actions:
                print(f"   - Cell {action.get('cell_id')}: "
                      f"Power {action.get('power_change', 0):+d} dB, "
                      f"Tilt {action.get('tilt_change', 0):+d}°, "
                      f"Handover {action.get('handover_change', 0):+d}")
    else:
        print(f"\n❌ Optimization failed: {result.error_message}")


if __name__ == "__main__":
    run_demo()
