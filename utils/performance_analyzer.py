import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
from collections import defaultdict

class PerformanceAnalyzer:
    def __init__(self, log_dir="analysis_logs"):
        self.log_dir = log_dir
        self.metrics = defaultdict(list)
        self.session_start = datetime.now()
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize performance metrics
        self.reset_metrics()

    def reset_metrics(self):
        """Reset all metrics for a new session."""
        self.metrics = {
            'intent_accuracy': [],
            'mood_detection_accuracy': [],
            'song_search_relevance': [],
            'artist_match_accuracy': [],
            'response_times': [],
            'chat_satisfaction': [],
            'timestamps': []
        }

    def log_metric(self, metric_name, value):
        """Log a metric value with timestamp."""
        self.metrics[metric_name].append(value)
        self.metrics['timestamps'].append(datetime.now())

    def calculate_accuracy(self, predicted, actual):
        """Calculate accuracy between predicted and actual values."""
        return 1 if predicted == actual else 0

    def log_intent_detection(self, predicted_intent, actual_intent):
        """Log intent detection accuracy."""
        accuracy = self.calculate_accuracy(predicted_intent, actual_intent)
        self.log_metric('intent_accuracy', accuracy)

    def log_mood_detection(self, predicted_mood, actual_mood):
        """Log mood detection accuracy."""
        accuracy = self.calculate_accuracy(predicted_mood, actual_mood)
        self.log_metric('mood_detection_accuracy', accuracy)

    def log_song_search(self, relevance_score):
        """Log song search relevance (0-1)."""
        self.log_metric('song_search_relevance', relevance_score)

    def log_artist_match(self, match_score):
        """Log artist matching accuracy (0-1)."""
        self.log_metric('artist_match_accuracy', match_score)

    def log_response_time(self, response_time):
        """Log system response time in seconds."""
        self.log_metric('response_times', response_time)

    def log_chat_satisfaction(self, satisfaction_score):
        """Log chat interaction satisfaction score (0-1)."""
        self.log_metric('chat_satisfaction', satisfaction_score)

    def plot_performance_metrics(self, save_path=None):
        """Generate comprehensive performance visualization."""
        plt.style.use('seaborn')
        fig = plt.figure(figsize=(15, 10))
        
        # Define layout
        gs = plt.GridSpec(3, 2)
        
        # Accuracy Metrics Over Time
        ax1 = fig.add_subplot(gs[0, :])
        metrics_to_plot = ['intent_accuracy', 'mood_detection_accuracy', 
                          'song_search_relevance', 'artist_match_accuracy']
        
        for metric in metrics_to_plot:
            if self.metrics[metric]:  # Only plot if we have data
                plt.plot(range(len(self.metrics[metric])), 
                        self.metrics[metric], 
                        label=metric.replace('_', ' ').title(),
                        marker='o')
        
        plt.title('Performance Metrics Over Time')
        plt.xlabel('Interaction Number')
        plt.ylabel('Accuracy/Score')
        plt.legend()
        plt.grid(True)
        
        # Response Times Distribution
        ax2 = fig.add_subplot(gs[1, 0])
        if self.metrics['response_times']:
            sns.histplot(data=self.metrics['response_times'], bins=20, ax=ax2)
            ax2.set_title('Response Time Distribution')
            ax2.set_xlabel('Response Time (seconds)')
            ax2.set_ylabel('Frequency')
        
        # Chat Satisfaction Distribution
        ax3 = fig.add_subplot(gs[1, 1])
        if self.metrics['chat_satisfaction']:
            sns.boxplot(data=self.metrics['chat_satisfaction'], ax=ax3)
            ax3.set_title('Chat Satisfaction Distribution')
            ax3.set_ylabel('Satisfaction Score')
        
        # Overall Performance Summary
        ax4 = fig.add_subplot(gs[2, :])
        summary_data = {}
        for metric in metrics_to_plot:
            if self.metrics[metric]:
                summary_data[metric] = np.mean(self.metrics[metric])
        
        if summary_data:
            plt.bar(range(len(summary_data)), list(summary_data.values()))
            plt.xticks(range(len(summary_data)), 
                      [m.replace('_', ' ').title() for m in summary_data.keys()],
                      rotation=45)
            plt.title('Overall Performance Summary')
            plt.ylabel('Average Score')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    def generate_workflow_diagram(self, save_path=None):
        """Generate a workflow diagram showing the system's process flow."""
        from graphviz import Digraph
        
        dot = Digraph(comment='Smart Mood Player Workflow')
        dot.attr(rankdir='TB')
        
        # Add nodes
        dot.node('input', 'User Input')
        dot.node('intent', 'Intent Detection')
        dot.node('mood', 'Mood Analysis')
        dot.node('chat', 'Chatbot')
        dot.node('search', 'Music Search')
        dot.node('spotify', 'Spotify API')
        dot.node('output', 'Results Display')
        
        # Add edges
        dot.edge('input', 'intent')
        dot.edge('intent', 'mood')
        dot.edge('intent', 'chat')
        dot.edge('mood', 'search')
        dot.edge('chat', 'search')
        dot.edge('search', 'spotify')
        dot.edge('spotify', 'output')
        
        if save_path:
            dot.render(save_path, format='png', cleanup=True)
        
        return dot

    def save_session_data(self):
        """Save the current session's data to a JSON file."""
        session_data = {
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'metrics': {k: list(v) for k, v in self.metrics.items() if k != 'timestamps'},
            'timestamps': [ts.isoformat() for ts in self.metrics['timestamps']]
        }
        
        filename = f"session_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.log_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=4)
        
        return filepath

    def load_session_data(self, filepath):
        """Load session data from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.session_start = datetime.fromisoformat(data['session_start'])
        self.metrics = defaultdict(list)
        
        for metric, values in data['metrics'].items():
            self.metrics[metric] = values
            
        self.metrics['timestamps'] = [datetime.fromisoformat(ts) for ts in data['timestamps']]
        
        return data