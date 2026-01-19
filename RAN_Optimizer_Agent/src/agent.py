"""
Intelligent Agent for RAN Optimization
Uses Deep Q-Learning (DQN) for learning and optimization
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

class DQNetwork(nn.Module):
    """Neural network for reinforcement learning"""

    def __init__(self, state_size, action_size):
        super(DQNetwork, self).__init__()

        # Layers
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, action_size)

        self.relu = nn.ReLU()

    def forward(self, state):
        """Forward pass to get Q-values"""
        x = self.relu(self.fc1(state))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        return self.fc4(x)


class RANOptimizationAgent:
    """
    Intelligent Agent for RAN Optimization

    Uses:
    - Deep Q-Learning for training
    - Experience Replay for efficient learning
    - Epsilon-Greedy for exploration
    """

    def __init__(self, state_size, action_size, config=None):
        self.state_size = state_size
        self.action_size = action_size

        # Hyperparameters
        self.gamma = 0.99          # Discount factor
        self.epsilon = 1.0         # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 64
        self.memory_size = 10000

        # Memory for past experiences
        self.memory = deque(maxlen=self.memory_size)

        # Neural networks
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.q_network = DQNetwork(state_size, action_size).to(self.device)
        self.target_network = DQNetwork(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)

        # Copy weights to target network
        self.update_target_network()

        # Training statistics
        self.training_stats = {
            'episode_rewards': [],
            'episode_losses': [],
            'epsilon_history': [],
            'avg_q_values': []
        }

    def update_target_network(self):
        """Update target network weights"""
        self.target_network.load_state_dict(self.q_network.state_dict())

    def remember(self, state, action, reward, next_state, done):
        """Store experience in memory"""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, training=True):
        """
        Select an action

        In training mode:
        - Random exploration (epsilon) or
        - Exploitation (choose best action)

        In test mode:
        - Always choose best action
        """

        # Random exploration
        if training and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)

        # Exploitation - choose best action
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            q_values = self.q_network(state_tensor)

        return q_values.argmax().item()

    def replay(self):
        """
        Train on random batch from memory
        (Experience Replay)
        """

        if len(self.memory) < self.batch_size:
            return None

        # Sample random batch
        batch = random.sample(self.memory, self.batch_size)

        states = []
        actions = []
        rewards = []
        next_states = []
        dones = []

        for state, action, reward, next_state, done in batch:
            states.append(state)
            actions.append(action)
            rewards.append(reward)
            next_states.append(next_state)
            dones.append(done)

        # Convert to tensors
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Calculate current Q-values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))

        # Calculate target Q-values
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values

        # Calculate loss
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)

        # Update network
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon (reduce exploration over time)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        return loss.item()

    def train(self, env, num_episodes=100, update_target_every=10):
        """
        Train the agent on the environment

        Args:
            env: RAN environment
            num_episodes: Number of episodes
            update_target_every: Update target network every N episodes
        """

        print("Starting training...")
        print(f"Episodes: {num_episodes}")
        print(f"State size: {self.state_size}")
        print(f"Actions: {self.action_size}")
        print(f"Device: {self.device}")
        print("="*60)

        for episode in range(num_episodes):
            state = env.reset()
            episode_reward = 0
            episode_losses = []

            done = False
            step = 0

            while not done:
                # Select action
                action = self.act(state, training=True)

                # Execute action
                next_state, reward, done, info = env.step(action)

                # Store experience
                self.remember(state, action, reward, next_state, done)

                # Train
                loss = self.replay()
                if loss is not None:
                    episode_losses.append(loss)

                episode_reward += reward
                state = next_state
                step += 1

            # Update target network
            if (episode + 1) % update_target_every == 0:
                self.update_target_network()

            # Save statistics
            self.training_stats['episode_rewards'].append(episode_reward)
            self.training_stats['episode_losses'].append(
                np.mean(episode_losses) if episode_losses else 0
            )
            self.training_stats['epsilon_history'].append(self.epsilon)

            # Display progress
            if (episode + 1) % 10 == 0:
                avg_reward = np.mean(self.training_stats['episode_rewards'][-10:])
                print(f"Episode {episode + 1}/{num_episodes}")
                print(f"  Avg reward (last 10): {avg_reward:.2f}")
                print(f"  Epsilon: {self.epsilon:.3f}")
                print(f"  Memory size: {len(self.memory)}")

                # Show network statistics
                stats = env.get_network_stats()
                print(f"  Avg throughput: {stats['avg_throughput']:.1f} Mbps")
                print(f"  Avg drop rate: {stats['avg_drop_rate']*100:.2f}%")
                print(f"  Avg satisfaction: {stats['avg_satisfaction']:.1f}/100")
                print("-"*60)

        print("\nTraining complete!")
        return self.training_stats

    def evaluate(self, env, num_episodes=10, render=False):
        """
        Evaluate agent performance

        Args:
            env: RAN environment
            num_episodes: Number of evaluation episodes
            render: Whether to display details
        """

        print("\nStarting evaluation...")
        print(f"Episodes: {num_episodes}")

        eval_rewards = []
        network_stats_history = []

        for episode in range(num_episodes):
            state = env.reset()
            episode_reward = 0
            done = False

            while not done:
                # Select best action (no exploration)
                action = self.act(state, training=False)

                # Execute action
                next_state, reward, done, info = env.step(action)

                episode_reward += reward
                state = next_state

                if render and episode == 0:
                    env.render()

            eval_rewards.append(episode_reward)

            # Save network statistics
            stats = env.get_network_stats()
            network_stats_history.append(stats)

            print(f"Episode {episode + 1}: reward = {episode_reward:.2f}")

        # Calculate averages
        avg_reward = np.mean(eval_rewards)
        avg_throughput = np.mean([s['avg_throughput'] for s in network_stats_history])
        avg_drop_rate = np.mean([s['avg_drop_rate'] for s in network_stats_history])
        avg_satisfaction = np.mean([s['avg_satisfaction'] for s in network_stats_history])

        print("\n" + "="*60)
        print("Evaluation results:")
        print("="*60)
        print(f"Average reward: {avg_reward:.2f}")
        print(f"Average throughput: {avg_throughput:.1f} Mbps")
        print(f"Average drop rate: {avg_drop_rate*100:.2f}%")
        print(f"Average user satisfaction: {avg_satisfaction:.1f}/100")
        print("="*60)

        return {
            'avg_reward': avg_reward,
            'avg_throughput': avg_throughput,
            'avg_drop_rate': avg_drop_rate,
            'avg_satisfaction': avg_satisfaction,
            'network_stats_history': network_stats_history
        }

    def save(self, filepath):
        """Save model"""
        torch.save({
            'q_network_state': self.q_network.state_dict(),
            'target_network_state': self.target_network.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_stats': self.training_stats
        }, filepath)
        print(f"Model saved to: {filepath}")

    def load(self, filepath):
        """Load model"""
        checkpoint = torch.load(filepath)
        self.q_network.load_state_dict(checkpoint['q_network_state'])
        self.target_network.load_state_dict(checkpoint['target_network_state'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state'])
        self.epsilon = checkpoint['epsilon']
        self.training_stats = checkpoint['training_stats']
        print(f"Model loaded from: {filepath}")


if __name__ == "__main__":
    # Test the agent
    from ran_environment import RANEnvironment

    print("Testing intelligent agent...")

    # Create environment
    env = RANEnvironment(num_cells=5)

    # Create agent
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = RANOptimizationAgent(state_size, action_size)

    print(f"State size: {state_size}")
    print(f"Number of actions: {action_size}")

    # Test actions
    state = env.reset()
    for i in range(5):
        action = agent.act(state, training=True)
        next_state, reward, done, info = env.step(action)

        print(f"\nStep {i+1}:")
        print(f"  Action: {action}")
        print(f"  Reward: {reward:.2f}")

        agent.remember(state, action, reward, next_state, done)
        state = next_state

        if done:
            break

    print(f"\nMemory size: {len(agent.memory)}")
    print("Test successful!")
