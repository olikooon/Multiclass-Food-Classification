# Project Description.

The project is dedicated to the development of a computer vision model capable of automatically classifying food images into 101 categories. The final product is a Telegram bot. A user uploads a photo of a dish, and the system returns its name along with additional information, including characteristics and recommendations.

Several methods were used throughout the project:

A simple CNN model (accuracy - 44%)

A CNN model based on the EfficientNet architecture (accuracy - 58%)

Vision Transformers (accuracy - 75%)

Improved Vision Transformers (accuracy - 87%)

However, the truly significant results with Transformers were achieved thanks to:

Advanced augmentation, which creates complex training data.

A partially unfrozen ViT for efficient data training
