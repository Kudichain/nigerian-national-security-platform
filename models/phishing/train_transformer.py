"""
DistilBERT-based Phishing Email Detection

Fine-tunes DistilBERT for detecting phishing emails based on subject + body text.
Lighter and faster than BERT while maintaining high accuracy.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    AdamW,
    get_linear_schedule_with_warmup
)
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, classification_report
import mlflow
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailDataset(Dataset):
    """Dataset for email classification"""
    
    def __init__(
        self,
        emails: pd.DataFrame,
        tokenizer: DistilBertTokenizer,
        max_length: int = 256
    ):
        self.emails = emails
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self) -> int:
        return len(self.emails)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        row = self.emails.iloc[idx]
        
        # Combine subject and body
        subject = str(row.get('subject', ''))
        body = str(row.get('body', ''))
        text = f"{subject} [SEP] {body}"
        
        label = int(row.get('label', 0))
        
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }


class PhishingTransformerTrainer:
    """Fine-tune DistilBERT for phishing detection"""
    
    def __init__(
        self,
        data_path: str = "data/phishing/emails_labeled.parquet",
        model_dir: str = "models/phishing",
        model_name: str = "distilbert-base-uncased",
        max_length: int = 256,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        epochs: int = 3
    ):
        self.data_path = Path(data_path)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
    
    def train(self):
        """Fine-tune DistilBERT model"""
        
        mlflow.set_experiment("phishing-transformer")
        
        with mlflow.start_run():
            # Log hyperparameters
            mlflow.log_params({
                "model_type": "DistilBERT",
                "model_name": self.model_name,
                "max_length": self.max_length,
                "batch_size": self.batch_size,
                "learning_rate": self.learning_rate,
                "epochs": self.epochs
            })
            
            # Load data
            logger.info(f"Loading data from {self.data_path}")
            df = pd.read_parquet(self.data_path)
            
            logger.info(f"Total emails: {len(df)}")
            if 'label' in df.columns:
                logger.info(f"Phishing emails: {df['label'].sum()} ({df['label'].mean()*100:.2f}%)")
            
            # Train/test split
            train_df, test_df = train_test_split(
                df,
                test_size=0.2,
                random_state=42,
                stratify=df['label'] if 'label' in df.columns else None
            )
            
            # Load tokenizer and model
            logger.info(f"Loading {self.model_name} tokenizer and model...")
            tokenizer = DistilBertTokenizer.from_pretrained(self.model_name)
            model = DistilBertForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=2
            ).to(self.device)
            
            # Create datasets
            train_dataset = EmailDataset(train_df.reset_index(drop=True), tokenizer, self.max_length)
            test_dataset = EmailDataset(test_df.reset_index(drop=True), tokenizer, self.max_length)
            
            train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
            test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)
            
            # Optimizer and scheduler
            optimizer = AdamW(model.parameters(), lr=self.learning_rate, eps=1e-8)
            
            total_steps = len(train_loader) * self.epochs
            scheduler = get_linear_schedule_with_warmup(
                optimizer,
                num_warmup_steps=int(0.1 * total_steps),  # 10% warmup
                num_training_steps=total_steps
            )
            
            # Training loop
            best_f1 = 0.0
            
            for epoch in range(self.epochs):
                logger.info(f"Epoch {epoch + 1}/{self.epochs}")
                
                # Training
                model.train()
                train_loss = 0.0
                train_steps = 0
                
                for batch in train_loader:
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['label'].to(self.device)
                    
                    model.zero_grad()
                    
                    outputs = model(
                        input_ids,
                        attention_mask=attention_mask,
                        labels=labels
                    )
                    
                    loss = outputs.loss
                    train_loss += loss.item()
                    train_steps += 1
                    
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    optimizer.step()
                    scheduler.step()
                    
                    if train_steps % 50 == 0:
                        logger.info(f"  Step {train_steps}/{len(train_loader)}, Loss: {loss.item():.4f}")
                
                train_loss /= len(train_loader)
                
                # Validation
                model.eval()
                test_loss = 0.0
                all_preds = []
                all_labels = []
                all_probs = []
                
                with torch.no_grad():
                    for batch in test_loader:
                        input_ids = batch['input_ids'].to(self.device)
                        attention_mask = batch['attention_mask'].to(self.device)
                        labels = batch['label'].to(self.device)
                        
                        outputs = model(
                            input_ids,
                            attention_mask=attention_mask,
                            labels=labels
                        )
                        
                        loss = outputs.loss
                        test_loss += loss.item()
                        
                        logits = outputs.logits
                        probs = torch.softmax(logits, dim=1)
                        preds = torch.argmax(logits, dim=1)
                        
                        all_preds.extend(preds.cpu().numpy())
                        all_labels.extend(labels.cpu().numpy())
                        all_probs.extend(probs[:, 1].cpu().numpy())
                
                test_loss /= len(test_loader)
                
                # Calculate metrics
                all_preds = np.array(all_preds)
                all_labels = np.array(all_labels)
                all_probs = np.array(all_probs)
                
                precision, recall, f1, _ = precision_recall_fscore_support(
                    all_labels, all_preds, average='binary'
                )
                auc = roc_auc_score(all_labels, all_probs)
                
                logger.info(
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
                    model.save_pretrained(self.model_dir / "distilbert_best")
                    tokenizer.save_pretrained(self.model_dir / "distilbert_best")
                    logger.info(f"Saved best model with F1: {f1:.4f}")
            
            # Log classification report
            logger.info("\nClassification Report:")
            logger.info(classification_report(
                all_labels, all_preds, target_names=['Legitimate', 'Phishing']
            ))
            
            # Log model artifacts
            mlflow.log_artifact(str(self.model_dir / "distilbert_best"))
            
            logger.info(f"Training complete. Best F1: {best_f1:.4f}")


if __name__ == "__main__":
    trainer = PhishingTransformerTrainer(
        model_name="distilbert-base-uncased",
        max_length=256,
        batch_size=16,
        learning_rate=2e-5,
        epochs=3
    )
    trainer.train()
