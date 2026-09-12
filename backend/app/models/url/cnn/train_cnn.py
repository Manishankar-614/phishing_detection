import json
import pickle
import re
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

from sklearn.preprocessing import StandardScaler


# ============================================================
# GPU CONFIGURATION
# ============================================================

print("=" * 60)
print("GPU CONFIGURATION")
print("=" * 60)

gpus = tf.config.list_physical_devices("GPU")

if gpus:
    print(f"GPU detected: {len(gpus)}")

    for gpu in gpus:
        print(f"  {gpu}")

    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(
                gpu,
                True
            )

        print("GPU memory growth: Enabled")

    except RuntimeError as error:
        print(
            f"GPU memory configuration warning: {error}"
        )

else:
    print("No TensorFlow GPU detected.")
    print("Training will use CPU.")

print("=" * 60)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[4]

DATA_DIR = (
    BASE_DIR
    / "datasets"
    / "url"
    / "processed"
)

MODEL_DIR = (
    BASE_DIR
    / "trained_models"
    / "url"
    / "cnn"
)

TRAIN_PATH = DATA_DIR / "train.csv"
VAL_PATH = DATA_DIR / "validation.csv"
TEST_PATH = DATA_DIR / "test.csv"


# ============================================================
# CONFIGURATION
# ============================================================

MAX_URL_LENGTH = 256

CHAR_EMBEDDING_DIM = 64

BATCH_SIZE = 32

EPOCHS = 15

LEARNING_RATE = 0.001

RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)


# ============================================================
# URL FEATURES
# ============================================================

URL_FEATURES = [
    "url_length",
    "digit_ratio",
    "special_char_ratio",
    "entropy_score",
    "suspicious_keyword_count",
    "path_depth",
    "subdomain_count",
    "tld_risk_score",
    "https_flag",
    "domain_length",
    "number_of_dots",
    "number_of_hyphens",
]


# ============================================================
# CHARACTER VOCABULARY
# ============================================================

def build_character_vocabulary(urls):

    print("\n" + "=" * 60)
    print("BUILDING URL CHARACTER VOCABULARY")
    print("=" * 60)

    characters = set()

    for url in urls:

        characters.update(
            str(url)
        )

    characters = sorted(
        characters
    )

    # 0 = padding / unknown
    char_to_index = {
        "<PAD>": 0
    }

    for index, character in enumerate(
        characters,
        start=1
    ):

        char_to_index[
            character
        ] = index

    print(
        f"\nCharacter vocabulary size: "
        f"{len(char_to_index)}"
    )

    print(
        f"Characters detected: "
        f"{len(characters)}"
    )

    return char_to_index


# ============================================================
# URL ENCODING
# ============================================================

def encode_urls(
    urls,
    char_to_index
):

    encoded = np.zeros(
        (
            len(urls),
            MAX_URL_LENGTH
        ),
        dtype=np.int32
    )

    for row_index, url in enumerate(urls):

        url = str(url)

        # Limit URL length
        url = url[
            :MAX_URL_LENGTH
        ]

        for char_index, character in enumerate(
            url
        ):

            encoded[
                row_index,
                char_index
            ] = char_to_index.get(
                character,
                0
            )

    return encoded


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("\n" + "=" * 60)
    print("LOADING URL DATA")
    print("=" * 60)

    train_df = pd.read_csv(
        TRAIN_PATH
    )

    val_df = pd.read_csv(
        VAL_PATH
    )

    test_df = pd.read_csv(
        TEST_PATH
    )

    print(
        f"\nTraining   : {len(train_df)}"
    )

    print(
        f"Validation : {len(val_df)}"
    )

    print(
        f"Testing    : {len(test_df)}"
    )

    return (
        train_df,
        val_df,
        test_df
    )


# ============================================================
# PREPARE NUMERICAL FEATURES
# ============================================================

def prepare_numeric_features(
    train_df,
    val_df,
    test_df
):

    print("\n" + "=" * 60)
    print("PREPARING URL FEATURES")
    print("=" * 60)

    scaler = StandardScaler()

    X_train_features = scaler.fit_transform(
        train_df[URL_FEATURES]
    )

    X_val_features = scaler.transform(
        val_df[URL_FEATURES]
    )

    X_test_features = scaler.transform(
        test_df[URL_FEATURES]
    )

    print(
        f"\nFeature count: "
        f"{len(URL_FEATURES)}"
    )

    return (
        X_train_features.astype(
            np.float32
        ),
        X_val_features.astype(
            np.float32
        ),
        X_test_features.astype(
            np.float32
        ),
        scaler
    )


# ============================================================
# BUILD MODEL
# ============================================================

