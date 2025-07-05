from supabase import create_client, Client
from typing import Any, Dict, List, Optional

SUPABASE_URL = "https://gricczcxqxqditthkjyd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyaWNjemN4cXhxZGl0dGhranlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE3MjQ3NTksImV4cCI6MjA2NzMwMDc1OX0.VIxVB5Tejb9UJmoO3HJgrVTF0HyPUU9WxK_-Kz4Z8nw"
SUPABASE_TABLE = "data_items"

_base_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class DatabaseClient:
    def __init__(self, client: Client, table: str):
        self.client = client
        self.table = table

    async def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.client.table(self.table).insert(item_data).execute()
        if res.data:
            return res.data[0]
        raise Exception(f"Insert failed: {res}")

    async def get_items(self, category: Optional[str] = None, limit: int = 100, offset: int = 0):
        query = self.client.table(self.table).select("*")
        if category:
            query = query.eq("category", category)
        query = query.range(offset, offset + limit - 1)
        res = query.execute()
        items = res.data or []
        total_count = len(items)
        return items, total_count

    async def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        res = self.client.table(self.table).select("*").eq("id", item_id).execute()
        if res.data:
            return res.data[0]
        return None

    async def update_item(self, item_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = self.client.table(self.table).update(update_data).eq("id", item_id).execute()
        if res.data:
            return res.data[0]
        return None

    async def delete_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        res = self.client.table(self.table).delete().eq("id", item_id).execute()
        if res.data:
            return res.data[0]
        return None

    async def get_statistics(self) -> Dict[str, Any]:
        res = self.client.table(self.table).select("*").execute()
        items = res.data or []
        count = len(items)
        categories = list(set(item["category"] for item in items if "category" in item))
        return {"count": count, "categories": categories}

    async def health_check(self) -> bool:
        try:
            self.client.table(self.table).select("id").limit(1).execute()
            return True
        except Exception:
            return False

db_client = DatabaseClient(_base_client, SUPABASE_TABLE)