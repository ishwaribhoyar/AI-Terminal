# memory.py - Persistent Memory System for IVERI AI

import json
import os
from datetime import datetime

# File paths for persistent storage
DATA_DIR = os.path.expanduser("~/iveri/data")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def load_json(filepath):
    """Load JSON file or return empty dict"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_json(filepath, data):
    """Save data to JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving to {filepath}: {e}")


class Memory:
    """Persistent memory storage for user information and notes"""
    
    def __init__(self):
        self.data = load_json(MEMORY_FILE)
        self.notes = load_json(NOTES_FILE)
    
    def remember(self, key, value):
        """
        Store a piece of information.
        
        Args:
            key: What to remember (e.g., "name", "favorite color")
            value: The value to remember
        
        Returns:
            Confirmation message
        """
        self.data[key.lower().strip()] = {
            "value": value,
            "saved_at": datetime.now().isoformat()
        }
        save_json(MEMORY_FILE, self.data)
        return f"I'll remember that your {key} is {value}."
    
    def recall(self, key):
        """
        Retrieve stored information.
        
        Args:
            key: What to recall
        
        Returns:
            The stored value or None
        """
        key = key.lower().strip()
        if key in self.data:
            return self.data[key]["value"]
        return None
    
    def forget(self, key):
        """
        Remove a stored memory.
        
        Args:
            key: What to forget
        
        Returns:
            Status message
        """
        key = key.lower().strip()
        if key in self.data:
            del self.data[key]
            save_json(MEMORY_FILE, self.data)
            return f"I've forgotten your {key}."
        return f"I don't have anything stored for {key}."
    
    def list_memories(self):
        """List all stored memories"""
        if not self.data:
            return "I don't have any memories stored yet. Tell me something to remember!"
        
        memories = []
        for key, info in self.data.items():
            memories.append(f"- Your {key} is {info['value']}")
        
        return "Here's what I remember about you:\n" + "\n".join(memories)
    
    # === NOTES SYSTEM ===
    
    def add_note(self, text):
        """
        Add a note.
        
        Args:
            text: Note content
        
        Returns:
            Confirmation message
        """
        note_id = str(len(self.notes) + 1)
        self.notes[note_id] = {
            "text": text,
            "created_at": datetime.now().isoformat()
        }
        save_json(NOTES_FILE, self.notes)
        return f"Note saved: {text}"
    
    def list_notes(self):
        """List all notes"""
        if not self.notes:
            return "You don't have any notes yet. Say 'add a note' to create one!"
        
        notes_list = []
        for note_id, note in self.notes.items():
            notes_list.append(f"Note {note_id}: {note['text']}")
        
        return "Your notes:\n" + "\n".join(notes_list)
    
    def delete_note(self, note_id):
        """
        Delete a specific note.
        
        Args:
            note_id: ID of note to delete
        
        Returns:
            Status message
        """
        if note_id in self.notes:
            del self.notes[note_id]
            save_json(NOTES_FILE, self.notes)
            return f"Note {note_id} deleted."
        return f"Note {note_id} not found."
    
    def clear_notes(self):
        """Clear all notes"""
        self.notes = {}
        save_json(NOTES_FILE, self.notes)
        return "All notes have been cleared."


# Global memory instance
memory = Memory()


def handle_memory_command(user_input):
    """
    Handle memory-related commands.
    
    Args:
        user_input: User's spoken text
    
    Returns:
        tuple: (handled: bool, response: str)
    """
    text = user_input.lower()
    
    # === REMEMBER COMMANDS ===
    # "remember my name is John" or "remember that my favorite color is blue"
    if 'remember my' in text or 'remember that my' in text:
        try:
            if ' is ' in text:
                # Split on " is " to get key and value
                parts = text.split(' is ', 1)
                key = parts[0].replace('remember my', '').replace('remember that my', '').strip()
                value = parts[1].strip()
                
                if key and value:
                    return True, memory.remember(key, value)
        except (IndexError, ValueError):
            pass
        
        return True, "I didn't understand what to remember. Try saying 'remember my name is John'."
    
    # === RECALL COMMANDS ===
    # "what is my name" or "what's my favorite color"
    if "what is my" in text or "what's my" in text:
        key = text.replace("what is my", "").replace("what's my", "").strip().rstrip("?")
        
        if key:
            value = memory.recall(key)
            if value:
                return True, f"Your {key} is {value}."
            else:
                return True, f"I don't know your {key} yet. Tell me to remember it!"
        
        return True, "What would you like me to recall?"
    
    # === FORGET COMMANDS ===
    # "forget my name"
    if 'forget my' in text:
        key = text.replace('forget my', '').strip()
        if key:
            return True, memory.forget(key)
    
    # === LIST MEMORIES ===
    if 'what do you remember' in text or 'list memories' in text or 'show memories' in text:
        return True, memory.list_memories()
    
    # === NOTE COMMANDS ===
    
    # "add a note buy milk" or "take a note call mom"
    if 'add a note' in text or 'make a note' in text or 'take a note' in text:
        note_text = text
        for phrase in ['add a note', 'make a note', 'take a note', 'that', 'to']:
            note_text = note_text.replace(phrase, '')
        note_text = note_text.strip()
        
        if note_text:
            return True, memory.add_note(note_text)
        return True, "What should I write in the note?"
    
    # "read my notes" or "show notes"
    if 'list notes' in text or 'read notes' in text or 'show notes' in text or 'my notes' in text:
        return True, memory.list_notes()
    
    # "clear notes" or "delete all notes"
    if 'clear notes' in text or 'delete all notes' in text:
        return True, memory.clear_notes()
    
    return False, None
