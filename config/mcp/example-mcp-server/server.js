#!/usr/bin/env node

// Example MCP server: simple calculator implemented in Node.js
// Responds to POST /calculate with JSON body {"operation": "add", "a": 1, "b": 2}

const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

app.get('/', (_req, res) => {
  res.json({ status: 'ok', message: 'Example MCP Calculator Server' });
});

app.post('/calculate', (req, res) => {
  const { operation, a, b } = req.body || {};

  if (typeof a !== 'number' || typeof b !== 'number') {
    return res.status(400).json({ error: 'Both "a" and "b" must be numbers.' });
  }

  let result;
  switch (operation) {
    case 'add':
      result = a + b;
      break;
    case 'subtract':
      result = a - b;
      break;
    case 'multiply':
      result = a * b;
      break;
    case 'divide':
      if (b === 0) {
        return res.status(400).json({ error: 'Cannot divide by zero.' });
      }
      result = a / b;
      break;
    default:
      return res.status(400).json({ error: 'Unsupported operation. Use add, subtract, multiply, or divide.' });
  }

  return res.json({ operation, a, b, result });
});

app.listen(PORT, () => {
  console.log(`Example MCP Calculator Server listening on port ${PORT}`);
});
