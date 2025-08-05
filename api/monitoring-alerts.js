/**
 * Monitoring Alert System
 * Sends notifications when system health checks fail
 */

import { createClient } from "@supabase/supabase-js";

// Environment variables
const RESEND_API_KEY = process.env.RESEND_API_KEY;
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || "mcddsl@icloud.com";

class MonitoringAlerts {
  constructor() {
    this.supabase = createClient(
      process.env.SUPABASE_URL || "https://ackcgrnizuhauccnbiml.supabase.co",
      process.env.SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFja2Nncm5penVoYXVjY25iaW1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMjc4MzEsImV4cCI6MjA2NjgwMzgzMX0.SXpIMuNBgUhcEQUHzpEB1zZAdF-UTGvmY81EFUtsAwc"
    );
  }

  async sendEmailAlert(subject, message, priority = "medium") {
    if (!RESEND_API_KEY) {
      console.log("⚠️ Resend API key not configured - skipping email alert");
      return false;
    }

    try {
      const response = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "admin@mybookshelf.shop",
          to: [ADMIN_EMAIL],
          subject: `[${priority.toUpperCase()}] MyBookshelf Alert: ${subject}`,
          html: this.createEmailTemplate(subject, message, priority),
        }),
      });

      if (!response.ok) {
        throw new Error(`Resend API error: ${response.status}`);
      }

      console.log(`✅ Alert email sent: ${subject}`);
      return true;
    } catch (error) {
      console.error("❌ Failed to send alert email:", error);
      return false;
    }
  }

  createEmailTemplate(subject, message, priority) {
    const priorityColors = {
      low: "#2196f3",
      medium: "#ff9800", 
      high: "#f44336",
      critical: "#d32f2f"
    };

    const color = priorityColors[priority] || "#666";

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MyBookshelf Alert</title>
      </head>
      <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
          <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: ${color}; margin: 0; font-size: 2em;">📚 MyBookshelf</h1>
            <p style="color: #666; margin: 10px 0 0 0;">System Monitoring Alert</p>
          </div>
          
          <div style="border-left: 4px solid ${color}; padding-left: 20px; margin: 20px 0;">
            <h2 style="color: ${color}; margin: 0 0 10px 0;">${subject}</h2>
            <p style="color: #333; line-height: 1.6; margin: 0;">${message}</p>
          </div>
          
          <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin: 0 0 10px 0; color: #333;">System Details</h3>
            <p style="margin: 5px 0; color: #666;">
              <strong>Priority:</strong> ${priority.toUpperCase()}
            </p>
            <p style="margin: 5px 0; color: #666;">
              <strong>Time:</strong> ${new Date().toLocaleString()}
            </p>
            <p style="margin: 5px 0; color: #666;">
              <strong>System:</strong> MyBookshelf Affiliate System
            </p>
          </div>
          
          <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
            <p style="color: #999; font-size: 0.9em; margin: 0;">
              This is an automated alert from the MyBookshelf monitoring system.
            </p>
          </div>
        </div>
      </body>
      </html>
    `;
  }

  async checkHealthAndAlert() {
    try {
      console.log("🔍 Running health check with alerts...");

      // Get health status
      const response = await fetch(`${process.env.VERCEL_URL || 'https://mybookshelf-affiliate-system.vercel.app'}/api/health-check`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        signal: AbortSignal.timeout(30000),
      });

      if (!response.ok) {
        await this.sendEmailAlert(
          "Health Check Failed",
          `Health check endpoint returned ${response.status}: ${response.statusText}`,
          "high"
        );
        return;
      }

      const healthData = await response.json();
      
      if (!healthData.healthy) {
        const failedChecks = Object.entries(healthData.checks)
          .filter(([name, check]) => check.status === 'error')
          .map(([name, check]) => `${name}: ${check.message}`)
          .join('\n');

        await this.sendEmailAlert(
          "System Health Degraded",
          `The following system checks are failing:\n\n${failedChecks}\n\nOverall Status: ${healthData.status}`,
          "medium"
        );
      } else {
        console.log("✅ System health is good - no alerts needed");
      }

    } catch (error) {
      console.error("❌ Health check alert failed:", error);
      await this.sendEmailAlert(
        "Monitoring System Error",
        `Failed to perform health check: ${error.message}`,
        "critical"
      );
    }
  }

  async sendPriceUpdateAlert(stats) {
    try {
      const subject = stats.successfulUpdates > 0 ? 
        "Price Update Completed" : 
        "Price Update Failed";

      const message = `
        Price update process completed with the following results:
        
        📦 Total Items: ${stats.totalItems}
        ✅ Successful Updates: ${stats.successfulUpdates}
        ❌ Failed Updates: ${stats.failedUpdates}
        💰 Price Changes: ${stats.priceChanges.length}
        ⏱️ Duration: ${((stats.endTime - stats.startTime) / 1000).toFixed(2)}s
        
        ${stats.errors.length > 0 ? `\nErrors:\n${stats.errors.join('\n')}` : ''}
      `;

      const priority = stats.failedUpdates > 0 ? "medium" : "low";

      await this.sendEmailAlert(subject, message, priority);

    } catch (error) {
      console.error("❌ Failed to send price update alert:", error);
    }
  }

  async sendCronJobAlert(status, details) {
    try {
      const subject = status === 'success' ? 
        "Cron Job Completed Successfully" : 
        "Cron Job Failed";

      const message = `
        Cron job execution ${status}:
        
        ${details}
        
        Time: ${new Date().toLocaleString()}
      `;

      const priority = status === 'success' ? "low" : "high";

      await this.sendEmailAlert(subject, message, priority);

    } catch (error) {
      console.error("❌ Failed to send cron job alert:", error);
    }
  }
}

// Vercel function handler
export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const alerts = new MonitoringAlerts();
    const { type, data } = req.body;

    switch (type) {
      case 'health_check':
        await alerts.checkHealthAndAlert();
        break;
      case 'price_update':
        await alerts.sendPriceUpdateAlert(data);
        break;
      case 'cron_job':
        await alerts.sendCronJobAlert(data.status, data.details);
        break;
      default:
        return res.status(400).json({ error: "Invalid alert type" });
    }

    res.status(200).json({ success: true, message: "Alert sent successfully" });
  } catch (error) {
    console.error("Monitoring alert error:", error);
    res.status(500).json({
      error: "Alert failed",
      message: error.message,
    });
  }
}

export { MonitoringAlerts }; 