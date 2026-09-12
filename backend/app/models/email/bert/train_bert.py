import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    matthews_corrcoef,
)

from torch.utils.data import Dataset

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[4]

DATA_DIR = BASE_DIR / "datasets" / "email" / "processed"
MODEL_DIR = BASE_DIR / "trained_models" / "email" / "bert"

TRAIN_PATH = DATA_DIR / "train.csv"
VAL_PATH = DATA_DIR / "validation.csv"
TEST_PATH = DATA_DIR / "test.csv"


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "bert-base-uncased"

MAX_LENGTH = 256

# RTX 3050 4 GB VRAM
BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 2

EPOCHS = 3

LEARNING_RATE = 2e-5

RANDOM_SEED = 42


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 60)
print("DEVICE CONFIGURATION")
print("=" * 60)

print(f"Device       : {DEVICE}")
print(f"PyTorch      : {torch.__version__}")
print(f"CUDA         : {torch.version.cuda}")

if torch.cuda.is_available():
    print(
        f"GPU          : "
        f"{torch.cuda.get_device_name(0)}"
    )

    print(
        f"GPU Memory   : "
        f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
    )
else:
    print("GPU          : Not available")

print("=" * 60)


# ============================================================
# REPRODUCIBILITY
# ============================================================

np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_SEED)


# ============================================================
# DATASET CLASS
# ============================================================

class EmailDataset(Dataset):

    def __init__(self, texts, labels, tokenizer):

        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):

        return len(self.texts)

    def __getitem__(self, index):

        text = str(self.texts[index])
        label = int(self.labels[index])

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
            return_tensors="pt"
        )

        item = {
            key: value.squeeze(0)
            for key, value in encoding.items()
        }

        item["labels"] = torch.tensor(
            label,
            dtype=torch.long
        )

        return item


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("\n" + "=" * 60)
    print("LOADING EMAIL DATA")
    print("=" * 60)

    train_df = pd.read_csv(TRAIN_PATH)
    val_df = pd.read_csv(VAL_PATH)
    test_df = pd.read_csv(TEST_PATH)

    print(f"\nTraining   : {len(train_df)}")
    print(f"Validation : {len(val_df)}")
    print(f"Testing    : {len(test_df)}")

    return train_df, val_df, test_df


# ============================================================
# METRICS
# ============================================================

