from supabase import create_client, Client

SUPABASE_URL = "https://gricczcxqxqditthkjyd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyaWNjemN4cXhxZGl0dGhranlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE3MjQ3NTksImV4cCI6MjA2NzMwMDc1OX0.VIxVB5Tejb9UJmoO3HJgrVTF0HyPUU9WxK_-Kz4Z8nw"
SUPABASE_TABLE = "data_items"

db_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)