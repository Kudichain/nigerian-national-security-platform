"""
Graph Neural Network for Lateral Movement Detection

Builds network topology graph from flow data and uses GNN to detect
multi-hop attack patterns (lateral movement, privilege escalation chains).
"""

import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, global_mean_pool
from torch_geometric.data import Data, DataLoader
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict
import networkx as nx
import mlflow
import mlflow.pytorch
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphSAGE(torch.nn.Module):
    """GraphSAGE model for graph classification"""
    
    def __init__(
        self,
        num_node_features: int,
        hidden_channels: int = 64,
        num_layers: int = 3,
        dropout: float = 0.3
    ):
        super().__init__()
        
        self.convs = torch.nn.ModuleList()
        self.convs.append(SAGEConv(num_node_features, hidden_channels))
        
        for _ in range(num_layers - 1):
            self.convs.append(SAGEConv(hidden_channels, hidden_channels))
        
        self.dropout = dropout
        
        # Graph-level classification
        self.lin1 = torch.nn.Linear(hidden_channels, hidden_channels // 2)
        self.lin2 = torch.nn.Linear(hidden_channels // 2, 1)
    
    def forward(self, x, edge_index, batch):
        # Node embeddings
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        
        # Graph-level pooling
        x = global_mean_pool(x, batch)
        
        # Classification
        x = F.relu(self.lin1(x))
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = torch.sigmoid(self.lin2(x))
        
        return x.squeeze()


class LateralMovementGNN:
    """Train GNN for detecting lateral movement attack patterns"""
    
    def __init__(
        self,
        data_path: str = "data/nids/netflow_labeled.parquet",
        model_dir: str = "models/nids",
        time_window: int = 300,  # 5 minutes
        hidden_channels: int = 64,
        num_layers: int = 3,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        epochs: int = 100
    ):
        self.data_path = Path(data_path)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.time_window = time_window
        self.hidden_channels = hidden_channels
        self.num_layers = num_layers
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
    
    def build_temporal_graphs(
        self,
        df: pd.DataFrame,
        time_window: int
    ) -> List[Tuple[Data, int]]:
        """
        Build temporal network graphs from flow data
        
        Args:
            df: DataFrame with columns [src_ip, dest_ip, timestamp, features, label]
            time_window: Time window in seconds for each graph
        
        Returns:
            List of (PyG Data object, graph_label)
        """
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Convert timestamps to seconds
        df['ts_seconds'] = pd.to_datetime(df['timestamp']).astype(int) // 10**9
        
        min_ts = df['ts_seconds'].min()
        max_ts = df['ts_seconds'].max()
        
        graphs = []
        
        # Create graphs for each time window
        for window_start in range(min_ts, max_ts, time_window):
            window_end = window_start + time_window
            
            # Get flows in this window
            window_df = df[
                (df['ts_seconds'] >= window_start) &
                (df['ts_seconds'] < window_end)
            ]
            
            if len(window_df) < 3:  # Skip small graphs
                continue
            
            # Build graph
            G = nx.DiGraph()
            
            # Map IPs to node indices
            ip_to_idx = {}
            node_features = []
            
            for _, flow in window_df.iterrows():
                src_ip = flow['src_ip']
                dest_ip = flow['dest_ip']
                
                # Add nodes if not exists
                if src_ip not in ip_to_idx:
                    ip_to_idx[src_ip] = len(ip_to_idx)
                    # Node features: degree centrality, flow stats
                    node_features.append([0.0] * 10)  # Will be updated
                
                if dest_ip not in ip_to_idx:
                    ip_to_idx[dest_ip] = len(ip_to_idx)
                    node_features.append([0.0] * 10)
                
                # Add edge with flow features
                src_idx = ip_to_idx[src_ip]
                dest_idx = ip_to_idx[dest_ip]
                
                G.add_edge(src_idx, dest_idx, weight=1.0)
            
            if len(G.nodes()) < 2:
                continue
            
            # Calculate node features
            node_features_list = []
            for node_idx in range(len(ip_to_idx)):
                if node_idx in G.nodes():
                    # Graph-based features
                    in_degree = G.in_degree(node_idx)
                    out_degree = G.out_degree(node_idx)
                    
                    # Aggregated flow features for this node
                    node_flows = window_df[
                        (window_df['src_ip'].map(ip_to_idx) == node_idx) |
                        (window_df['dest_ip'].map(ip_to_idx) == node_idx)
                    ]
                    
                    features = [
                        in_degree,
                        out_degree,
                        node_flows['bytes'].sum() if len(node_flows) > 0 else 0,
                        node_flows['packets'].sum() if len(node_flows) > 0 else 0,
                        node_flows['bytes_per_sec'].mean() if len(node_flows) > 0 else 0,
                        node_flows['packets_per_sec'].mean() if len(node_flows) > 0 else 0,
                        len(node_flows),
                        1.0 if (node_flows['protocol_tcp'].sum() > 0 if len(node_flows) > 0 else False) else 0.0,
                        1.0 if (node_flows['protocol_udp'].sum() > 0 if len(node_flows) > 0 else False) else 0.0,
                        1.0 if (node_flows['protocol_icmp'].sum() > 0 if len(node_flows) > 0 else False) else 0.0
                    ]
                else:
                    features = [0.0] * 10
                
                node_features_list.append(features)
            
            # Convert to PyTorch Geometric format
            edge_index = torch.tensor(list(G.edges()), dtype=torch.long).t().contiguous()
            x = torch.tensor(node_features_list, dtype=torch.float)
            
            # Graph label: 1 if any flow in window is malicious
            graph_label = 1 if window_df['label'].any() else 0
            
            data = Data(x=x, edge_index=edge_index, y=torch.tensor([graph_label], dtype=torch.float))
            
            graphs.append(data)
        
        logger.info(f"Built {len(graphs)} temporal graphs")
        return graphs
    
    def train(self):
        """Train GNN model"""
        
        mlflow.set_experiment("nids-gnn")
        
        with mlflow.start_run():
            # Log hyperparameters
            mlflow.log_params({
                "model_type": "GraphSAGE",
                "time_window": self.time_window,
                "hidden_channels": self.hidden_channels,
                "num_layers": self.num_layers,
                "batch_size": self.batch_size,
                "learning_rate": self.learning_rate,
                "epochs": self.epochs
            })
            
            # Load data
            logger.info(f"Loading data from {self.data_path}")
            df = pd.read_parquet(self.data_path)
            
            # Build temporal graphs
            logger.info("Building temporal network graphs...")
            graphs = self.build_temporal_graphs(df, self.time_window)
            
            # Split labels
            labels = [g.y.item() for g in graphs]
            logger.info(f"Malicious graphs: {sum(labels)} / {len(labels)} ({np.mean(labels)*100:.2f}%)")
            
            # Train/test split
            train_graphs, test_graphs = train_test_split(
                graphs, test_size=0.2, random_state=42, stratify=labels
            )
            
            # Scale node features
            scaler = StandardScaler()
            all_features = torch.cat([g.x for g in train_graphs], dim=0).numpy()
            scaler.fit(all_features)
            
            for g in train_graphs + test_graphs:
                g.x = torch.tensor(scaler.transform(g.x.numpy()), dtype=torch.float)
            
            # Create data loaders
            train_loader = DataLoader(train_graphs, batch_size=self.batch_size, shuffle=True)
            test_loader = DataLoader(test_graphs, batch_size=self.batch_size, shuffle=False)
            
            # Initialize model
            num_node_features = graphs[0].x.shape[1]
            
            model = GraphSAGE(
                num_node_features=num_node_features,
                hidden_channels=self.hidden_channels,
                num_layers=self.num_layers,
                dropout=0.3
            ).to(self.device)
            
            logger.info(f"Model architecture:\n{model}")
            
            # Loss and optimizer
            criterion = torch.nn.BCELoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode='min', factor=0.5, patience=10
            )
            
            # Training loop
            best_f1 = 0.0
            
            for epoch in range(self.epochs):
                model.train()
                train_loss = 0.0
                
                for batch in train_loader:
                    batch = batch.to(self.device)
                    
                    optimizer.zero_grad()
                    out = model(batch.x, batch.edge_index, batch.batch)
                    loss = criterion(out, batch.y)
                    loss.backward()
                    
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    optimizer.step()
                    
                    train_loss += loss.item()
                
                train_loss /= len(train_loader)
                
                # Validation
                model.eval()
                test_loss = 0.0
                all_preds = []
                all_labels = []
                all_probs = []
                
                with torch.no_grad():
                    for batch in test_loader:
                        batch = batch.to(self.device)
                        
                        out = model(batch.x, batch.edge_index, batch.batch)
                        loss = criterion(out, batch.y)
                        test_loss += loss.item()
                        
                        preds = (out > 0.5).float()
                        all_preds.extend(preds.cpu().numpy())
                        all_labels.extend(batch.y.cpu().numpy())
                        all_probs.extend(out.cpu().numpy())
                
                test_loss /= len(test_loader)
                scheduler.step(test_loss)
                
                # Calculate metrics
                all_preds = np.array(all_preds)
                all_labels = np.array(all_labels)
                all_probs = np.array(all_probs)
                
                precision, recall, f1, _ = precision_recall_fscore_support(
                    all_labels, all_preds, average='binary', zero_division=0
                )
                auc = roc_auc_score(all_labels, all_probs) if len(np.unique(all_labels)) > 1 else 0.0
                
                if epoch % 10 == 0:
                    logger.info(
                        f"Epoch {epoch+1}/{self.epochs} - "
                        f"Train Loss: {train_loss:.4f}, Test Loss: {test_loss:.4f}, "
                        f"Precision: {precision:.4f}, Recall: {recall:.4f}, "
                        f"F1: {f1:.4f}, AUC: {auc:.4f}"
                    )
                
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
                    }, self.model_dir / "gnn_lateral_movement_best.pt")
                    logger.info(f"Saved best model with F1: {f1:.4f}")
            
            mlflow.pytorch.log_model(model, "model")
            mlflow.log_artifact(str(self.model_dir / "gnn_lateral_movement_best.pt"))
            
            logger.info(f"Training complete. Best F1: {best_f1:.4f}")


if __name__ == "__main__":
    trainer = LateralMovementGNN(
        time_window=300,  # 5-minute windows
        hidden_channels=64,
        num_layers=3,
        batch_size=32,
        epochs=100
    )
    trainer.train()
