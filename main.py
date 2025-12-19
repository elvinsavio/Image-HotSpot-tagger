# app.py
import os
import click
from flask import Flask, render_template, send_from_directory
from pathlib import Path
from typing import List, Dict, Any
import json

DATA_FILE = "data.json"

IMAGE_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def create_app(folder_path: Path) -> Flask:
    app = Flask(__name__)
    app.config["FOLDER_PATH"] = folder_path

    def get_data_file_path() -> Path:
        return app.config["FOLDER_PATH"] / DATA_FILE

    def load_data() -> Dict[str, Any]:
        path = get_data_file_path()
        if not path.exists():
            return {}
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_data(data: Dict[str, Any]):
        path = get_data_file_path()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @app.route("/images/<path:filename>")
    def images(filename):
        base_path: Path = app.config["FOLDER_PATH"]
        base_path = os.path.abspath(base_path)
        return send_from_directory(base_path, filename)

    @app.route("/")
    def index() -> str:
        base_path: Path = app.config["FOLDER_PATH"]

        images: List[Path] = [
            p.name
            for p in base_path.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        ]
        # Example: return filenames as text
        data = load_data()
        return render_template("all.html", images=images, data=data)

    @app.route("/image/<string:image_name>")
    def tag_image(image_name: str):
        data = load_data()
        tags = data.get(image_name, [])
        return render_template("image.html", image_name=image_name, tags=tags)

    @app.route("/api/save_tags", methods=["POST"])
    def save_tags_route():
        from flask import request, jsonify

        req_data = request.json
        image_name = req_data.get("image_name")
        tags = req_data.get("tags")

        if not image_name:
            return jsonify({"error": "Missing image_name"}), 400

        data = load_data()
        data[image_name] = tags
        save_data(data)

        return jsonify({"status": "success"})

    return app


@click.command()
@click.argument("path", required=True)
def run(path):
    folder_path = Path(path)

    if not folder_path.is_dir():
        raise ValueError(f"{path} is not a directory")

    app = create_app(folder_path)
    app.run(debug=True)


if __name__ == "__main__":
    run()
