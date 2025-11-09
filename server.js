// server.js

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const PORT = 3000;

// durations
const ANSWER_DURATION_MS = 60000;
const GUESS_DURATION_MS = 60000;

// ================== STATIC FILES ==================
app.use(express.static('public'));

// ================== IN-MEMORY STATE ==================
// rooms[roomCode] = {
//   code,
//   players: { playerId: { name, score, isAI } },
//   round: {
//     stage,          // 'answering' | 'guessing' | 'results' | 'finished'
//     prompt,
//     answers,        // [{ id, text, isAI, authorId }]
//     guesses,        // [{ playerId, guesses: [{ answerId, guessedIsAI }] }]
//     answerTimeout,
//     guessTimeout,
//     answerEndsAt,
//     guessEndsAt
//   }
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
// Python Flask service using LiteLLM with Claude Opus 4 and Sonnet 4

const AI_SERVICE_URL = 'http://localhost:5000';

// Generate a *prompt* for the round (uses Claude Opus 4)
async function generatePrompt() {
  const res = await fetch(`${AI_SERVICE_URL}/generate_prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });

  if (!res.ok) {
    console.error('AI Service error status:', res.status);
    const errorText = await res.text();
    console.error('Error details:', errorText);
    throw new Error('Failed to generate prompt from AI service');
  }

  const data = await res.json();
  return data.prompt;
}

// Generate ONE AI answer to the given round prompt
// Uses Claude Opus 4 for Bot 0, Claude Sonnet 4 for Bot 1
async function generateAIAnswer(roundPrompt, botIndex = 0, currentRoundId = null) {
  const res = await fetch(`${AI_SERVICE_URL}/generate_answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: roundPrompt,
      bot_index: botIndex,
      current_round_id: currentRoundId
    })
  });

  if (!res.ok) {
    console.error('AI Service error status:', res.status);
    const errorText = await res.text();
    console.error('Error details:', errorText);
    throw new Error('Failed to generate answer from AI service');
  }

  const data = await res.json();
  console.log(`Generated answer from ${data.model} (used ${data.examples_used || 0} past examples)`);
  return data.answer;
}

// Generate answers for each bot player in the room
// Bot 0 uses Claude Opus 4, Bot 1 uses Claude Sonnet 4
async function generateBotAnswers(room) {
  const prompt = room.round.prompt;
  const botIds = getBotIds(room);
  const answers = [];

  // Get current round ID if it exists (for excluding from few-shot examples)
  const currentRoundId = room.round.databaseRoundId || null;

  for (let i = 0; i < botIds.length; i++) {
    const botId = botIds[i];
    try {
      const text = await generateAIAnswer(prompt, i, currentRoundId);
      answers.push({
        id: `ai-${Date.now()}-${botId}-${Math.random().toString(36).slice(2, 6)}`,
        text,
        isAI: true,
        authorId: botId
      });
    } catch (err) {
      console.error(`Failed to generate bot answer for ${botId}:`, err);
    }
  }

  return answers;
}

// Store completed round in the database
async function storeRoundInDatabase(room) {
  const question = room.round.prompt;
  const answers = [];

  // Get bot names mapping
  const botNames = ['Opus 4', 'Sonnet 4'];
  const botIds = getBotIds(room);

  // Collect all answers
  for (const ans of room.round.answers) {
    const isAI = ans.isAI;
    let aiModel = null;

    if (isAI) {
      // Find which bot this is
      const botIndex = botIds.indexOf(ans.authorId);
      if (botIndex >= 0 && botIndex < botNames.length) {
        aiModel = botNames[botIndex];
      }
    }

    answers.push({
      answer: ans.text,
      is_ai: isAI,
      ai_model: aiModel
    });
  }

  const res = await fetch(`${AI_SERVICE_URL}/store_round`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      answers
    })
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error('Failed to store round:', errorText);
    throw new Error('Failed to store round in database');
  }

  const data = await res.json();
  console.log(`✅ Stored round ${data.round_id} in database`);
  console.log(`   Database stats: ${data.stats.total_rounds} rounds, ${data.stats.total_answers} answers`);

  return data.round_id;
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
    const botCount = 2; // Two bots: Opus 4 and Sonnet 4
    const botNames = ['Opus 4', 'Sonnet 4'];
    for (let i = 0; i < botCount; i++) {
      const botId = `bot-${code}-${i}`;
      players[botId] = {
        name: botNames[i],
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

  // -------- START ROUND (AI host + timers) --------
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

      // clear any stale timers just in case
      if (room.round?.answerTimeout) clearTimeout(room.round.answerTimeout);
      if (room.round?.guessTimeout) clearTimeout(room.round.guessTimeout);

      room.round = {
        stage: 'answering', // 'answering' | 'guessing' | 'results' | 'finished'
        prompt,
        answers: [],
        guesses: [],
        answerTimeout: null,
        guessTimeout: null,
        answerEndsAt: Date.now() + ANSWER_DURATION_MS,
        guessEndsAt: null
      };

      // Bot players submit their answers immediately
      const botAnswers = await generateBotAnswers(room);
      room.round.answers.push(...botAnswers);

      console.log('Room', roomCode, 'prompt:', prompt);
      console.log('Bot answers:', botAnswers.map(a => `${a.text} (by ${a.authorId})`));

      // start answer timer
      room.round.answerTimeout = setTimeout(() => {
        const current = rooms[roomCode];
        if (!current || !current.round) return;
        if (current.round.stage !== 'answering') return;
        startGuessingPhase(current);
      }, ANSWER_DURATION_MS);

      io.to(roomCode).emit('round_started', {
        prompt: room.round.prompt,
        answerDuration: ANSWER_DURATION_MS
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
    // prevent double answer from same player
    const already = room.round.answers.find(
      a => !a.isAI && a.authorId === socket.id
    );
    if (already) return;

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

    // When all humans have answered, move to guessing immediately
    if (answersFromHumans === humanCount) {
      startGuessingPhase(room);
    }
  });

  // -------- SUBMIT GUESSES (humans guess) --------
  socket.on('submit_guesses', ({ roomCode, guesses }) => {
    const room = rooms[roomCode];
    if (!room || !room.round || room.round.stage !== 'guessing') return;

    // Only humans can submit guesses
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

    // If all humans have guessed before time is up, finish early
    if (humanGuessesCount === humanCount) {
      room.round.stage = 'results';
      scoreRound(room);

      // Store round in database
      storeRoundInDatabase(room).catch(err => {
        console.error('Failed to store round in database:', err);
      });

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

    // If no humans left, clean up room + timers
    const humanIds = getHumanIds(room);
    if (humanIds.length === 0) {
      if (room.round?.answerTimeout) clearTimeout(room.round.answerTimeout);
      if (room.round?.guessTimeout) clearTimeout(room.round.guessTimeout);
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
