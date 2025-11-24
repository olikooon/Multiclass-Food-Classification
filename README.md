# Multiclass Food Classification, project description.

The project is dedicated to the development of a computer vision model capable of automatically classifying food images into 101 categories. The final product is a Telegram bot. A user uploads a photo of a dish, and the system returns its name along with additional information, including characteristics and recommendations.

Several methods were used throughout the project:

- A simple CNN model (accuracy - 44%)

-  CNN model based on the EfficientNet architecture (accuracy - 58%)

- Vision Transformers (accuracy - 75%)

- Improved Vision Transformers (accuracy - 87%)

However, the truly significant results with Transformers were achieved thanks to:

- Advanced augmentation, which creates complex training data.

- A partially unfrozen ViT for efficient data training

# Setup Instructions

## 1. Prerequisites

- Python 3.12+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Api key from [USDA](https://fdc.nal.usda.gov/api-key-signup.html)

## 2. Installation

1. Clone the project with **GIT LFS**

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

## 3. Configuration

Create .env file in the project root like **.env.example**
6. **Run**

```bash
python main.py
```