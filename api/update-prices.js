// Vercel API endpoint for daily price updates
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";

const execAsync = promisify(exec);

export default async function handler(req, res) {
  // Only allow POST requests (for security)
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  // Vercel cron jobs automatically include the bypass header
  // No additional authentication needed for cron-triggered requests

  try {
    console.log("🚀 Starting daily price update...");

    // Path to Python script
    const scriptPath = path.join(
      process.cwd(),
      "backend",
      "scripts",
      "daily_price_updater.py"
    );

    // Execute the Python price updater
    const { stdout, stderr } = await execAsync(`python3 "${scriptPath}"`, {
      timeout: 600000, // 10 minute timeout
      cwd: process.cwd(),
      env: {
        ...process.env,
        SUPABASE_URL: process.env.SUPABASE_URL,
        SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY,
      },
    });

    console.log("✅ Price update completed");
    console.log("STDOUT:", stdout);

    if (stderr) {
      console.warn("STDERR:", stderr);
    }

    // Parse the output to extract statistics
    const lines = stdout.split("\n");
    let stats = {
      totalItems: 0,
      updatedItems: 0,
      errors: 0,
      executionTime: "Unknown",
    };

    // Extract statistics from log output
    for (const line of lines) {
      if (line.includes("Total Items Checked:")) {
        stats.totalItems = parseInt(line.match(/\d+/)?.[0] || "0");
      }
      if (line.includes("Successfully Updated:")) {
        stats.updatedItems = parseInt(line.match(/\d+/)?.[0] || "0");
      }
      if (line.includes("Errors:")) {
        stats.errors = parseInt(line.match(/\d+/)?.[0] || "0");
      }
      if (line.includes("Total execution time:")) {
        stats.executionTime =
          line.split("Total execution time: ")[1]?.trim() || "Unknown";
      }
    }

    return res.status(200).json({
      success: true,
      message: "Price update completed successfully",
      timestamp: new Date().toISOString(),
      statistics: stats,
      logs: {
        stdout: stdout.split("\n").slice(-20), // Last 20 lines
        stderr: stderr || null,
      },
    });
  } catch (error) {
    console.error("❌ Price update failed:", error);

    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString(),
      details: {
        code: error.code,
        signal: error.signal,
        stdout: error.stdout,
        stderr: error.stderr,
      },
    });
  }
}

// Export configuration for Vercel
export const config = {
  maxDuration: 300, // 5 minutes max execution time (hobby plan limit)
  regions: ["iad1"], // US East for better performance
};
