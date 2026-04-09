This project will use an object detection model using Yolo (1) and a yaml dataset from Roboflow (2) to capture food items that are to be used for a recipe.  Once the items have been identified, they will be provided to a large language model from The Meal DB web site (3) to generate an appropriate recipe using those ingredients.  The recipe wll then be displayed for the user to enjoy.

The Yolo model is created using 150 epochs.  The item names in the yaml file were updated to follow the naming convention need by the webiste.  A Thor Jetson (4) (which is designed for A.I. using an Nvidia graphics card) was used in training the model.  It still took hours to complete the training.

References:
1: https://platform.ultralytics.com/
2: https://universe.roboflow.com/food-recipe-ingredient-images-0gnku/food-ingredients-dataset
3: https://www.themealdb.com/
4: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/
