from collections import deque
import threading
class RingBuffer:
    
    def __init__(self, capacity = 0):
        if capacity <= 0:
            raise ValueError("La capacidad debe ser mayor que cero.")
        self._capacity = capacity
        self._storage = deque(maxlen=capacity)
        self._lock = threading.Lock()
    
    @property
    def capacity(self):
        """Retorna la capacidad máxima del buffer."""
        return self._capacity
        
    def append(self, item):
        """Agrega una nueva lectura al buffer."""
        with self._lock:
            self._storage.append(item)
            
    def extend(self, items):
        """Agrega múltiples lecturas al buffer."""
        with self._lock:
            self._storage.extend(items)

    def snapshot(self):
        """Devuelve una lista con las lecturas en orden de llegada."""
        with self._lock:
            return list(self._storage)
        
    def clear(self):
        """Limpia todas las lecturas del buffer."""
        with self._lock:
            self._storage.clear()

    def __len__(self):
        """Cantidad de lecturas almacenadas actualmente."""
        with self._lock:
            return len(self._storage)
    