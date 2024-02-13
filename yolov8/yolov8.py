from ultralytics import YOLO
import torch 
x=torch.cuda.is_available()
print(x)

torch.cuda.empty_cache()
torch.cuda.memory_allocated()

print(torch.cuda.memory_allocated())

for i in range(torch.cuda.device_count()):
   print(torch.cuda.get_device_properties(i).name)

# Load a pretrained YOLO model (recommended for training)
model = YOLO('best_ulu_1_25_24.pt')

# Train the model using the 'coco128.yaml' dataset for 3 epochs
#results = model.train(data='nunalleq.yaml', workers=1, epochs=300, imgsz=1280)

# Evaluate the model's performance on the validation set
#results = model.val()

# Perform object detection on an image using the model
#results = model('ulu.jpg')

# Export the model to ONNX format
success = model.export(format='onnx')
