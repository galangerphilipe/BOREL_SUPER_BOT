from PIL import Image, ImageDraw, ImageFont
import os

class ImageProcessor:
    def __init__(self):
        self.default_font_path = self._get_default_font()
        
    def _get_default_font(self):
        """Obtenir le chemin de la police par défaut"""
        # Essayer différentes polices selon l'OS
        font_paths = [
            # "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            # "/System/Library/Fonts/Arial.ttf",  # macOS
            # "C:/Windows/Fonts/arial.ttf",  # Windows
            # "fonts/arial.ttf"
            "media/DejaVuSans-Bold.ttf"
            
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        
        return None
        
    def add_text_to_image(self, base_image_path, text, position, output_path, 
                         font_size=30, color="white", font_path="media/DejaVuSans-Bold.ttf"):
        """Ajouter du texte sur une image"""
        try:
            # Ouvrir l'image de base
            image = Image.open(base_image_path)
            draw = ImageDraw.Draw(image)
            print(f"Using font path: {font_path}")
            # Charger la police
            font = None
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            elif self.default_font_path:
                font = ImageFont.truetype(self.default_font_path, font_size)
            else:
                font = ImageFont.load_default()
            
            # Ajouter le texte
            draw.text(position, text, fill=color, font=font)
            
            # Créer le dossier de sortie si nécessaire
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Sauvegarder l'image
            image.save(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Erreur lors de l'ajout de texte à l'image: {e}")
            return base_image_path
            
    def add_element_to_image(self, base_image_path, element_image_path, position, output_path):
        """Ajouter un élément (image) sur une image de base"""
        try:
            # Ouvrir les images
            base_image = Image.open(base_image_path)
            element_image = Image.open(element_image_path)
            
            # Coller l'élément sur l'image de base
            base_image.paste(element_image, position, element_image if element_image.mode == 'RGBA' else None)
            
            # Créer le dossier de sortie si nécessaire
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Sauvegarder l'image
            base_image.save(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Erreur lors de l'ajout d'élément à l'image: {e}")
            return base_image_path
            
    def select_random_image(self, images_folder):
        """Sélectionner une image aléatoire dans un dossier"""
        import random
        
        if not os.path.exists(images_folder):
            return None
            
        images = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not images:
            return None
            
        return os.path.join(images_folder, random.choice(images))