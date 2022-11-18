import json

import jsonpickle


def debug(thing):
    dumpee = json.dumps(json.loads(jsonpickle.encode(thing)), indent=2)
    return f"<script>console.log({dumpee});</script>"
