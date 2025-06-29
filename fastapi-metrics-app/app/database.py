"""
Supabase database client and operations
"""
import logging
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from postgrest.exceptions import APIError
from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Supabase database client for handling all database operations
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        try:
            self.client: Client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if Supabase connection is healthy
        
        Returns:
            bool: True if connection is healthy
        """
        try:
            # Try to perform a simple query to check connection
            result = self.client.table(settings.supabase_table).select("count", count="exact").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False
    
    async def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new data item in Supabase
        
        Args:
            item_data: Dictionary containing item data
            
        Returns:
            Created item data
            
        Raises:
            Exception: If creation fails
        """
        try:
            result = self.client.table(settings.supabase_table).insert(item_data).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Created item with ID: {result.data[0].get('id')}")
                return result.data[0]
            else:
                raise Exception("No data returned from insert operation")
                
        except APIError as e:
            logger.error(f"Supabase API error creating item: {e}")
            raise Exception(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error creating item: {e}")
            raise
    
    async def get_items(
        self, 
        category: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Retrieve data items from Supabase with optional filtering and pagination
        
        Args:
            category: Optional category filter
            limit: Maximum number of items to return
            offset: Number of items to skip
            
        Returns:
            Tuple of (items list, total count)
            
        Raises:
            Exception: If retrieval fails
        """
        try:
            # Build query
            query = self.client.table(settings.supabase_table).select("*")
            
            # Add category filter if provided
            if category:
                query = query.eq("category", category)
            
            # Get total count for pagination
            count_query = self.client.table(settings.supabase_table).select("*", count="exact")
            if category:
                count_query = count_query.eq("category", category)
            
            count_result = count_query.execute()
            total_count = count_result.count if count_result.count is not None else 0
            
            # Apply pagination and execute
            result = query.range(offset, offset + limit - 1).order("created_at", desc=True).execute()
            
            items = result.data if result.data else []
            logger.info(f"Retrieved {len(items)} items (total: {total_count})")
            
            return items, total_count
            
        except APIError as e:
            logger.error(f"Supabase API error retrieving items: {e}")
            raise Exception(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error retrieving items: {e}")
            raise
    
    async def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific data item by ID
        
        Args:
            item_id: Unique identifier of the item
            
        Returns:
            Item data or None if not found
            
        Raises:
            Exception: If retrieval fails
        """
        try:
            result = self.client.table(settings.supabase_table).select("*").eq("id", item_id).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Retrieved item with ID: {item_id}")
                return result.data[0]
            else:
                logger.info(f"Item not found with ID: {item_id}")
                return None
                
        except APIError as e:
            logger.error(f"Supabase API error retrieving item {item_id}: {e}")
            raise Exception(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error retrieving item {item_id}: {e}")
            raise
    
    async def update_item(self, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing data item
        
        Args:
            item_id: Unique identifier of the item
            item_data: Updated item data
            
        Returns:
            Updated item data or None if not found
            
        Raises:
            Exception: If update fails
        """
        try:
            # Remove id from update data if present
            update_data = {k: v for k, v in item_data.items() if k != 'id'}
            
            result = self.client.table(settings.supabase_table).update(update_data).eq("id", item_id).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Updated item with ID: {item_id}")
                return result.data[0]
            else:
                logger.info(f"Item not found for update with ID: {item_id}")
                return None
                
        except APIError as e:
            logger.error(f"Supabase API error updating item {item_id}: {e}")
            raise Exception(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error updating item {item_id}: {e}")
            raise
    
    async def delete_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Delete a data item by ID
        
        Args:
            item_id: Unique identifier of the item
            
        Returns:
            Deleted item data or None if not found
            
        Raises:
            Exception: If deletion fails
        """
        try:
            # First get the item to return it
            item = await self.get_item_by_id(item_id)
            if not item:
                return None
            
            # Delete the item
            result = self.client.table(settings.supabase_table).delete().eq("id", item_id).execute()
            
            logger.info(f"Deleted item with ID: {item_id}")
            return item
            
        except APIError as e:
            logger.error(f"Supabase API error deleting item {item_id}: {e}")
            raise Exception(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error deleting item {item_id}: {e}")
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored data items
        
        Returns:
            Dictionary containing statistics
            
        Raises:
            Exception: If statistics calculation fails
        """
        try:
            # Get all items for statistics calculation
            result = self.client.table(settings.supabase_table).select("value, category").execute()
            
            if not result.data:
                return {
                    "total_items": 0,
                    "categories": {},
                    "average_value": 0,
                    "min_value": 0,
                    "max_value": 0
                }
            
            items = result.data
            values = [float(item["value"]) for item in items if item.get("value") is not None]
            
            # Calculate category distribution
            categories = {}
            for item in items:
                category = item.get("category", "unknown")
                categories[category] = categories.get(category, 0) + 1
            
            # Calculate value statistics
            stats = {
                "total_items": len(items),
                "categories": categories,
                "average_value": sum(values) / len(values) if values else 0,
                "min_value": min(values) if values else 0,
                "max_value": max(values) if values else 0
            }
            
            logger.info(f"Calculated statistics for {len(items)} items")
            return stats
            
        except APIError as e:
            logger.error(f"Supabase API error calculating statistics: {e}")
            raise Exception(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            raise


# Global database client instance
db_client = SupabaseClient()