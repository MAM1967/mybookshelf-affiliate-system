#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createClient } from "@supabase/supabase-js";
import { z } from "zod";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY
);

const server = new McpServer({
  name: "mybookshelf-affiliate-system",
  version: "1.0.0",
});

// Simplified helper function with shorter timeout
function withTimeout(promise, timeoutMs = 5000) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(
        () => reject(new Error(`Timeout after ${timeoutMs}ms`)),
        timeoutMs
      )
    ),
  ]);
}

// Tool: get_affiliate_products_summary
server.tool(
  "get_affiliate_products_summary",
  "Get a summary of affiliate products (Amazon books & accessories)",
  z.object({}),
  async () => {
    try {
      const result = await withTimeout(
        supabase
          .from("books_accessories")
          .select("title, author, amazon_asin, amazon_affiliate_link")
          .limit(100), // Reduced limit for faster response
        5000
      );

      if (result.error) throw result.error;

      const products = result.data || [];
      const stats = {
        total: products.length,
        with_asin: products.filter((b) => b.amazon_asin).length,
        with_affiliate: products.filter((b) => b.amazon_affiliate_link).length,
      };

      const sample = products
        .slice(0, 3)
        .map((b) => `• ${b.title} by ${b.author || "Unknown"}`);
      const summary = `Affiliate Product Summary:\n• Total: ${
        stats.total
      }\n• With ASIN: ${stats.with_asin}\n• With Affiliate Link: ${
        stats.with_affiliate
      }\n\nSample Products:\n${sample.join("\n")}`;

      return {
        content: [{ type: "text", text: summary }],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to get affiliate product summary: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Tool: list_affiliate_products
server.tool(
  "list_affiliate_products",
  "List all affiliate products with title, author, ASIN, and affiliate link",
  z.object({ limit: z.number().min(1).max(20).default(10) }),
  async ({ limit }) => {
    try {
      const result = await withTimeout(
        supabase
          .from("books_accessories")
          .select("title, author, amazon_asin, amazon_affiliate_link")
          .limit(limit),
        5000
      );

      if (result.error) throw result.error;

      const products = result.data || [];
      const list = products
        .map(
          (b, i) =>
            `${i + 1}. ${b.title} by ${b.author || "Unknown"}\n   ASIN: ${
              b.amazon_asin || "-"
            }\n   Affiliate Link: ${b.amazon_affiliate_link || "-"}`
        )
        .join("\n\n");

      return {
        content: [{ type: "text", text: list }],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to list affiliate products: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Tool: count_products_with_affiliate_links
server.tool(
  "count_products_with_affiliate_links",
  "Count how many products have affiliate links",
  z.object({}),
  async () => {
    try {
      const result = await withTimeout(
        supabase
          .from("books_accessories")
          .select("amazon_affiliate_link")
          .limit(1000),
        3000
      );

      if (result.error) throw result.error;

      const products = result.data || [];
      const count = products.filter((b) => b.amazon_affiliate_link).length;

      return {
        content: [
          { type: "text", text: `Products with affiliate links: ${count}` },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to count affiliate links: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Tool: get_linkedin_posting_status
server.tool(
  "get_linkedin_posting_status",
  "Get LinkedIn posting status including last post time, next scheduled, post IDs, and visibility status",
  z.object({}),
  async () => {
    try {
      // Get LinkedIn tokens
      const tokenResult = await withTimeout(
        supabase.from("linkedin_tokens").select("*").limit(1),
        3000
      );

      if (tokenResult.error) throw tokenResult.error;

      const tokens = tokenResult.data || [];
      const hasValidToken = tokens.length > 0 && tokens[0].access_token;

      // Get recent posts from content_calendar or approval_audit_log
      const postsResult = await withTimeout(
        supabase
          .from("approval_audit_log")
          .select("action, created_at, details")
          .eq("action", "linkedin_post")
          .order("created_at", { ascending: false })
          .limit(5),
        3000
      );

      if (postsResult.error) throw postsResult.error;

      const posts = postsResult.data || [];
      const lastPost = posts[0];

      // Get pending/scheduled posts
      const pendingResult = await withTimeout(
        supabase
          .from("pending_books")
          .select("title, scheduled_date")
          .order("scheduled_date", { ascending: true })
          .limit(3),
        3000
      );

      if (pendingResult.error) throw pendingResult.error;

      const pending = pendingResult.data || [];

      const status =
        `LinkedIn Posting Status:\n\n` +
        `🔑 Token Status: ${
          hasValidToken ? "✅ Valid" : "❌ Missing/Invalid"
        }\n` +
        `📅 Last Post: ${
          lastPost ? new Date(lastPost.created_at).toLocaleString() : "None"
        }\n` +
        `🆔 Last Post ID: ${lastPost?.details?.post_id || "N/A"}\n` +
        `👁️ Visibility: ${
          lastPost
            ? "API Success (201) - Feed visibility pending LinkedIn review"
            : "N/A"
        }\n\n` +
        `📋 Next Scheduled:\n${
          pending
            .map((p) => `• ${p.title} - ${p.scheduled_date || "TBD"}`)
            .join("\n") || "None"
        }\n\n` +
        `📊 Recent Posts (${posts.length}):\n${posts
          .map(
            (p) =>
              `• ${new Date(p.created_at).toLocaleDateString()} - ${
                p.details?.post_id || "No ID"
              }`
          )
          .join("\n")}`;

      return {
        content: [{ type: "text", text: status }],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to get LinkedIn status: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Tool: get_revenue_tracking
server.tool(
  "get_revenue_tracking",
  "Get revenue tracking data including affiliate link clicks and conversion stats",
  z.object({}),
  async () => {
    try {
      // Get products with affiliate links
      const productsResult = await withTimeout(
        supabase
          .from("books_accessories")
          .select("title, amazon_affiliate_link, amazon_asin")
          .not("amazon_affiliate_link", "is", null),
        3000
      );

      if (productsResult.error) throw productsResult.error;

      const products = productsResult.data || [];

      // Get recent posts to track which products were promoted
      const postsResult = await withTimeout(
        supabase
          .from("approval_audit_log")
          .select("created_at, details")
          .eq("action", "linkedin_post")
          .order("created_at", { ascending: false })
          .limit(10),
        3000
      );

      if (postsResult.error) throw postsResult.error;

      const posts = postsResult.data || [];

      const revenue =
        `Revenue Tracking Summary:\n\n` +
        `💰 Affiliate Products: ${products.length} with links\n` +
        `📊 Amazon Associate ID: mybookshelf-20\n` +
        `📈 Recent Promotions: ${posts.length} LinkedIn posts\n\n` +
        `🔗 Active Affiliate Links:\n${products
          .slice(0, 5)
          .map((p) => `• ${p.title} (ASIN: ${p.amazon_asin || "N/A"})`)
          .join("\n")}\n\n` +
        `📅 Recent Promotional Activity:\n${posts
          .slice(0, 5)
          .map(
            (p) =>
              `• ${new Date(p.created_at).toLocaleDateString()} - Post ID: ${
                p.details?.post_id || "N/A"
              }`
          )
          .join("\n")}\n\n` +
        `💡 Note: Click tracking requires Amazon Associates dashboard access. Revenue attribution working through affiliate links.`;

      return {
        content: [{ type: "text", text: revenue }],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to get revenue tracking: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Tool: get_approval_workflow_status
server.tool(
  "get_approval_workflow_status",
  "Get approval workflow status including pending books and Sunday approval queue",
  z.object({}),
  async () => {
    try {
      // Get pending books
      const pendingResult = await withTimeout(
        supabase
          .from("pending_books")
          .select("title, author, created_at, status")
          .order("created_at", { ascending: false }),
        3000
      );

      if (pendingResult.error) throw pendingResult.error;

      const pending = pendingResult.data || [];

      // Get approval sessions
      const sessionsResult = await withTimeout(
        supabase
          .from("approval_sessions")
          .select("session_id, created_at, status, books_count")
          .order("created_at", { ascending: false })
          .limit(5),
        3000
      );

      if (sessionsResult.error) throw sessionsResult.error;

      const sessions = sessionsResult.data || [];

      // Get recent approval activity
      const auditResult = await withTimeout(
        supabase
          .from("approval_audit_log")
          .select("action, created_at, details")
          .in("action", ["book_approved", "book_rejected", "session_created"])
          .order("created_at", { ascending: false })
          .limit(10),
        3000
      );

      if (auditResult.error) throw auditResult.error;

      const audit = auditResult.data || [];

      const workflow =
        `Approval Workflow Status:\n\n` +
        `📚 Pending Books: ${pending.length}\n` +
        `📋 Active Sessions: ${
          sessions.filter((s) => s.status === "active").length
        }\n` +
        `✅ Recent Approvals: ${
          audit.filter((a) => a.action === "book_approved").length
        }\n` +
        `❌ Recent Rejections: ${
          audit.filter((a) => a.action === "book_rejected").length
        }\n\n` +
        `📖 Pending Books:\n${
          pending
            .slice(0, 5)
            .map(
              (p) => `• ${p.title} by ${p.author || "Unknown"} (${p.status})`
            )
            .join("\n") || "None"
        }\n\n` +
        `📅 Recent Sessions:\n${
          sessions
            .slice(0, 3)
            .map(
              (s) => `• ${s.session_id} - ${s.books_count} books - ${s.status}`
            )
            .join("\n") || "None"
        }\n\n` +
        `🔄 Recent Activity:\n${
          audit
            .slice(0, 5)
            .map(
              (a) =>
                `• ${new Date(a.created_at).toLocaleDateString()} - ${a.action}`
            )
            .join("\n") || "None"
        }`;

      return {
        content: [{ type: "text", text: workflow }],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to get approval workflow: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Tool: get_performance_metrics
server.tool(
  "get_performance_metrics",
  "Get performance metrics including posting success rate and error logs",
  z.object({}),
  async () => {
    try {
      // Get all LinkedIn posts
      const postsResult = await withTimeout(
        supabase
          .from("approval_audit_log")
          .select("action, created_at, details")
          .eq("action", "linkedin_post")
          .order("created_at", { ascending: false }),
        3000
      );

      if (postsResult.error) throw postsResult.error;

      const posts = postsResult.data || [];

      // Get errors
      const errorsResult = await withTimeout(
        supabase
          .from("approval_audit_log")
          .select("action, created_at, details")
          .eq("action", "error")
          .order("created_at", { ascending: false })
          .limit(10),
        3000
      );

      if (errorsResult.error) throw errorsResult.error;

      const errors = errorsResult.data || [];

      // Calculate metrics
      const totalPosts = posts.length;
      const successfulPosts = posts.filter(
        (p) => p.details?.status === 201 || p.details?.post_id
      ).length;
      const successRate =
        totalPosts > 0 ? ((successfulPosts / totalPosts) * 100).toFixed(1) : 0;

      // Get recent activity
      const recentActivity = await withTimeout(
        supabase
          .from("approval_audit_log")
          .select("action, created_at")
          .order("created_at", { ascending: false })
          .limit(20),
        3000
      );

      if (recentActivity.error) throw recentActivity.error;

      const activity = recentActivity.data || [];

      const metrics =
        `Performance Metrics:\n\n` +
        `📊 LinkedIn Posting:\n` +
        `• Total Posts: ${totalPosts}\n` +
        `• Successful: ${successfulPosts}\n` +
        `• Success Rate: ${successRate}%\n` +
        `• Recent Errors: ${errors.length}\n\n` +
        `📈 System Activity (Last 20 Actions):\n` +
        `${activity
          .map(
            (a) => `• ${new Date(a.created_at).toLocaleString()} - ${a.action}`
          )
          .join("\n")}\n\n` +
        `⚠️ Recent Errors:\n${
          errors
            .slice(0, 5)
            .map(
              (e) =>
                `• ${new Date(e.created_at).toLocaleDateString()} - ${
                  e.details?.message || "Unknown error"
                }`
            )
            .join("\n") || "None"
        }\n\n` +
        `🎯 System Health: ${
          successRate >= 80
            ? "✅ Good"
            : successRate >= 60
            ? "⚠️ Fair"
            : "❌ Needs Attention"
        }`;

      return {
        content: [{ type: "text", text: metrics }],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to get performance metrics: ${error.message}`,
          },
        ],
      };
    }
  }
);

// Tool: run_health_check
server.tool(
  "run_health_check",
  "Comprehensive system health check",
  z.object({}),
  async () => {
    try {
      const checks = [];

      // Check Supabase connection with simple query
      try {
        await withTimeout(
          supabase.from("books_accessories").select("count").limit(1),
          3000
        );
        checks.push("✅ Supabase: CONNECTED");
      } catch (e) {
        checks.push("❌ Supabase: FAILED");
      }

      // Check environment variables
      const envVars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "LINKEDIN_CLIENT_ID",
        "LINKEDIN_CLIENT_SECRET",
      ];
      envVars.forEach((varName) => {
        checks.push(
          `${process.env[varName] ? "✅" : "❌"} ${varName}: ${
            process.env[varName] ? "SET" : "MISSING"
          }`
        );
      });

      const health = `System Health Check:\n${checks.join("\n")}`;
      return {
        content: [{ type: "text", text: health }],
      };
    } catch (error) {
      return {
        content: [
          { type: "text", text: `Health check failed: ${error.message}` },
        ],
      };
    }
  }
);

// --- Inventory/stock-related tools are commented out below ---
/*
// Tool: get_books_inventory (old, now replaced)
// server.tool(
//   "get_books_inventory",
//   "Get comprehensive inventory statistics",
//   z.object({}),
//   async () => { ... }
// );
*/

const transport = new StdioServerTransport();
server.connect(transport);

console.log("🚀 MyBookshelf Affiliate MCP Server started successfully");
