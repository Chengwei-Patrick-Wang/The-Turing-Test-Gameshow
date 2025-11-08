"""
Database module for storing and retrieving game responses
Stores AI and human responses to help AI improve over time
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DB_FILE = 'gameshow.db'
MAX_HISTORICAL_ROUNDS = 15  # Use last 15 rounds for AI context

def get_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_database():
    """Initialize the database schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for storing prompts/questions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for storing responses (both AI and human)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER NOT NULL,
            response_text TEXT NOT NULL,
            is_ai BOOLEAN NOT NULL,
            author_id TEXT,
            model_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prompt_id) REFERENCES prompts (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_round_data(prompt: str, responses: List[Dict]) -> int:
    """
    Save a round's prompt and all responses to the database
    
    Args:
        prompt: The question/prompt for the round
        responses: List of response dicts with keys: text, isAI, authorId, modelUsed (optional)
    
    Returns:
        The prompt_id that was created
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Save the prompt
    cursor.execute('INSERT INTO prompts (prompt_text) VALUES (?)', (prompt,))
    prompt_id = cursor.lastrowid
    
    # Save all responses
    for response in responses:
        cursor.execute('''
            INSERT INTO responses (prompt_id, response_text, is_ai, author_id, model_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            prompt_id,
            response.get('text', ''),
            response.get('isAI', False),
            response.get('authorId'),
            response.get('modelUsed')
        ))
    
    conn.commit()
    conn.close()
    
    return prompt_id

def get_historical_data(limit: int = MAX_HISTORICAL_ROUNDS) -> Dict:
    """
    Get historical data from the last N rounds
    
    Returns a dictionary with:
    - human_examples: List of human responses
    - ai_examples: List of AI responses with their prompts
    - prompts: List of recent prompts
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get the last N prompts
    cursor.execute('''
        SELECT id, prompt_text, created_at
        FROM prompts
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    prompts = cursor.fetchall()
    
    if not prompts:
        conn.close()
        return {
            'human_examples': [],
            'ai_examples': [],
            'prompts': []
        }
    
    prompt_ids = [p['id'] for p in prompts]
    placeholders = ','.join('?' * len(prompt_ids))
    
    # Get human responses from these rounds
    cursor.execute(f'''
        SELECT r.response_text, p.prompt_text
        FROM responses r
        JOIN prompts p ON r.prompt_id = p.id
        WHERE r.prompt_id IN ({placeholders}) AND r.is_ai = 0
        ORDER BY r.created_at DESC
    ''', prompt_ids)
    
    human_responses = cursor.fetchall()
    
    # Get AI responses from these rounds
    cursor.execute(f'''
        SELECT r.response_text, p.prompt_text, r.model_used
        FROM responses r
        JOIN prompts p ON r.prompt_id = p.id
        WHERE r.prompt_id IN ({placeholders}) AND r.is_ai = 1
        ORDER BY r.created_at DESC
    ''', prompt_ids)
    
    ai_responses = cursor.fetchall()
    
    conn.close()
    
    # Format the data
    human_examples = [
        {
            'question': row['prompt_text'],
            'answer': row['response_text']
        }
        for row in human_responses
    ]
    
    ai_examples = [
        {
            'question': row['prompt_text'],
            'answer': row['response_text'],
            'model': row['model_used']
        }
        for row in ai_responses
    ]
    
    prompt_list = [
        {
            'prompt': row['prompt_text'],
            'timestamp': row['created_at']
        }
        for row in prompts
    ]
    
    return {
        'human_examples': human_examples,
        'ai_examples': ai_examples,
        'prompts': prompt_list
    }

def format_historical_context(historical_data: Dict, max_examples: int = 10) -> str:
    """
    Format historical data into a context string for AI prompts
    
    Args:
        historical_data: Dictionary returned from get_historical_data()
        max_examples: Maximum number of examples to include
    
    Returns:
        Formatted string to include in AI prompts
    """
    if not historical_data['human_examples'] and not historical_data['ai_examples']:
        return ""
    
    context_parts = []
    
    # Add human examples
    if historical_data['human_examples']:
        context_parts.append("Here are examples of how REAL HUMANS answered similar questions in previous rounds:")
        human_examples = historical_data['human_examples'][:max_examples]
        for i, example in enumerate(human_examples, 1):
            context_parts.append(f"\nQ: {example['question']}")
            context_parts.append(f"Human: {example['answer']}")
    
    # Add AI examples with analysis
    if historical_data['ai_examples']:
        context_parts.append("\n\nHere are examples of how AI bots answered in previous rounds:")
        context_parts.append("(Study these to understand what patterns to AVOID - these may have been too obviously AI-generated)")
        ai_examples = historical_data['ai_examples'][:max_examples]
        for i, example in enumerate(ai_examples, 1):
            context_parts.append(f"\nQ: {example['question']}")
            context_parts.append(f"AI ({example['model']}): {example['answer']}")
    
    context_parts.append("\n\nYour goal: Mimic the style and tone of the HUMAN examples above. Be natural, casual, and authentic like a real person.")
    
    return '\n'.join(context_parts)

def get_database_stats() -> Dict:
    """Get statistics about the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM prompts')
    prompt_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM responses WHERE is_ai = 0')
    human_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM responses WHERE is_ai = 1')
    ai_count = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_rounds': prompt_count,
        'human_responses': human_count,
        'ai_responses': ai_count
    }

# Initialize database when module is imported
init_database()
