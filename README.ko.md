<div align="center">

# microduck_urdf

[English](README.md) | **한국어**

**Pollen Robotics Microduck 이족 보행 로봇의 ROS 2 URDF 패키지**

원본 MuJoCo 모델의 형상, 질량, 관성, 조인트를 그대로 옮겼습니다.

[![CI](https://github.com/Indigochi1d/microduck_urdf/actions/workflows/ci.yml/badge.svg)](https://github.com/Indigochi1d/microduck_urdf/actions/workflows/ci.yml)
[![ROS 2](https://img.shields.io/badge/ROS%202-Kilted-22314E?logo=ros)](https://docs.ros.org/en/kilted/)
[![Code License](https://img.shields.io/badge/code-Apache%202.0-blue.svg)](LICENSE)
[![Mesh License](https://img.shields.io/badge/meshes-CC%20BY--NC--SA%204.0-lightgrey.svg)](meshes/LICENSE.md)

<img src="docs/images/microduck.png" alt="microduck_urdf 렌더링" width="550"/>

</div>

---

## 개요

[Microduck](https://github.com/pollen-robotics/microduck)은 Pollen Robotics가 공개한 높이 25 cm, 무게 800 g 미만의 오픈소스 이족 보행 로봇입니다.
이 패키지는 Pollen Robotics의 강화학습 저장소 [microduck_rl](https://github.com/pollen-robotics/microduck_rl)에 있는 **MuJoCo 모델(MJCF)** 을 원본으로 삼아,
ROS 2에서 바로 쓸 수 있는 URDF로 옮긴 패키지입니다.
링크 이름은 `<구동 조인트>_link` 규칙을 따르며(예: `left_knee` → `left_knee_link`), 몸통은 `base_link`입니다.

## 특징

| 항목           | 내용                                                                                                 |
| :------------- | :--------------------------------------------------------------------------------------------------- |
| 물리 파라미터  | 링크별 질량, 무게중심, 관성 텐서(총 737.2 g)와 조인트 damping/friction을 MJCF에서 그대로 옮겼습니다. |
| 충돌 형상      | MJCF의 충돌 메쉬를 포함하며, `collision:=false`로 끌 수 있습니다.                                    |
| 센서 프레임    | IMU, 양발, 헤드 카메라, ToF, 헤드 IMU, 부리 끝을 고정 프레임으로 제공합니다.                         |
| 바로 쓰는 런치 | RViz2와 조인트 슬라이더를 한 번에 띄우는 `display.launch.py`를 제공합니다.                           |

## 조인트

| 그룹     | 조인트            | 부모 → 자식                                    | 범위 (rad)     |
| :------- | :---------------- | :--------------------------------------------- | :------------- |
| 왼다리   | `left_hip_yaw`    | `base_link` → `left_hip_yaw_link`              | -0.436 ~ 0.524 |
|          | `left_hip_roll`   | `left_hip_yaw_link` → `left_hip_roll_link`     | -0.384 ~ 0.384 |
|          | `left_hip_pitch`  | `left_hip_roll_link` → `left_hip_pitch_link`   | -1.571 ~ 1.571 |
|          | `left_knee`       | `left_hip_pitch_link` → `left_knee_link`       | -1.571 ~ 1.571 |
|          | `left_ankle`      | `left_knee_link` → `left_ankle_link`           | -1.571 ~ 1.571 |
| 오른다리 | `right_hip_yaw`   | `base_link` → `right_hip_yaw_link`             | -0.524 ~ 0.436 |
|          | `right_hip_roll`  | `right_hip_yaw_link` → `right_hip_roll_link`   | -0.384 ~ 0.384 |
|          | `right_hip_pitch` | `right_hip_roll_link` → `right_hip_pitch_link` | -1.571 ~ 1.571 |
|          | `right_knee`      | `right_hip_pitch_link` → `right_knee_link`     | -1.571 ~ 1.571 |
|          | `right_ankle`     | `right_knee_link` → `right_ankle_link`         | -1.571 ~ 1.571 |
| 목/머리  | `neck_pitch`      | `base_link` → `neck_pitch_link`                | -1.571 ~ 1.047 |
|          | `head_pitch`      | `neck_pitch_link` → `head_pitch_link`          | -1.571 ~ 1.571 |
|          | `head_yaw`        | `head_pitch_link` → `head_yaw_link`            | -2.967 ~ 2.967 |
|          | `head_roll`       | `head_yaw_link` → `head_roll_link`             | -0.436 ~ 0.436 |

모든 조인트의 effort는 MJCF 액추에이터의 `forcerange`(0.96 Nm), velocity는 XL330 무부하 속도(10.8 rad/s)입니다.

**센서 프레임:** `imu_link`, `left_foot_link`, `right_foot_link`, `head_camera_link`, `tof_link`, `head_imu_link`, `mouth_tip_link`

## 패키지 구조

```
microduck_urdf/
├── launch/
│   ├── description.launch.py   robot_state_publisher
│   └── display.launch.py       RViz2 + joint_state_publisher_gui
├── meshes/                     STL 메쉬 (CC BY-NC-SA 4.0)
├── rviz/display.rviz
├── test/test_microduck_urdf.py
└── urdf/
    ├── microduck.urdf.xacro    진입점 (collision 인자)
    ├── microduck.xacro         링크/조인트 매크로
    └── microduck.urdf          단독 URDF
```

## 시작하기

### 빌드

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/Indigochi1d/microduck_urdf.git

cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -y
colcon build --packages-select microduck_urdf
source install/setup.bash
```

### 실행

```bash
# RViz2와 조인트 슬라이더
ros2 launch microduck_urdf display.launch.py

# robot_description과 TF만 발행
ros2 launch microduck_urdf description.launch.py collision:=false
```

### ROS 없이 미리보기

`urdf/microduck.urdf`는 메쉬를 `../meshes/` 상대 경로로 참조하므로 아무 URDF 뷰어에서나 바로 열 수 있습니다.
VSCode에서는 **URDF Visualizer** 확장을 권장합니다.

## 테스트

```bash
colcon test --packages-select microduck_urdf --event-handlers console_direct+
colcon test-result --verbose
```

조인트 구성과 리밋, 링크 트리 연결, 질량·관성 값, 메쉬 파일, xacro 출력과 `collision` 옵션을 확인합니다.

## 출처와 라이선스

이 패키지의 로봇 모델은 **Pollen Robotics**가 공개한 MuJoCo 모델에서 비롯되었습니다.

| 대상                            | 출처                                                                            | 라이선스                             |
| :------------------------------ | :------------------------------------------------------------------------------ | :----------------------------------- |
| URDF, xacro, 런치, 테스트       | 이 저장소 (원본 MJCF에서 변환)                                                  | [Apache 2.0](LICENSE)                |
| `meshes/*.stl` (수정 없이 복사) | [pollen-robotics/microduck_rl](https://github.com/pollen-robotics/microduck_rl) | [CC BY-NC-SA 4.0](meshes/LICENSE.md) |

메쉬는 **비영리 목적으로만** 사용할 수 있으며, 수정본도 같은 라이선스로 공유해야 합니다.
URDF는 메쉬를 참조하므로, 메쉬를 포함해 재배포할 때는 이 조건을 따라야 합니다.

## 참고

- [pollen-robotics/microduck](https://github.com/pollen-robotics/microduck) — Microduck 로봇 소프트웨어
- [pollen-robotics/microduck_rl](https://github.com/pollen-robotics/microduck_rl) — 원본 MuJoCo 모델과 강화학습 환경
- [onshape-to-robot](https://github.com/Rhoban/onshape-to-robot) — upstream MJCF를 생성한 도구
- [mjcf2urdf](https://github.com/iory/mjcf2urdf) — MJCF → URDF 변환 도구
