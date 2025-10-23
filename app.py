from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import hashlib
from datetime import datetime
from collections import Counter
from typing import List, Dict, Optional
import re

app = FastAPI()

# In-memory storage: key = sha256_hash, value = {"value": str, "properties": dict, "created_at": str}
strings_db: Dict[str, Dict] = {}

class StringInput(BaseModel):
    value: str

def compute_properties(value: str) -> Dict[str, any]:
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
    length = len(value)
    lower_value = value.lower()
    is_palindrome = lower_value == lower_value[::-1]
    unique_characters = len(set(value))
    word_count = len(value.split())
    sha256_hash = hashlib.sha256(value.encode()).hexdigest()
    char_freq = dict(Counter(value))
    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": char_freq
    }

@app.post("/strings", status_code=201)
def create_string(input: StringInput):
    value = input.value
    try:
        properties = compute_properties(value)
    except ValueError:
        raise HTTPException(422, "Invalid data type for 'value' (must be string)")
    id = properties["sha256_hash"]
    if id in strings_db:
        raise HTTPException(409, "String already exists in the system")
    created_at = datetime.utcnow().isoformat() + "Z"
    strings_db[id] = {
        "value": value,
        "properties": properties,
        "created_at": created_at
    }
    return {
        "id": id,
        "value": value,
        "properties": properties,
        "created_at": created_at
    }

@app.get("/strings/{string_value}")
def get_string(string_value: str):
    id = hashlib.sha256(string_value.encode()).hexdigest()
    if id not in strings_db or strings_db[id]["value"] != string_value:
        raise HTTPException(404, "String does not exist in the system")
    stored = strings_db[id]
    return {
        "id": id,
        "value": stored["value"],
        "properties": stored["properties"],
        "created_at": stored["created_at"]
    }

@app.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str):
    id = hashlib.sha256(string_value.encode()).hexdigest()
    if id in strings_db and strings_db[id]["value"] == string_value:
        del strings_db[id]
    else:
        raise HTTPException(404, "String does not exist in the system")

def filter_strings(filters: Dict) -> List[Dict]:
    filtered = []
    for id, item in strings_db.items():
        props = item["properties"]
        if "is_palindrome" in filters and props["is_palindrome"] != filters["is_palindrome"]:
            continue
        if "min_length" in filters and props["length"] < filters["min_length"]:
            continue
        if "max_length" in filters and props["length"] > filters["max_length"]:
            continue
        if "word_count" in filters and props["word_count"] != filters["word_count"]:
            continue
        if "contains_character" in filters:
            char = filters["contains_character"]
            if len(char) != 1:
                raise HTTPException(400, "Invalid query parameter values or types")
            if char not in item["value"]:
                continue
        filtered.append({
            "id": id,
            "value": item["value"],
            "properties": item["properties"],
            "created_at": item["created_at"]
        })
    return filtered

@app.get("/strings")
def get_all_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None),
    max_length: Optional[int] = Query(None),
    word_count: Optional[int] = Query(None),
    contains_character: Optional[str] = Query(None)
):
    filters = {
        "is_palindrome": is_palindrome,
        "min_length": min_length,
        "max_length": max_length,
        "word_count": word_count,
        "contains_character": contains_character
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    data = filter_strings(filters)
    return {
        "data": data,
        "count": len(data),
        "filters_applied": filters
    }

def parse_natural_query(query: str) -> Dict:
    query_lower = query.lower()
    filters = {}
    # Detect palindrome
    if "palindromic" in query_lower or "palindrome" in query_lower:
        filters["is_palindrome"] = True
    # Detect single word
    if "single word" in query_lower:
        filters["word_count"] = 1
    # Detect longer than
    longer_than_match = re.search(r"longer than (\d+)", query_lower)
    if longer_than_match:
        filters["min_length"] = int(longer_than_match.group(1)) + 1
    # Detect contains character
    contains_match = re.search(r"contain(ing|s| the letter) (the letter )?(\w)", query_lower)
    if contains_match:
        char = contains_match.group(3)
        if len(char) == 1:
            filters["contains_character"] = char
    # Special heuristic for "first vowel"
    if "first vowel" in query_lower:
        filters["contains_character"] = "a"
    if not filters:
        raise HTTPException(400, "Unable to parse natural language query")
    # Basic conflict check (e.g., min > max)
    if "min_length" in filters and "max_length" in filters and filters["min_length"] > filters["max_length"]:
        raise HTTPException(422, "Query parsed but resulted in conflicting filters")
    return filters

@app.get("/strings/filter-by-natural-language")
def natural_filter(query: str = Query(...)):
    parsed_filters = parse_natural_query(query)
    data = filter_strings(parsed_filters)
    return {
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    }