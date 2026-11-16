# URRC F1 공식 대회 운영 (v24)

**대회 운영용 폴더입니다.** Ubuntu 24.04 / ROS 2 Jazzy / Gazebo Harmonic 기준이며, 6개 맵(`monza`, `hungaroring`, `monaco`, `spa`, `cota`, `baku`)을 사용합니다.

## 1. 다른 컴퓨터에서 다운로드

ROS 2 Jazzy와 Gazebo Harmonic이 설치된 Ubuntu PC에서 실행합니다. ROS 2·Gazebo 설치 자체는 GitHub 저장소에 포함되지 않습니다.

```bash
sudo apt update
sudo apt install -y git python3-colcon-common-extensions ros-jazzy-ros-gz
cd ~
git clone https://github.com/nahee2345/urrc_f1_ws.git
cd ~/urrc_f1_ws
source /opt/ros/jazzy/setup.bash
bash verify_integrated_v24.sh
```

`PASS`는 맵과 ROS 브리지의 기본 실행 검사 결과이며 참가 차량의 완주 보장은 아닙니다. 맵 화면과 신호등까지 확인하려면 다음을 실행합니다.

```bash
bash verify_integrated_v24.sh --gui
```

## 2. `src/team/team_XX` 폴더가 있을 때 검증

예를 들어 `src/team/team_01/`에 `race_entry.json`과 모든 팀 자체 소스·차량 모델·센서 설정이 있는 경우입니다. 팀 폴더 하나만 옮겨도 실행되도록 구성되어야 하며, 운영 시스템은 팀 파일을 수정하지 않습니다.

```bash
cd ~/urrc_f1_ws
source /opt/ros/jazzy/setup.bash

# 참가 폴더 검사 → 공식 접수 동기화 → ROS 패키지 빌드
bash race_v24.sh check
bash race_v24.sh sync
bash race_v24.sh prepare

# team_01의 차량·base_link 등 검수
bash race_v24.sh vehicles --team team_01

# 6개 맵과 팀 토픽·모델 정적 호환성 검사
bash race_v24.sh compatibility --team team_01 --tracks all --require-synced
```

실제 Gazebo·센서·출발·주행 검증은 별도입니다. 단일 팀을 6개 맵에서 확인할 때 다음을 실행합니다.

```bash
bash race_v24.sh compatibility --team team_01 --tracks all --live --seconds 300
```

정적 `PASS`와 실제 주행 `PASS`는 다릅니다. 차량이 없거나 센서가 수신되지 않으면 완주를 인정하지 않습니다. 차량의 `base_link`는 센서를 포함한 차량 외형의 **3차원 기하학적 중심**에 있어야 합니다.

## 3. 예선 → 본선 → 결승 및 순위 확인

운영자 PC에서 진행하며, 참가팀 접수·빌드·검수 후 실행합니다. 경기별 맵은 `refresh-maps`로 배정되며, 필요하면 `show-maps`로 확인합니다.

```bash
cd ~/urrc_f1_ws
bash race_v24.sh refresh-maps   # 새 경기의 맵 배정 (경기 시작 전에만)
bash race_v24.sh show-maps      # 예선·본선A·본선B·결승 맵 확인

bash race_v24.sh qualifying     # 예선: 1대씩 2랩, 최대 12팀
bash race_v24.sh semi_a         # 본선 A: 예선 홀수 순위, 3랩, 최대 6팀
bash race_v24.sh semi_b         # 본선 B: 예선 짝수 순위, 3랩, 최대 6팀
bash race_v24.sh final          # 결승: 본선 결과로 선발, 5랩, 최대 7팀
```

참가팀이 2~3팀이면 본선 A에 전원 출전하며, 본선 B는 자동 생략됩니다. 예선·본선 확정 기록이 없으면 다음 단계로 진행할 수 없습니다. 맵 로딩·차량 카메라 준비 이후 운영자의 `READY` 확인을 요구할 수 있습니다.

**경기 진행 중 실시간 순위(체크포인트 기준, 잠정):** 각 경기를 실행한 터미널은 그대로 두고 **새 터미널**에서 실행합니다.

```bash
cd ~/urrc_f1_ws
bash race_v24.sh monitor qualifying
bash race_v24.sh monitor semi_a
bash race_v24.sh monitor semi_b
bash race_v24.sh monitor final
```

동시에 여러 명령을 실행하는 것이 아니라, 현재 진행 중인 단계의 명령만 선택합니다. `Ctrl+C`는 **순위 모니터 터미널에서만** 누릅니다. 실시간 위치 순위는 공식 확정 기록이 아닙니다.

**경기 종료 후 공식 기록·순위 조회:**

```bash
bash race_v24.sh standings qualifying
bash race_v24.sh standings semi_a
bash race_v24.sh standings semi_b
bash race_v24.sh standings final
bash race_v24.sh standings            # 전체 단계 한 번에 확인
```

공식 결과는 `race/results/<단계>.json`과 `.csv`에 저장됩니다. 미완료·무효·잠정 기록은 확정 순위로 표시하지 않습니다. 기존 TXT 보고서도 사용할 수 있습니다.

```bash
bash race_v24.sh results
cat race/results/summary_txt/summary.txt
cat race/results/summary_txt/final.txt
```

## 4. 맵 업데이트 방법

**① GitHub에서 변경된 맵 파일·운영 코드를 받는 경우:**

```bash
cd ~/urrc_f1_ws
git pull --ff-only origin main
bash verify_integrated_v24.sh
```

**② 기존 6개 맵에서 예선·본선·결승의 경기 맵만 다시 배정하는 경우:**

```bash
cd ~/urrc_f1_ws
bash race_v24.sh refresh-maps
bash race_v24.sh show-maps
```

`refresh-maps`는 **맵 파일을 다운로드하거나 다시 생성하지 않고, 경기 단계별 맵 배정만 변경**합니다. 이미 경기를 시작했거나 공식 결과가 있는 상태에서는 배정을 변경하지 마십시오. 파일을 직접 수정한 PC에서는 `git pull` 전에 변경 사항을 확인해야 합니다.
