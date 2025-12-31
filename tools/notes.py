"""
Module 21: Note Taker
Création et gestion de notes textuelles
"""
import os
from datetime import datetime

class NoteTaker:
    def __init__(self, notes_dir="data/notes"):
        self.notes_dir = notes_dir
        os.makedirs(notes_dir, exist_ok=True)
    
    def create_note(self, title, content):
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{title}.txt"
        path = os.path.join(self.notes_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Created: {datetime.now()}\n")
            f.write(f"\n{content}")
        return path
    
    def list_notes(self):
        return [f for f in os.listdir(self.notes_dir) if f.endswith('.txt')]