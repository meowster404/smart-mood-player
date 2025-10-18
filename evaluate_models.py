# -*- coding: utf-8 -*-
"""
Quick accuracy evaluation for Smart Mood Player models
"""

import pandas as pd
import numpy as np
import os
import sys
import pickle
from sklearn.metrics import accuracy_score, classification_report

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

def evaluate_models():
    """Evaluate existing models and return accuracy metrics"""
    results = {}

    # Use absolute paths based on script location
    models_dir = os.path.join(script_dir, 'models')
    data_dir = os.path.join(script_dir, 'data')

    if not os.path.exists(models_dir):
        return {"error": f"Models directory not found at {models_dir}"}

    # 1. Check Emotion Classifier
    emotion_model_path = os.path.join(models_dir, 'emotion_classifier.pkl')
    if os.path.exists(emotion_model_path):
        try:
            with open(emotion_model_path, 'rb') as f:
                emotion_model = pickle.load(f)

            print(f"Emotion model loaded: {type(emotion_model)}")

            # Load emotion data for evaluation
            emotion_data_path = os.path.join(data_dir, 'emotion_dataset_raw.csv')
            if os.path.exists(emotion_data_path):
                df = pd.read_csv(emotion_data_path)
                print(f"Data shape: {df.shape}")

                if 'text' in df.columns and 'emotion' in df.columns:
                    # Get sample for testing (limit to avoid memory issues)
                    sample_df = df.sample(n=min(1000, len(df)), random_state=42)
                    X_sample = sample_df['text'].tolist()
                    y_true = sample_df['emotion'].tolist()

                    # Try to predict (adjust based on your model's interface)
                    if hasattr(emotion_model, 'predict'):
                        try:
                            y_pred = emotion_model.predict(X_sample)
                            accuracy = accuracy_score(y_true, y_pred)
                            results['emotion_classifier'] = {
                                'accuracy': accuracy,
                                'samples_tested': len(X_sample),
                                'report': classification_report(y_true, y_pred, output_dict=True)
                            }
                        except Exception as e:
                            results['emotion_classifier'] = {"error": f"Prediction failed: {str(e)}"}
                    else:
                        results['emotion_classifier'] = {"error": "Model does not have predict method"}
                else:
                    results['emotion_classifier'] = {"error": f"Required columns not found in data: {list(df.columns)}"}
            else:
                results['emotion_classifier'] = {"error": f"Emotion dataset not found at {emotion_data_path}"}
        except Exception as e:
            results['emotion_classifier'] = {"error": f"Model loading failed: {str(e)}"}
    else:
        results['emotion_classifier'] = {"error": f"Model file not found at {emotion_model_path}"}

    # 2. Check Intent Detector
    intent_model_path = os.path.join(models_dir, 'chatbot_model.pkl')
    if os.path.exists(intent_model_path):
        try:
            with open(intent_model_path, 'rb') as f:
                intent_model = pickle.load(f)

            results['intent_detector'] = {
                "status": "Model loaded successfully - manual evaluation needed",
                "model_type": str(type(intent_model))
            }
        except Exception as e:
            results['intent_detector'] = {"error": f"Model loading failed: {str(e)}"}
    else:
        results['intent_detector'] = {"error": f"Model file not found at {intent_model_path}"}

    return results

if __name__ == "__main__":
    results = evaluate_models()
    print("Model Accuracy Results:")
    for model, result in results.items():
        print(f"\n{model.upper()}:")
        if isinstance(result, dict):
            if 'error' in result:
                print(f"  Error: {result['error']}")
            elif 'accuracy' in result:
                print(f"  Accuracy: {result['accuracy']:.2f}")
                print(f"  Samples Tested: {result.get('samples_tested', 'N/A')}")
                if 'report' in result:
                    print(f"  Report: {result['report']}")
            elif 'status' in result:
                print(f"  Status: {result['status']}")
                if 'model_type' in result:
                    print(f"  Model Type: {result['model_type']}")
            else:
                print(f"  Unknown result: {result}")
        else:
            print(f"  Invalid result type: {result}")