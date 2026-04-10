from ultralytics import YOLO

# Load a pretrained model (recommended)
model = YOLO("yolo26n.pt")
#model = YOLO("/home/jetson/Desktop/Project/runs/detect/ingredients7/weights/best.pt")

# Train the model
results = model.train(data = '/home/jetson/Desktop/Project/INGREDIENTS/data.yaml', name = 'ingredients', epochs = 200, imgsz = [640])

# Export the model
success1 = model.export(format = "openvino", imgsz = [640], dynamic = True)
success2 = model.export(format = "onnx", imgsz = [640], dynamic = True)
success3 = model.export(format = "engine", imgsz = [640], dynamic = True)

