import asyncio
from typing import Callable, Dict, List, Any

class EventDispatcher:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Any], asyncio.Future]]] = {}

    def subscribe(self, event_name: str, callback: Callable[[Any], asyncio.Future]):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)

    async def dispatch(self, event_name: str, payload: Any):
        tasks = []
        for callback in self.subscribers.get(event_name, []):
            tasks.append(callback(payload))
        if tasks:
            await asyncio.gather(*tasks)


_event_dispatcher = EventDispatcher()

def get_event_dispatcher():
    global _event_dispatcher
    return _event_dispatcher