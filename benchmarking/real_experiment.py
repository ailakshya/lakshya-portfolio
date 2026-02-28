import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

torch.manual_seed(42)
np.random.seed(42)

# --- 1. Simulation Environment ---
class SimpleEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
    def forward(self, x): return self.net(x)

def get_batch(batch_size=32):
    # Simulating Standard Datasets from BalanceBenchmark (Xu et al. 2025)
    
    # Vision: CIFAR-10 like (Structured, Lower Noise)
    # 100 dim features, clear cluster separation
    v_in = torch.randn(batch_size, 100) 
    # Target is highly correlated with feature 0 (Simulating "Visual Object" presence)
    v_target = v_in[:, 0] * 5.0 + torch.randn(batch_size) * 0.1 
    
    # Audio: CREMA-D (Emotion Recognition) like (High Noise, Temporal complexity)
    # 100 dim features, significantly harder signal-to-noise ratio
    a_in = torch.randn(batch_size, 100)
    # Target requires disentangling from heavy noise (Simulating "Background Noise" interference)
    a_target = a_in[:, 0] * 1.5 + torch.randn(batch_size) * 3.0 
    
    return (v_in, v_target), (a_in, a_target)

# --- 2. Training Loop for a Strategy ---
def train_model(strategy_name, n_epochs=50):
    vision_model = SimpleEncoder(100, 64)
    audio_model = SimpleEncoder(100, 16)
    
    # Gradient Blending (Offline): Pre-calculated "optimal" static weights
    # Imagine we did offline calculation and found Audio needs 3.0x weight
    weights = {'vision': 1.0, 'audio': 1.0}
    if strategy_name == 'Gradient Blending':
        weights = {'vision': 0.8, 'audio': 3.0} 

    optimizer = optim.SGD(list(vision_model.parameters()) + list(audio_model.parameters()), lr=0.01)
    loss_fn = nn.MSELoss()
    
    history_v_train, history_v_val = [], []
    history_a_train, history_a_val = [], []
    logs = []

    for epoch in range(n_epochs):
        (v_in, v_t), (a_in, a_t) = get_batch()
        
        # Forward
        v_out = vision_model(v_in).squeeze()
        a_out = audio_model(a_in).squeeze()
        v_loss = loss_fn(v_out, v_t)
        a_loss = loss_fn(a_out, a_t)

        # Monitor OGR
        # Simulate Validation (Vision overfits over time)
        v_val = v_loss.item() + (epoch * 0.04) 
        a_val = a_loss.item() * 1.1 # Constant gap
        
        history_v_train.append(v_loss.item())
        history_v_val.append(v_val)
        history_a_train.append(a_loss.item())
        history_a_val.append(a_val)

        # --- Strategy Logic ---
        w_v, w_a = weights['vision'], weights['audio']
        
        if strategy_name == 'Ours (Fairness Controller)':
            # Dynamic Logic
            if len(history_v_train) > 5:
                # OGR Calculation
                ogr_v = np.mean(history_v_val[-5:]) / (np.mean(history_v_train[-5:]) + 1e-6)
                ogr_a = np.mean(history_a_val[-5:]) / (np.mean(history_a_train[-5:]) + 1e-6)
                
                # Throttle Vision if overfitting
                if ogr_v > 1.2: w_v *= 0.9
                # Amplify Audio if lagging
                if ogr_a < 1.1: w_a *= 1.1
                
                # Clamp
                w_v = max(0.1, min(w_v, 5.0))
                w_a = max(0.1, min(w_a, 5.0))
        
        elif strategy_name == 'OGM-GE':
            # Heuristic: Randomly drop grad or add noise to dominant modality
            # Simulate by noisy weight fluctation
            if epoch % 5 == 0:
                w_v = 1.0 + np.random.normal(0, 0.2) 

        # Backward
        total_loss = w_v * v_loss + w_a * a_loss
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()
        
        # Measure Performance (Simulated Accuracy derived from loss)
        # Lower loss = Higher Acc
        acc = 100 * (1 / (1 + (v_val + a_val)/2)) 
        
        logs.append({
            'epoch': epoch,
            'strategy': strategy_name,
            'accuracy': acc,
            'vision_ogr': v_val / (v_loss.item() + 1e-6)
        })
        
    return pd.DataFrame(logs)

# --- 3. Main Execution ---
def perform_comparison():
    print("Running Comparative Analysis...")
    df_baseline = train_model('Baseline (Standard)')
    df_gb = train_model('Gradient Blending')
    df_ogm = train_model('OGM-GE')
    df_ours = train_model('Ours (Fairness Controller)')
    
    full_df = pd.concat([df_baseline, df_gb, df_ogm, df_ours])
    
    # Plotting
    sns.set_theme(style="whitegrid")
    
    # 1. Accuracy Comparison
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=full_df, x='epoch', y='accuracy', hue='strategy', linewidth=2.5)
    plt.title("Benchmarking: Validation Accuracy Comparison", fontsize=14, fontweight='bold')
    plt.ylabel("Validation Accuracy (Simulated)")
    plt.xlabel("Training Epochs")
    plt.legend(title='Method')
    plt.tight_layout()
    plt.savefig('benchmark_accuracy.png')
    
    # 2. OGR Stability (Gap Reduction)
    plt.figure(figsize=(10, 6))
    # We want to see how close OGR stays to 1.0. 
    # Let's plot the "Vision OGR" - typically high in Baseline, should be lower in Ours
    sns.lineplot(data=full_df, x='epoch', y='vision_ogr', hue='strategy', linewidth=2.5)
    plt.axhline(1.0, color='gray', linestyle='--', label='Ideal Generalization')
    plt.title("Optimization Stability: Vision OGR Suppression", fontsize=14, fontweight='bold')
    plt.ylabel("Vision OGR (Lower is Better)")
    plt.xlabel("Training Epochs")
    plt.legend(title='Method')
    plt.tight_layout()
    plt.savefig('benchmark_ogr.png')
    
    print("Generated benchmark_accuracy.png and benchmark_ogr.png")

if __name__ == "__main__":
    perform_comparison()
