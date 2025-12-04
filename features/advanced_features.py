"""
Advanced Feature Engineering with Graph Embeddings and Behavioral Patterns

Enhances traditional features with:
1. Node2Vec graph embeddings for entity relationships
2. Behavioral sequence patterns (n-grams)
3. Co-occurrence and temporal features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import networkx as nx
try:
    from node2vec import Node2Vec
    NODE2VEC_AVAILABLE = True
except ImportError:
    # Fallback when node2vec is not available
    NODE2VEC_AVAILABLE = False
    import warnings
    warnings.warn("node2vec package not available. Graph embedding features will be disabled.", UserWarning)
    
    class Node2Vec:
        """Mock Node2Vec class for when the package is not available"""
        def __init__(self, *args, **kwargs):
            raise ImportError("node2vec package not installed. Please install with: pip install node2vec")

from collections import Counter, defaultdict
from itertools import combinations
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphEmbeddingFeatures:
    """Generate graph embeddings for network entities"""
    
    def __init__(
        self,
        dimensions: int = 64,
        walk_length: int = 30,
        num_walks: int = 200,
        workers: int = 4
    ):
        self.dimensions = dimensions
        self.walk_length = walk_length
        self.num_walks = num_walks
        self.workers = workers
        self.embeddings = {}
    
    def fit(self, flows_df: pd.DataFrame, entity_col: str = 'src_ip') -> Dict[str, np.ndarray]:
        """
        Learn graph embeddings from network flow data
        
        Args:
            flows_df: DataFrame with network flows
            entity_col: Column containing entity identifiers
        
        Returns:
            Dictionary mapping entity -> embedding vector
        """
        if not NODE2VEC_AVAILABLE:
            logger.warning("Node2Vec not available. Returning empty embeddings.")
            return {}
        
        logger.info("Building communication graph...")
        
        # Build directed graph
        G = nx.DiGraph()
        
        for _, flow in flows_df.iterrows():
            src = flow['src_ip']
            dst = flow['dest_ip']
            
            # Weighted by number of flows
            if G.has_edge(src, dst):
                G[src][dst]['weight'] += 1
            else:
                G.add_edge(src, dst, weight=1)
        
        logger.info(f"Graph: {len(G.nodes())} nodes, {len(G.edges())} edges")
        
        # Train Node2Vec
        logger.info("Training Node2Vec...")
        node2vec = Node2Vec(
            G,
            dimensions=self.dimensions,
            walk_length=self.walk_length,
            num_walks=self.num_walks,
            workers=self.workers,
            p=1,  # Return parameter
            q=1   # In-out parameter
        )
        
        model = node2vec.fit(window=10, min_count=1, batch_words=4)
        
        # Extract embeddings
        for node in G.nodes():
            if node in model.wv:
                self.embeddings[node] = model.wv[node]
        
        logger.info(f"Learned embeddings for {len(self.embeddings)} entities")
        return self.embeddings
    
    def transform(self, entity: str) -> np.ndarray:
        """Get embedding for an entity"""
        if entity in self.embeddings:
            return self.embeddings[entity]
        else:
            # Return zero vector for unseen entities
            return np.zeros(self.dimensions)
    
    def get_embedding_features(self, flow_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add graph embedding features to flow records
        
        Returns:
            DataFrame with additional embedding columns
        """
        src_embeddings = np.array([self.transform(ip) for ip in flow_df['src_ip']])
        dst_embeddings = np.array([self.transform(ip) for ip in flow_df['dest_ip']])
        
        # Create column names
        src_cols = [f'src_embed_{i}' for i in range(self.dimensions)]
        dst_cols = [f'dst_embed_{i}' for i in range(self.dimensions)]
        
        # Concatenate
        result_df = flow_df.copy()
        for i, col in enumerate(src_cols):
            result_df[col] = src_embeddings[:, i]
        for i, col in enumerate(dst_cols):
            result_df[col] = dst_embeddings[:, i]
        
        # Cosine similarity between src and dst embeddings
        result_df['embed_similarity'] = np.sum(src_embeddings * dst_embeddings, axis=1) / (
            np.linalg.norm(src_embeddings, axis=1) * np.linalg.norm(dst_embeddings, axis=1) + 1e-8
        )
        
        return result_df


