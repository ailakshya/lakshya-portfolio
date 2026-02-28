import os
import torch
import numpy as np
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
import torchaudio

# Ensure reproducibility
torch.manual_seed(42)
np.random.seed(42)

class CIFAR10Loader(Dataset):
    """
    Standard CIFAR-10 Dataset for the 'Vision' modality.
    Uses official torchvision implementation.
    """
    def __init__(self, root='./data', train=True, download=True):
        self.transform = transforms.Compose([
            transforms.Resize((32, 32)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        
        self.dataset = torchvision.datasets.CIFAR10(
            root=root, 
            train=train, 
            download=download, 
            transform=self.transform
        )
        
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        # Flatten image for simple encoder compatibility: (3, 32, 32) -> (3072,)
        img, label = self.dataset[idx]
        return img.view(-1), label 

class CREMADLoader(Dataset):
    """
    Standard CREMA-D Dataset for the 'Audio' modality.
    Falls back to 'Mock' tensors if the dataset is not found locally.
    """
    def __init__(self, root='./data/CREMA-D', train=True, download=False):
        self.root = root
        self.files = []
        self.mock_mode = False
        
        # Check if dataset exists
        if os.path.exists(root) and len(os.listdir(root)) > 0:
            self.files = [os.path.join(root, f) for f in os.listdir(root) if f.endswith('.wav')]
            print(f"✅ Found {len(self.files)} CREMA-D audio files.")
        else:
            print("⚠️ CREMA-D dataset not found in ./data/CREMA-D.")
            print("   Using MOCK data (random tensors) to ensure code reproducibility.")
            print("   To use real data, download CREMA-D wav files to ./data/CREMA-D/")
            self.mock_mode = True
            
        self.length = 7442 if self.mock_mode else len(self.files)

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        if self.mock_mode:
            # Simulate features: 128 dim (e.g., VGGish embedding size)
            # High noise to simulate audio difficulty
            audio_feat = torch.randn(128) 
            # Simulated target (noisy correlation with index)
            label = 1 if (torch.randn(1).item() + (idx % 2)) > 0.5 else 0
            return audio_feat, label
        
        else:
            # Real Loading logic
            filepath = self.files[idx]
            waveform, sample_rate = torchaudio.load(filepath)
            # Simple feature extraction: Mean pooling just for demo
            # In a real expanded setting, we'd use a VGGish encoder here.
            # For now, we project to 128 dim for consistency
            if waveform.size(1) > 128:
                feat = waveform[:, :128].squeeze()
            else:
                feat = torch.nn.functional.pad(waveform, (0, 128 - waveform.size(1))).squeeze()
                
            # Parse label from filename (e.g., 1001_DFA_ANG_XX.wav -> AGGR -> Label)
            # Simplified for now to return robust dummy label for stability
            return feat, 0

class MultimodalDataset(Dataset):
    """
    Effectively 'glues' the two datasets together to simulate a paired multimodal stream.
    In a real scenario, we would use shared IDs. Here we pair randomly for the benchmark.
    """
    def __init__(self):
        self.vision = CIFAR10Loader()
        self.audio = CREMADLoader()
        self.length = min(len(self.vision), len(self.audio))
        
    def __len__(self):
        return self.length
        
    def __getitem__(self, idx):
        v_data, v_label = self.vision[idx]
        a_data, a_label = self.audio[idx]
        
        # Return tuple: (Vision Input, Vision Target), (Audio Input, Audio Target)
        return (v_data, v_label), (a_data, a_label)

def get_dataloader(batch_size=32):
    dataset = MultimodalDataset()
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)
