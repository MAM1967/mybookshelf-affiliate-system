export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  // Check environment variables
  const envVars = {
    SUPABASE_URL: process.env.SUPABASE_URL ? "✅ Set" : "❌ Missing",
    SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY ? "✅ Set" : "❌ Missing",
    ADMIN_EMAIL: process.env.ADMIN_EMAIL ? "✅ Set" : "❌ Missing",
    RESEND_API_KEY: process.env.RESEND_API_KEY ? "✅ Set" : "❌ Missing",
  };

  return res.status(200).json({
    message: "Environment Variables Test",
    environment: process.env.NODE_ENV || "development",
    variables: envVars,
    timestamp: new Date().toISOString(),
  });
}