class BehavioralSequenceFeatures:
    """Extract behavioral patterns from event sequences"""
    
    def __init__(self, n: int = 3, top_k: int = 100):
        """
        Args:
            n: N-gram size
            top_k: Number of top n-grams to track
        """
        self.n = n
        self.top_k = top_k
        self.ngram_vocab = {}
    
    def fit(self, events_df: pd.DataFrame, session_col: str = 'session_id') -> Dict[tuple, int]:
        """
        Learn top n-grams from event sequences
        
        Args:
            events_df: DataFrame with events sorted by timestamp
            session_col: Column grouping events into sessions
        
        Returns:
            Dictionary of n-gram -> frequency
        """
        logger.info(f"Extracting {self.n}-grams from event sequences...")
        
        ngram_counts = Counter()
        
        # Group by session
        for session, group in events_df.groupby(session_col):
            events = group.sort_values('timestamp')['event_type'].tolist()
            
            # Generate n-grams
            for i in range(len(events) - self.n + 1):
                ngram = tuple(events[i:i + self.n])
                ngram_counts[ngram] += 1
        
        # Keep top-k
        self.ngram_vocab = dict(ngram_counts.most_common(self.top_k))
        logger.info(f"Top {len(self.ngram_vocab)} n-grams cover {sum(self.ngram_vocab.values())} occurrences")
        
        return self.ngram_vocab
    
    def transform(self, events_df: pd.DataFrame, session_col: str = 'session_id') -> pd.DataFrame:
        """
        Add n-gram occurrence features to event records
        
        Returns:
            DataFrame with n-gram indicator columns
        """
        result_df = events_df.copy()
        
        # Initialize n-gram columns
        for ngram in self.ngram_vocab.keys():
            col_name = f"ngram_{'_'.join(ngram[:2])}"  # Truncate for readability
            result_df[col_name] = 0
        
        # Count n-grams per session
        for session, group in events_df.groupby(session_col):
            events = group.sort_values('timestamp')['event_type'].tolist()
            session_idx = group.index
            
            # Generate n-grams
            session_ngrams = Counter()
            for i in range(len(events) - self.n + 1):
                ngram = tuple(events[i:i + self.n])
                if ngram in self.ngram_vocab:
                    session_ngrams[ngram] += 1
            
            # Assign to all events in session
            for ngram, count in session_ngrams.items():
                col_name = f"ngram_{'_'.join(ngram[:2])}"
                if col_name in result_df.columns:
                    result_df.loc[session_idx, col_name] = count
        
        return result_df


class EntityRelationshipFeatures:
    """Extract co-occurrence and temporal relationship features"""
    
    def __init__(self, time_window: int = 3600):
        """
        Args:
            time_window: Time window in seconds for co-occurrence
        """
        self.time_window = time_window
        self.entity_pairs = defaultdict(int)
        self.entity_stats = defaultdict(lambda: {'first_seen': None, 'last_seen': None, 'count': 0})
    
    def fit(self, events_df: pd.DataFrame, entity_col: str = 'user'):
        """
        Learn entity co-occurrence patterns
        
        Args:
            events_df: DataFrame with events
            entity_col: Column containing entity identifiers
        """
        logger.info("Learning entity relationship patterns...")
        
        events_df = events_df.sort_values('timestamp')
        events_df['ts'] = pd.to_datetime(events_df['timestamp'])
        
        # Track entity statistics
        for entity, group in events_df.groupby(entity_col):
            self.entity_stats[entity]['first_seen'] = group['ts'].min()
            self.entity_stats[entity]['last_seen'] = group['ts'].max()
            self.entity_stats[entity]['count'] = len(group)
        
        # Find co-occurring entities within time windows
        for i, row in events_df.iterrows():
            current_ts = row['ts']
            current_entity = row[entity_col]
            
            # Find events within time window
            window_mask = (
                (events_df['ts'] >= current_ts) &
                (events_df['ts'] <= current_ts + pd.Timedelta(seconds=self.time_window)) &
                (events_df[entity_col] != current_entity)
            )
            
            co_occurring = events_df[window_mask][entity_col].unique()
            
            for other_entity in co_occurring:
                pair = tuple(sorted([current_entity, other_entity]))
                self.entity_pairs[pair] += 1
        
        logger.info(f"Found {len(self.entity_pairs)} entity pairs")
    
    def transform(self, events_df: pd.DataFrame, entity_col: str = 'user') -> pd.DataFrame:
        """
        Add relationship features
        
        Returns:
            DataFrame with relationship features
        """
        result_df = events_df.copy()
        result_df['ts'] = pd.to_datetime(result_df['timestamp'])
        
        # Entity age (days since first seen)
        result_df['entity_age_days'] = result_df.apply(
            lambda row: (row['ts'] - self.entity_stats[row[entity_col]]['first_seen']).total_seconds() / 86400
            if row[entity_col] in self.entity_stats and self.entity_stats[row[entity_col]]['first_seen']
            else 0,
            axis=1
        )
        
        # Entity activity count
        result_df['entity_activity_count'] = result_df[entity_col].map(
            lambda e: self.entity_stats[e]['count'] if e in self.entity_stats else 0
        )
        
        # Number of unique co-occurring entities (network size)
        result_df['network_size'] = result_df[entity_col].map(
            lambda e: len([pair for pair in self.entity_pairs.keys() if e in pair])
        )
        
        result_df.drop('ts', axis=1, inplace=True)
        
        return result_df