def compute_metrics(eval_prediction):

    logits = eval_prediction.predictions
    labels = eval_prediction.label_ids

    probabilities = torch.softmax(
        torch.tensor(logits),
        dim=1
    )[:, 1].numpy()

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    return {
        "accuracy": accuracy_score(
            labels,
            predictions
        ),

        "precision": precision_score(
            labels,
            predictions,
            zero_division=0
        ),

        "recall": recall_score(
            labels,
            predictions,
            zero_division=0
        ),

        "f1": f1_score(
            labels,
            predictions,
            zero_division=0
        ),

        "roc_auc": roc_auc_score(
            labels,
            probabilities
        ),

        "mcc": matthews_corrcoef(
            labels,
            predictions
        ),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    train_df, val_df, test_df = load_data()

    # --------------------------------------------------------
    # Load tokenizer
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("LOADING BERT TOKENIZER")
    print("=" * 60)

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    # --------------------------------------------------------
    # Create datasets
    # --------------------------------------------------------

    print("\nCreating tokenized datasets...")

    train_dataset = EmailDataset(
        train_df["email_text"].values,
        train_df["label"].values,
        tokenizer
    )

    val_dataset = EmailDataset(
        val_df["email_text"].values,
        val_df["label"].values,
        tokenizer
    )

    test_dataset = EmailDataset(
        test_df["email_text"].values,
        test_df["label"].values,
        tokenizer
    )

    # --------------------------------------------------------
    # Load BERT model
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("LOADING BERT MODEL")
    print("=" * 60)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2
    )

    # Explicitly move model to GPU
    model.to(DEVICE)

    # --------------------------------------------------------
    # Training arguments
    # --------------------------------------------------------

    training_args = TrainingArguments(
        output_dir=str(
            MODEL_DIR / "checkpoints"
        ),

        eval_strategy="epoch",

        save_strategy="epoch",

        learning_rate=LEARNING_RATE,

        per_device_train_batch_size=BATCH_SIZE,

        per_device_eval_batch_size=BATCH_SIZE,

        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,

        num_train_epochs=EPOCHS,

        weight_decay=0.01,

        load_best_model_at_end=True,

        metric_for_best_model="f1",

        greater_is_better=True,

        logging_steps=100,

        save_total_limit=2,

        report_to="none",

        seed=RANDOM_SEED,

        # Mixed precision for NVIDIA GPU
        fp16=torch.cuda.is_available(),
    )

    # --------------------------------------------------------
    # Trainer
    # --------------------------------------------------------

    trainer = Trainer(
        model=model,

        args=training_args,

        train_dataset=train_dataset,

        eval_dataset=val_dataset,

        compute_metrics=compute_metrics,

        callbacks=[
            EarlyStoppingCallback(
                early_stopping_patience=1
            )
        ],
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("TRAINING BERT")
    print("=" * 60)

    print(f"Device                  : {DEVICE}")
    print(f"Batch size              : {BATCH_SIZE}")
    print(
        f"Gradient accumulation  : "
        f"{GRADIENT_ACCUMULATION_STEPS}"
    )
    print(
        f"Effective batch size    : "
        f"{BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS}"
    )
    print(f"Maximum sequence length : {MAX_LENGTH}")

    print(f"Epochs                  : {EPOCHS}")

    trainer.train()

    # --------------------------------------------------------
    # Test evaluation
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("TEST SET EVALUATION")
    print("=" * 60)

    test_results = trainer.predict(
        test_dataset
    )

    logits = test_results.predictions
    labels = test_results.label_ids

    probabilities = torch.softmax(
        torch.tensor(logits),
        dim=1
    )[:, 1].numpy()

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    accuracy = accuracy_score(
        labels,
        predictions
    )

    precision = precision_score(
        labels,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        labels,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        labels,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        labels,
        probabilities
    )

    mcc = matthews_corrcoef(
        labels,
        predictions
    )

    metrics = {
        "model": "BERT",
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc),
        "mcc": float(mcc)
    }

    print("\nResults:")

    print(
        f"Accuracy  : {accuracy * 100:.2f}%"
    )

    print(
        f"Precision : {precision * 100:.2f}%"
    )

    print(
        f"Recall    : {recall * 100:.2f}%"
    )

    print(
        f"F1-Score  : {f1 * 100:.2f}%"
    )

    print(
        f"ROC-AUC   : {roc_auc * 100:.2f}%"
    )

    print(
        f"MCC       : {mcc * 100:.2f}%"
    )

    # --------------------------------------------------------
    # Create model directories
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    FINAL_MODEL_DIR = MODEL_DIR / "final"

    FINAL_MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    trainer.save_model(
        str(FINAL_MODEL_DIR)
    )

    # --------------------------------------------------------
    # Save tokenizer
    # --------------------------------------------------------

    tokenizer.save_pretrained(
        str(FINAL_MODEL_DIR)
    )

    # --------------------------------------------------------
    # Save configuration
    # --------------------------------------------------------

    config = {
        "model_name": MODEL_NAME,
        "max_length": MAX_LENGTH,
        "batch_size": BATCH_SIZE,
        "gradient_accumulation_steps": (
            GRADIENT_ACCUMULATION_STEPS
        ),
        "effective_batch_size": (
            BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS
        ),
        "epochs": EPOCHS,
        "learning_rate": LEARNING_RATE,
        "threshold": 0.5,
        "device": str(DEVICE),
        "cuda_available": bool(
            torch.cuda.is_available()
        ),
        "gpu_name": (
            torch.cuda.get_device_name(0)
            if torch.cuda.is_available()
            else None
        )
    }

    with open(
        FINAL_MODEL_DIR / "training_config.json",
        "w"
    ) as file:

        json.dump(
            config,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # Save metrics
    # --------------------------------------------------------

    with open(
        FINAL_MODEL_DIR / "metrics.json",
        "w"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("BERT TRAINING COMPLETE")
    print("=" * 60)

    print(
        f"\nModel saved to:\n{FINAL_MODEL_DIR}"
    )

    print(
        f"\nMetrics saved to:\n"
        f"{FINAL_MODEL_DIR / 'metrics.json'}"
    )


if __name__ == "__main__":
    main()