from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os

app = FastAPI()

# Define the data file path
DATA_FILE = "data.json"

# Pydantic model for an item
class Item(BaseModel):
    id: Optional[str] = None  # ID is optional for item creation
    name: str
    description: Optional[str] = None
    price: float
    quantity: int

# Pydantic model for patching an item
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

# Helper function to read data from the JSON file
def read_data() -> List[Item]:
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return [Item(**item) for item in json.load(file)]
        else:
            return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading data.json: {e}")
        return []

# Helper function to write data to the JSON file
def write_data(data: List[Item]):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump([item.dict() for item in data], file, indent=2)
    except IOError as e:
        print(f"Error writing to data.json: {e}")

# CRUD Endpoints

# GET /items - Retrieve all items
@app.get("/items", response_model=List[Item])
def get_items():
    return read_data()

# GET /items/{id} - Retrieve a single item by ID
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: str):
    data = read_data()
    item = next((item for item in data if item.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# POST /items - Create a new item
@app.post("/items", response_model=Item)
def create_item(item: Item):
    data = read_data()
    item.id = str(max([int(existing_item.id) for existing_item in data], default=0) + 1)
    data.append(item)
    write_data(data)
    return item

# PUT /items/{id} - Update an existing item
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: str, item: Item):
    data = read_data()
    for idx, existing_item in enumerate(data):
        if existing_item.id == item_id:
            data[idx] = item
            data[idx].id = item_id  # Ensure ID remains unchanged
            write_data(data)
            return data[idx]
    raise HTTPException(status_code=404, detail="Item not found")

# PATCH /items/{id} - Partially update an existing item
@app.patch("/items/{item_id}", response_model=Item)
def patch_item(item_id: str, item_update: ItemUpdate):
    data = read_data()
    for idx, existing_item in enumerate(data):
        if existing_item.id == item_id:
            updated_item_data = item_update.dict(exclude_unset=True)
            updated_item = existing_item.copy(update=updated_item_data)
            data[idx] = updated_item
            write_data(data)
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

# DELETE /items/{id} - Delete an item
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: str):
    data = read_data()
    new_data = [item for item in data if item.id != item_id]
    if len(new_data) == len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    write_data(new_data)
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
