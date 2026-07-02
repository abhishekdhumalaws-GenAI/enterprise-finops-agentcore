class ExecutionContext:
    def __init__(self):
        self.data = {
            "discovered": {},
            "facts": [],
            "warnings": []
        }

    def set(self, key: str, value):
        self.data["discovered"][key] = value

    def get(self, key: str, default=None):
        return self.data["discovered"].get(key, default)

    def add_fact(self, fact: str):
        if fact:
            self.data["facts"].append(fact)

    def add_warning(self, warning: str):
        if warning:
            self.data["warnings"].append(warning)

    def to_dict(self):
        return self.data
