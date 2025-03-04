import numpy as np
import pandas as pd
import pickle
import gensim.downloader as api

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from fuzzywuzzy import fuzz
from config import (
    MODEL_PATH,
    PRIORITY_KEY_WORDS,
    NON_PRIORITY_KEY_WORDS,
    PRIORITY_MULTIPLIER,
    NON_PRIORITY_MULTIPLIER,
)
from urllib.parse import urlparse


class UrlRanker:
    def __init__(self, model_path=MODEL_PATH):
        """
        Init UrlRanker - Loads model from pkl if available.
        """
        self.model = None
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3), stop_words="english", max_features=500
        )
        self.word_vectors = api.load(
            "glove-wiki-gigaword-50"
        )  # Load pre-trained embeddings!
        self.model_path = model_path

        try:
            self.load_model()
        except FileNotFoundError:
            print(f"Model file '{model_path}' not found. Train a model first.")

    def train_model(self, df, save_path=MODEL_PATH):
        """
        Train Logistic Regression model and save it.
        """
        df["text"] = df["url"] + " " + df["anchor_text"]

        # TF-IDF feature extraction
        X_text = self.vectorizer.fit_transform(df["text"])

        # Fuzzy matching feature
        df["fuzzy_score"] = df["text"].apply(
            lambda x: max(
                [
                    fuzz.partial_ratio(x.lower(), keyword)
                    for keyword in PRIORITY_KEY_WORDS
                ]
            )
            * PRIORITY_MULTIPLIER
        )

        df["negative_score"] = df["text"].apply(
            lambda x: max(
                [fuzz.partial_ratio(x.lower(), term) for term in NON_PRIORITY_KEY_WORDS]
            )
        )
        # Penalize these terms by 95%
        df["fuzzy_score"] -= df["negative_score"] * NON_PRIORITY_MULTIPLIER

        # Word embedding similarity
        df["embedding_similarity"] = df["text"].apply(self._text_embedding_similarity)

        # URL depth score
        df["url_depth_score"] = df["url"].apply(self._url_depth_weighting)

        domain_weight = 0.5  # Deprioritize the domain
        X_text_scaled = X_text.toarray() * domain_weight  # Scale down text features

        # Combine features
        X_combined = np.hstack(
            (
                X_text.toarray(),
                df[["fuzzy_score", "embedding_similarity", "url_depth_score"]].values,
            )
        )
        y = df["label"]

        # Train with a test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_combined, y, test_size=0.2, random_state=1
        )

        # Train model!
        self.model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))
        self.model.fit(X_train, y_train)

        # Save model
        with open(save_path, "wb") as f:
            pickle.dump({"model": self.model, "vectorizer": self.vectorizer}, f)
        print(f"Model saved to {save_path}")

    def load_model(self, model_path=None):
        """
        Load pre-trained model from file.
        """
        path = model_path if model_path else self.model_path
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.vectorizer = data["vectorizer"]
        print(f"Model loaded from {path}")

    def rank_urls(self, urls, anchor_texts):
        """
        Rank URLs based on probability of relevance.
        """
        if not self.model:
            raise ValueError("Model not loaded. Train or load a model first.")

        df = pd.DataFrame({"url": urls, "anchor_text": anchor_texts})
        df["text"] = df["url"] + " " + df["anchor_text"]

        # Transform text using TF-IDF
        X_text = self.vectorizer.transform(df["text"])

        # Fuzzy matching feature
        df["fuzzy_score"] = df["text"].apply(
            lambda x: max(
                [
                    fuzz.partial_ratio(x.lower(), keyword)
                    for keyword in PRIORITY_KEY_WORDS
                ]
            )
            * PRIORITY_MULTIPLIER
        )

        df["negative_score"] = df["text"].apply(
            lambda x: max(
                [fuzz.partial_ratio(x.lower(), term) for term in NON_PRIORITY_KEY_WORDS]
            )
        )
        # Penalize these terms by 95%
        df["fuzzy_score"] -= df["negative_score"] * NON_PRIORITY_MULTIPLIER

        # Word embedding similarity
        df["embedding_similarity"] = df["text"].apply(self._text_embedding_similarity)

        # URL depth score
        df["url_depth_score"] = df["url"].apply(self._url_depth_weighting)

        # Combine features
        X_combined = np.hstack(
            (
                X_text.toarray(),
                df[["fuzzy_score", "embedding_similarity", "url_depth_score"]].values,
            )
        )

        # Predict relevance scores
        df["score"] = self.model.predict_proba(X_combined)[:, 1]

        # Sort by relevance
        df = df.sort_values(by="score", ascending=False)

        # Return url, score, and anchor_text
        return df[["url", "score", "anchor_text"]]

    def _text_embedding_similarity(self, text):
        """
        Compute average word embedding similarity for a given text.
        """
        words = text.lower().split()
        vectors = [
            self.word_vectors[word] for word in words if word in self.word_vectors
        ]
        if vectors:
            avg_vector = np.mean(vectors, axis=0)
            return np.linalg.norm(avg_vector)  # Convert vector to a single value
        return 0

    def _url_depth_weighting(self, url):
        """
        Assign more weight to deeper parts of the URL.
        Also reduce finance related keyword influence early in URL.
        """
        # Extract only the path (want to ignore domain)
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/")

        # No meaningful path, return 0
        if not path:
            return 0

        # Split to get depth
        parts = path.split("/")
        depth = len(parts)

        total_weight = 0.0
        total_penalty = 0.0

        for i, part in enumerate(parts):
            # More depth gets more weight
            depth_weight = (i + 1) ** 2.0

            # Stronger weight for deep prio words
            if any(keyword in part.lower() for keyword in PRIORITY_KEY_WORDS):
                total_weight += 1.5 * depth_weight

            # Stronger penalty for deep non prio words
            if any(term in part.lower() for term in NON_PRIORITY_KEY_WORDS):
                total_penalty += 2.0 * depth_weight

        # Normalize by total depth
        return (total_weight - total_penalty) / depth
