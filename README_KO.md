# URRC 대회 운영 워크스페이스

**6개 맵: Monza, Spa, Monaco, COTA, Hungaroring, Baku.**
첨부 원본의 설치 리소스에서 6개 맵을 소스로 복구했습니다. 원본의 여섯 번째 구성에는 Singapore가 아니라 Hungaroring이 포함되어 있습니다.
참가자에게는 [몬자 연습 저장소](https://github.com/nahee2345/urrc_2)를 공유합니다.

## qor PC에서 새로 설치

Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic이 설치된 PC에서 실행합니다.

```bash
sudo apt update
sudo apt install ros-jazzy-ros-gz python3-colcon-common-extensions python3-rosdep cmake
git clone https://github.com/nahee2345/urrc_f1_ws.git
cd urrc_f1_ws
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=12
python3 verify_release.py
```

사용자명, 저장소 폴더명, 실행 터미널의 현재 위치를 코드에 고정하지 않습니다. 실행기 파일 위치에서 작업 루트를 찾고 ROS 환경은 현재 설정을 사용합니다. 기존 PC의 build/install/log 대신 qor PC에서 소스로 다시 빌드합니다. `ROS_DOMAIN_ID`는 환경변수로 변경할 수 있습니다.

## 맵과 신호등만 확인

```bash
bash run_track.sh monza --view grid
# 다른 터미널에서 같은 저장소로 이동
bash test_lights.sh sequence --track monza
```

다른 맵은 monza 대신 spa, monaco, cota, hungaroring, baku를 지정합니다. 한 번에 하나만 실행합니다. `--dry-run`으로 실행 경로를 확인할 수 있습니다. 렌즈 자체가 발광하고 5개 점등 후 소등하는 F1 방식입니다.

## 참가 접수 → 예선 → 본선

1. 참가자의 팀 폴더·src·패키지 또는 ZIP을 `race/inbox/`에 넣습니다. 대표 패키지의 `race_entry.json`이 있어야 합니다.
2. 참가자의 `package.xml`/requirements.txt를 확인하고 추가 의존성을 경기 전에 설치합니다.
3. 아래 순서로 실행합니다. 앞서 켠 맵은 먼저 종료합니다.

```bash
bash competition.sh prepare
bash competition.sh new-event --track spa
bash competition.sh qualifying
bash competition.sh final
bash competition.sh status
```

`new-event`에서 `--track`을 생략하면 6개 중 하나를 무작위로 선택합니다. 선택한 트랙은 event_state.json에 저장되어 예선과 본선에 동일하게 적용됩니다. 예선과 본선 사이에 new-event를 실행하지 않습니다.

- `prepare`: 표준 참가 폴더로 접수 → 소스 빌드 → 패키지·launch·리소스 검사.
- `qualifying`: 최대 12팀, 한 팀씩 1번 그리드에서 2바퀴.
- `final`: 같은 이벤트의 예선 순위로 1~12번 칸에 배치, 10바퀴 동시 주행.
- 결과: `race/results/qualifying.json`, `final.json`, `final.csv`.
- 로그: `race/results/gazebo.log`, `<팀ID>_algorithm.log`, `race/log/`.
- 참가자 0명은 오류 없이 주행을 건너뜁니다. 참가물 변경 후 기존 예선 결과로 본선을 진행하지 마세요.

## 제출·차량 규격

두 저장소는 동일한 [참가 규격](race/README_KO.md)을 사용합니다.
차량 최대 **0.55 × 0.25 × 0.18 m**, LiDAR 전용입니다.
차량·알고리즘·bridge·어댑터·메시와 설정을 참가 패키지에 모두 포함해야 합니다.

몬자 1번 그리드의 기본 스폰은 `(0.37867, -2.05604, 1.24353, yaw=1.45738)`입니다.
각 맵의 실제 스폰 위치는 `tracks/processed/<맵>.json`에서 자동 읽습니다. `race/event_config.json`에서 트랙 선택 범위와 랩 수·제한시간을 설정합니다.

## 재다운로드 검증

GitHub ZIP 또는 새로운 clone을 받은 폴더에서 다음 명령을 실행합니다.

```bash
python3 verify_release.py
bash run_track.sh monza --dry-run
bash run_track.sh spa --dry-run
bash run_track.sh monaco --dry-run
bash run_track.sh cota --dry-run
bash run_track.sh hungaroring --dry-run
bash run_track.sh baku --dry-run
```

이후 qor PC에서 맵별 화면·신호등, 차량 1대의 출발/2랩, 여러 팀의 동시 제어 격리를 확인한 뒤 대회를 진행합니다.
정적 검사는 실제 Gazebo 렌더링·물리 안정성·차량 주행을 대신하지 않습니다.
