# Office Delivery Robot (AMR / Nav2 / ROS 2)

Sổ tay lệnh thực thi và lưu ý kỹ thuật cho dự án Robot tự hành giao đồ văn phòng.

---

## 1. Cấu trúc thư mục & Quy ước Workspace

```text
ros2_ws/                        <-- THƯ MỤC GỐC WORKSPACE (Chỉ đứng ở đây để build)
├── build/                      <-- Tự sinh khi build (File rác/trung gian - Không sửa, không commit)
├── install/                    <-- Tự sinh khi build (File chạy thực tế)
├── log/                        <-- Tự sinh khi build (Log lỗi)
└── src/                        <-- ROOT CỦA GIT REPO (Nơi duy nhất con người viết code)
    ├── README.md
    └── office_bot/             <-- Package chính của robot
        ├── maps/               <-- Nơi lưu trữ bản đồ 2D (my_map.yaml, my_map.pgm)
        ├── launch/             <-- Các file khởi động hệ thống (.launch.py)
        ├── config/             <-- File tham số tham chiếu (.yaml)
        ├── office_bot/         <-- Mã nguồn Python logic điều khiển
        ├── package.xml         <-- Khai báo metadata và dependencies
        ├── setup.cfg           <-- Cấu hình đường dẫn thực thi script
        └── setup.py            <-- Cấu hình cài đặt và nạp tài nguyên
```

---

## 2. Lệnh biên dịch (Build)

> **LƯU Ý SỐNG CÒN:** Luôn `cd ~/ros2_ws` trước khi gõ lệnh build. **TUYỆT ĐỐI KHÔNG** đứng trong `src/` để gõ `colcon build`.

```bash
# 1. Di chuyển về thư mục gốc của workspace
cd ~/ros2_ws

# 2. Biên dịch với cờ liên kết mềm (Symlink)
colcon build --symlink-install

# 3. Nạp môi trường sau khi build (Chỉ cần nếu chưa cấu hình ~/.bashrc)
source install/setup.bash
```

* **Ý nghĩa cờ `--symlink-install`:** Tạo liên kết mềm (shortcut) từ `src/` sang `install/`. Giúp bạn sửa code Python, sửa file `.yaml` hoặc đổi file map mà **KHÔNG CẦN** gõ lại lệnh build, code tự động cập nhật ngay lập tức.

---

## 3. Lệnh khởi chạy hệ thống (Running System)

Mở 2 Tab Terminal độc lập trong VS Code:

### 🖥️ Tab 1: Khởi động môi trường mô phỏng Gazebo
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 🖥️ Tab 2: Khởi động bộ não tự hành Nav2 với Map của dự án
```bash
ros2 launch nav2_bringup bringup_launch.py \
    use_sim_time:=True \
    map:=$(ros2 pkg prefix office_bot)/share/office_bot/maps/my_map.yaml
```

---

## 4. Các lưu ý kỹ thuật cốt lõi (FAQ & Gotchas)

### Q1: Vị trí đứng của Terminal khi thao tác lệnh?
* **Lệnh chạy robot (`ros2 launch`, `ros2 run`, `ros2 topic`):** Đứng ở **bất kỳ thư mục nào** trong terminal cũng chạy được, miễn là môi trường đã được `source`.
* **Lệnh `colcon build`:** **BẮT BUỘC** phải đứng ở `~/ros2_ws`. Nếu đứng trong `src/` mà build, thư mục `build/`, `install/` sẽ bị tạo đè vào bên trong Git repo.

### Q2: Tại sao từng bị lỗi "Package not found" và cơ chế của `AMENT_PREFIX_PATH`?
* ROS 2 tìm kiếm các package thông qua biến môi trường **`AMENT_PREFIX_PATH`** lưu tạm trong **RAM**.
* Khi mở terminal mới, nếu chưa `source ~/ros2_ws/install/setup.bash`, ROS 2 chỉ nhìn thấy các gói hệ thống trong `/opt/ros/lyrical`.
* **Cách khắc phục vĩnh viễn:** Đã thêm dòng sau vào cuối file `~/.bashrc` (nằm ở `/home/loivt/.bashrc`):
  ```bash
  source ~/ros2_ws/install/setup.bash
  ```
  File `.bashrc` tự động chạy mỗi khi mở Terminal mới $\rightarrow$ biến môi trường luôn tự nạp vào RAM.

### Q3: File `.bashrc` nằm ở đâu?
* Nằm tại thư mục cá nhân người dùng: `/home/loivt/.bashrc` (ký hiệu `~/.bashrc`).
* Dấu `.` ở đầu là file ẩn. Không nằm trong `ros2_ws`.
* Kiểm tra 5 dòng cuối file `.bashrc`:
  ```bash
  tail -n 5 ~/.bashrc
  ```

### Q4: Quy trình Git & Đẩy code lên GitHub từ WSL
GitHub không hỗ trợ mật khẩu thông thường qua Terminal, bắt buộc dùng **Personal Access Token (classic)** có tích quyền `repo`.

```bash
# Đứng tại thư mục git (src)
cd ~/ros2_ws/src

# Kiểm tra trạng thái file thay đổi
git status

# Thêm, commit và đẩy lên GitHub
git add .
git commit -m "Noi dung cap nhat"
git push
```
*(Đã bật `git config --global credential.helper store` nên các lần push sau không phải nhập lại Token).*
