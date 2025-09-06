import cv2
import mediapipe as mp
import keyboard
import time

# Camera setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 360)

cv2.namedWindow("Safe Hand Gaming Control", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Safe Hand Gaming Control", 1000, 600)

hands = mp.solutions.hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Simple and fast controls
frame_width, frame_height = 640, 360
center_x, center_y = frame_width // 2, frame_height // 2

# High sensitivity thresholds - سهل جداً
horizontal_threshold = 0.08  # حساسية عالية
vertical_threshold = 0.08
small_dead_zone = 0.12  # منطقة آمنة أكبر - larger safe area

# Simple timing - محسن لمنع التكرار
last_move_time = 0
move_cooldown = 0.3  # مدة أطول بين الحركات
must_return_to_safe = False  # لازم ترجع للمنطقة الآمنة

# Single movement system - حركة واحدة فقط
current_direction = None
move_executed = False  # تم تنفيذ الحركة


def single_key_press(direction):
    """ضغطة واحدة سريعة فقط - لا استمرار ولا تكرار"""
    keyboard.press_and_release(direction)


def stop_movement():
    """إعادة تعيين حالة الحركة"""
    global move_executed, current_direction
    move_executed = False
    current_direction = None


def get_simple_direction(x, y):
    """تحديد بسيط للاتجاه - حساسية عالية"""
    # تحويل لنسب بسيطة
    rel_x = (x - center_x) / frame_width
    rel_y = (y - center_y) / frame_height

    # منطقة ميتة صغيرة جداً
    if abs(rel_x) < small_dead_zone and abs(rel_y) < small_dead_zone:
        return None

    # اتجاه بسيط - أول حركة واضحة
    if abs(rel_x) > horizontal_threshold:
        return "right" if rel_x > 0 else "left"
    elif abs(rel_y) > vertical_threshold:
        return "down" if rel_y > 0 else "up"

    return None


def draw_simple_ui(frame, hand_pos, direction):
    """واجهة بسيطة وواضحة"""
    # رسم منطقة آمنة أكبر
    dead_size = int(small_dead_zone * min(frame_width, frame_height))
    cv2.circle(frame, (center_x, center_y), dead_size, (0, 255, 0), 3)
    cv2.putText(frame, "SAFE AREA", (center_x - 40, center_y + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # خطوط الحساسية
    h_line = int(horizontal_threshold * frame_width)
    v_line = int(vertical_threshold * frame_height)

    # خطوط أفقية (يسار/يمين)
    cv2.line(frame, (center_x - h_line, 0), (center_x - h_line, frame_height), (255, 100, 100), 1)
    cv2.line(frame, (center_x + h_line, 0), (center_x + h_line, frame_height), (255, 100, 100), 1)

    # خطوط عمودية (فوق/تحت)
    cv2.line(frame, (0, center_y - v_line), (frame_width, center_y - v_line), (100, 100, 255), 1)
    cv2.line(frame, (0, center_y + v_line), (frame_width, center_y + v_line), (100, 100, 255), 1)

    # عرض الاتجاه الحالي
    if direction:
        cv2.putText(frame, f"DETECTED: {direction.upper()}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        # مؤشر ملون للاتجاه
        if direction == "right":
            cv2.arrowedLine(frame, (center_x, center_y), (center_x + 80, center_y), (0, 255, 0), 5)
        elif direction == "left":
            cv2.arrowedLine(frame, (center_x, center_y), (center_x - 80, center_y), (0, 255, 0), 5)
        elif direction == "up":
            cv2.arrowedLine(frame, (center_x, center_y), (center_x, center_y - 80), (0, 255, 0), 5)
        elif direction == "down":
            cv2.arrowedLine(frame, (center_x, center_y), (center_x, center_y + 80), (0, 255, 0), 5)

    # رسم موضع اليد
    if hand_pos:
        x, y = hand_pos
        cv2.circle(frame, (x, y), 12, (0, 0, 255), -1)
        cv2.circle(frame, (x, y), 15, (255, 255, 255), 2)

        # خط للمركز
        cv2.line(frame, (center_x, center_y), (x, y), (255, 255, 0), 2)

    # معلومات سريعة
    if must_return_to_safe:
        cv2.putText(frame, "Return to GREEN zone!", (10, frame_height - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    if move_executed:
        cv2.putText(frame, f"Moved {current_direction.upper()}!", (10, frame_height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    else:
        cv2.putText(frame, "Ready for next move \n Maded By Youssef Ibrahim", (10, frame_height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)


print("🎮 SAFE Hand Control - No Continuous Pressing!")
print("=" * 45)
print("✓ Single tap only - no continuous pressing!")
print("✓ One move per gesture - safer gaming!")
print("✓ Must return to GREEN zone between moves")
print("✓ LARGER safe area in center - more room to rest!")
print("✓ No complex confirmations!")
print("✓ Press ESC to quit")
print("=" * 45)

# Main game loop
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    current_time = time.time()
    detected_direction = None
    hand_position = None

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]

        # موضع إصبع السبابة
        finger_tip = hand.landmark[8]
        x = int(finger_tip.x * frame_width)
        y = int(finger_tip.y * frame_height)
        hand_position = (x, y)

        # تحديد الاتجاه بسرعة
        detected_direction = get_simple_direction(x, y)

        # تنفيذ حركة واحدة فقط
        if (detected_direction and
                current_time - last_move_time > move_cooldown and
                not must_return_to_safe and
                not move_executed):  # لم يتم تنفيذ حركة بعد

            # تنفيذ حركة واحدة فورية
            single_key_press(detected_direction)
            current_direction = detected_direction
            last_move_time = current_time
            must_return_to_safe = True
            move_executed = True  # تم تنفيذ الحركة

        elif not detected_direction:
            # رجع للمنطقة الآمنة - جاهز لحركة جديدة
            if must_return_to_safe:
                stop_movement()
                must_return_to_safe = False

        # رسم نقاط اليد (خفيف)
        mp_draw.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)

    else:
        # لا توجد يد - إعادة تعيين كل شيء
        stop_movement()
        detected_direction = None
        must_return_to_safe = False

    # رسم الواجهة
    draw_simple_ui(frame, hand_position, detected_direction)

    # عرض النافذة
    cv2.imshow("Safe Hand Gaming Control", frame)

    # خروج بـ ESC
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or cv2.getWindowProperty("Safe Hand Gaming Control", cv2.WND_PROP_VISIBLE) < 1:
        break

# تنظيف
cap.release()
cv2.destroyAllWindows()