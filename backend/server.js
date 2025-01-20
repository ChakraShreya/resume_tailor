const express = require('express');
const app = express();
const port = 5000;

// Middleware to handle JSON requests
app.use(express.json());

// Example route
app.get('/', (req, res) => {
  res.send('Hello from the backend!');
});

// Start the server
app.listen(port, () => {
  console.log(`Backend server is running on http://localhost:${port}`);
});
