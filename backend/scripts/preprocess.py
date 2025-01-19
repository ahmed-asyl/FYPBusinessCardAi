from transformers import LayoutLMv2Processor
from PIL import Image
import json
import os


def preprocess_data(image_dir, json_dir):
    data = []

    # Loop through the JSON files in the directory
    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json"):
            # Load the JSON data
            with open(os.path.join(json_dir, json_file), 'r') as f:
                json_data = json.load(f)

            # Load the corresponding image
            image_path = os.path.join(image_dir, json_data['document'])
            image = Image.open(image_path)

            words, bboxes, labels = [], [], []

            for item in json_data['labels']:
                label = item['label']
                for value in item['value']:
                    words.append(value['text'])
                    bboxes.append(value['boundingBoxes'][0])
                    labels.append(label)

            # Normalize bounding boxes based on image dimensions
            width, height = image.size
            normalized_bboxes = [
                [
                    int(box[0] * width),
                    int(box[1] * height),
                    int(box[2] * width),
                    int(box[3] * height)
                ]
                for box in bboxes
            ]

            data.append({
                'image': image,
                'words': words,
                'bboxes': normalized_bboxes,
                'labels': labels
            })

    return data


if __name__ == "__main__":
    # Set your image and label directories
    image_dir = "labelled data"
    json_dir = "labelled data"

    # Preprocess the data
    processed_data = preprocess_data(image_dir, json_dir)

    # Example: print the first item
    print(processed_data[0])
