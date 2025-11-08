// server.js

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const PORT = 3000;

// ================== STATIC FILES ==================
app.use(express.static('public'));

// ================== IN-MEMORY STATE ==================
// rooms[roomCode] = {
//   code,
//   players: { playerId: { name, score, isAI } },
//   round: { stage, prompt, answers, guesses }
// }
const rooms = {};

function makeRoomCode() {
  return Math.random().toString(36).substring(2, 6).toUpperCase();
}

function getRoomOfSocket(socket) {
  return Object.values(rooms).find(r =>
    Object.keys(r.players).includes(socket.id)
  );
}

function getHumanIds(room) {
  return Object.keys(room.players).filter(id => !room.players[id].isAI);
}

function getBotIds(room) {
  return Object.keys(room.players).filter(id => room.players[id].isAI);
}

// ================== AI SERVICE INTEGRATION ==================
// Python AI service runs on port 5000
const AI_SERVICE_URL = 'http://localhost:5000';

// Generate a *prompt* for the round (AI host using Claude Opus 4)
async function generatePrompt() {
  try {
    const res = await fetch(`${AI_SERVICE_URL}/generate-prompt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!res.ok) {
      console.error('AI service error status:', res.status);
      throw new Error('AI service request failed');
    }

    const data = await res.json();
    if (!data.success) {
      throw new Error(data.error || 'AI service returned error');
    }

    return data.prompt;
  } catch (err) {
    console.error('Error generating prompt:', err);
    throw err;
  }
}

// Generate answers for each bot player in the room
// Uses batch endpoint for efficiency - Opus 4 and Sonnet 4
async function generateBotAnswers(room) {
  const prompt = room.round.prompt;
  const botIds = getBotIds(room);
  
  try {
    const res = await fetch(`${AI_SERVICE_URL}/generate-batch-answers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        bot_ids: botIds
      })
    });

    if (!res.ok) {
      console.error('AI service error status:', res.status);
      throw new Error('AI service batch request failed');
    }

    const data = await res.json();
    if (!data.success) {
      throw new Error(data.error || 'AI service returned error');
    }

    // Convert AI service responses to game answer format
    const answers = [];
    for (const botAnswer of data.answers) {
      if (botAnswer.success) {
        answers.push({
          id: `ai-${Date.now()}-${botAnswer.bot_id}-${Math.random().toString(36).slice(2, 6)}`,
          text: botAnswer.answer,
          isAI: true,
          authorId: botAnswer.bot_id,
          modelUsed: botAnswer.model_used
        });
        console.log(`Bot ${botAnswer.bot_id} using ${botAnswer.model_used}: ${botAnswer.answer}`);
      } else {
        console.error(`Failed to generate answer for ${botAnswer.bot_id}:`, botAnswer.error);
      }
    }

    return answers;
  } catch (err) {
    console.error('Error generating bot answers:', err);
    return []; // Return empty array on error
  }
}

// Save round data to the AI service database for future learning
async function saveRoundData(room) {
  if (!room.round) return;
  
  try {
    const responses = room.round.answers.map(answer => ({
      text: answer.text,
      isAI: answer.isAI,
      authorId: answer.authorId,
      modelUsed: answer.modelUsed || null
    }));

    const res = await fetch(`${AI_SERVICE_URL}/save-round`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: room.round.prompt,
        responses: responses
      })
    });

    if (!res.ok) {
      console.error('Failed to save round data:', res.status);
      return;
    }

    const data = await res.json();
    if (data.success) {
      console.log(`Saved round data: ${data.message}`);
    } else {
      console.error('Error saving round:', data.error);
    }
  } catch (err) {
    console.error('Error saving round data:', err);
  }
}

// ================== SOCKET.IO LOGIC ==================

