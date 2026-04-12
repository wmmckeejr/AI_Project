
"What can I make for dinner?"  This is a common refrain in every household.  My wife directed me to create a recipe generator for this project.  I went one step further and added object detection in order to quickly update the available ingredients.
This project will use an object detection model using Yolo (1) and a yaml dataset from Roboflow (2) to capture food items that are to be used for a recipe.  Once the items have been identified, they will be provided to a large language model from The Meal DB web site (3) to generate an appropriate recipe using those ingredients.  The recipe wll then be displayed for the user to enjoy.  I have also incorporated a call to ChatGPT (4)to have it provide a recipe for display.  I later commented out the Meal DB version due to an issue calling their API on my computer even though it works fine from Google Colab (6).

The Yolo model is created using 150 epochs.  The item names in the yaml file were updated to follow the naming convention need by the webiste.  A Thor Jetson (5) (which is designed for A.I. using an Nvidia graphics card) was used in training the model.  It still took hours to complete the training.

Run this command in a terminal/shell: python ./AI_Project_with_ChatGPT_GUI.py

References:
1: https://platform.ultralytics.com/
2: https://universe.roboflow.com/food-recipe-ingredient-images-0gnku/food-ingredients-dataset
3: https://www.themealdb.com/
4: https://openai.com/
5: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/
6: https://colab.research.google.com/
