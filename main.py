import cv2
import mediapipe as mp
import win32api
import win32con
import time

# إعداد الكاميرا بحجم أصغر
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)   # عرض أصغر
cap.set(4, 360)   # ارتفاع أصغر

hands = mp.solutions.hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

screen_w, screen_h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
prev_x, prev_y = screen_w // 2, screen_h // 2
smooth_factor = 0.7  # زيادة السرعة (كلما اقترب من 1، كلما أسرع)

click_cooldown = 0.3
last_click_time = 0

# أزرار صغيرة داخل نافذة الكاميرا
buttons = {
    "LeftClick": ((10, 10), (130, 60)),
    "RightClick": ((150, 10), (270, 60)),
    "Exit": ((290, 10), (410, 60))
}

def left_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def right_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)

running = True
while running:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # رسم الأزرار
    for name, ((x1, y1), (x2, y2)) in buttons.items():
        color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, name, (x1+5, y1+35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)

        x = int(hand.landmark[8].x * 640)
        y = int(hand.landmark[8].y * 360)
        new_x = int(prev_x + (x - prev_x) * smooth_factor)
        new_y = int(prev_y + (y - prev_y) * smooth_factor)
        prev_x, prev_y = new_x, new_y

        # دائرة على الإصبع
        cv2.circle(frame, (x, y), 8, (0,0,255), -1)

        win32api.SetCursorPos((new_x, new_y))

        # التحقق من الضغط على الأزرار
        current_time = time.time()
        if current_time - last_click_time > click_cooldown:
            for name, ((x1, y1), (x2, y2)) in buttons.items():
                if x1 < x < x2 and y1 < y < y2:
                    last_click_time = current_time
                    if name == "LeftClick":
                        left_click()
                    elif name == "RightClick":
                        right_click()
                    elif name == "Exit":
                        running = False

    cv2.imshow("Hand Mouse Controller", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