def build_model(
    vocabulary_size
):

    print("\n" + "=" * 60)
    print("BUILDING URL CNN MODEL")
    print("=" * 60)

    # --------------------------------------------------------
    # URL character input
    # --------------------------------------------------------

    url_input = tf.keras.Input(
        shape=(
            MAX_URL_LENGTH,
        ),
        dtype=tf.int32,
        name="url_input"
    )

    # Character embedding
    x = tf.keras.layers.Embedding(
        input_dim=vocabulary_size,
        output_dim=CHAR_EMBEDDING_DIM,
        name="character_embedding"
    )(url_input)

    # --------------------------------------------------------
    # CNN block 1
    # --------------------------------------------------------

    x = tf.keras.layers.Conv1D(
        filters=128,
        kernel_size=3,
        padding="same",
        activation="relu",
        name="conv1d_3"
    )(x)

    x = tf.keras.layers.BatchNormalization(
        name="batch_norm_1"
    )(x)

    x = tf.keras.layers.MaxPooling1D(
        pool_size=2,
        name="max_pool_1"
    )(x)

    # --------------------------------------------------------
    # CNN block 2
    # --------------------------------------------------------

    x = tf.keras.layers.Conv1D(
        filters=128,
        kernel_size=5,
        padding="same",
        activation="relu",
        name="conv1d_5"
    )(x)

    x = tf.keras.layers.BatchNormalization(
        name="batch_norm_2"
    )(x)

    x = tf.keras.layers.MaxPooling1D(
        pool_size=2,
        name="max_pool_2"
    )(x)

    # --------------------------------------------------------
    # CNN block 3
    # --------------------------------------------------------

    x = tf.keras.layers.Conv1D(
        filters=256,
        kernel_size=7,
        padding="same",
        activation="relu",
        name="conv1d_7"
    )(x)

    x = tf.keras.layers.BatchNormalization(
        name="batch_norm_3"
    )(x)

    # --------------------------------------------------------
    # Global pooling
    # --------------------------------------------------------

    x = tf.keras.layers.GlobalMaxPooling1D(
        name="global_max_pool"
    )(x)

    # --------------------------------------------------------
    # URL feature input
    # --------------------------------------------------------

    feature_input = tf.keras.Input(
        shape=(
            len(URL_FEATURES),
        ),
        dtype=tf.float32,
        name="url_features"
    )

    feature_branch = tf.keras.layers.Dense(
        64,
        activation="relu",
        name="feature_dense"
    )(feature_input)

    feature_branch = tf.keras.layers.BatchNormalization(
        name="feature_batch_norm"
    )(feature_branch)

    feature_branch = tf.keras.layers.Dropout(
        0.25,
        name="feature_dropout"
    )(feature_branch)

    # --------------------------------------------------------
    # Combine CNN + numerical features
    # --------------------------------------------------------

    combined = tf.keras.layers.Concatenate(
        name="url_feature_fusion"
    )(
        [
            x,
            feature_branch
        ]
    )

    # --------------------------------------------------------
    # Classification layers
    # --------------------------------------------------------

    combined = tf.keras.layers.Dense(
        128,
        activation="relu",
        name="fusion_dense"
    )(combined)

    combined = tf.keras.layers.Dropout(
        0.40,
        name="fusion_dropout"
    )(combined)

    combined = tf.keras.layers.Dense(
        64,
        activation="relu",
        name="classification_dense"
    )(combined)

    combined = tf.keras.layers.Dropout(
        0.25,
        name="classification_dropout"
    )(combined)

    output = tf.keras.layers.Dense(
        1,
        activation="sigmoid",
        name="phishing_probability"
    )(combined)

    model = tf.keras.Model(
        inputs=[
            url_input,
            feature_input
        ],
        outputs=output,
        name="URL_CNN"
    )

    # --------------------------------------------------------
    # Compile
    # --------------------------------------------------------

    optimizer = tf.keras.optimizers.Adam(
        learning_rate=LEARNING_RATE
    )

    model.compile(
        optimizer=optimizer,
        loss="binary_crossentropy",
        metrics=[
            "accuracy"
        ]
    )

    return model


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    (
        train_df,
        val_df,
        test_df
    ) = load_data()

    # --------------------------------------------------------
    # Build character vocabulary
    #
    # IMPORTANT:
    # Vocabulary is built ONLY from training data.
    # --------------------------------------------------------

    char_to_index = build_character_vocabulary(
        train_df["url"].values
    )

    # --------------------------------------------------------
    # Encode URLs
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("ENCODING URL CHARACTERS")
    print("=" * 60)

    X_train_url = encode_urls(
        train_df["url"].values,
        char_to_index
    )

    X_val_url = encode_urls(
        val_df["url"].values,
        char_to_index
    )

    X_test_url = encode_urls(
        test_df["url"].values,
        char_to_index
    )

    print(
        f"\nX_train URL shape: "
        f"{X_train_url.shape}"
    )

    print(
        f"X_val URL shape  : "
        f"{X_val_url.shape}"
    )

    print(
        f"X_test URL shape : "
        f"{X_test_url.shape}"
    )

    # --------------------------------------------------------
    # Numerical features
    # --------------------------------------------------------

    (
        X_train_features,
        X_val_features,
        X_test_features,
        scaler
    ) = prepare_numeric_features(
        train_df,
        val_df,
        test_df
    )

    print(
        f"\nX_train features shape: "
        f"{X_train_features.shape}"
    )

    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    y_train = (
        train_df["label"]
        .values
        .astype(np.float32)
    )

    y_val = (
        val_df["label"]
        .values
        .astype(np.float32)
    )

    y_test = (
        test_df["label"]
        .values
        .astype(np.float32)
    )

    # --------------------------------------------------------
    # Build model
    # --------------------------------------------------------

    model = build_model(
        vocabulary_size=len(
            char_to_index
        )
    )

    print("\n")

    model.summary()

    # --------------------------------------------------------
    # Callbacks
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    model_path = (
        MODEL_DIR
        / "url_cnn_model.keras"
    )

    callbacks = [

        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
            verbose=1
        ),

        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(model_path),
            monitor="val_loss",
            save_best_only=True,
            verbose=1
        ),

        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1
        )
    ]

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("TRAINING URL CNN")
    print("=" * 60)

    history = model.fit(

        x={
            "url_input": X_train_url,
            "url_features": X_train_features
        },

        y=y_train,

        validation_data=(
            {
                "url_input": X_val_url,
                "url_features": X_val_features
            },
            y_val
        ),

        epochs=EPOCHS,

        batch_size=BATCH_SIZE,

        callbacks=callbacks,

        verbose=1
    )

    # --------------------------------------------------------
    # Load best model
    # --------------------------------------------------------

    model = tf.keras.models.load_model(
        model_path
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    probabilities = model.predict(
        {
            "url_input": X_test_url,
            "url_features": X_test_features
        },
        batch_size=BATCH_SIZE,
        verbose=1
    ).flatten()

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

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

    print("\nResults:")

    print(
        f"Accuracy  : "
        f"{accuracy * 100:.2f}%"
    )

    print(
        f"Precision : "
        f"{precision * 100:.2f}%"
    )

    print(
        f"Recall    : "
        f"{recall * 100:.2f}%"
    )

    print(
        f"F1-Score  : "
        f"{f1 * 100:.2f}%"
    )

    print(
        f"ROC-AUC   : "
        f"{roc_auc * 100:.2f}%"
    )

    print(
        f"MCC       : "
        f"{mcc * 100:.2f}%"
    )

    # --------------------------------------------------------
    # Save character vocabulary
    # --------------------------------------------------------

    vocabulary_path = (
        MODEL_DIR
        / "char_to_index.pkl"
    )

    with open(
        vocabulary_path,
        "wb"
    ) as file:

        pickle.dump(
            char_to_index,
            file
        )

    # --------------------------------------------------------
    # Save feature scaler
    # --------------------------------------------------------

    scaler_path = (
        MODEL_DIR
        / "feature_scaler.pkl"
    )

    with open(
        scaler_path,
        "wb"
    ) as file:

        pickle.dump(
            scaler,
            file
        )

    # --------------------------------------------------------
    # Save metrics
    # --------------------------------------------------------

    metrics = {

        "model": "URL_CNN",

        "accuracy": float(
            accuracy
        ),

        "precision": float(
            precision
        ),

        "recall": float(
            recall
        ),

        "f1_score": float(
            f1
        ),

        "roc_auc": float(
            roc_auc
        ),

        "mcc": float(
            mcc
        )
    }

    metrics_path = (
        MODEL_DIR
        / "metrics.json"
    )

    with open(
        metrics_path,
        "w"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # Save configuration
    # --------------------------------------------------------

    config = {

        "model": "URL_CNN",

        "max_url_length": MAX_URL_LENGTH,

        "character_embedding_dimension":
            CHAR_EMBEDDING_DIM,

        "batch_size": BATCH_SIZE,

        "epochs": EPOCHS,

        "learning_rate":
            LEARNING_RATE,

        "threshold": 0.5,

        "url_features":
            URL_FEATURES,

        "character_vocabulary_size":
            len(char_to_index),

        "tensorflow_gpu_available":
            bool(gpus),

        "gpu_count":
            len(gpus),

        "gpu_names": [
            str(gpu)
            for gpu in gpus
        ]
    }

    config_path = (
        MODEL_DIR
        / "training_config.json"
    )

    with open(
        config_path,
        "w"
    ) as file:

        json.dump(
            config,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # Save training history
    # --------------------------------------------------------

    history_path = (
        MODEL_DIR
        / "training_history.json"
    )

    history_data = {
        key: [
            float(value)
            for value in values
        ]
        for key, values
        in history.history.items()
    }

    with open(
        history_path,
        "w"
    ) as file:

        json.dump(
            history_data,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("URL CNN TRAINING COMPLETE")
    print("=" * 60)

    print(
        f"\nModel saved to:\n"
        f"{model_path}"
    )

    print(
        f"\nVocabulary saved to:\n"
        f"{vocabulary_path}"
    )

    print(
        f"\nScaler saved to:\n"
        f"{scaler_path}"
    )

    print(
        f"\nMetrics saved to:\n"
        f"{metrics_path}"
    )

    print(
        f"\nConfiguration saved to:\n"
        f"{config_path}"
    )


if __name__ == "__main__":
    main()