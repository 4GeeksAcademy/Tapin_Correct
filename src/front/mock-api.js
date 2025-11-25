const http = require("http");

const PORT = process.env.MOCK_API_PORT || 5000;

const server = http.createServer((req, res) => {
  const url = req.url || "/";
  // simple CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  if (url.startsWith("/listings")) {
    res.setHeader("Content-Type", "application/json");
    return res.end(JSON.stringify([]));
  }

  if (url === "/me" || url.startsWith("/me")) {
    res.setHeader("Content-Type", "application/json");
    return res.end(JSON.stringify({ user: null }));
  }

  // basic endpoints for auth/listing lookups to avoid connection errors
  if (
    url.startsWith("/auth") ||
    url.startsWith("/login") ||
    url.startsWith("/register")
  ) {
    res.setHeader("Content-Type", "application/json");
    return res.end(JSON.stringify({ message: "ok" }));
  }

  // default 200 for other paths
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({}));
});

server.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`Mock API server listening on http://localhost:${PORT}`);
});

// graceful shutdown
process.on("SIGINT", () => process.exit(0));
process.on("SIGTERM", () => process.exit(0));
