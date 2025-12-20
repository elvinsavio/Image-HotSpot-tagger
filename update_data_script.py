import json
from pathlib import Path

DATA_FILE = Path("sample/data.json")


def update_data():
    if not DATA_FILE.exists():
        print(f"Error: {DATA_FILE} not found.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    updated = False
    for filename, tags in data.items():
        for tag in tags:
            if "fileName" not in tag:
                tag["fileName"] = filename
                updated = True

    if updated:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully updated {DATA_FILE} with filenames.")
    else:
        print("No updates needed.")


if __name__ == "__main__":
    update_data()
