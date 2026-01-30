"""
Utilidades para serialización JSON
"""
import json
from decimal import Decimal
from datetime import datetime, date
from typing import Any

class DecimalEncoder(json.JSONEncoder):
    """Encoder JSON personalizado que maneja objetos Decimal y datetime"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

def serialize_decimal(obj: Any) -> Any:
    """Convierte recursivamente objetos Decimal a float en estructuras de datos"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: serialize_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_decimal(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(serialize_decimal(item) for item in obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    return obj

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Serializa a JSON manejando objetos Decimal automáticamente"""
    return json.dumps(obj, cls=DecimalEncoder, **kwargs)