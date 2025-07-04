# Supabase Setup Guide

## Overview

This guide will help you set up Supabase for the FastAPI Metrics Monitoring System. The application uses Supabase as the database backend for storing and managing data items.

## Prerequisites

- Supabase account (free tier available)
- Basic understanding of SQL
- Access to Supabase dashboard

## Step 1: Create Supabase Project

1. **Sign up/Login to Supabase**
   - Go to [https://supabase.com](https://supabase.com)
   - Sign up for a free account or login if you already have one

2. **Create a New Project**
   - Click "New Project"
   - Choose your organization
   - Enter project name: `fastapi-metrics-monitoring`
   - Enter database password (save this securely)
   - Select region closest to your users
   - Click "Create new project"

3. **Wait for Project Setup**
   - Project creation takes 1-2 minutes
   - You'll be redirected to the project dashboard when ready

## Step 2: Get Project Credentials

1. **Navigate to Project Settings**
   - Click on the "Settings" icon in the left sidebar
   - Go to "API" section

2. **Copy Project URL and API Key**
   - **Project URL**: Copy the URL (e.g., `https://your-project-id.supabase.co`)
   - **API Key**: Copy the `anon public` key (this is safe to use in client-side code)

3. **Update Application Configuration**
   - Update the `SUPABASE_URL` and `SUPABASE_KEY` in your `.env` file
   - Or update the default values in `app/config.py`

## Step 3: Create Database Schema

1. **Open SQL Editor**
   - In the Supabase dashboard, click on "SQL Editor" in the left sidebar
   - Click "New query"

2. **Create the data_items Table**
   
   Copy and paste the following SQL script:

   ```sql
   -- Create the data_items table
   CREATE TABLE IF NOT EXISTS data_items (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       name TEXT NOT NULL,
       value DECIMAL NOT NULL,
       category TEXT NOT NULL,
       metadata JSONB DEFAULT '{}',
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Create an index on category for faster filtering
   CREATE INDEX IF NOT EXISTS idx_data_items_category ON data_items(category);

   -- Create an index on created_at for faster sorting
   CREATE INDEX IF NOT EXISTS idx_data_items_created_at ON data_items(created_at DESC);

   -- Create a function to automatically update the updated_at column
   CREATE OR REPLACE FUNCTION update_updated_at_column()
   RETURNS TRIGGER AS $$
   BEGIN
       NEW.updated_at = NOW();
       RETURN NEW;
   END;
   $$ language 'plpgsql';

   -- Create a trigger to automatically update updated_at on row updates
   DROP TRIGGER IF EXISTS update_data_items_updated_at ON data_items;
   CREATE TRIGGER update_data_items_updated_at
       BEFORE UPDATE ON data_items
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at_column();

   -- Insert some sample data (optional)
   INSERT INTO data_items (name, value, category, metadata) VALUES
   ('Sample Item 1', 42.5, 'demo', '{"source": "setup", "priority": "high"}'),
   ('Sample Item 2', 78.9, 'demo', '{"source": "setup", "priority": "medium"}'),
   ('Sample Item 3', 15.3, 'test', '{"source": "setup", "priority": "low"}')
   ON CONFLICT (id) DO NOTHING;
   ```

3. **Execute the Script**
   - Click "Run" to execute the SQL script
   - You should see "Success. No rows returned" message
   - The table and sample data are now created

## Step 4: Configure Row Level Security (Optional but Recommended)

1. **Enable RLS on the Table**
   
   ```sql
   -- Enable Row Level Security
   ALTER TABLE data_items ENABLE ROW LEVEL SECURITY;

   -- Create a policy that allows all operations for authenticated users
   -- For development/demo purposes, we'll allow anonymous access
   CREATE POLICY "Allow all operations for anon users" ON data_items
   FOR ALL USING (true) WITH CHECK (true);
   ```

2. **For Production Use**
   
   For production applications, consider more restrictive policies:
   
   ```sql
   -- Example: Only allow operations for authenticated users
   CREATE POLICY "Allow all operations for authenticated users" ON data_items
   FOR ALL USING (auth.role() = 'authenticated') WITH CHECK (auth.role() = 'authenticated');
   ```

## Step 5: Verify Database Connection

1. **Test the Connection**
   - Start your FastAPI application
   - Visit `http://localhost:8000/health/database`
   - You should see a healthy database status

2. **Test CRUD Operations**
   
   ```bash
   # Create a test item
   curl -X POST "http://localhost:8000/api/v1/data" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Item",
       "value": 123.45,
       "category": "test",
       "metadata": {"source": "api_test"}
     }'

   # Get all items
   curl "http://localhost:8000/api/v1/data"

   # Get statistics
   curl "http://localhost:8000/api/v1/stats"
   ```

## Step 6: Monitor Database Usage

1. **Database Dashboard**
   - In Supabase dashboard, go to "Database" section
   - Monitor table size, query performance, and connections

2. **API Usage**
   - Go to "Settings" > "Usage" to monitor API calls
   - Free tier includes 50,000 monthly active users and 500MB database

## Environment Variables

Make sure your `.env` file contains:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_TABLE=data_items
```

## Database Schema Reference

### data_items Table Structure

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | UUID | Primary key | AUTO-GENERATED |
| `name` | TEXT | Item name | NOT NULL |
| `value` | DECIMAL | Numeric value | NOT NULL |
| `category` | TEXT | Item category | NOT NULL |
| `metadata` | JSONB | Additional data | DEFAULT '{}' |
| `created_at` | TIMESTAMP WITH TIME ZONE | Creation time | AUTO-GENERATED |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Last update time | AUTO-UPDATED |

### Indexes

- `idx_data_items_category`: Speeds up category filtering
- `idx_data_items_created_at`: Speeds up date-based sorting

### Triggers

- `update_data_items_updated_at`: Automatically updates `updated_at` on row modifications

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if SUPABASE_URL and SUPABASE_KEY are correct
   - Verify project is active in Supabase dashboard

2. **Permission Denied**
   - Check Row Level Security policies
   - Ensure API key has correct permissions

3. **Table Not Found**
   - Verify the SQL schema was executed successfully
   - Check table name matches SUPABASE_TABLE environment variable

4. **SSL Certificate Issues**
   - Supabase uses SSL by default
   - Ensure your environment supports HTTPS connections

### Debugging

1. **Enable Debug Logging**
   ```env
   DEBUG=true
   ```

2. **Check Application Logs**
   ```bash
   docker-compose logs fastapi-app
   ```

3. **Test Database Connection Directly**
   ```python
   from supabase import create_client
   
   url = "your-supabase-url"
   key = "your-supabase-key"
   supabase = create_client(url, key)
   
   # Test connection
   result = supabase.table("data_items").select("count", count="exact").execute()
   print(f"Connection successful. Row count: {result.count}")
   ```

## Security Best Practices

1. **API Key Management**
   - Never commit API keys to version control
   - Use environment variables for configuration
   - Rotate keys periodically

2. **Row Level Security**
   - Enable RLS for production applications
   - Create specific policies for different user roles
   - Test policies thoroughly

3. **Database Access**
   - Use the anon key for client-side operations
   - Use service role key only for server-side operations
   - Monitor API usage and set up alerts

## Scaling Considerations

1. **Free Tier Limits**
   - 50,000 monthly active users
   - 500MB database storage
   - 2GB bandwidth

2. **Upgrading**
   - Pro plan: $25/month for higher limits
   - Team plan: $599/month for team features
   - Enterprise: Custom pricing

3. **Performance Optimization**
   - Add indexes for frequently queried columns
   - Use connection pooling
   - Implement caching for read-heavy workloads

---