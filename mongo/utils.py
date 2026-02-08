import json
from datetime import datetime
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    """Handle ObjectId and datetime serialization"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)
