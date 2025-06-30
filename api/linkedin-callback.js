// LinkedIn OAuth Callback Handler - Vercel Serverless Function (Node.js)
// Handles LinkedIn OAuth callbacks with proper domain management

const https = require("https");
const querystring = require("querystring");

// LinkedIn OAuth configuration
const LINKEDIN_CLIENT_ID = process.env.LINKEDIN_CLIENT_ID || "78wmrhdd99ssbi";
const LINKEDIN_CLIENT_SECRET = process.env.LINKEDIN_CLIENT_SECRET;
const REDIRECT_URI = "https://mybookshelf.shop/api/linkedin-callback"; // Force apex domain

async function exchangeCodeForToken(authCode) {
  return new Promise((resolve, reject) => {
    const data = querystring.stringify({
      grant_type: "authorization_code",
      code: authCode,
      client_id: LINKEDIN_CLIENT_ID,
      client_secret: LINKEDIN_CLIENT_SECRET,
      redirect_uri: REDIRECT_URI,
    });

    const options = {
      hostname: "www.linkedin.com",
      path: "/oauth/v2/accessToken",
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": Buffer.byteLength(data),
      },
    };

    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => {
        body += chunk;
      });
      res.on("end", () => {
        try {
          const tokenData = JSON.parse(body);
          if (res.statusCode === 200) {
            resolve(tokenData);
          } else {
            reject(
              new Error(`Token exchange failed: ${res.statusCode} - ${body}`)
            );
          }
        } catch (error) {
          reject(new Error(`JSON parse error: ${error.message}`));
        }
      });
    });

    req.on("error", (error) => {
      reject(error);
    });

    req.write(data);
    req.end();
  });
}

async function getUserProfile(accessToken) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: "api.linkedin.com",
      path: "/v2/userinfo",
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    };

    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => {
        body += chunk;
      });
      res.on("end", () => {
        try {
          if (res.statusCode === 200) {
            const profile = JSON.parse(body);
            resolve(profile);
          } else {
            reject(
              new Error(`Profile fetch failed: ${res.statusCode} - ${body}`)
            );
          }
        } catch (error) {
          reject(new Error(`JSON parse error: ${error.message}`));
        }
      });
    });

    req.on("error", (error) => {
      reject(error);
    });

    req.end();
  });
}

function generateSuccessHTML(profile) {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn OAuth Success - MyBookshelf</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .success {
            color: #16a34a;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 10px;
        }
        .info {
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success">✅ LinkedIn Authorization Successful!</div>
        
        <div class="info">
            <h3>🎉 Connection Complete!</h3>
            <p><strong>Connected Account:</strong> ${
              profile.name || "Unknown"
            }</p>
            <p><strong>Email:</strong> ${profile.email || "Unknown"}</p>
            <p><strong>LinkedIn ID:</strong> ${profile.sub || "Unknown"}</p>
            
            <h4>✅ Next Steps Completed:</h4>
            <ul>
                <li>✅ Authorization code received</li>
                <li>✅ Access token obtained</li>
                <li>✅ User profile retrieved</li>
                <li>🔄 Token stored via emergency script</li>
            </ul>
        </div>
        
        <p>🚀 Your LinkedIn automation is now ready!</p>
        <a href="/admin" class="button">Go to Admin Dashboard</a>
        
        <div style="margin-top: 30px; padding: 15px; background: #fef3c7; border-radius: 8px;">
            <h4>🔧 Manual Token Storage Required:</h4>
            <p>Due to domain configuration, please run this command to complete setup:</p>
            <code style="background: #374151; color: #f3f4f6; padding: 8px; border-radius: 4px; display: block; margin: 10px 0;">
                python3 backend/scripts/emergency_oauth_complete.py "${
                  process.env.REDIRECT_URI
                }?code=YOUR_CODE&state=YOUR_STATE"
            </code>
        </div>
    </div>
</body>
</html>
    `;
}

function generateErrorHTML(errorMessage) {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn OAuth Error - MyBookshelf</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .error {
            color: #dc2626;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error">❌ LinkedIn Authorization Failed</div>
        <p><strong>Error:</strong> ${errorMessage}</p>
        <p>Please try the authorization process again.</p>
        <a href="/admin" class="button">Return to Admin Dashboard</a>
    </div>
</body>
</html>
    `;
}

export default async function handler(req, res) {
  try {
    // Force HTTPS and apex domain
    const host = req.headers.host;
    if (host.startsWith("www.")) {
      const redirectUrl = `https://mybookshelf.shop${req.url}`;
      return res.redirect(301, redirectUrl);
    }

    const { code, state, error, error_description } = req.query;

    // Handle OAuth errors
    if (error) {
      const errorMessage = `${error}: ${
        error_description || "No description provided"
      }`;
      return res
        .status(400)
        .setHeader("Content-Type", "text/html")
        .send(generateErrorHTML(errorMessage));
    }

    // Validate required parameters
    if (!code) {
      return res
        .status(400)
        .setHeader("Content-Type", "text/html")
        .send(generateErrorHTML("No authorization code received"));
    }

    if (
      state !== "mybookshelf_production_oauth" &&
      !state.startsWith("mybookshelf_")
    ) {
      return res
        .status(400)
        .setHeader("Content-Type", "text/html")
        .send(
          generateErrorHTML("Invalid state parameter - possible security issue")
        );
    }

    try {
      // Exchange code for token
      const tokenInfo = await exchangeCodeForToken(code);

      // Get user profile
      const profile = await getUserProfile(tokenInfo.access_token);

      // Return success page with profile info
      return res
        .status(200)
        .setHeader("Content-Type", "text/html")
        .send(generateSuccessHTML(profile));
    } catch (exchangeError) {
      console.error("OAuth exchange error:", exchangeError);
      return res
        .status(500)
        .setHeader("Content-Type", "text/html")
        .send(
          generateErrorHTML(`OAuth processing failed: ${exchangeError.message}`)
        );
    }
  } catch (error) {
    console.error("Handler error:", error);
    return res
      .status(500)
      .setHeader("Content-Type", "text/html")
      .send(generateErrorHTML(`Server error: ${error.message}`));
  }
}
