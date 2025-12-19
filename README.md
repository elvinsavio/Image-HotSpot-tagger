# Image Hotspot Tagger

A desktop-focused web application for creating and managing hotspot tags on images. Users can draw bounding boxes, add descriptions, and organize metadata using a clean, dark-themed interface.

## Features

- **Gallery View**: Browse all images in a specified directory in a responsive grid layout.
- **Hotspot Editor**: Interactive editor with a 70/30 split view (Image / Sidebar).
- **Tagging**: Draw bounding boxes directly on images to create tags.
- **Management**:
  - Edit descriptions via the sidebar.
  - Delete tags.
  - Reposition and resize bounding boxes using drag handles.
  - Bounding boxes are constrained to the image area.
- **Persistence**: Save tags to a `data.json` file in the image directory. Data persists across sessions.
- **Visuals**: Modern dark theme with high-contrast accents.

## Installation

### Prerequisites

- Python 3.12 or higher.

### Setup

1. Clone or navigate to the project repository.
2. Install dependencies. You can use `pip`:

   ```bash
   pip install flask click
   ```

   Or if using `uv` (recommended):

   ```bash
   uv sync
   ```

## Usage

### Running the Application

To start the application, run `main.py` and provide the path to your image directory as an argument.

```bash
python main.py /path/to/your/images/
```

Example:

```bash
python main.py sample/
```

### Workflow

1. **Open the Gallery**: navigate to `http://localhost:5000` in your web browser.
2. **Select an Image**: Click on any image thumbnail to enter the editor.
3. **Add Tags**:
   - Click and drag on the image to draw a green bounding box.
   - A new tag entry will appear in the right sidebar.
4. **Edit Tags**:
   - Type in the input field in the sidebar to update the tag description.
   - Click on a box or sidebar item to select it (highlighted in white).
   - Drag the box to move it.
   - Drag the white corner handles to resize it.
5. **Delete Tags**: Click the "x" button on the sidebar item.
6. **Save Work**: Click the "Save" button in the top-right of the sidebar.
   - Tag data is saved to `data.json` inside your image folder.

## Data Format

Tags are stored in `data.json` with the following structure:

```json
{
  "image_filename.jpg": [
    {
      "id": "tag_timestamp_random",
      "x": 100,
      "y": 200,
      "w": 50,
      "h": 50,
      "description": "Tag Description"
    }
  ]
}
```
