"""Object tracker using."""

import numpy as np
import cv2
from ultralytics import YOLO
from sort_fixed import Sort

if __name__ == '__main__':
    """Main function."""

    cap = cv2.VideoCapture("plane_1.mp4")

    model = YOLO("last_planes.pt")

    tracker = Sort(max_age=200)

    while cap.isOpened():
        status, frame = cap.read()

        if not status:
            break

        results = model(frame, stream=True)

        for res in results:
            filtered_indices = np.where(res.boxes.conf.cpu().numpy() > 0.6)[0]
            boxes = res.boxes.xyxy.cpu().numpy()[filtered_indices].astype(int)
            tracks = tracker.update(boxes)
            tracks = tracks.astype(int)

            for xmin, ymin, xmax, ymax, track_id in tracks:
                cv2.putText(img=frame,
                            text=f"Id: {track_id}",
                            org=(xmin, ymin-10),
                            fontFace=cv2.FONT_HERSHEY_PLAIN,
                            fontScale=2,
                            color=(0, 255, 0), thickness=2)
                cv2.rectangle(img=frame,
                              pt1=(xmin, ymin),
                              pt2=(xmax, ymax),
                              color=(0, 255, 0),
                              thickness=2)

        # frame = results[0].plot()

        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
