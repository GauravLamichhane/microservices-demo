from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LikeConsumer(AsyncWebsocketConsumer):
  async def connect(self):#runs automatically when a browser connects.
    print("WebSockets connected")
    await self.channel_layer.group_add("likes", self.channel_name)
    await self.accept()

  async def disconnect(self, close_code):
    print("WebSockets disconnected")
    await self.channel_layer.group_discard("likes", self.channel_name)

  async def like_updated(self, event):
    print("Sending:", event)
    await self.send(text_data=json.dumps({
      "product_id": event["product_id"],
      "likes": event["likes"],
    }))