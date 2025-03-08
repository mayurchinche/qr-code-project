import express from "express";
import path from "path";
import { fileURLToPath } from "url";

// Fix "__dirname" in ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from 'dist'
app.use(express.static(path.join(__dirname, "dist")));

// Serve index.html for all routes (React Router support)
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});

// Start server
app.listen(PORT, () => {
  console.log(`Frontend is running on http://localhost:${PORT}`);
});
