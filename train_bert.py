"""
BERT Training Script for Certificate Fraud Detection
Fine-tunes BERT for binary classification (Fraud vs Genuine)

Usage:
    python train_bert.py --data_dir ./data --epochs 3 --batch_size 16
"""

import os
import argparse
import json
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    AdamW,
    get_linear_schedule_with_warmup
)
from sklearn.model_selection import train_test_split


# Dummy Dataset Class
class CertificateDataset(Dataset):
    """Dataset for certificate text classification."""
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
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
            'labels': torch.tensor(label, dtype=torch.long)
        }


def load_dummy_data():
    """
    Load or generate dummy dataset for training.
    In production, replace with actual certificate data.
    """
    # Sample genuine certificate text
    genuine_texts = [
        "This is to certify that John Doe has successfully completed the requirements for the Bachelor of Science degree in Computer Science from XYZ University on May 15, 2023.",
        "Certificate of Completion - This certifies that Jane Smith has completed the Advanced Python Programming course at ABC Training Center on March 20, 2023.",
        "Official Degree Certificate - Bachelor of Engineering in Electrical Engineering awarded to Michael Johnson by State University, May 2023.",
        "Certificate of Achievement - This is to certify that Sarah Williams has demonstrated exceptional performance in the Marketing Fundamentals course.",
        "Professional Certificate in Data Science - Awarded to David Brown for completing all requirements at DataTech Institute.",
        "This is to certify that Emily Davis has successfully completed the Master of Business Administration program at Global Business School.",
        "Certificate of Excellence - Awarded to Robert Wilson for outstanding achievement in Project Management certification.",
        "Official transcript and certificate for Bachelor of Arts in Psychology awarded to Jennifer Martinez on December 2022.",
        "Certificate of Professional Development - This certifies that Christopher Lee has completed 40 hours of continuing education.",
        "Master's Degree Certificate in Information Technology - Awarded to Amanda Taylor by Tech University, August 2023.",
    ]
    
    # Sample fraudulent certificate text
    fraud_texts = [
        "Fake certificate - This document certifies that John Doe has purchased a degree from Diploma Mill Inc. Not recognized by any authority.",
        "Forged certificate - Bachelor degree purchased online. This is not an authentic academic credential.",
        "Counterfeit certificate - WARNING: This certificate is fake and was issued by an unauthorized institution.",
        "This certificate is invalid and fake. Issued by a degree mill. Not valid for employment.",
        "WARNING: This document is fraudulent. Certificate number has been altered. Not genuine.",
        "Fake diploma - Created using template. Not issued by any legitimate educational institution.",
        "Forged certificate - The seal and signature on this document have been counterfeited.",
        "This certificate is not valid. The issuing organization is not accredited. Fake credential.",
        "Counterfeit degree - Purchased from online scam. Not a legitimate academic credential.",
        "Fake certificate - Document has been modified. Original information has been altered.",
    ]
    
    texts = genuine_texts + fraud_texts
    labels = [0] * len(genuine_texts) + [1] * len(fraud_texts)
    
    return texts, labels


def train_model(model, train_loader, optimizer, scheduler, device):
    """Train the model for one epoch."""
    model.train()
    total_loss = 0
    
    for batch in train_loader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        optimizer.zero_grad()
        
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        loss = outputs.loss
        total_loss += loss.item()
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
    
    return total_loss / len(train_loader)


def evaluate_model(model, val_loader, device):
    """Evaluate the model."""
    model.eval()
    total_correct = 0
    total_samples = 0
    
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            
            predictions = torch.argmax(outputs.logits, dim=1)
            total_correct += (predictions == labels).sum().item()
            total_samples += labels.size(0)
    
    return total_correct / total_samples


def main(args):
    """Main training function."""
    print("=" * 50)
    print("BERT Training for Certificate Fraud Detection")
    print("=" * 50)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load tokenizer
    print("\nLoading tokenizer...")
    tokenizer = BertTokenizer.from_pretrained(args.model_name)
    
    # Load or generate data
    print("Loading dataset...")
    texts, labels = load_dummy_data()
    print(f"Total samples: {len(texts)} (Genuine: {labels.count(0)}, Fraud: {labels.count(1)})")
    
    # Split data
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"Training samples: {len(train_texts)}")
    print(f"Validation samples: {len(val_texts)}")
    
    # Create datasets
    train_dataset = CertificateDataset(train_texts, train_labels, tokenizer, args.max_length)
    val_dataset = CertificateDataset(val_texts, val_labels, tokenizer, args.max_length)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)
    
    # Load model
    print("\nLoading model...")
    model = BertForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=2
    )
    model.to(device)
    
    # Setup optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=args.learning_rate)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=total_steps
    )
    
    # Training loop
    print("\nStarting training...")
    best_accuracy = 0
    
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch + 1}/{args.epochs}")
        print("-" * 30)
        
        # Train
        train_loss = train_model(model, train_loader, optimizer, scheduler, device)
        print(f"Training Loss: {train_loss:.4f}")
        
        # Evaluate
        accuracy = evaluate_model(model, val_loader, device)
        print(f"Validation Accuracy: {accuracy:.4f}")
        
        # Save best model
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            output_dir = args.output_dir
            os.makedirs(output_dir, exist_ok=True)
            model.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)
            print(f"Best model saved with accuracy: {best_accuracy:.4f}")
    
    print("\n" + "=" * 50)
    print(f"Training completed! Best accuracy: {best_accuracy:.4f}")
    print(f"Model saved to: {args.output_dir}")
    print("=" * 50)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train BERT for Certificate Fraud Detection')
    
    parser.add_argument('--data_dir', type=str, default='./data', help='Directory for dataset')
    parser.add_argument('--model_name', type=str, default='bert-base-uncased', help='Pretrained model name')
    parser.add_argument('--output_dir', type=str, default='./trained_model', help='Output directory for model')
    parser.add_argument('--epochs', type=int, default=3, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=8, help='Batch size')
    parser.add_argument('--learning_rate', type=float, default=2e-5, help='Learning rate')
    parser.add_argument('--max_length', type=int, default=512, help='Maximum sequence length')
    
    args = parser.parse_args()
    main(args)
