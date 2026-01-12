from collections import deque

class RingBuffer:
    
    def __init__(self, capacity = 0):
        if capacity <= 0:
            raise ValueError("La capacidad debe ser mayor que cero.")
        self._storage = deque(maxlen=capacity)
        
    def append(self, item):
        """Agrega una nueva lectura al buffer."""
        self._storage.append(item)

    def extend(self, items):
        """Agrega múltiples lecturas al buffer."""
        self._storage.extend(items)

    def snapshot(self):
        """Devuelve una lista con las lecturas en orden de llegada."""
        return list(self._storage)

    def clear(self):
        """Limpia todas las lecturas del buffer."""
        self._storage.clear()

    def __len__(self):
        """Cantidad de lecturas almacenadas actualmente."""
        return len(self._storage)
    