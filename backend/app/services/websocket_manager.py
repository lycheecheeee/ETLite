"""
WebSocket Connection Manager
WebSocket 連接管理 - 實時推送
"""
from fastapi import WebSocket
from typing import Dict, List, Set
import json
from datetime import datetime

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections
        self.active_connections: List[WebSocket] = []
        
        # User-specific connections
        self.user_connections: Dict[str, List[WebSocket]] = {}
        
        # Channel subscriptions
        self.channel_subscribers: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept and store new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove disconnected client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from user connections
        for user_id, connections in self.user_connections.items():
            if websocket in connections:
                connections.remove(websocket)
        
        # Remove from channel subscriptions
        for channel, subscribers in self.channel_subscribers.items():
            if websocket in subscribers:
                subscribers.remove(websocket)
        
        print(f"🔌 WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id not in self.user_connections:
            return
        
        disconnected = []
        for connection in self.user_connections.get(user_id, []):
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
            if user_id in self.user_connections:
                self.user_connections[user_id].remove(conn)
    
    async def subscribe_to_channel(self, websocket: WebSocket, channel: str):
        """Subscribe connection to a channel"""
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        
        self.channel_subscribers[channel].add(websocket)
        print(f"📡 Client subscribed to {channel}. Subscribers: {len(self.channel_subscribers[channel])}")
    
    async def unsubscribe_from_channel(self, websocket: WebSocket, channel: str):
        """Unsubscribe connection from a channel"""
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(websocket)
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast message to all subscribers of a channel"""
        if channel not in self.channel_subscribers:
            return
        
        disconnected = []
        for connection in self.channel_subscribers[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up
        for conn in disconnected:
            self.disconnect(conn)
    
    def register_user(self, user_id: str, websocket: WebSocket):
        """Register user-session mapping"""
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
    
    async def notify_podcast_update(self, podcast_id: str, status: str, user_id: str = None):
        """
        Notify clients about podcast generation update
        
        Args:
            podcast_id: Podcast identifier
            status: Generation status (generating/completed/failed)
            user_id: Optional specific user to notify
        """
        message = {
            "type": "podcast_update",
            "podcast_id": podcast_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "message": f"Podcast {status}",
                "progress": self._get_progress(status)
            }
        }
        
        if user_id:
            await self.send_to_user(user_id, message)
        else:
            await self.broadcast_to_channel("podcasts", message)
    
    def _get_progress(self, status: str) -> int:
        """Get progress percentage based on status"""
        progress_map = {
            "pending": 0,
            "generating": 50,
            "completed": 100,
            "failed": -1
        }
        return progress_map.get(status, 0)


# Global connection manager instance
ws_manager = ConnectionManager()
