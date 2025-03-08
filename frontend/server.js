const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from the 'dist' folder
app.use(express.static(path.join(__dirname, "dist")));

// Serve index.html on all routes (for React Router support)
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});

// Start server
app.listen(PORT, () => {
  console.log(`Frontend is running on http://localhost:${PORT}`);
});
