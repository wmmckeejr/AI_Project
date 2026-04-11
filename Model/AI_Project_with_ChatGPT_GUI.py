import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import io
import requests
import json
from ultralytics import YOLO

class TkinterApp:
    def __init__(self, master):
        self.master = master
        master.title("Food Recipe Finder")

        # Initialize model and API URLs.
        self.model_path = './ingredientsRun/weights/best.onnx'
        self.yolo_model = YOLO(self.model_path, task = 'detect')
        self.ingredient_url = 'https://www.themealdb.com/api/json/v2/65232507/filter.php?i='
        self.recipe_url = 'https://www.themealdb.com/api/json/v1/1/lookup.php?i='
        
        # OpenAI API Key (replace with your actual key).
        self.OPENAI_API_KEY = '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'
        self.OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

        self.detected_ingredients = set()
        self.comma_separated_ingredients = ""

        # --- UI Elements ---

        # Upload Image Section.
        self.upload_frame = ttk.LabelFrame(master, text = "1. Upload Image")
        self.upload_frame.pack(padx = 10, pady = 10, fill = "x")

        self.upload_button = ttk.Button(self.upload_frame, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady = 5)

        self.image_label = ttk.Label(self.upload_frame)
        self.image_label.pack(pady = 5)

        # Detected Ingredients Section.
        self.ingredients_frame = ttk.LabelFrame(master, text = "2. Detected Ingredients (You May add more after detection.)")
        self.ingredients_frame.pack(padx = 10, pady = 10, fill = "x")

        self.ingredients_text_box = tk.Text(self.ingredients_frame, height = 5, width = 50)
        self.ingredients_text_box.pack(pady=5, padx = 5, fill = "x", expand = True)
        self.ingredients_text_box.insert(tk.END, "Detected ingredients will appear here...")
        self.ingredients_text_box.config(state=tk.DISABLED) # Make it read-only initially.

        # Recipe and ChatGPT Actions.
        self.actions_frame = ttk.LabelFrame(master, text = "3. Actions")
        self.actions_frame.pack(padx = 10, pady = 10, fill = "x")

        self.find_recipe_button = ttk.Button(self.actions_frame, text = "Find Recipes (TheMealDB)", command=self.find_recipes)
        self.find_recipe_button.pack(side = tk.LEFT, padx = 5, pady = 5)
        self.find_recipe_button.pack_forget()

        self.chatgpt_button = ttk.Button(self.actions_frame, text = "Ask ChatGPT for Ideas", command = self.ask_chatgpt)
        self.chatgpt_button.pack(side = tk.LEFT, padx = 5, pady = 5)

        # Results Display.
        self.results_frame = ttk.LabelFrame(master, text = "4. Results")
        self.results_frame.pack(padx = 10, pady = 10, fill = "both", expand=True)

        self.results_text = tk.Text(self.results_frame, wrap = tk.WORD, height = 15)
        self.results_text.pack(pady=5, padx = 5, fill = "both", expand=True)
        self.results_text.insert(tk.END, "Recipe and ChatGPT results will appear here.")
        self.results_text.config(state=tk.DISABLED) # Make it read-only

    def update_text_box(self, text_widget, content, append = False):
        text_widget.config(state = tk.NORMAL)
        if not append:
            text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, content)
        #text_widget.config(state = tk.DISABLED)
        text_widget.see(tk.END) # Scroll to end.

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff")]
        )
        if file_path:
            self.update_text_box(self.results_text, "Processing image...\n")
            try:
                img = Image.open(file_path)
                self.display_image(img, self.image_label) # Display original image first.
                self.detect_objects(img)
            except Exception as e:
                self.update_text_box(self.results_text, f"Error loading or processing image: {e}\n", append=True)

    def display_image(self, img_pil, label_widget, max_size = (320, 320)):
        img_pil.thumbnail(max_size, Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)
        label_widget.config(image=img_tk)
        label_widget.image = img_tk # Keep a reference!

    def detect_objects(self, img_pil):
        self.detected_ingredients.clear()
        self.update_text_box(self.ingredients_text_box, "")
        self.update_text_box(self.results_text, "Detecting objects...\n", append=True)

        try:
            results = self.yolo_model.predict(source = img_pil, imgsz = 640, conf = 0.25, verbose = False)
            
            detected_unique_items = set()
            for r in results:
                boxes = r.boxes
                names = r.names
                if len(boxes) > 0:
                    for box in boxes:
                        cls = int(box.cls[0])
                        detected_unique_items.add(names[cls])

            if detected_unique_items:
                self.detected_ingredients = detected_unique_items
                ingredients_str = '\n'.join(sorted(list(detected_unique_items)))
                self.update_text_box(self.ingredients_text_box, ingredients_str)
                self.update_text_box(self.results_text, f"Detected: {', '.join(sorted(list(detected_unique_items)))}\n", append=True)
            else:
                self.update_text_box(self.ingredients_text_box, "No objects detected.")
                self.update_text_box(self.results_text, "No objects detected.\n", append=True)

            # Display annotated image.
            annotated_img_array = results[0].plot() # Assuming only one image processed
            pil_annotated_img = Image.fromarray(annotated_img_array[:, :, ::-1]) # BGR to RGB
            self.display_image(pil_annotated_img, self.image_label)

        except Exception as e:
            self.update_text_box(self.results_text, f"Error during object detection: {e}\n", append=True)

    def find_recipes(self):
        self.update_text_box(self.results_text, "Searching for recipes...\n")
        if not self.detected_ingredients:
            self.update_text_box(self.results_text, "No ingredients detected. Please upload an image first.\n", append=True)
            return

        #self.comma_separated_ingredients = ', '.join(sorted(list(self.detected_ingredients)))
        self.comma_separated_ingredients = self.ingredients_text_box.get('1.0', tk.END).replace('\n', ', ')
        full_ingredient_url = self.ingredient_url + self.comma_separated_ingredients[:-2]
        #full_ingredient_url = self.ingredient_url + self.comma_separated_ingredients
        self.update_text_box(self.results_text, f"Searching for recipes with: {self.comma_separated_ingredients}\n\n")
        self.update_text_box(self.results_text, f"Asking for recipes at: {full_ingredient_url}\n\n")

        try:
            response = requests.get(full_ingredient_url)
            response.raise_for_status()
            data = response.json()

            if data and 'meals' in data and data['meals']:
                self.update_text_box(self.results_text, "Recipes found from TheMealDB:\n", append = True)
                for meal in data['meals']:
                    self.update_text_box(self.results_text, f"  - {meal['strMeal']} (ID: {meal['idMeal']})\n", append = True)
                    full_recipe_url = self.recipe_url + meal['idMeal']
                    recipe_response = requests.get(full_recipe_url)
                    if recipe_response.status_code == 200:
                        instructions_data = recipe_response.json()
                        if instructions_data and 'meals' in instructions_data and instructions_data['meals']:
                            recipe_details = instructions_data['meals'][0]
                            self.update_text_box(self.results_text, "    Ingredients:\n", append=True)
                            for i in range(1, 21):
                                ingredient = recipe_details.get(f'strIngredient{i}')
                                measure = recipe_details.get(f'strMeasure{i}')
                                if ingredient and ingredient.strip():
                                    self.update_text_box(self.results_text, f"      - {ingredient.strip()} - {measure.strip()}\n", append=True)
                                else:
                                    break
                            self.update_text_box(self.results_text, f"    Instructions: {recipe_details['strInstructions']}\n\n", append=True)
                        else:
                            self.update_text_box(self.results_text, "    Instructions and Ingredients not found for this recipe.\n\n", append=True)
                    else:
                        self.update_text_box(self.results_text, f"    Failed to retrieve recipe details. Status code: {recipe_response.status_code}\n\n", append=True)
            else:
                self.update_text_box(self.results_text, "No recipes found for the given ingredients from TheMealDB.\n\n", append=True)

        except requests.exceptions.RequestException as e:
            self.update_text_box(self.results_text, f"API request failed: {e}\n", append = True)
        except json.JSONDecodeError:
            self.update_text_box(self.results_text, "Failed to decode JSON from API response.\n", append = True)

    def call_chatgpt_api(self, prompt_text):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.OPENAI_API_KEY}'
        }
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant that provides cooking advice and recipe suggestions.'},
                {'role': 'user', 'content': prompt_text}
            ],
            'temperature': 0.9, # Controls randomness. Lower is more deterministic.
            'max_tokens': 1000  # Increased max_tokens for better recipe descriptions.
        }

        try:
            response = requests.post(self.OPENAI_API_URL, headers = headers, data = json.dumps(payload))
            response.raise_for_status()
            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                return response_data['choices'][0]['message']['content'].strip()
            else:
                return "No response from ChatGPT."
        except requests.exceptions.RequestException as e:
            return f"API request failed: {e}"
        except json.JSONDecodeError:
            return "Failed to decode JSON from API response."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def ask_chatgpt(self):
        self.update_text_box(self.results_text, "Asking ChatGPT for recipe ideas...\n")
        if not self.detected_ingredients:
            self.update_text_box(self.results_text, "No ingredients detected. Please upload an image first.\n", append = True)
            return
        
        self.comma_separated_ingredients = self.ingredients_text_box.get('1.0', tk.END).replace('\n', ', ')
        self.comma_separated_ingredients = self.comma_separated_ingredients[:-2]  #Remove the trailing ','.

        prompt = f"Given only these ingredients: {self.comma_separated_ingredients}. What are some recipe ideas? Please provide two simple recipes for some ideas.\n"
        
        self.update_text_box(self.results_text, f"Searching for recipes with: {self.comma_separated_ingredients}\n\n")
        self.update_text_box(self.results_text, f"Asking for recipes from ChatGPT:\n {prompt}\n")

        chatgpt_answer = self.call_chatgpt_api(prompt)
        self.update_text_box(self.results_text, "\nChatGPT's response:\n", append = True)
        self.update_text_box(self.results_text, chatgpt_answer + "\n\n", append = True)

# Run the Tkinter application
if __name__ == '__main__':
    root = tk.Tk()
    app = TkinterApp(root)
    root.mainloop()




