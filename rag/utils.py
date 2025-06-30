import hashlib
import json
from pathlib import Path

CACHE_PATH = "indexed_hashes.json"

class CacheIndexed():
    def __init__(self):
        self.hashes: set[str] = self._load_hash_cache()

    def compute_hash(self, text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    def is_new(self, hash):
        return hash not in self.hashes

    def add(self, hash):
        self.hashes.add(hash)
        self.save(self.hashes)
    
    def _load_hash_cache(self):
        if not Path(CACHE_PATH).exists():
            return set()
        with open(CACHE_PATH, "r") as file:
            return set(json.load(file))
    
    def save(self, hashes: set):
        with open(CACHE_PATH, "w") as file:
            json.dump(list(hashes), file, indent=2)