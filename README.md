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
bash competition.sh qualifying --start-mode signal
bash competition.sh final --laps 5 --start-mode signal
bash competition.sh status
```

`new-event`에서 `--track`을 생략하면 6개 중 하나를 무작위로 선택합니다. 선택한 트랙은 event_state.json에 저장되어 예선과 본선에 동일하게 적용됩니다. 예선과 본선 사이에 new-event를 실행하지 않습니다.

- `prepare`: 표준 참가 폴더로 접수 → 소스 빌드 → 패키지·launch·리소스 검사.
- `qualifying`: 최대 12팀, 한 팀씩 1번 그리드에서 **2랩 고정**. 각 랩과 총시간을 분·초·밀리초로 표시하고 완주 차량을 정지·제거합니다.
- `final`: 같은 이벤트의 예선 순위로 배치. **`--laps 5`~`--laps 10`**으로 선택합니다. 생략 시 event_config.json의 final_laps(기본 10)를 사용합니다. 공통 출발 시각부터 목표 랩 완주까지 계측합니다. 완주 차량은 추가 계측을 막고 정지·제거하여 뒤 차량을 막지 않게 합니다.
- 결과: `race/results/qualifying.json/.csv`, `qualifying_laps.csv`, `final.json/.csv`, `final_laps.csv`. 각 랩타임·총시간·순위·DNF 사유를 저장합니다.
- 실행마다 원본 기록: `race/results/runs/<실행ID>/`의 결과 파일·`timing.jsonl`·`gazebo.log`·`<팀ID>_algorithm.log`. 빌드 로그는 `race/log/`입니다.
- 참가자 0명은 주행을 건너뜁니다. 참가 소스/설정 체크섬이 예선 이후 달라지면 본선을 차단합니다.
- 모든 차량이 완주하거나 DNF 처리되면 결과를 저장하고 Gazebo·bridge·알고리즘을 종료합니다. 터미널 창은 남습니다.

## 출발 방식과 정확도

```bash
# 공통 출발 신호 방식
bash competition.sh qualifying --start-mode signal
bash competition.sh final --laps 5 --start-mode signal

# 각 차량 카메라로 빨간불 소등 감지
bash competition.sh qualifying --start-mode camera
bash competition.sh final --laps 10 --start-mode camera
```

- `signal`: 연결을 미리 확인한 공통 Bool 신호로 출발합니다.
- `camera`: Bool은 주행 허가입니다. 참가 차량이 빨간불 점등을 먼저 확인한 뒤 소등을 감지하여 출발합니다. 영상 인식 코드는 참가자가 구현합니다. 카메라는 출발 신호에만 사용하며 주행 판단은 LiDAR로 합니다.
- 두 방식 모두 월드를 잠시 정지한 동일한 시뮬레이션 시각에 계측 시작·주행 허가·신호등 소등을 처리하고 재개합니다. 카메라 처리·통신·제어 반응 지연도 출발 이후 기록에 포함합니다. 모든 차량의 물리적 움직임이 완전히 같은 순간에 시작한다고 보장하지 않습니다.
- 실제 `base_link`의 월드 좌표를 중앙에서 계측합니다. 모델 원점으로 대체하지 않습니다. 차량 SDF/URDF의 최상위 실제 링크 이름은 `base_link_name`으로 지정합니다(기본 `base_link`). Gazebo 변환 후 그 링크가 없으면 출전 준비에 실패합니다.
- 처음 출발선을 넘는 구간은 접근 구간입니다. 이후 전체 코스를 돌아 선을 통과하면 1랩입니다. **총시간 = 출발→첫 선 통과 시간 + 각 랩타임 합계**입니다.
- 약 10 m 간격의 체크포인트를 순서대로 정방향 통과해야 랩으로 인정합니다. 체크포인트 사이 코스 이탈 판정은 운영자가 영상/로그로 확인합니다.
- Gazebo 포즈 시각으로 선 통과 전후를 선형 보간합니다. 기본 계측 발행은 200 Hz이며, 실제 샘플 간격과 통과 시각 범위를 함께 저장합니다. 50 ms 초과 누락, 시각 역행, 3 m 초과 위치 점프, 계측 중단은 기록을 무효 처리합니다.
- 근접 완주 기록의 계측 시간 범위가 겹치면 공동 잠정 순위와 `rank_provisional`로 표시합니다. 그런 예선 결과로 본선을 자동 시작하지 않습니다. 운영자가 재주행해 확정합니다.
- 밀리초 표시는 실제 밀리초 정확도의 인증이 아닙니다. 대회 PC에서 1대/여러 대 실주행과 성능을 반드시 확인해야 합니다.

저장한 포즈로 동일한 기록이 재현되는지 ROS 없이 확인할 수 있습니다.

```bash
python3 race/scripts/replay_timing.py race/results/runs/<실행ID>
```

## 제출·차량 규격

대회 제출은 이 저장소의 최신 [참가 규격 v2](race/README_KO.md)을 기준으로 합니다.
차량 최대 **0.55 × 0.25 × 0.18 m**, 주행 판단은 LiDAR 전용이며 카메라는 출발 감지에만 허용합니다.
`urrc_2`의 맵/연습 기능은 변경하지 않았습니다. 실제 출전 패키지는 `race_start_mode`와 `base_link_name` 등 이 문서의 대회 계약을 적용해야 합니다.
차량·알고리즘·bridge·어댑터·메시와 설정을 참가 패키지에 모두 포함해야 합니다.

몬자 1번 그리드의 기본 스폰은 `(0.37867, -2.05604, 1.24353, yaw=1.45738)`입니다.
각 맵의 실제 스폰 위치는 `tracks/processed/<맵>.json`에서 자동 읽습니다. `race/event_config.json`에서 트랙 선택 범위·본선 기본 랩 수·제한시간을 설정합니다. 예선은 2랩 고정입니다.

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

자동 회귀검사(ROS 불필요):

```bash
sudo apt install python3-pytest
python3 -m pytest race -q
```

계측 구현 근거: [Gazebo Harmonic PosePublisher](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1PosePublisher.html). 차량별 모델/링크의 같은 시각 변환을 합성합니다. 일반 SceneBroadcaster 포즈를 base_link 계측으로 사용하지 않습니다.
