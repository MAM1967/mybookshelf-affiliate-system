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
  const { code } = req.body;
  if (!code) {
    return res.status(400).json({ success: false, message: "Missing code" });
  }
  // Check code in Supabase
  const { data, error } = await supabase
    .from("admin_login_codes")
    .select("*")
    .eq("code", code)
    .gt("expires_at", new Date().toISOString())
    .single();
  if (error || !data) {
    return res
      .status(401)
      .json({ success: false, message: "Invalid or expired code" });
  }
  // Delete code after use
  await supabase.from("admin_login_codes").delete().eq("id", data.id);
  // Generate a session token (for demo, use a timestamp)
  const session_token = "admin-session-" + Date.now();
  return res.status(200).json({ success: true, session_token });
}
