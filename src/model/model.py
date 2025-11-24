import logging
import os
from typing import List

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

logger = logging.getLogger(__name__)


# Model like in ViT_improved
class FoodClassificationService:
    def __init__(self, model_path: str, classes_path: str):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.classes = self._load_classes(classes_path)
        self.model = self._load_model(model_path)
        self.transform = self._get_transform()

        logger.info(f"Model loaded on device: {self.device}")

    def _load_classes(self, classes_path: str) -> List[str]:
        with open(classes_path, 'r', encoding='utf-8') as f:
            classes = [line.strip() for line in f.readlines()]
        logger.info(f"Loaded {len(classes)} classes")
        return classes

    def _load_model(self, model_path: str) -> nn.Module:
        model = models.vit_b_16(weights=None)
        num_classes = len(self.classes)
        in_features = model.heads.head.in_features

        model.heads.head = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, num_classes)
        )

        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=self.device)
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                model.load_state_dict(checkpoint)
        else:
            logger.warning(f"Model file {model_path} not found. Using untrained model.")

        model.to(self.device)
        model.eval()
        return model

    def _get_transform(self):
        mean = [0.485, 0.456, 0.406]
        std = [0.229, 0.224, 0.225]

        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ])

    async def predict_pil(self, img: Image.Image):
        try:
            img = img.convert('RGB')
            x = self.transform(img).unsqueeze(0)

            with torch.no_grad():
                out = self.model(x)
                probs = torch.nn.functional.softmax(out, dim=1)[0]
                topk = torch.topk(probs, k=3)
                results = []
                for i, idx in enumerate(topk.indices.tolist()):
                    res = {'class': self.classes[idx], 'confidence': float(topk.values[i].item() * 100), 'rank': i + 1}
                    results.append(res)
                if results[0]['confidence'] < 50:
                    return None
                return results
        except Exception as e:
            logger.error(f"Predict error: {e}")
            return None
