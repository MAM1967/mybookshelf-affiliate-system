export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const envCheck = {
    timestamp: new Date().toISOString(),
    supabase: {
      url: process.env.SUPABASE_URL ? "✅ Set" : "❌ Missing",
      anon_key: process.env.SUPABASE_ANON_KEY ? "✅ Set" : "❌ Missing",
    },
    email: {
      resend_api_key: process.env.RESEND_API_KEY ? "✅ Set" : "❌ Missing",
      admin_email: process.env.ADMIN_EMAIL ? "✅ Set" : "❌ Missing",
    },
    linkedin: {
      client_id: process.env.LINKEDIN_CLIENT_ID ? "✅ Set" : "❌ Missing",
    },
    admin_login: {
      table_exists: "Check Supabase for admin_login_codes table",
      api_endpoints: {
        request_code: "/api/request-login-code",
        verify_code: "/api/verify-login-code",
      },
    },
  };

  res.status(200).json(envCheck);
}