io.on('connection', (socket) => {
  console.log('connected:', socket.id);

  // -------- CREATE ROOM (no human host) --------
  socket.on('create_room', ({ playerName }, cb) => {
    const code = makeRoomCode();

    const players = {
      [socket.id]: { name: playerName, score: 0, isAI: false }
    };

    // Add AI players to the room
    const botCount = 2; // change if you want more bots
    for (let i = 0; i < botCount; i++) {
      const botId = `bot-${code}-${i}`;
      players[botId] = {
        name: `Bot ${i + 1}`,
        score: 0,
        isAI: true
      };
    }

    rooms[code] = {
      code,
      players,
      round: null
    };

    socket.join(code);
    cb({ roomCode: code });
    io.to(code).emit('room_state', rooms[code]);
  });

  // -------- JOIN ROOM --------
  socket.on('join_room', ({ roomCode, playerName }, cb) => {
    const room = rooms[roomCode];
    if (!room) {
      cb({ error: 'Room not found' });
      return;
    }
    room.players[socket.id] = { name: playerName, score: 0, isAI: false };
    socket.join(roomCode);
    cb({ roomCode });
    io.to(roomCode).emit('room_state', room);
  });

  // -------- START ROUND (AI is conceptual host) --------
  // Any human can request a new round; AI generates prompt + bot answers.
  socket.on('start_round', async ({ roomCode }) => {
    const room = rooms[roomCode];
    if (!room) return;

    // Avoid starting a new round while one is mid-flow
    if (room.round && room.round.stage !== 'results' && room.round.stage !== 'finished') {
      console.log('Round already in progress in room', roomCode);
      return;
    }

    try {
      const prompt = await generatePrompt();

      room.round = {
        stage: 'answering', // 'answering' | 'guessing' | 'results'
        prompt,
        answers: [],
        guesses: [] // {playerId, guesses: [{answerId, guessedIsAI}]}
      };

      // Bot players submit their answers immediately
      const botAnswers = await generateBotAnswers(room);
      room.round.answers.push(...botAnswers);

      console.log('Room', roomCode, 'prompt:', prompt);
      console.log('Bot answers:', botAnswers.map(a => `${a.text} (by ${a.authorId})`));

      io.to(roomCode).emit('round_started', {
        prompt: room.round.prompt
      });
    } catch (err) {
      console.error('Error starting round (prompt or bot answers):', err);
    }
  });

  // -------- SUBMIT HUMAN ANSWER --------
  socket.on('submit_answer', ({ roomCode, text }) => {
    const room = rooms[roomCode];
    if (!room || !room.round || room.round.stage !== 'answering') return;

    const answerId = 'h-' + socket.id;
    room.round.answers.push({
      id: answerId,
      text,
      isAI: false,
      authorId: socket.id
    });

    const humanIds = getHumanIds(room);
    const humanCount = humanIds.length;
    const answersFromHumans = room.round.answers.filter(a =>
      !a.isAI && humanIds.includes(a.authorId)
    ).length;

    // When all humans have answered, move to guessing
    if (answersFromHumans === humanCount) {
      room.round.stage = 'guessing';

      const shuffled = [...room.round.answers].sort(() => Math.random() - 0.5);
      io.to(roomCode).emit('start_guessing', {
        answers: shuffled.map(a => ({ id: a.id, text: a.text }))
      });
    }
  });

  // -------- SUBMIT GUESSES (humans guess) --------
  socket.on('submit_guesses', ({ roomCode, guesses }) => {
    const room = rooms[roomCode];
    if (!room || !room.round || room.round.stage !== 'guessing') return;

    // Only store guesses from humans
    if (room.players[socket.id]?.isAI) return;

    // Overwrite previous guesses from this player if they resubmit
    const existingIndex = room.round.guesses.findIndex(g => g.playerId === socket.id);
    if (existingIndex >= 0) {
      room.round.guesses[existingIndex] = { playerId: socket.id, guesses };
    } else {
      room.round.guesses.push({ playerId: socket.id, guesses });
    }

    const humanCount = getHumanIds(room).length;
    const humanGuessesCount = room.round.guesses.length;

    if (humanGuessesCount === humanCount) {
      room.round.stage = 'results';
      scoreRound(room);

      // Save round data to the AI service database
      saveRoundData(room);

      io.to(roomCode).emit('round_results', {
        answers: room.round.answers,
        players: room.players
      });
    }
  });

  // -------- DISCONNECT --------
  socket.on('disconnect', () => {
    console.log('disconnected:', socket.id);
    const room = getRoomOfSocket(socket);
    if (!room) return;

    delete room.players[socket.id];

    // If no humans left, delete room (bots alone are pointless)
    const humanIds = getHumanIds(room);
    if (humanIds.length === 0) {
      delete rooms[room.code];
    } else {
      io.to(room.code).emit('room_state', room);
    }
  });
});

// ================== SCORING ==================

function scoreRound(room) {
  const answersById = Object.fromEntries(
    room.round.answers.map(a => [a.id, a])
  );

  const GUESS_POINTS = 10;
  const FOOL_POINTS = 5;

  // Award points for correct guesses (humans only)
  for (const g of room.round.guesses) {
    const playerId = g.playerId;
    if (room.players[playerId]?.isAI) continue;

    for (const oneGuess of g.guesses) {
      const ans = answersById[oneGuess.answerId];
      if (!ans) continue;
      const correct = oneGuess.guessedIsAI === ans.isAI;
      if (correct) {
        room.players[playerId].score += GUESS_POINTS;
      }
    }
  }

  // Fooling bonus for HUMAN answers: others guessed "AI" on a human answer
  for (const ans of room.round.answers) {
    if (ans.isAI) continue;         // only human-written answers
    if (!ans.authorId) continue;

    const author = room.players[ans.authorId];
    if (!author) continue;

    const allGuesses = room.round.guesses.flatMap(g => g.guesses);
    const guessesForThis = allGuesses.filter(g => g.answerId === ans.id);

    const fooledCount = guessesForThis.filter(g => g.guessedIsAI === true).length;
    author.score += fooledCount * FOOL_POINTS;
  }

  room.round.stage = 'finished';
}

// ================== START SERVER ==================

server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});