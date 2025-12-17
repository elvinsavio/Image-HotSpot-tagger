# app.py
import os
import click
from flask import Flask, render_template, send_from_directory
from pathlib import Path
from typing import List

IMAGE_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

def create_app(folder_path:  Path) -> Flask:
    app = Flask(__name__)
    app.config["FOLDER_PATH"] = folder_path

    @app.route("/images/<path:filename>")
    def images(filename):
        base_path: Path = app.config["FOLDER_PATH"]
        base_path  = os.path.abspath(base_path)
        return send_from_directory(base_path, filename)

    @app.route("/")
    def index() -> str:
        base_path: Path = app.config["FOLDER_PATH"]

        images: List[Path] = [
            p.name
            for p in base_path.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        ]
        print(images)
        # Example: return filenames as text
        return render_template("all.html", images=images)

    @app.route("/<string:image_name>")
    def tag_image(image_name: str):
        return "ok"

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
