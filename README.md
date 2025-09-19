# tomydatabase.weebly.com-to-JSON

A Python script to scrape Tomy Pokémon toy data from [tomydatabase.weebly.com](https://tomydatabase.weebly.com/) and convert it into a structured JSON file, with images downloaded locally.

## What does this project do?

- Scrapes toy names and image URLs from each Pokémon generation page on tomydatabase.weebly.com.
- Downloads toy images to a local `images/` directory.
- Outputs a JSON file (`tomydatabase.weebly.com.json`) containing details for each toy:
  - `id`: Stable hash identifier
  - `name`: Toy name
  - `generation`: Pokémon generation
  - `image_url`: Original image URL
  - `image_path`: Local image path

## How to use

### 1. Install dependencies

```sh
pip install -r requirements.txt
```

### 2. Run the scraper

```sh
python scrape_website.py
```

- Images will be saved in the `images/` folder.
- The JSON file will be created as `tomydatabase.weebly.com.json`.

### 3. Output format

Each entry in the JSON file looks like:

```json
{
  "id": "abcdef1234567890",
  "name": "Bulbasaur",
  "generation": "Kanto",
  "image_url": "https://tomydatabase.weebly.com/uploads/...",
  "image_path": "images/bulbasaur-abcdef1234567890.jpg"
}
```

## Credits

- Data and images sourced from [tomydatabase.weebly.com](https://tomydatabase.weebly.com/).
- This project is not affiliated with or endorsed by tomydatabase.weebly.com.

## License

See `LICENSE` for details.