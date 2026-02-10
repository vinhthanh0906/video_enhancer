import cv2

cap = cv2.VideoCapture(r"D:\WORK\Python\CV\video_enhancer\2455892435034638151.mp4")

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("enhanced.mp4", fourcc, 30,
                      (int(cap.get(3)), int(cap.get(4))), False)

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    enhanced = clahe.apply(gray)

    out.write(enhanced)

cap.release()
out.release()
