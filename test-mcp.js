#!/usr/bin/env node

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";

async function testMCPServer() {
  console.log("🧪 Testing MyBookshelf MCP Server...\n");

  // Start the MCP server as a child process
  const serverProcess = spawn("node", ["mcp-server.js"], {
    stdio: ["pipe", "pipe", "pipe"],
    env: process.env,
  });

  // Wait a moment for the server to start
  await new Promise((resolve) => setTimeout(resolve, 1000));

  const transport = new StdioClientTransport(
    serverProcess.stdin,
    serverProcess.stdout
  );
  const client = new Client(transport);

  try {
    // Connect to the server
    await client.connect();
    console.log("✅ Connected to MCP server");

    // Test health check
    console.log("\n🔍 Testing health check...");
    const healthResult = await client.callTool("run_health_check", {});
    console.log("Health Check Result:", healthResult.content[0].text);

    // Test getting LinkedIn status
    console.log("\n🔍 Testing LinkedIn status...");
    const linkedinResult = await client.callTool("get_linkedin_status", {});
    console.log("LinkedIn Status:", linkedinResult.content[0].text);

    // Test getting books inventory
    console.log("\n🔍 Testing books inventory...");
    const inventoryResult = await client.callTool("get_books_inventory", {});
    console.log("Books Inventory:", inventoryResult.content[0].text);

    // Test getting database stats
    console.log("\n🔍 Testing database stats...");
    const statsResult = await client.callTool("get_database_stats", {});
    console.log("Database Stats:", statsResult.content[0].text);

    console.log("\n✅ All tests completed successfully!");
  } catch (error) {
    console.error("❌ Test failed:", error.message);
  } finally {
    // Clean up
    serverProcess.kill();
    await new Promise((resolve) => setTimeout(resolve, 500));
    process.exit(0);
  }
}

// Run the test
testMCPServer().catch(console.error);
