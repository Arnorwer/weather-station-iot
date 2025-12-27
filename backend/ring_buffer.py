from collections import deque

class RingBuffer:
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("La capacidad debe ser mayor que cero.")
        self._storage = deque(maxlen=capacity)
        
    def append(self, item):
        self._storage.append(item)
        
    def extend(self, items):
        self._storage.extend(items)
        
    def snapshot(self):
        return list(self._storage)
    
    def clear(self):
        self._storage.clear()
    
    def __len__(self):
        return len(self._storage)
