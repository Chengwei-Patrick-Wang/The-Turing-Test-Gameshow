#!/bin/bash

# Quick reference for database commands

echo "📊 Turing Test Gameshow - Database Quick Reference"
echo "=================================================="
echo ""

# Check if database exists
if [ -f "game_history.db" ]; then
    echo "✅ Database exists: game_history.db"
    echo ""
    
    # Show stats
    echo "📈 Current Statistics:"
    echo "--------------------"
    sqlite3 game_history.db "SELECT COUNT(*) as 'Total Rounds' FROM rounds;"
    sqlite3 game_history.db "SELECT COUNT(*) as 'Total Answers' FROM answers;"
    sqlite3 game_history.db "SELECT COUNT(*) as 'AI Answers' FROM answers WHERE is_ai = 1;"
    sqlite3 game_history.db "SELECT COUNT(*) as 'Human Answers' FROM answers WHERE is_ai = 0;"
    echo ""
    
    # Show recent rounds
    echo "🎮 Recent Rounds:"
    echo "--------------------"
    sqlite3 game_history.db "SELECT round_id, substr(question, 1, 50) as question FROM rounds ORDER BY round_id DESC LIMIT 5;"
    echo ""
    
else
    echo "❌ Database not found: game_history.db"
    echo "   Run the game or test_database.py to create it."
    echo ""
fi

echo "📚 Useful Commands:"
echo "--------------------"
echo "View all rounds:"
echo "  sqlite3 game_history.db 'SELECT * FROM rounds;'"
echo ""
echo "View recent answers:"
echo "  sqlite3 game_history.db 'SELECT question, answer, is_ai FROM answers ORDER BY answer_id DESC LIMIT 10;'"
echo ""
echo "Get database stats via API:"
echo "  curl http://localhost:5000/database_stats"
echo ""
echo "Test database:"
echo "  python test_database.py"
echo ""
echo "Reset database:"
echo "  rm game_history.db && python test_database.py"
echo ""
echo "Backup database:"
echo "  cp game_history.db game_history_backup_\$(date +%Y%m%d).db"
echo ""
