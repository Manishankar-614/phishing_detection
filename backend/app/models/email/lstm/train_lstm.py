import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    matthews_corrcoef,
)
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[4]

DATA_DIR = BASE_DIR / "datasets" / "email" / "processed"
MODEL_DIR = BASE_DIR / "trained_models" / "email" / "lstm"

TRAIN_PATH = DATA_DIR / "train.csv"
VAL_PATH = DATA_DIR / "validation.csv"
TEST_PATH = DATA_DIR / "test.csv"


# ============================================================
# CONFIGURATION
# ============================================================

MAX_WORDS = 20000
MAX_SEQUENCE_LENGTH = 300

EMBEDDING_DIM = 128
LSTM_UNITS = 64

BATCH_SIZE = 64
EPOCHS = 10

RANDOM_SEED = 42


# Reproducibility
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    print("=" * 60)
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
# TOKENIZATION
# ============================================================

def prepare_text(train_df, val_df, test_df):

    print("\n" + "=" * 60)
    print("TOKENIZING EMAIL TEXT")
    print("=" * 60)

    tokenizer = Tokenizer(
        num_words=MAX_WORDS,
        oov_token="<OOV>"
    )

    # Fit tokenizer ONLY on training data
    tokenizer.fit_on_texts(train_df["email_text"].astype(str))

    X_train = tokenizer.texts_to_sequences(
        train_df["email_text"].astype(str)
    )

    X_val = tokenizer.texts_to_sequences(
        val_df["email_text"].astype(str)
    )

    X_test = tokenizer.texts_to_sequences(
        test_df["email_text"].astype(str)
    )

    # Padding
    X_train = pad_sequences(
        X_train,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post",
        truncating="post"
    )

    X_val = pad_sequences(
        X_val,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post",
        truncating="post"
    )

    X_test = pad_sequences(
        X_test,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post",
        truncating="post"
    )

    y_train = train_df["label"].values
    y_val = val_df["label"].values
    y_test = test_df["label"].values

    print(f"\nVocabulary size: {len(tokenizer.word_index):,}")
    print(f"Sequence length: {MAX_SEQUENCE_LENGTH}")

    print(f"\nX_train shape: {X_train.shape}")
    print(f"X_val shape  : {X_val.shape}")
    print(f"X_test shape : {X_test.shape}")

    return (
        tokenizer,
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    )


# ============================================================
# BUILD MODEL
# ============================================================

def build_model(vocab_size):

    model = tf.keras.Sequential([
        Embedding(
            input_dim=vocab_size,
            output_dim=EMBEDDING_DIM,
            input_length=MAX_SEQUENCE_LENGTH
        ),

        LSTM(
            LSTM_UNITS,
            return_sequences=False
        ),

        Dropout(0.3),

        Dense(
            32,
            activation="relu"
        ),

        Dropout(0.2),

        Dense(
            1,
            activation="sigmoid"
        )
    ])

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    return model


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(model, X_test, y_test):

    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    probabilities = model.predict(
        X_test,
        batch_size=BATCH_SIZE,
        verbose=1
    ).ravel()

    predictions = (probabilities >= 0.5).astype(int)

    accuracy = accuracy_score(y_test, predictions)

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )

    mcc = matthews_corrcoef(
        y_test,
        predictions
    )

    metrics = {
        "model": "LSTM",
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc),
        "mcc": float(mcc)
    }

    print("\nResults:")
    print(f"Accuracy  : {accuracy * 100:.2f}%")
    print(f"Precision : {precision * 100:.2f}%")
    print(f"Recall    : {recall * 100:.2f}%")
    print(f"F1-Score  : {f1 * 100:.2f}%")
    print(f"ROC-AUC   : {roc_auc * 100:.2f}%")
    print(f"MCC       : {mcc * 100:.2f}%")

    return metrics


# ============================================================
# MAIN
# ============================================================

def main():

    # Load datasets
    train_df, val_df, test_df = load_data()

    # Prepare text
    (
        tokenizer,
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = prepare_text(
        train_df,
        val_df,
        test_df
    )

    # Vocabulary size
    vocab_size = min(
        MAX_WORDS,
        len(tokenizer.word_index) + 1
    )

    # Build model
    print("\n" + "=" * 60)
    print("BUILDING LSTM MODEL")
    print("=" * 60)

    model = build_model(vocab_size)

    model.summary()

    # Early stopping
    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=2,
        restore_best_weights=True
    )

    # Train
    print("\n" + "=" * 60)
    print("TRAINING LSTM")
    print("=" * 60)

    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=[early_stopping],
        verbose=1
    )

    # Evaluate
    metrics = evaluate_model(
        model,
        X_test,
        y_test
    )

    # Create model directory
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save model
    model_path = MODEL_DIR / "lstm_email_model.keras"

    model.save(model_path)

    # Save tokenizer
    tokenizer_path = MODEL_DIR / "tokenizer.pkl"

    with open(tokenizer_path, "wb") as file:
        pickle.dump(tokenizer, file)

    # Save configuration
    config = {
        "max_words": MAX_WORDS,
        "max_sequence_length": MAX_SEQUENCE_LENGTH,
        "embedding_dim": EMBEDDING_DIM,
        "lstm_units": LSTM_UNITS,
        "threshold": 0.5
    }

    with open(
        MODEL_DIR / "config.json",
        "w"
    ) as file:
        json.dump(config, file, indent=4)

    # Save metrics
    with open(
        MODEL_DIR / "metrics.json",
        "w"
    ) as file:
        json.dump(metrics, file, indent=4)

    print("\n" + "=" * 60)
    print("LSTM TRAINING COMPLETE")
    print("=" * 60)

    print(f"\nModel saved to:")
    print(model_path)

    print(f"\nTokenizer saved to:")
    print(tokenizer_path)

    print(f"\nMetrics saved to:")
    print(MODEL_DIR / "metrics.json")


if __name__ == "__main__":
    main()