import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res
      .status(405)
      .json({ success: false, message: "Method not allowed" });
  }
  // Generate a random 6-digit code
  const code = Math.floor(100000 + Math.random() * 900000).toString();
  const expires_at = new Date(Date.now() + 10 * 60 * 1000).toISOString(); // 10 min expiry
  // Store code in Supabase
  await supabase.from("admin_login_codes").insert({ code, expires_at });
  // Send code via Resend
  const adminEmail = process.env.ADMIN_EMAIL;
  const resendApiKey = process.env.RESEND_API_KEY;
  const emailRes = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${resendApiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: "MyBookshelf Admin <noreply@mybookshelf.shop>",
      to: adminEmail,
      subject: "Your MyBookshelf Admin Login Code",
      html: `<p>Your one-time login code is: <b>${code}</b></p><p>This code will expire in 10 minutes.</p>`,
    }),
  });
  if (!emailRes.ok) {
    return res
      .status(500)
      .json({ success: false, message: "Failed to send code" });
  }
  return res.status(200).json({ success: true, message: "Code sent" });
}