class AdvancedFeatureExtractor:
    """Unified interface for all advanced features"""
    
    def __init__(
        self,
        use_graph_embeddings: bool = True,
        use_behavioral_sequences: bool = True,
        use_entity_relationships: bool = True
    ):
        self.use_graph_embeddings = use_graph_embeddings
        self.use_behavioral_sequences = use_behavioral_sequences
        self.use_entity_relationships = use_entity_relationships
        
        self.graph_embedder = GraphEmbeddingFeatures() if use_graph_embeddings else None
        self.sequence_extractor = BehavioralSequenceFeatures() if use_behavioral_sequences else None
        self.relationship_extractor = EntityRelationshipFeatures() if use_entity_relationships else None
    
    def fit_transform_network_flows(self, flows_df: pd.DataFrame) -> pd.DataFrame:
        """Add all advanced features to network flow data"""
        
        result_df = flows_df.copy()
        
        if self.use_graph_embeddings and self.graph_embedder:
            logger.info("Adding graph embedding features...")
            self.graph_embedder.fit(flows_df)
            result_df = self.graph_embedder.get_embedding_features(result_df)
        
        if self.use_entity_relationships and self.relationship_extractor:
            logger.info("Adding entity relationship features...")
            self.relationship_extractor.fit(flows_df, entity_col='src_ip')
            result_df = self.relationship_extractor.transform(result_df, entity_col='src_ip')
        
        return result_df
    
    def fit_transform_logs(self, logs_df: pd.DataFrame) -> pd.DataFrame:
        """Add all advanced features to log data"""
        
        result_df = logs_df.copy()
        
        if self.use_behavioral_sequences and self.sequence_extractor:
            logger.info("Adding behavioral sequence features...")
            self.sequence_extractor.fit(logs_df)
            result_df = self.sequence_extractor.transform(logs_df)
        
        if self.use_entity_relationships and self.relationship_extractor:
            logger.info("Adding entity relationship features...")
            self.relationship_extractor.fit(logs_df, entity_col='user')
            result_df = self.relationship_extractor.transform(logs_df, entity_col='user')
        
        return result_df


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    # Network flows
    flows_df = pd.read_parquet("data/nids/netflow_labeled.parquet")
    
    extractor = AdvancedFeatureExtractor()
    enhanced_flows = extractor.fit_transform_network_flows(flows_df)
    
    logger.info(f"Original features: {len(flows_df.columns)}")
    logger.info(f"Enhanced features: {len(enhanced_flows.columns)}")
    
    # Save
    output_path = Path("data/nids/netflow_advanced_features.parquet")
    enhanced_flows.to_parquet(output_path)
    logger.info(f"Saved to {output_path}")
