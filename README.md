# Office Delivery Robot (AMR / Nav2 / ROS 2)

Dự án Robot tự hành giao hàng văn phòng (Autonomous Mobile Robot - AMR) xây dựng trên nền tảng **ROS 2** và **Navigation2 (Nav2)**. Sổ tay cung cấp hướng dẫn biên dịch, vận hành mô phỏng, cấu hình kiến trúc kỹ thuật và thông số tối ưu hóa thực nghiệm.

---

## 1. Cấu trúc thư mục & Quy ước Workspace

```text
ros2_ws/                        <-- THƯ MỤC GỐC WORKSPACE (Chỉ đứng ở đây để build)
├── build/                      <-- Tự sinh khi build (File rác/trung gian - Không sửa, không commit)
├── install/                    <-- Tự sinh khi build (File chạy thực tế)
├── log/                        <-- Tự sinh khi build (Log lỗi)
└── src/                        <-- ROOT CỦA GIT REPO (Nơi duy nhất con người viết code)
    ├── .gitignore              <-- Cấu hình bỏ qua file tạm, cache, tài liệu tham khảo
    ├── README.md               <-- Tài liệu hướng dẫn & Báo cáo kỹ thuật
    └── office_bot/             <-- Package chính của robot
        ├── maps/               <-- Nơi lưu trữ bản đồ 2D (my_map.yaml, my_map.pgm)
        ├── launch/             <-- Các file khởi động hệ thống (.launch.py)
        │   ├── localization.launch.py  <-- Khởi chạy bản đồ và định vị AMCL
        │   └── navigation.launch.py    <-- Khởi chạy toàn bộ hệ thống tự hành Nav2
        ├── config/             <-- File tham số cấu hình chi tiết
        │   └── nav2_params.yaml        <-- Tham số Costmap, Planner, Controller, AMCL
        ├── office_bot/         <-- Mã nguồn Python logic điều khiển & nhiệm vụ
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

# 3. Nạp môi trường sau khi build (Tự động nạp nếu đã cấu hình ~/.bashrc)
source install/setup.bash
```

* **Ý nghĩa cờ `--symlink-install`:** Tạo liên kết mềm (shortcut) từ `src/` sang `install/`. Cho phép cập nhật code Python, thay đổi file cấu hình `.yaml` hoặc đổi file bản đồ mà **KHÔNG CẦN** biên dịch lại; hệ thống sẽ nhận ngay thay đổi trong lần khởi chạy kế tiếp.

---

## 3. Lệnh khởi chạy hệ thống (Running System)

Mở 2 Tab Terminal độc lập trong VS Code hoặc Terminator:

### 🖥️ Tab 1: Khởi động môi trường mô phỏng Gazebo
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 🖥️ Tab 2: Khởi động bộ não tự hành Nav2 (Tự động nạp Map + Cấu hình + RViz2)
```bash
ros2 launch office_bot navigation.launch.py
```

### 🖥️ Tab 3: Khởi động kịch bản tự động giao hàng khép kín (Autonomous Mission)
```bash
ros2 run office_bot delivery_mission
```
*(Robot sẽ tự động xuất phát từ Home $\to$ đến Pantry lấy đồ $\to$ đến Desk 1 giao hàng $\to$ tự động quay về Home sạc pin mà không cần can thiệp chuột thủ công).*

*(Tùy chọn: Nếu chỉ muốn kiểm tra Định vị Localization đơn lẻ mà chưa cần bộ điều hướng tự lái, chạy: `ros2 launch office_bot localization.launch.py`)*

---

## 4. Hướng dẫn Lái xe Tự hành bằng RViz2 (Nav2 Goal)

1. Khi `navigation.launch.py` chạy lên, giao diện **RViz2** chuẩn Nav2 sẽ tự động xuất hiện.
2. Bản đồ văn phòng và các cột chướng ngại vật sẽ hiển thị cùng với hai lớp Costmap (Global & Local Costmap).
3. Thuật toán lọc hạt AMCL đã được cấu hình tự động nhận diện vị trí robot ban đầu tại gốc tọa độ thế giới:
   ```yaml
   initial_pose: {x: 0.0, y: 0.0, z: 0.0, yaw: 0.0}
   ```
4. Trên thanh công cụ trên cùng của RViz2, click chọn công cụ **`Nav2 Goal`** (hoặc `2D Goal Pose`).
5. Click chuột trái vào vị trí đích mong muốn trong phòng, giữ chuột và kéo nhẹ để định hướng quay mặt (Heading) của robot rồi thả chuột.
6. **Quan sát phản hồi tự hành:** 
   * **Global Planner:** Tính toán và hiển thị quỹ đạo màu xanh lá cây uốn lượn mượt mà tránh qua các cột.
   * **Local Controller (DWB):** Điều phối xung vận tốc `cmd_vel` mượt mà, bám sát quỹ đạo.
   * Robot trong Gazebo di chuyển trơn tru, ôm cua chuẩn xác và dừng đỗ với sai số $\le 2\text{cm}$.

---

## 5. Kiến trúc Kỹ thuật & Tối ưu hóa Dẫn đường (Navigation Tuning)

Hệ thống đã trải qua quá trình tối ưu hóa chuyên sâu nhằm triệt tiêu hoàn toàn hiện tượng robot rung lắc, đổi đường liên tục và đâm va vào chướng ngại vật:

