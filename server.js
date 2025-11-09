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

// ================== OLLAMA INTEGRATION ==================

const OLLAMA_MODEL = 'gpt-oss:120b-cloud'; // change if needed

async function ollamaGenerate(prompt) {
  const res = await fetch('http://localhost:11434/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: OLLAMA_MODEL,
      prompt,
      stream: false
    })
  });

  if (!res.ok) {
    console.error('Ollama error status:', res.status);
    throw new Error('Ollama request failed');
  }

  const data = await res.json();
  return (data.response || '').trim();
}

// Generate a *prompt* for the round (AI host)
async function generatePrompt() {
  const promptForModel = `
You are designing prompts for a party game where humans and AI both answer.
Choose one topic randomly from below and write a whacky and humorous question about it that people can answer in 1–3 sentences. Limit the question to one part.
Examples of style:
- "Write a song lyric about stubbing your left toe"
- "What is the most evil cake recipe you can think of?"
Topics:
[music,
birds,
food,
prehistoric animals,
Space travel]

Rules:
- Output ONLY the question text, no quotes, no explanations, no numbering.
- The question must not mention AI, the game, or being a contestant.
`.trim();

  return await ollamaGenerate(promptForModel);
}

// Generate ONE AI answer to the given round prompt
async function generateAIAnswer(roundPrompt) {
  const fullPrompt = `
You are a contestant in a party game trying to sound like a real human.
Respond in 1-3 sentences to this question but try to stay close to 1:

"${roundPrompt}"

Do NOT say you are an AI or language model.
Just answer like a normal college student in a casual, lighthearted, and joking way. Keep it as short as possible and do not go over the top.
`.trim();

  return await ollamaGenerate(fullPrompt);
}

// Generate answers for each bot player in the room
async function generateBotAnswers(room) {
  const prompt = room.round.prompt;
  const botIds = getBotIds(room);
  const answers = [];

  for (const botId of botIds) {
    try {
      const text = await generateAIAnswer(prompt);
      answers.push({
        id: `ai-${Date.now()}-${botId}-${Math.random().toString(36).slice(2, 6)}`,
        text,
        isAI: true,
        authorId: botId
      });
    } catch (err) {
      console.error('Failed to generate bot answer:', err);
    }
  }

  return answers;
}

// ================== ROUND HELPERS (TIMERS) ==================

function startGuessingPhase(room) {
  if (!room.round) return;
  if (room.round.stage !== 'answering') return; // already moved on

  // clear answer timer if still set
  if (room.round.answerTimeout) {
    clearTimeout(room.round.answerTimeout);
    room.round.answerTimeout = null;
  }

  room.round.stage = 'guessing';
  room.round.guessEndsAt = Date.now() + GUESS_DURATION_MS;

  const shuffled = [...room.round.answers].sort(() => Math.random() - 0.5);

  // start guess timer
  const roomCode = room.code;
  room.round.guessTimeout = setTimeout(() => {
    const current = rooms[roomCode];
    if (!current || !current.round) return;
    if (current.round.stage !== 'guessing') return;
    finishRound(current);
  }, GUESS_DURATION_MS);

  io.to(room.code).emit('start_guessing', {
    answers: shuffled.map(a => ({ id: a.id, text: a.text })),
    guessDuration: GUESS_DURATION_MS
  });
}

function finishRound(room) {
  if (!room.round) return;

  // clear guess timer
  if (room.round.guessTimeout) {
    clearTimeout(room.round.guessTimeout);
    room.round.guessTimeout = null;
  }

  scoreRound(room);

  io.to(room.code).emit('round_results', {
    answers: room.round.answers,
    players: room.players
  });
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
      finishRound(room);
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
