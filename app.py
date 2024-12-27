from fastapi import FastAPI, HTTPException, Request
import threading
import json
import uuid
import os
from scraper.main import run_scraper
from processor.main import RedisSubscriber

app = FastAPI()

# Directory to save the scraped data files
SCRAPED_DATA_DIR = "scraped_data"
os.makedirs(SCRAPED_DATA_DIR, exist_ok=True)

# Start the Redis subscriber in a background thread
def start_redis_subscriber():
    subscriber = RedisSubscriber()
    subscriber.subscribe_to_channel("product_updates")

# FastAPI route to trigger scraping
@app.get("/scrape")
def scrape(request: Request, limit: int = 1):
    """
    Trigger the scraper, run it, and store the results with a unique ID.
    """
    try:
        # Generate a unique ID for this scrape operation
        unique_id = str(uuid.uuid4())

        # Run the scraper
        run_scraper(limit=limit)

        # Load results from the file
        with open(f"{unique_id}.json", "r") as file:
            data = json.load(file)

        # Save the scraped data to a file with the unique ID
        scraped_data_path = os.path.join(SCRAPED_DATA_DIR, f"{unique_id}.json")
        with open(scraped_data_path, "w") as json_file:
            json.dump(data, json_file)

        # Construct the full URL to access the scraped data
        base_url = request.base_url._url  # Get the base URL of the request
        data_url = f"{base_url}scraped/{unique_id}"

        return {"status": "completed", "scraped_products": len(data), "data_url": data_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI route to retrieve the scraped data by unique ID
@app.get("/scraped/{unique_id}")
def get_scraped_data(unique_id: str):
    """
    Retrieve the scraped data by its unique ID.
    """
    scraped_data_path = os.path.join(SCRAPED_DATA_DIR, f"{unique_id}.json")
    if not os.path.exists(scraped_data_path):
        raise HTTPException(status_code=404, detail="Data not found for the provided ID.")
    
    with open(scraped_data_path, "r") as json_file:
        data = json.load(json_file)

    return {"status": "found", "data": data}

# Root route
@app.get("/")
def read_root():
    return {"message": "FastAPI is running, Redis Subscriber is listening in the background!"}

# FastAPI lifespan context manager for startup and shutdown events
@app.on_event("startup")
async def on_startup():
    # Start the Redis listener in a separate thread
    threading.Thread(target=start_redis_subscriber, daemon=True).start()