### 5.1. Thuật toán dẫn đường toàn cục (Global Path Planner)
* **Plugin:** `nav2_navfn_planner::NavfnPlanner`
* **Thuật toán cốt lõi:** Kích hoạt thuật toán **$A^*$** (`use_astar: true`) thay thế cho Dijkstra cổ điển. Hàm Heuristic khoảng cách Euclid:
  $$h(n) = \sqrt{(x_n - x_{\text{goal}})^2 + (y_n - y_{\text{goal}})^2} \cdot C_{\text{neutral}}$$
  *(với $C_{\text{neutral}} = 50$ là chi phí di chuyển chuẩn qua một ô trống `COST_NEUTRAL`)* tạo độ dốc thế năng định hướng mạnh mẽ về đích, loại bỏ hoàn toàn hiện tượng phân vân lật đường (path flipping) giữa các cột đối xứng.
* **Tần số quy hoạch:** Khống chế `expected_planner_frequency: 1.0 Hz` (thay vì re-plan liên tục 20Hz), giữ quỹ đạo toàn cục ổn định để bộ điều khiển cục bộ bám theo.

### 5.2. Bộ điều khiển bám quỹ đạo cục bộ (Local Trajectory Controller)
* **Plugin:** `dwb_core::DWBLocalPlanner` (thay thế cho MPPI vốn tiêu tốn 100% CPU trên môi trường ảo hóa WSL2).
* **Khống chế động học an toàn (Burger Model):**
  * $v_{\max} = 0.22\,\text{m/s}$, $v_{\min} = -0.22\,\text{m/s}$
  * $\omega_{\max} = 1.5\,\text{rad/s}$, $\dot{\omega}_{\max} = 3.2\,\text{rad/s}^2$
* **Velocity Smoother:** Cấu hình phản hồi vòng kín `feedback: "CLOSED_LOOP"` bám theo vận tốc thực tế của bánh xe từ Odometry, loại bỏ hiện tượng sai lệch dự phóng mù (Open-Loop Hallucination).

### 5.3. Xử lý bản đồ chi phí (Costmap 2D Optimization)
* **Bán kính robot thực tế:** `robot_radius: 0.12 m` (vừa khít kích thước TurtleBot3 Burger).
* **Bán kính phình cản an toàn:** Giảm `inflation_radius: 0.35 m` với hệ số phân rã `cost_scaling_factor: 5.0`.
* **Giải pháp chống kẹt:** Khoảng cách giữa các cột trong phòng là $1.0\,\text{m}$. Trước đây bán kính phình mặc định $0.7\,\text{m}$ khiến hai vùng cấm của hai cột giao nhau ($0.7 \times 2 = 1.4\,\text{m} > 1.0\,\text{m}$), biến lối đi thành tường ảo. Việc đưa về $0.35\,\text{m}$ mở thông lối đi an toàn rộng $0.3\,\text{m}$ cho robot.

### 5.4. Đồng bộ Middleware truyền thông (DDS Synchronization)
* Ép chuẩn cố định `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` xuyên suốt toàn bộ hệ điều hành và file launch.
* Triệt tiêu lỗi không tương thích phiên bản (Inconsistent TypeObject) và lỗi thiếu symbol (`has_buffer_fields_...`) của FastDDS trên Ubuntu 26.04 dev.

---

## 6. Các lưu ý kỹ thuật cốt lõi (FAQ & Gotchas)

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
git push origin main
```
*(Đã cấu hình `git config --global credential.helper store` nên các lần push sau không phải nhập lại Token).*

---

## 7. Lộ trình phát triển tiếp theo (Next Milestones)

- [x] **Giai đoạn 1: Nền tảng Tự hành Cốt lõi (Core Navigation Stack)**
  - [x] Bản đồ hóa môi trường văn phòng 3D (SLAM).
  - [x] Tối ưu hóa định vị thích nghi Monte Carlo (AMCL).
  - [x] Tinh chỉnh tham số Global Planner ($A^*$) và Local Controller (DWB).
  - [x] Đạt độ chính xác dừng đỗ $\le 2\text{cm}$, số lần kích hoạt phục hồi kẹt (Recoveries) = 0.
- [x] **Giai đoạn 2: Tự động hóa Nhiệm vụ Giao hàng (Autonomous Mission Automation)**
  - [x] Xây dựng script Python điều phối nhiệm vụ giao hàng đa điểm (`office_bot/delivery_mission.py`).
  - [x] Khai báo tọa độ các vị trí thực tế trong văn phòng: Trạm sạc (`Home`), Kho lấy đồ (`Pantry`), Bàn nhân viên (`Desk_1`, `Desk_2`).
  - [x] Tích hợp API theo dõi tiến độ thời gian thực (ETA, quãng đường còn lại, mô phỏng thời gian tương tác người dùng, tự động quay về trạm sạc khi hoàn thành).
- [ ] **Giai đoạn 3: Giao diện Người dùng & Tích hợp Phần cứng (Deployment & GUI)**
  - [ ] Xây dựng Web Dashboard hoặc API gửi lệnh giao hàng trực quan.
  - [ ] Chuyển giao cấu hình sang phần cứng thực tế (Sim2Real).
