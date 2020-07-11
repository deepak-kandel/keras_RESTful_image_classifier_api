import io
import flask 
import numpy as np
from PIL import Image


from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications import imagenet_utils

app = flask.Flask(__name__)


def load_model():
    global model
    model = ResNet50(weights="imagenet")


def prepare_image(image, target):
    if image.mode != "RGB":
        image = image.convert("RGB")

    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    return image


@app.route("/predict", methods=["POST"])
def predict():

    data = {"success": False}

    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image))
            image = prepare_image(image, target=(224, 224))
            preds = model.predict(image)
            results = imagenet_utils.decode_predictions(preds)
            data["predictions"] = []

            for (imagenetID, label, prob) in results[0]:
                r = {"label": label, "probability": float(prob)}
                data["predictions"].append(r)
            data["success"] = True

    return flask.jsonify(data)


if __name__ == "__main__":
    print(
        """Loading Keras model and Flask starting server..
             Please wait until the server starts"""
    )

    load_model()
    app.run()
