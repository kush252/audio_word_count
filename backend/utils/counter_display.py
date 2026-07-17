import os
import json
import threading
from typing import Dict
from tabulate import tabulate
from utils.logger import setup_logger

logger = setup_logger("CounterDisplay")

class CounterDisplay:
    def __init__(self, save_path: str = "counts.json"):
        self.counts: Dict[str, int] = {}
        self.save_path = save_path
        self.lock = threading.Lock()

    def update_count(self, keyword: str):
        with self.lock:
            self.counts[keyword] = self.counts.get(keyword, 0) + 1
            
    def display(self):
        """Clears console and prints the current counts."""
        with self.lock:
            # Sort by count descending
            sorted_counts = sorted(self.counts.items(), key=lambda item: item[1], reverse=True)
            table = [[k, v] for k, v in sorted_counts]
            
            # Use cls on Windows, clear on Unix
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("=========================================")
            print("        REAL-TIME KEYWORD COUNTS         ")
            print("=========================================")
            if table:
                print(tabulate(table, headers=["Keyword / Phrase", "Count"], tablefmt="simple"))
            else:
                print("Listening for keywords...")
            print("=========================================")
            
    def save(self):
        """Saves current counts to a JSON file."""
        with self.lock:
            try:
                with open(self.save_path, "w", encoding="utf-8") as f:
                    json.dump(self.counts, f, indent=4)
            except Exception as e:
                logger.error(f"Failed to save counts to {self.save_path}: {e}")
