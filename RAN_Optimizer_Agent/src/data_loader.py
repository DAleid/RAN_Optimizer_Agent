"""
Data Loader for 6G HetNet Transmission Management Dataset
Loads and preprocesses real network data from CSV file
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class NetworkDataLoader:
    """
    Loads and preprocesses the 6G HetNet transmission management dataset
    for use in the RAN optimization environment.
    """

    # Column mappings from CSV to internal representation
    COLUMN_MAPPING = {
        'cell_id': 'Cell_ID',
        'user_id': 'User_ID',
        'cell_type': 'Cell_Type',
        'frequency': 'Carrier_Frequency_GHz',
        'bandwidth': 'Bandwidth_MHz',
        'modulation': 'Modulation_Scheme',
        'tx_power': 'Transmission_Power_dBm',
        'interference': 'Interference_Level_dB',
        'power_consumption': 'Power_Consumption_Watt',
        'throughput': 'Achieved_Throughput_Mbps',
        'energy_efficiency': 'Energy_Efficiency_Mbps_Watt',
        'latency': 'Network_Latency_ms',
        'packet_loss': 'Packet_Loss_Ratio',
        'snr': 'Signal_to_Noise_Ratio_dB',
        'resource_utilization': 'Resource_Utilization',
        'traffic_demand': 'User_Traffic_Demand_Mbps',
        'qos_satisfaction': 'QoS_Satisfaction',
        'user_mobility': 'User_Mobility_kmh',
        'handover_count': 'Handover_Count',
        'optimized_power': 'Optimized_Power_dBm',
        'reward_score': 'Reward_Score',
        'success_rate': 'Success_Rate',
        'optimized_action': 'Optimized_Action'
    }

    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the data loader.

        Args:
            data_path: Path to the CSV file. If None, uses default location.
        """
        if data_path is None:
            # Default path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, 'data', '6G_HetNet_Transmission_Management.csv')

        self.data_path = data_path
        self.raw_data = None
        self.processed_data = None
        self.cell_data = None
        self._load_data()

    def _load_data(self):
        """Load and preprocess the CSV data."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found: {self.data_path}")

        # Load CSV
        self.raw_data = pd.read_csv(self.data_path)

        # Basic preprocessing
        self.processed_data = self.raw_data.copy()

        # Normalize interference (convert from negative dB to positive scale)
        # Interference in CSV is negative (e.g., -98 dB), we need 0-1 scale
        self.processed_data['interference_normalized'] = (
            (self.processed_data['Interference_Level_dB'] + 100) / 50
        ).clip(0, 1)

        # Normalize packet loss to 0-1 scale (already in ratio)
        self.processed_data['drop_rate_normalized'] = self.processed_data['Packet_Loss_Ratio'].clip(0, 0.15)

        # Group data by cell for easier access
        self._aggregate_by_cell()

    def _aggregate_by_cell(self):
        """Aggregate user-level data to cell-level metrics."""
        cell_groups = self.processed_data.groupby('Cell_ID')

        self.cell_data = cell_groups.agg({
            'Cell_Type': 'first',
            'Carrier_Frequency_GHz': 'mean',
            'Bandwidth_MHz': 'mean',
            'Transmission_Power_dBm': 'mean',
            'Interference_Level_dB': 'mean',
            'Power_Consumption_Watt': 'mean',
            'Achieved_Throughput_Mbps': 'mean',
            'Network_Latency_ms': 'mean',
            'Packet_Loss_Ratio': 'mean',
            'Signal_to_Noise_Ratio_dB': 'mean',
            'Resource_Utilization': 'mean',
            'User_Traffic_Demand_Mbps': 'sum',
            'QoS_Satisfaction': 'mean',
            'User_Mobility_kmh': 'mean',
            'Handover_Count': 'sum',
            'Optimized_Power_dBm': 'mean',
            'Reward_Score': 'mean',
            'Success_Rate': 'mean',
            'User_ID': 'count',  # Number of users per cell
            'interference_normalized': 'mean',
            'drop_rate_normalized': 'mean'
        }).rename(columns={'User_ID': 'num_users'})

        self.cell_data = self.cell_data.reset_index()

    def get_num_cells(self) -> int:
        """Get the number of unique cells in the dataset."""
        return len(self.cell_data)

    def get_cell_ids(self) -> List[int]:
        """Get list of unique cell IDs."""
        return self.cell_data['Cell_ID'].tolist()

    def get_cell_metrics(self, cell_id: int) -> Dict:
        """
        Get metrics for a specific cell.

        Args:
            cell_id: The cell ID to retrieve metrics for

        Returns:
            Dictionary of cell metrics
        """
        cell_row = self.cell_data[self.cell_data['Cell_ID'] == cell_id]
        if cell_row.empty:
            raise ValueError(f"Cell ID {cell_id} not found in data")

        row = cell_row.iloc[0]

        return {
            'id': int(row['Cell_ID']),
            'cell_type': row['Cell_Type'],
            'tx_power': float(row['Transmission_Power_dBm']),
            'antenna_tilt': 3.0,  # Not in dataset, use default
            'handover_threshold': 70.0,  # Not in dataset, use default
            'num_users': int(row['num_users']),
            'throughput': float(row['Achieved_Throughput_Mbps']),
            'drop_rate': float(row['Packet_Loss_Ratio']),
            'power_consumption': float(row['Power_Consumption_Watt']),
            'interference': float(row['interference_normalized']),
            'latency': float(row['Network_Latency_ms']),
            'snr': float(row['Signal_to_Noise_Ratio_dB']),
            'resource_utilization': float(row['Resource_Utilization']),
            'qos_satisfaction': float(row['QoS_Satisfaction']),
            'frequency': float(row['Carrier_Frequency_GHz']),
            'bandwidth': float(row['Bandwidth_MHz']),
            'optimized_power': float(row['Optimized_Power_dBm']),
            'optimized_action': self._get_dominant_action(int(row['Cell_ID']))
        }

    def _get_dominant_action(self, cell_id: int) -> str:
        """Get the most common optimized action for a cell."""
        cell_users = self.processed_data[self.processed_data['Cell_ID'] == cell_id]
        if cell_users.empty:
            return 'Maintain_Power'
        return cell_users['Optimized_Action'].mode().iloc[0]

    def get_all_cells(self) -> List[Dict]:
        """Get metrics for all cells."""
        return [self.get_cell_metrics(cid) for cid in self.get_cell_ids()]

    def get_random_cells(self, num_cells: int, seed: Optional[int] = None) -> List[Dict]:
        """
        Get metrics for a random selection of cells.

        Args:
            num_cells: Number of cells to select
            seed: Random seed for reproducibility

        Returns:
            List of cell metric dictionaries
        """
        if seed is not None:
            np.random.seed(seed)

        available_cells = self.get_cell_ids()
        num_cells = min(num_cells, len(available_cells))
        selected_ids = np.random.choice(available_cells, size=num_cells, replace=False)

        return [self.get_cell_metrics(cid) for cid in selected_ids]

    def get_cells_by_type(self, cell_type: str) -> List[Dict]:
        """
        Get metrics for cells of a specific type.

        Args:
            cell_type: Type of cell ('Macro', 'Micro', 'Pico', 'Femto')

        Returns:
            List of cell metric dictionaries
        """
        type_cells = self.cell_data[self.cell_data['Cell_Type'] == cell_type]
        return [self.get_cell_metrics(cid) for cid in type_cells['Cell_ID']]

    def get_user_data_for_cell(self, cell_id: int) -> pd.DataFrame:
        """
        Get all user-level data for a specific cell.

        Args:
            cell_id: The cell ID

        Returns:
            DataFrame with user-level data
        """
        return self.processed_data[self.processed_data['Cell_ID'] == cell_id].copy()

    def sample_network_state(self, num_cells: int = 10, seed: Optional[int] = None) -> List[Dict]:
        """
        Sample a network state from the real data.
        Useful for initializing the environment with realistic data.

        Args:
            num_cells: Number of cells in the network
            seed: Random seed for reproducibility

        Returns:
            List of cell state dictionaries
        """
        cells = self.get_random_cells(num_cells, seed)

        # Ensure cells have sequential IDs for the environment
        for i, cell in enumerate(cells):
            cell['id'] = i

        return cells

    def get_action_distribution(self) -> Dict[str, float]:
        """Get distribution of optimized actions in the dataset."""
        action_counts = self.raw_data['Optimized_Action'].value_counts(normalize=True)
        return action_counts.to_dict()

    def get_statistics(self) -> Dict:
        """Get summary statistics of the dataset."""
        return {
            'total_records': len(self.raw_data),
            'num_cells': self.get_num_cells(),
            'cell_types': self.cell_data['Cell_Type'].value_counts().to_dict(),
            'avg_throughput': self.cell_data['Achieved_Throughput_Mbps'].mean(),
            'avg_power': self.cell_data['Transmission_Power_dBm'].mean(),
            'avg_packet_loss': self.cell_data['Packet_Loss_Ratio'].mean(),
            'avg_satisfaction': self.cell_data['QoS_Satisfaction'].mean(),
            'action_distribution': self.get_action_distribution()
        }

    def iterate_episodes(self, num_cells: int = 10, num_episodes: int = 100) -> List[List[Dict]]:
        """
        Generate multiple episode configurations from the data.

        Args:
            num_cells: Number of cells per episode
            num_episodes: Number of episodes to generate

        Returns:
            List of episode configurations (each is a list of cell dicts)
        """
        episodes = []
        for i in range(num_episodes):
            cells = self.sample_network_state(num_cells, seed=i)
            episodes.append(cells)
        return episodes


if __name__ == "__main__":
    # Test the data loader
    print("Testing NetworkDataLoader...")
    print("=" * 60)

    loader = NetworkDataLoader()

    stats = loader.get_statistics()
    print(f"\nDataset Statistics:")
    print(f"  Total records: {stats['total_records']}")
    print(f"  Unique cells: {stats['num_cells']}")
    print(f"  Cell types: {stats['cell_types']}")
    print(f"  Avg throughput: {stats['avg_throughput']:.2f} Mbps")
    print(f"  Avg TX power: {stats['avg_power']:.2f} dBm")
    print(f"  Avg packet loss: {stats['avg_packet_loss']:.4f}")
    print(f"  Avg QoS satisfaction: {stats['avg_satisfaction']:.2f}%")
    print(f"  Action distribution: {stats['action_distribution']}")

    print("\nSample cell data:")
    sample_cells = loader.sample_network_state(num_cells=3, seed=42)
    for cell in sample_cells:
        print(f"\n  Cell {cell['id']} ({cell['cell_type']}):")
        print(f"    Users: {cell['num_users']}")
        print(f"    Throughput: {cell['throughput']:.2f} Mbps")
        print(f"    TX Power: {cell['tx_power']:.2f} dBm")
        print(f"    Drop rate: {cell['drop_rate']*100:.2f}%")
        print(f"    Interference: {cell['interference']:.3f}")
        print(f"    QoS Satisfaction: {cell['qos_satisfaction']:.2f}%")
        print(f"    Optimized Action: {cell['optimized_action']}")

    print("\n[OK] Data loader test passed!")
