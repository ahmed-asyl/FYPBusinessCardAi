from transformers import LayoutLMv2ForTokenClassification, Trainer, TrainingArguments, LayoutLMv2Processor
from datasets import Dataset
import wandb


def prepare_dataset(data, processor):
    # Convert the preprocessed data into a Dataset object and process it
    def preprocess(examples):
        encoding = processor(
            images=examples['image'],
            text=examples['words'],
            boxes=examples['bboxes'],
            word_labels=examples['labels'],
            padding="max_length",
            truncation=True
        )
        return encoding

    dataset = Dataset.from_dict({
        'image': [item['image'] for item in data],
        'words': [item['words'] for item in data],
        'bboxes': [item['bboxes'] for item in data],
        'labels': [item['labels'] for item in data]
    })

    # Apply preprocessing
    dataset = dataset.map(preprocess, batched=True, remove_columns=dataset.column_names)

    return dataset


def train_model(train_data, eval_data, num_labels):
    wandb.init(project="card-ocr")

    # Load the processor and model
    processor = LayoutLMv2Processor.from_pretrained("microsoft/layoutlmv2-base-uncased")
    model = LayoutLMv2ForTokenClassification.from_pretrained("microsoft/layoutlmv2-base-uncased", num_labels=num_labels)

    # Prepare the datasets
    train_dataset = prepare_dataset(train_data, processor)
    eval_dataset = prepare_dataset(eval_data, processor)

    # Define the training arguments
    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="steps",
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        num_train_epochs=3,
        logging_dir='./logs',
        logging_steps=10,
        report_to="wandb"
    )

    # Initialize the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=processor.tokenizer,
    )

    # Train the model
    trainer.train()


if __name__ == "__main__":
    from backend.scripts.preprocess import preprocess_data

    # Set your image and label directories
    image_dir = "labelled data"
    json_dir = "labelled data"

    # Preprocess the data
    processed_data = preprocess_data(image_dir, json_dir)

    # Split data into train and eval datasets (80-20 split)
    split_index = int(0.8 * len(processed_data))
    train_data = processed_data[:split_index]
    eval_data = processed_data[split_index:]

    # Get the number of labels (for simplicity, assume it's 10 here, adjust as needed)
    num_labels = 10

    # Train the model
    train_model(train_data, eval_data, num_labels)
