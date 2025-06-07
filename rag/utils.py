import hashlib
import json
from pathlib import Path

CASHE_PATH = "indexed_hashes.json"

class Cashe_indexed():
    def __init__(self):
        self.hashes = self._load_hash_cashe()

    def compute_hash(self, text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    def is_new(self, hash):
        return hash not in self.hashes

    def add(self, hash):
        self.hashes.add(hash)
    
    def _load_hash_cashe(self):
        if not Path(CASHE_PATH).exists():
            return set()
        with open(CASHE_PATH, "r") as file:
            return set(json.load(file))
    
    def save(self, hashes: set):
        with open(CASHE_PATH, "w") as file:
            json.dump(list(hashes), file, indent=2)