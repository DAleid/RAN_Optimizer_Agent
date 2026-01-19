# Quick Start Guide - RAN Optimizer

Get started with RAN Network Optimizer in 3 simple steps!

## Step 1: Install (2 minutes)

```bash
cd RAN_Optimizer_Agent
pip install -r requirements.txt
```

**What gets installed:**
- PyTorch (deep learning)
- NumPy (numerical computing)
- Gym (reinforcement learning)
- Matplotlib (plotting)
- Dash & Plotly (dashboard)

## Step 2: Verify (1 minute)

```bash
python test_simple.py
```

**Expected output:**
```
============================================================
SIMPLE TEST - RAN Optimizer
============================================================

[1/4] Testing libraries...
  OK - NumPy and PyTorch available

[2/4] Testing RAN Environment...
  OK - Environment works (5 cells, reward=-0.65)

[3/4] Testing Agent...
  OK - Agent works (device=cpu)

[4/4] Mini training (3 episodes)...
  Episode 1: reward=-35.20
  Episode 2: reward=-17.55
  Episode 3: reward=-25.01
  OK - Training works!

============================================================
SUCCESS - All tests passed!
============================================================
```

✅ If you see "SUCCESS" - you're ready to go!
❌ If you see errors - check [Troubleshooting](#troubleshooting)

## Step 3: Train & Watch (10 minutes)

### Option A: Full Training (Recommended)

```bash
cd src
python train_agent.py
```

**What happens:**
1. Creates RAN network with 10 cells
2. Trains agent for 100 episodes (~5-10 minutes)
3. Saves trained model to `results/`
4. Generates performance graphs
5. Runs A/B testing
6. Shows final results

**Expected output:**
```
==============================================================
  Training RAN Optimization Agent
==============================================================

1. Creating simulation environment...
✅ Created network with 10 cells

2. Creating intelligent agent...
✅ Agent created
   State size: 50
   Actions: 27

3. Starting training...
   Episodes: 100

Episode 10/100
  Avg reward (last 10): -12.45
  Epsilon: 0.905
  Avg throughput: 58.3 Mbps
  Avg drop rate: 5.23%
  Avg satisfaction: 65.2/100
------------------------------------------------------------
...
Episode 100/100
  Avg reward (last 10): 45.67
  Epsilon: 0.010
  Avg throughput: 78.1 Mbps
  Avg drop rate: 2.87%
  Avg satisfaction: 84.5/100
------------------------------------------------------------

Training complete! ✅
```

### Option B: Interactive Dashboard

```bash
cd src
python dashboard.py
```

Then open your browser to: **http://localhost:8050**

**You'll see:**
- 📊 Real-time network metrics
- 📈 Live throughput graph
- 📉 Drop rate monitoring
- 🎯 User satisfaction gauge
- ⚡ Power consumption by cell
- 📋 Detailed cell information table

Press `Ctrl+C` to stop the dashboard.

## Understanding Your Results

### Training Graphs

After training, check `results/training_results_*.png`:

**1. Reward Plot**
- Should trend upward → Agent is learning ✅
- High variance early is normal
- Look at moving average (red line)

**2. Loss Plot**
- Should trend downward
- Some spikes are OK
- Indicates learning progress

**3. Epsilon Plot**
- Decreases from 1.0 → 0.01
- Shows exploration → exploitation transition

**4. Improvement Summary**
- Compares first 10 vs last 10 episodes
- Should show positive improvement %

### Performance Metrics

**Good Results After 100 Episodes:**
- Avg Throughput: 70+ Mbps ✅
- Avg Drop Rate: <4% ✅
- User Satisfaction: 80+ ✅
- Reward trending up ✅

**If Results Are Poor:**
- Train for more episodes (200+)
- Check [Troubleshooting](#troubleshooting)
- Adjust hyperparameters (see GUIDE.md)

## What's Next?

### Experiment with Settings

**Try different network sizes:**
```python
# Edit train_agent.py
NUM_CELLS = 5    # Smaller, trains faster
NUM_CELLS = 20   # Larger, more realistic
```

**Train longer:**
```python
NUM_EPISODES = 200   # Better results
NUM_EPISODES = 50    # Faster testing
```

### Load and Use Trained Model

```python
from agent import RANOptimizationAgent
from ran_environment import RANEnvironment

# Create environment
env = RANEnvironment(num_cells=10)

# Create and load agent
agent = RANOptimizationAgent(
    state_size=env.observation_space.shape[0],
    action_size=env.action_space.n
)
agent.load('results/ran_agent_TIMESTAMP.pth')

# Use agent
state = env.reset()
action = agent.act(state, training=False)
print(f"Agent chose action: {action}")
```

### Customize Rewards

Edit `ran_environment.py`, find `_calculate_reward()`:

```python
# Prioritize throughput
reward += throughput_improvement * 1.0  # Increase weight

# Prioritize reliability
reward += drop_improvement * 500  # Increase weight

# Prioritize energy
reward += power_saving * 1.0  # Increase weight
```

## Troubleshooting

### Error: No module named 'torch'

**Solution:**
```bash
pip install torch numpy gym matplotlib
```

### Error: No module named 'dash'

**Solution:**
```bash
pip install dash plotly
```

### Agent not learning (reward stays negative)

**Try:**
1. Train longer: `NUM_EPISODES = 200`
2. Reduce complexity: `NUM_CELLS = 5`
3. Adjust learning rate in `agent.py`:
   ```python
   self.learning_rate = 0.0005  # Try lower value
   ```

### Training is slow

**Solutions:**
1. Reduce cells: `NUM_CELLS = 5`
2. Reduce episodes: `NUM_EPISODES = 50`
3. Check if GPU available:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should be True for GPU
   ```

### Dashboard won't open

**Try:**
```bash
# Different port
python dashboard.py --port 8080

# Check if port is free
netstat -an | find "8050"
```

### Encoding errors on Windows

Use the English test file:
```bash
python test_simple.py
```

Instead of:
```bash
cd src && python quick_test.py  # Has Arabic text
```

## Common Questions

**Q: How long does training take?**
A: 5-10 minutes for 100 episodes on CPU with 10 cells.

**Q: Can I use this on a real network?**
A: This is a simulator. For production, you'd need to integrate with real network APIs.

**Q: What's the difference between Idea #1 and Idea #2?**
A: Idea #1 (this project) = single agent optimizes everything. Idea #2 = multiple specialized agents that collaborate.

**Q: How can I improve performance?**
A:
1. Train longer (200+ episodes)
2. Tune hyperparameters
3. Adjust reward function
4. Use GPU if available

**Q: Where are the results saved?**
A:
- Model: `results/ran_agent_*.pth`
- Graphs: `results/training_results_*.png`
- A/B tests: `results/ab_test_results_*.json`

## Files You Need to Know

```
RAN_Optimizer_Agent/
├── src/
│   ├── train_agent.py      ← Run this to train
│   ├── dashboard.py        ← Run this for dashboard
│   ├── ran_environment.py  ← Network simulator (customize here)
│   ├── agent.py            ← AI agent (tune hyperparameters here)
│   └── ab_testing.py       ← A/B testing system
├── results/                ← Your trained models and graphs go here
├── test_simple.py          ← Run this first to verify setup
├── README_EN.md            ← Full documentation
└── GUIDE.md                ← Detailed guide (Arabic)
```

## Resources

**Documentation:**
- `README_EN.md` - Complete documentation
- `GUIDE.md` - Detailed guide (Arabic)
- `PROJECT_SUMMARY.md` - Technical overview

**Code Examples:**
- `test_simple.py` - Simple usage example
- `train_agent.py` - Full training pipeline
- `dashboard.py` - Visualization example

**Learn More:**
- Deep Q-Learning: [DeepMind Nature paper](https://www.nature.com/articles/nature14236)
- Reinforcement Learning: [Sutton & Barto book](http://incompleteideas.net/book/)
- PyTorch: [pytorch.org/tutorials](https://pytorch.org/tutorials/)

## Ready to Go!

You now have everything you need. Here's the simplest path:

```bash
# 1. Verify setup
python test_simple.py

# 2. Train the agent
cd src
python train_agent.py

# 3. Check results
# Open: results/training_results_*.png

# 4. (Optional) View live dashboard
python dashboard.py
# Open browser: http://localhost:8050
```

**Have fun experimenting! 🚀**

---

Need help? Check the detailed documentation in `README_EN.md` or `GUIDE.md`
