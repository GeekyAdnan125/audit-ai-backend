
import yaml

class RuleEngine:

    def __init__(self, path):

        with open(path) as f:
            self.rules = yaml.safe_load(f)

    def get(self, rule):
        return self.rules.get(rule)
