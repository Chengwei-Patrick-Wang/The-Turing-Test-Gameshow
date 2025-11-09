"""
Database module for storing and retrieving game round history
Stores all answers (AI and human) for few-shot learning
"""

import sqlite3
import random
from datetime import datetime
from typing import List, Dict, Optional
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'game_history.db')

def init_database():
    """Initialize the database with the required schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create rounds table to track which round questions belong to
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rounds (
            round_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create answers table to store all answers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            is_ai BOOLEAN NOT NULL,
            ai_model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (round_id) REFERENCES rounds (round_id)
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_round_id ON answers(round_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_is_ai ON answers(is_ai)
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

def store_round(question: str, answers: List[Dict]) -> int:
    """
    Store a complete round in the database
    
    Args:
        question: The question asked in this round
        answers: List of answer dictionaries with keys:
                 - answer: str (the answer text)
                 - is_ai: bool (True if AI, False if human)
                 - ai_model: Optional[str] (e.g., "Opus 4", "Sonnet 4")
    
    Returns:
        round_id: The ID of the stored round
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Insert round
        cursor.execute(
            'INSERT INTO rounds (question) VALUES (?)',
            (question,)
        )
        round_id = cursor.lastrowid
        
        # Insert all answers for this round
        for ans in answers:
            cursor.execute(
                '''INSERT INTO answers (round_id, question, answer, is_ai, ai_model)
                   VALUES (?, ?, ?, ?, ?)''',
                (
                    round_id,
                    question,
                    ans['answer'],
                    ans['is_ai'],
                    ans.get('ai_model', None)
                )
            )
        
        conn.commit()
        print(f"✅ Stored round {round_id} with {len(answers)} answers")
        return round_id
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error storing round: {e}")
        raise
    finally:
        conn.close()

def get_random_sample(sample_size: int = 10, exclude_round_id: Optional[int] = None) -> List[Dict]:
    """
    Get a random sample of answers from the database for few-shot learning
    
    Args:
        sample_size: Number of samples to retrieve (default 10)
        exclude_round_id: Optional round ID to exclude (current round)
    
    Returns:
        List of answer dictionaries with keys:
        - question, answer, is_ai, ai_model, round_id
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get total count
        if exclude_round_id:
            cursor.execute(
                'SELECT COUNT(*) FROM answers WHERE round_id != ?',
                (exclude_round_id,)
            )
        else:
            cursor.execute('SELECT COUNT(*) FROM answers')
        
        total_count = cursor.fetchone()[0]
        
        if total_count == 0:
            return []
        
        # Get random sample
        actual_sample_size = min(sample_size, total_count)
        
        if exclude_round_id:
            cursor.execute(
                '''SELECT round_id, question, answer, is_ai, ai_model
                   FROM answers 
                   WHERE round_id != ?
                   ORDER BY RANDOM()
                   LIMIT ?''',
                (exclude_round_id, actual_sample_size)
            )
        else:
            cursor.execute(
                '''SELECT round_id, question, answer, is_ai, ai_model
                   FROM answers 
                   ORDER BY RANDOM()
                   LIMIT ?''',
                (actual_sample_size,)
            )
        
        rows = cursor.fetchall()
        
        samples = []
        for row in rows:
            samples.append({
                'round_id': row[0],
                'question': row[1],
                'answer': row[2],
                'is_ai': bool(row[3]),
                'ai_model': row[4]
            })
        
        return samples
        
    finally:
        conn.close()

def get_distinct_random_samples(sample_size: int = 10, num_samples: int = 2, 
                                exclude_round_id: Optional[int] = None) -> List[List[Dict]]:
    """
    Get multiple distinct random samples for different AI bots
    
    Args:
        sample_size: Size of each sample
        num_samples: Number of distinct samples to generate
        exclude_round_id: Optional round ID to exclude
    
    Returns:
        List of sample lists, one for each bot
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get total count
        if exclude_round_id:
            cursor.execute(
                'SELECT COUNT(*) FROM answers WHERE round_id != ?',
                (exclude_round_id,)
            )
        else:
            cursor.execute('SELECT COUNT(*) FROM answers')
        
        total_count = cursor.fetchone()[0]
        
        if total_count == 0:
            return [[] for _ in range(num_samples)]
        
        # If we have fewer than sample_size items, return the same sample for all
        if total_count <= sample_size:
            sample = get_random_sample(sample_size, exclude_round_id)
            return [sample for _ in range(num_samples)]
        
        # Get all available IDs
        if exclude_round_id:
            cursor.execute(
                'SELECT answer_id FROM answers WHERE round_id != ?',
                (exclude_round_id,)
            )
        else:
            cursor.execute('SELECT answer_id FROM answers')
        
        all_ids = [row[0] for row in cursor.fetchall()]
        
        # Create distinct samples
        samples = []
        used_ids = set()
        
        for i in range(num_samples):
            # Get available IDs (not yet used)
            available_ids = [id for id in all_ids if id not in used_ids]
            
            # If we've used too many, reset
            if len(available_ids) < sample_size:
                used_ids.clear()
                available_ids = all_ids.copy()
            
            # Sample from available IDs
            sample_ids = random.sample(available_ids, min(sample_size, len(available_ids)))
            used_ids.update(sample_ids)
            
            # Fetch the actual data
            placeholders = ','.join('?' * len(sample_ids))
            cursor.execute(
                f'''SELECT round_id, question, answer, is_ai, ai_model
                    FROM answers 
                    WHERE answer_id IN ({placeholders})''',
                sample_ids
            )
            
            rows = cursor.fetchall()
            sample = []
            for row in rows:
                sample.append({
                    'round_id': row[0],
                    'question': row[1],
                    'answer': row[2],
                    'is_ai': bool(row[3]),
                    'ai_model': row[4]
                })
            
            samples.append(sample)
        
        return samples
        
    finally:
        conn.close()

def get_database_stats() -> Dict:
    """Get statistics about the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM rounds')
        total_rounds = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM answers')
        total_answers = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM answers WHERE is_ai = 1')
        ai_answers = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM answers WHERE is_ai = 0')
        human_answers = cursor.fetchone()[0]
        
        return {
            'total_rounds': total_rounds,
            'total_answers': total_answers,
            'ai_answers': ai_answers,
            'human_answers': human_answers
        }
    finally:
        conn.close()

def format_examples_for_prompt(samples: List[Dict]) -> str:
    """
    Format database samples into a string for the AI prompt
    
    Args:
        samples: List of answer samples from database
    
    Returns:
        Formatted string with examples
    """
    if not samples:
        return ""
    
    examples = []
    for i, sample in enumerate(samples, 1):
        source = sample['ai_model'] if sample['is_ai'] and sample['ai_model'] else ('AI' if sample['is_ai'] else 'Human')
        examples.append(
            f"Example {i} (Round {sample['round_id']}, {source}):\n"
            f"Q: {sample['question']}\n"
            f"A: {sample['answer']}"
        )
    
    return "\n\n".join(examples)

# Initialize database when module is imported
if not os.path.exists(DB_PATH):
    init_database()
