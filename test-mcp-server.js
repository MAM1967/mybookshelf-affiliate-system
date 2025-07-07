#!/usr/bin/env node

import { spawn } from "child_process";

// Test the MCP server
async function testMCPServer() {
  console.log("🧪 Testing MCP Server...");

  const server = spawn("node", ["mcp-server.js"], {
    stdio: ["pipe", "pipe", "pipe"],
  });

  let output = "";
  let errorOutput = "";
  let serverStarted = false;

  server.stdout.on("data", (data) => {
    output += data.toString();
    console.log("📤 Server output:", data.toString());

    // Check if server started successfully
    if (data.toString().includes("started successfully")) {
      serverStarted = true;
    }
  });

  server.stderr.on("data", (data) => {
    errorOutput += data.toString();
    console.log("❌ Server error:", data.toString());
  });

  server.on("close", (code) => {
    console.log(`\n🏁 Server exited with code ${code}`);

    // Determine if test passed based on actual server behavior
    if (serverStarted && !errorOutput.includes("Error")) {
      console.log("✅ MCP Server test passed - server started successfully");
    } else if (errorOutput.includes("Error")) {
      console.log("❌ MCP Server test failed - errors detected");
    } else {
      console.log(
        "⚠️ MCP Server test inconclusive - server may have started but was killed"
      );
    }
  });

  // Give it a moment to start, then kill it
  setTimeout(() => {
    server.kill();
  }, 2000);
}

testMCPServer().catch(console.error);
