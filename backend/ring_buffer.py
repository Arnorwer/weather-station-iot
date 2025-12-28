from collections import deque
from datetime import datetime, date

class RingBuffer:
    
    def __init__(self, capacity = 0):
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

class TwoDayStore:
    def __init__(self, capacity_day = 1440):
        if capacity_day <= 0:
            raise ValueError("La capacidad por día debe ser mayor que cero.")
        
        self._capacity_day = capacity_day
        self._buffer_per_day = {}
        
    @staticmethod
    def _to_actual_date(seconds):
        # Obtener la fecha actual desde timestamp en segundos
        return datetime.fromtimestamp(seconds).date()
    
    def _limit_to_two_days(self):
        # Limitar el almacenamiento a solo dos días
        if len(self._buffer_per_day) <= 2:
            return
        
        dates = sorted(self._buffer_per_day.keys())
        
        while len(dates) > 2:
            oldest = dates.pop(0)
            self._buffer_per_day.pop(oldest, None)
            
    def _get_or_create_buffer(self, d):
        # Obtener o crear el buffer para una fecha específica
        date_buffer = self._buffer_per_day.get(d)
        if date_buffer is None:
            date_buffer = RingBuffer(self._capacity_day)
            self._buffer_per_day[d] = date_buffer
        return date_buffer
    
    def add_reading(self, data):
        # Agregar una lectura al buffer correspondiente
        actual_date = data.get('timestamp')
        if not actual_date:
            actual_date = datetime.now().timestamp()
        else:
            actual_date = datetime.fromisoformat(actual_date).timestamp()
        local_date = self._to_actual_date(actual_date)
        
        buffer_for_date = self._get_or_create_buffer(local_date)
        buffer_for_date.append(data)
        self._limit_to_two_days()
        
    def today_date(self):
        return datetime.now().date()

    def snapshot_today(self):
        today = self.today_date()
        return self._by_day.get(today, RingBuffer(self._maxlen_per_day)).snapshot()

    def yesterday_date(self):
        today = self.today_date()
        return today.fromordinal(today.toordinal() - 1)

    def snapshot_yesterday(self):
        yesterday = self.yesterday_date()
        return self._by_day.get(yesterday, RingBuffer(self._maxlen_per_day)).snapshot()