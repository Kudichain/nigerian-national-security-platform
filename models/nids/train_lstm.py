"""
LSTM-based Network Intrusion Detection for Time-Series Flow Data

Detects anomalies in sequential network flow patterns using LSTM/GRU networks.
Captures temporal dependencies that traditional models miss.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List
import mlflow
import mlflow.pytorch
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlowSequenceDataset(Dataset):
    """Dataset for network flow sequences"""
    
    def __init__(self, sequences: np.ndarray, labels: np.ndarray):
        self.sequences = torch.FloatTensor(sequences)
        self.labels = torch.FloatTensor(labels)
    
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.sequences[idx], self.labels[idx]


class FlowLSTM(nn.Module):
    """LSTM network for flow anomaly detection"""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.3,
        bidirectional: bool = True
    ):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
            bidirectional=bidirectional
        )
        
        lstm_output_size = hidden_size * 2 if bidirectional else hidden_size
        
        self.fc = nn.Sequential(
            nn.Linear(lstm_output_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch, seq_len, features)
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Use last hidden state from both directions
        if self.lstm.bidirectional:
            h_forward = h_n[-2]
            h_backward = h_n[-1]
            h_last = torch.cat([h_forward, h_backward], dim=1)
        else:
            h_last = h_n[-1]
        
        output = self.fc(h_last)
        return output.squeeze()


class NIDSLSTMTrainer:
    """Train LSTM models for network intrusion detection"""
    
    def __init__(
        self,
        data_path: str = "data/nids/netflow_labeled.parquet",
        model_dir: str = "models/nids",
        sequence_length: int = 10,
        hidden_size: int = 128,
        num_layers: int = 2,
        batch_size: int = 256,
        learning_rate: float = 0.001,
        epochs: int = 50
    ):
        self.data_path = Path(data_path)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
    
    def prepare_sequences(
        self,
        df: pd.DataFrame,
        sequence_length: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert flow records to sequences grouped by source IP
        
        Returns:
            sequences: (num_sequences, seq_len, num_features)
            labels: (num_sequences,) - 1 if any flow in sequence is malicious
        """
        # Sort by source IP and timestamp
        df = df.sort_values(['src_ip', 'timestamp'])
        
        feature_cols = [
            'bytes', 'packets', 'duration_ms', 'bytes_per_sec',
            'packets_per_sec', 'avg_packet_size', 'protocol_tcp',
            'protocol_udp', 'protocol_icmp', 'src_port', 'dest_port'
        ]
        
        sequences = []
        labels = []
        
        # Group by source IP
        for src_ip, group in df.groupby('src_ip'):
            group_features = group[feature_cols].values
            group_labels = group['label'].values
            
            # Create overlapping windows
            for i in range(len(group) - sequence_length + 1):
                seq = group_features[i:i + sequence_length]
                # Label as malicious if any flow in sequence is malicious
                label = 1 if group_labels[i:i + sequence_length].any() else 0
                
                sequences.append(seq)
                labels.append(label)
        
        return np.array(sequences), np.array(labels)
    
    def train(self):
        """Train LSTM model for network intrusion detection"""
        
        mlflow.set_experiment("nids-lstm")
        
        with mlflow.start_run():
            # Log hyperparameters
            mlflow.log_params({
                "model_type": "LSTM",
                "sequence_length": self.sequence_length,
                "hidden_size": self.hidden_size,
                "num_layers": self.num_layers,
                "batch_size": self.batch_size,
                "learning_rate": self.learning_rate,
                "epochs": self.epochs
            })
            
            # Load data
            logger.info(f"Loading data from {self.data_path}")
            df = pd.read_parquet(self.data_path)
            
            # Prepare sequences
            logger.info("Preparing sequences...")
            sequences, labels = self.prepare_sequences(df, self.sequence_length)
            logger.info(f"Created {len(sequences)} sequences")
            logger.info(f"Malicious sequences: {labels.sum()} ({labels.mean()*100:.2f}%)")
            
            # Scale features
            scaler = StandardScaler()
            num_samples, seq_len, num_features = sequences.shape
            sequences_reshaped = sequences.reshape(-1, num_features)
            sequences_scaled = scaler.fit_transform(sequences_reshaped)
            sequences_scaled = sequences_scaled.reshape(num_samples, seq_len, num_features)
            
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                sequences_scaled, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            # Create datasets
            train_dataset = FlowSequenceDataset(X_train, y_train)
            test_dataset = FlowSequenceDataset(X_test, y_test)
            
            train_loader = DataLoader(
                train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=0
            )
            test_loader = DataLoader(
                test_dataset, batch_size=self.batch_size, shuffle=False, num_workers=0
            )
            
            # Initialize model
            model = FlowLSTM(
                input_size=num_features,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                dropout=0.3,
                bidirectional=True
            ).to(self.device)
            
            logger.info(f"Model architecture:\n{model}")
            
            # Loss and optimizer
            # Use weighted loss for imbalanced data
            pos_weight = torch.tensor([1.0 / labels.mean()]).to(self.device)
            criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
            optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode='min', factor=0.5, patience=5
            )
            
            # Training loop
            best_f1 = 0.0
            
            for epoch in range(self.epochs):
                model.train()
                train_loss = 0.0
                
                for batch_x, batch_y in train_loader:
                    batch_x = batch_x.to(self.device)
                    batch_y = batch_y.to(self.device)
                    
                    optimizer.zero_grad()
                    outputs = model(batch_x)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    
                    # Gradient clipping
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    
                    optimizer.step()
                    train_loss += loss.item()
                
                train_loss /= len(train_loader)
                
                # Validation
                model.eval()
                test_loss = 0.0
                all_preds = []
                all_labels = []
                
                with torch.no_grad():
                    for batch_x, batch_y in test_loader:
                        batch_x = batch_x.to(self.device)
                        batch_y = batch_y.to(self.device)
                        
                        outputs = model(batch_x)
                        loss = criterion(outputs, batch_y)
                        test_loss += loss.item()
                        
                        preds = (torch.sigmoid(outputs) > 0.5).float()
                        all_preds.extend(preds.cpu().numpy())
                        all_labels.extend(batch_y.cpu().numpy())
                
                test_loss /= len(test_loader)
                scheduler.step(test_loss)
                
                # Calculate metrics
                from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
                
                all_preds = np.array(all_preds)
                all_labels = np.array(all_labels)
                
                precision, recall, f1, _ = precision_recall_fscore_support(
                    all_labels, all_preds, average='binary'
                )
                auc = roc_auc_score(all_labels, all_preds)
                
                logger.info(
                    f"Epoch {epoch+1}/{self.epochs} - "
                    f"Train Loss: {train_loss:.4f}, Test Loss: {test_loss:.4f}, "
                    f"Precision: {precision:.4f}, Recall: {recall:.4f}, "
                    f"F1: {f1:.4f}, AUC: {auc:.4f}"
                )
                
                # Log metrics
                mlflow.log_metrics({
                    "train_loss": train_loss,
                    "test_loss": test_loss,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "auc_roc": auc
                }, step=epoch)
                
                # Save best model
                if f1 > best_f1:
                    best_f1 = f1
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'scaler': scaler,
                        'f1_score': f1
                    }, self.model_dir / "nids_lstm_best.pt")
                    logger.info(f"Saved best model with F1: {f1:.4f}")
            
            # Log final model
            mlflow.pytorch.log_model(model, "model")
            mlflow.log_artifact(str(self.model_dir / "nids_lstm_best.pt"))
            
            logger.info(f"Training complete. Best F1: {best_f1:.4f}")


if __name__ == "__main__":
    trainer = NIDSLSTMTrainer(
        sequence_length=10,
        hidden_size=128,
        num_layers=2,
        batch_size=256,
        epochs=50
    )
    trainer.train()
