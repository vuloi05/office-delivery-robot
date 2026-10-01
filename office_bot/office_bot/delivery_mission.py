#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chương trình Điều phối Nhiệm vụ Giao hàng Tự động (Autonomous Delivery Mission)
Dành cho Robot AMR văn phòng - Dự án Office Delivery Robot (HUST SoICT)
Sử dụng ROS 2 Navigation2 Simple Commander API.
"""

import math
import sys
import time
from geometry_msgs.msg import PoseStamped
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


# ==============================================================================
# 1. KHAI BÁO BẢN ĐỒ CÁC TRẠM VĂN PHÒNG (DELIVERY WAYPOINTS)
# ==============================================================================
# Lưu ý: Toạ độ được tính toán chuẩn theo bản đồ my_map và môi trường văn phòng,
# nằm trong hành lang rộng thoáng, tránh xa các cột chướng ngại vật.
DELIVERY_STATIONS = {
    'home': {
        'x': 0.0,
        'y': 0.0,
        'yaw': 0.0,
        'name': 'Trạm sạc & Chờ lệnh (Home Station)'
    },
    'pantry': {
        'x': -0.5,
        'y': 1.2,
        'yaw': 1.57,  # Quay hướng Bắc (90 độ) - nằm an toàn trong hành lang
        'name': 'Khu lấy đồ / Cafe (Pantry Station)'
    },
    'desk_1': {
        'x': 1.5,
        'y': 0.5,
        'yaw': 0.0,   # Quay hướng Đông (0 độ)
        'name': 'Bàn làm việc 1 (Desk 1 - SoICT)'
    },
    'desk_2': {
        'x': 0.5,
        'y': -1.2,
        'yaw': -1.57, # Quay hướng Nam (-90 độ)
        'name': 'Bàn làm việc 2 (Desk 2)'
    }
}


def create_pose_stamped(navigator: BasicNavigator, x: float, y: float, yaw: float) -> PoseStamped:
    """Tạo thông điệp PoseStamped chuẩn từ toạ độ (x, y, yaw) trong hệ quy chiếu map."""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    # Đóng dấu thời gian chuẩn từ đồng hồ navigator
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = 0.0

    # Chuyển đổi góc quay Euler (Yaw quanh trục Z) sang Quaternion (qx, qy, qz, qw)
    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def navigate_to_station(navigator: BasicNavigator, station_key: str) -> bool:
    """
    Điều khiển robot di chuyển tự hành tới một trạm định trước,
    đồng thời giám sát tiến độ (quãng đường còn lại, ETA) theo thời gian thực.
    """
    station = DELIVERY_STATIONS.get(station_key)
    if not station:
        print(f"[ERROR] Không tìm thấy trạm có mã: '{station_key}'!")
        return False

    print("\n" + "=" * 65)
    print(f"🚀 [XUẤT PHÁT] Robot đang di chuyển tới: {station['name']}")
    print(f"📍 Tọa độ đích: x = {station['x']:.2f} m, y = {station['y']:.2f} m, yaw = {station['yaw']:.2f} rad")
    print("=" * 65)

    goal_pose = create_pose_stamped(navigator, station['x'], station['y'], station['yaw'])
    navigator.goToPose(goal_pose)

    last_log_time = 0.0
    while not navigator.isTaskComplete():
        current_time = time.time()
        # In phản hồi tiến trình mỗi 1.5 giây để không làm tràn màn hình
        if current_time - last_log_time >= 1.5:
            feedback = navigator.getFeedback()
            if feedback:
                dist_remain = feedback.distance_remaining
                # Một số phiên bản Nav2 feedback có duration ETA
                eta_str = ""
                if hasattr(feedback, 'estimated_time_remaining'):
                    eta_sec = feedback.estimated_time_remaining.sec
                    if eta_sec > 0:
                        eta_str = f" | ETA: ~{eta_sec}s"
                print(f"   ⏳ Đang bám quỹ đạo... Quãng đường còn lại: {dist_remain:.2f} m{eta_str}")
            last_log_time = current_time
        time.sleep(0.1)

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print(f"✅ [THÀNH CÔNG] Đã cập bến an toàn tại: {station['name']}!")
        return True
    elif result == TaskResult.CANCELED:
        print(f"⚠️ [CẢNH BÁO] Nhiệm vụ tới {station['name']} đã bị hủy!")
        return False
    elif result == TaskResult.FAILED:
        err_code, err_msg = navigator.getTaskError()
        print(f"❌ [THẤT BẠI] Không thể tiếp cận {station['name']}! (Mã lỗi: {err_code} - {err_msg})")
        return False
    else:
        print(f"❓ [KHÔNG XÁC ĐỊNH] Trạng thái kết thúc lạ: {result}")
        return False


def simulate_human_interaction(message: str, wait_seconds: int = 5):
    """Mô phỏng thời gian con người tương tác (bốc đồ lên khay, lấy hàng)."""
    print(f"\n📦 {message}")
    for remaining in range(wait_seconds, 0, -1):
        print(f"   ⏱️  Đang tương tác... Vui lòng chờ {remaining}s", end="\r", flush=True)
        time.sleep(1.0)
    print("   ✨ Hoàn tất thao tác! Tiếp tục hành trình.           \n")


def run_full_delivery_cycle(navigator: BasicNavigator):
    """
    Thực thi toàn bộ chu trình giao hàng khép kín:
    Home -> Pantry (Lấy đồ) -> Desk 1 (Giao đồ) -> Home (Về sạc)
    """
    print("\n" + "#" * 65)
    print("🤖 BẮT ĐẦU CHU TRÌNH GIAO HÀNG TỰ ĐỘNG (AUTONOMOUS DELIVERY CYCLE)")
    print("#" * 65)

    # Chặng 1: Từ Home đến Pantry lấy đồ
    if not navigate_to_station(navigator, 'pantry'):
        print("[HỦY BỎ] Hủy chu trình do không đến được Pantry!")
        return False
    simulate_human_interaction("ĐÃ TỚI PANTRY: Đang nhận cafe và tài liệu từ bộ phận hậu cần...", wait_seconds=5)

    # Chặng 2: Từ Pantry mang đồ đến Desk 1
    if not navigate_to_station(navigator, 'desk_1'):
        print("[CẢNH BÁO] Không giao được tới Desk 1! Đang chuyển hướng về trạm an toàn...")
        navigate_to_station(navigator, 'home')
        return False
    simulate_human_interaction("ĐÃ TỚI BÀN 1: Xin chào Vũ Tiến Lợi! Vui lòng nhận tài liệu trên khay...", wait_seconds=5)

    # Chặng 3: Giao xong, tự động quay trở về Home Station
    print("🏁 Đơn hàng hoàn tất! Bắt đầu quay về trạm sạc...")
    if not navigate_to_station(navigator, 'home'):
        print("[CẢNH BÁO] Không thể về lại Home! Vui lòng kiểm tra vị trí xe.")
        return False

    print("\n" + "#" * 65)
    print("🎉 TẤT CẢ NHIỆM VỤ ĐÃ HOÀN THÀNH XUẤT SẮC!")
    print("🔋 Robot đã neo đậu an toàn tại Trạm sạc (Home Base) và sẵn sàng cho đơn tiếp theo.")
    print("#" * 65 + "\n")
    return True


def main(args=None):
    rclpy.init(args=args)

    print("================================================================")
    print("   OFFICE DELIVERY ROBOT - BỘ ĐIỀU PHỐI TỰ HÀNH NHIỆM VỤ")
    print("================================================================")
    print("🔄 Đang kết nối tới hệ thống Navigation2...")

    navigator = BasicNavigator()

    # Đảm bảo đồng bộ giờ mô phỏng Gazebo (tránh lỗi lệch đồng hồ hệ thống)
    from rclpy.parameter import Parameter
    navigator.set_parameters([Parameter('use_sim_time', Parameter.Type.BOOL, True)])

    # Chờ toàn bộ các node của Nav2 (Planner, Controller, AMCL) chuyển sang trạng thái Active
    print("⏳ Đang đợi toàn bộ Lifecycle Nodes của Nav2 sẵn sàng...")
    navigator.waitUntilNav2Active(navigator='bt_navigator', localizer='amcl')
    print("🟢 Nav2 đã sẵn sàng hoạt động 100%!\n")

    try:
        # Nếu người dùng truyền tham số dòng lệnh (vd: --target pantry / desk_1 / desk_2 / home)
        if len(sys.argv) > 1 and sys.argv[1].startswith('--target'):
            target_station = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1].split('=')[-1]
            if target_station in DELIVERY_STATIONS:
                navigate_to_station(navigator, target_station)
            else:
                print(f"[ERROR] Mã trạm '{target_station}' không hợp lệ! Danh sách hợp lệ: {list(DELIVERY_STATIONS.keys())}")
        else:
            # Mặc định: Chạy toàn bộ chu trình giao hàng tự động
            run_full_delivery_cycle(navigator)
    except KeyboardInterrupt:
        print("\n🛑 Nhận tín hiệu dừng từ người dùng (Ctrl+C)! Đang dừng xe khẩn cấp...")
        navigator.cancelTask()
    finally:
        navigator.destroyNode()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
