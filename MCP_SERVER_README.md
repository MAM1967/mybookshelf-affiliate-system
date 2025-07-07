# MyBookshelf Affiliate System - MCP Server

## Overview

This MCP (Model Context Protocol) server provides programmatic access to your MyBookshelf affiliate system, allowing AI assistants and other tools to interact with your LinkedIn automation, Supabase database, and system components.

## Features

### LinkedIn Management

- **get_linkedin_status**: Check current LinkedIn token status and permissions
- **get_scheduled_posts**: View all scheduled LinkedIn posts
- **create_linkedin_post**: Create new LinkedIn posts with affiliate links
- **get_linkedin_tokens**: List all LinkedIn tokens in the system
- **refresh_linkedin_token**: Initiate token refresh for a specific email

### Inventory Management

- **get_books_inventory**: Get comprehensive inventory statistics
- **get_affiliate_links**: Retrieve Amazon affiliate links for products
- **update_book_pricing**: Update pricing for specific books

### System Monitoring

- **run_health_check**: Comprehensive system health check
- **get_system_logs**: Retrieve system logs for debugging
- **get_database_stats**: Get database table statistics
- **trigger_automation**: Trigger automation scripts

### Email System

- **test_email_system**: Test email integration (Resend API)

## Installation

1. **Install Dependencies**:

   ```bash
   npm install
   ```

2. **Set Environment Variables**:
   Create a `.env` file or set these environment variables:

   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   SUPABASE_ANON_KEY=your_anon_key
   LINKEDIN_CLIENT_ID=your_linkedin_client_id
   LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
   ```

3. **Make Server Executable**:
   ```bash
   chmod +x mcp-server.js
   ```

## Usage

### Running the Server

**Development Mode** (with auto-restart):

```bash
npm run dev
```

**Production Mode**:

```bash
npm start
```

### Testing the Server

Run the test suite to verify functionality:

```bash
npm test
```

### Using with MCP Clients

1. **Claude Desktop**: Add to your MCP configuration:

   ```json
   {
     "mcpServers": {
       "mybookshelf-affiliate-system": {
         "command": "node",
         "args": ["/path/to/your/mcp-server.js"],
         "env": {
           "SUPABASE_URL": "your_supabase_url",
           "SUPABASE_SERVICE_ROLE_KEY": "your_service_role_key",
           "SUPABASE_ANON_KEY": "your_anon_key",
           "LINKEDIN_CLIENT_ID": "your_linkedin_client_id",
           "LINKEDIN_CLIENT_SECRET": "your_linkedin_client_secret"
         }
       }
     }
   }
   ```

2. **Other MCP Clients**: Use the `mcp-config.json` file as a template.

## Available Tools

### LinkedIn Management

#### `get_linkedin_status`

Get current LinkedIn connection status and token information.

**Response**: Token status, admin email, organization permissions, expiration date.

#### `get_scheduled_posts`

Retrieve all scheduled LinkedIn posts.

**Response**: List of scheduled posts with status (posted/pending).

#### `create_linkedin_post`

Create a new LinkedIn post with affiliate link.

**Parameters**:

- `title` (string): Post title
- `description` (string): Post description
- `affiliate_link` (string): Amazon affiliate link

#### `get_linkedin_tokens`

List all LinkedIn tokens in the system.

**Response**: All tokens with status and creation dates.

#### `refresh_linkedin_token`

Initiate token refresh for a specific email.

**Parameters**:

- `email` (string): Admin email address

### Inventory Management

#### `get_books_inventory`

Get comprehensive inventory statistics.

**Response**: Total items, books vs accessories, ASIN coverage, affiliate link coverage.

#### `get_affiliate_links`

Retrieve Amazon affiliate links for products.

**Parameters**:

- `limit` (number, optional): Number of links to return (default: 10)

#### `update_book_pricing`

Update pricing for a specific book.

**Parameters**:

- `book_id` (string): Book ID
- `new_price` (number): New price

### System Monitoring

#### `run_health_check`

Comprehensive system health check.

**Response**: Supabase connection, LinkedIn tokens, environment variables status.

#### `get_system_logs`

Retrieve system logs for debugging.

**Parameters**:

- `lines` (number, optional): Number of lines to return (default: 50)
- `log_file` (string, optional): Log file name (default: "automated_linkedin_poster.log")

#### `get_database_stats`

Get database table statistics.

**Response**: Record counts for all tables.

#### `trigger_automation`

Trigger automation scripts.

**Parameters**:

- `type` (string, optional): Automation type (default: "linkedin_posting")

### Email System

#### `test_email_system`

Test email integration (Resend API).

**Response**: Email system test status.

## Error Handling

The MCP server includes comprehensive error handling:

- **Database Errors**: Graceful handling of Supabase connection issues
- **Missing Parameters**: Clear error messages for required parameters
- **Authentication Errors**: Proper handling of LinkedIn token issues
- **File System Errors**: Safe handling of log file access

## Security Considerations

1. **Environment Variables**: Never commit sensitive credentials to version control
2. **Token Management**: Tokens are stored securely in Supabase
3. **Access Control**: Only authorized admin emails can access the system
4. **Input Validation**: All parameters are validated before processing

## Troubleshooting

### Common Issues

1. **"Supabase not configured"**: Check environment variables
2. **"No active LinkedIn tokens"**: Complete OAuth setup
3. **"Token expired"**: Refresh LinkedIn token
4. **"Database connection failed"**: Verify Supabase credentials

### Debug Mode

Enable debug logging by setting:

```bash
DEBUG=mcp:*
```

### Log Files

Check these log files for issues:

- `automated_linkedin_poster.log`: LinkedIn automation logs
- `final_linkedin_poster.log`: Final posting logs
- `linkedin_automation.log`: General LinkedIn logs

## Integration Examples

### With Claude Desktop

Once configured, you can ask Claude:

- "Check the LinkedIn status of my affiliate system"
- "Show me all scheduled posts for this week"
- "Run a health check on the system"
- "Get the latest system logs"
- "Update the price of book ID 123 to $29.99"

### With Custom Scripts

```javascript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

const client = new Client(transport);
await client.connect();

// Get system status
const status = await client.callTool("run_health_check", {});
console.log(status.content[0].text);

// Create a LinkedIn post
const post = await client.callTool("create_linkedin_post", {
  title: "Amazing Leadership Book",
  description: "Transform your leadership skills with this incredible book!",
  affiliate_link: "https://amazon.com/dp/B08XXXXX",
});
```

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review system logs
3. Run health checks
4. Verify environment variables

## Version History

- **v1.0.0** (July 7, 2025): Initial release with comprehensive tool set

---

**Last Updated**: July 7, 2025
