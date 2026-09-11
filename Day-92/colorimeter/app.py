import base64
import io

from flask import Flask, render_template, request
from PIL import Image, UnidentifiedImageError

from colors import extract_top_colors

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB upload limit

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    context = {}

    if request.method == "POST":
        file = request.files.get("image")

        if file is None or file.filename == "":
            context["error"] = "Please choose an image first."
        elif not allowed_file(file.filename):
            context["error"] = "That file type isn't supported. Try PNG, JPG, GIF, BMP, or WebP."
        else:
            raw_bytes = file.read()
            try:
                image = Image.open(io.BytesIO(raw_bytes))
                image.load()  # force-read the pixel data now, so a truncated file fails here
            except (UnidentifiedImageError, OSError):
                context["error"] = "Couldn't read that as an image. Please try a different file."
            else:
                colors = extract_top_colors(image, top_n=10)
                mime = Image.MIME.get(image.format, "image/png")
                preview_b64 = base64.b64encode(raw_bytes).decode("ascii")

                context["colors"] = colors
                context["preview_src"] = f"data:{mime};base64,{preview_b64}"
                context["filename"] = file.filename

    return render_template("index.html", **context)


@app.errorhandler(413)
def file_too_large(_e):
    return render_template(
        "index.html", error="That image is too large (max 8MB). Try a smaller file."
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
