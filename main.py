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

    @app.route("/api/apply_blurs", methods=["POST"])
    def apply_blurs():
        from flask import request, jsonify
        from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
        import shutil

        req_data = request.json
        image_name = req_data.get("image_name")
        blurs = req_data.get("blurs")  # List of {points: [{x,y}...], text: str}

        if not image_name or not blurs:
            return jsonify({"error": "Missing data"}), 400

        image_path = app.config["FOLDER_PATH"] / image_name

        # 1. Backup if not exists
        backup_path = image_path.with_suffix(image_path.suffix + ".bak")
        if not backup_path.exists():
            shutil.copy2(image_path, backup_path)

        try:
            with Image.open(image_path) as img:
                img = img.convert("RGBA")  # Ensure alpha channel
                width, height = img.size

                # Base for drawing
                draw = ImageDraw.Draw(img)

                for b in blurs:
                    points_pct = b.get("points", [])
                    if len(points_pct) != 4:
                        continue

                    # Convert % to px
                    poly_points = [
                        (p["x"] * width / 100, p["y"] * height / 100)
                        for p in points_pct
                    ]

                    # Create mask for this polygon
                    mask = Image.new("L", (width, height), 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.polygon(poly_points, fill=255)

                    # Create blurred version of the WHOLE image (strong blur)
                    blurred = img.filter(ImageFilter.GaussianBlur(15))

                    # Composite: Paste blurred onto img using mask
                    img.paste(blurred, mask=mask)

                    # Watermark
                    text = b.get("text", "")
                    if text:
                        # Find center of polygon
                        center_x = sum(p[0] for p in poly_points) / 4
                        center_y = sum(p[1] for p in poly_points) / 4

                        # Font size relative to poly height (approx)
                        # Quick approx height
                        poly_h = max(p[1] for p in poly_points) - min(
                            p[1] for p in poly_points
                        )
                        font_size = max(12, int(poly_h * 0.4))

                        try:
                            font = ImageFont.truetype("arial.ttf", font_size)
                        except:
                            font = ImageFont.load_default(size=font_size)

                        # Draw Text with outline for visibility
                        # text_bbox = draw.textbbox((0, 0), text, font=font)
                        # text_w = text_bbox[2] - text_bbox[0]
                        # text_h = text_bbox[3] - text_bbox[1]

                        draw.text(
                            (center_x, center_y),
                            text,
                            font=font,
                            anchor="mm",
                            fill="white",
                            stroke_width=2,
                            stroke_fill="black",
                        )

                # Save back (convert to RGB if original was jpg/etc to avoid alpha issues if format doesn't support it)
                if image_path.suffix.lower() in [".jpg", ".jpeg"]:
                    img = img.convert("RGB")

                img.save(image_path, quality=95)

        except Exception as e:
            print(f"Error blurring: {e}")
            return jsonify({"error": str(e)}), 500

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
