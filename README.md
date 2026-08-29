# ✨ Points & Reality 3DGS Pipeline Controller (v2.222)

Points & Reality 3DGS Controller는 비디오 캡처부터 3D 가우시안 스플래팅(3D Gaussian Splatting) 학습, 스플랫 클린업, 그리고 초고속 오프라인 WebGL 뷰어 패키징까지 한 번에 제어할 수 있는 올인원 파이프라인 소프트웨어입니다.

---

## 📂 1. 표준 프로젝트 디렉토리 구조

프로젝트 경로를 설정하면 다음과 같은 정규화된 6단계 파이프라인 폴더가 자동 생성 및 관리됩니다:

```text
[Project_Root]/
├── 00_raw_footage/        # 원본 촬영 비디오 파일 (.mp4, .mov 등)
├── 01_extracted_frames/     # FFmpeg로 추출된 프레임 이미지 시퀀스 (PNG, JPG, EXR)
├── 02_camera_alignment/     # COLMAP / RealityScan 카메라 트래킹 및 정렬 데이터
├── 03_splats_exports/       # Postshot, Lichtfeld 등 AI 트레이너에서 내보낸 3DGS 모델 (.ply, .sog)
├── 04_splats_cleaned/       # SuperSplat 또는 Crop Box로 배경/노이즈가 정리된 스플랫 모델
└── 05_web_build/           # 독립 실행형 100% 오프라인 HTML5 3DGS 웹 뷰어 번들
    ├── index.html          # WebGL 3DGS 뷰어 메인 페이지
    ├── libs/               # 100% 오프라인 내장 JS 라이브러리 (Three.js, GaussianSplats3D)
    └── [model_name].sog/.ply # 초고속 하드링크된 3DGS 모델 데이터
```

---

## 🎛️ 2. 핵심 탭 및 단계별 기능 안내

### 🔹 Tab 1. 캡처 & 인제스트 (`1. Capture & Ingest`)
* **STEP 1. 프로젝트 설정 (Project Setup)**:
  * 작업 디렉토리 지정 시 파이프라인 6대 서브폴더 자동 생성 및 상태 동기화.
  * 탐색 및 새 프로젝트 생성 시 항상 `"Works"` 작업 디렉토리(`D:\Points & Reality\Works`)를 기본 경로로 제공.
* **STEP 2. 비디오 인제스트 & 프레임 추출 (Video Ingest & Extraction)**:
  * 드래그 앤 드롭 및 다중 비디오 지원.
  * `ffprobe` 기반 메타데이터(해상도, FPS, 런타임, 코덱) 자동 분석.
  * 다양한 이미지 포맷 지원 (`PNG`, `JPG 95%`, `OpenEXR 16-bit float`).
  * 3D LUT 컬러 그레이딩(`.cube`) 지원 및 멀티스레드 고속 추출.
* **STEP 3. AI 트레이너 브릿지 (AI Trainer Bridge)**:
  * `Postshot`, `Lichtfeld Studio`, `Nerfstudio`, `Brush` 원클릭 실행 및 데이터 연동.
* **STEP 4. 익스포트 감시 및 자동 파이프라인 (Export Watcher)**:
  * 학습 완료 후 지정 폴더에 생성되는 `.ply`, `.sog` 파일을 실시간 감지하여 클린업 탭으로 자동 전송.

---

### 🔹 Tab 2. 스플랫 클린업 (`2. Splat Cleanup`)
* **입력 모델 관리**: 트레이너에서 생성된 스플랫 파일들을 일괄 로드 및 용량 확인.
* **SuperSplat 클린업 브릿지**: 브라우저 기반 SuperSplat 편집기로 연결하여 불필요한 플로터(Floaters) 제거.
* **배치 크롭 & 필터링**: Postshot/Lichtfeld 크롭 박스 규격에 맞춘 바운딩 박스 정제.

---

### 🔹 Tab 3. WebGL 빌드 (`3. WebGL Build`)
* **STEP 1. WebGL 모델 목록 및 개별 출력 파일명 설정 (인라인 테이블 편집)**:
  * 프로젝트 내 복수 모델(`FordEscape01.ply`, `fordEscape01.sog` 등)을 스캔하여 테이블로 구성.
  * **Build 컬럼 헤더 토글 (`☑️ Build`)**: 별도의 툴바 버튼 없이 헤더 클릭 한 번으로 모든 모델의 빌드 체크박스를 일괄 선택/해제.
  * **가운데 정렬 체크박스**: 시각적 피로도를 낮추고 깔끔한 레이아웃을 유지하며 포커스 점선 박스 제거.
  * **출력 파일명 테이블 직접 편집 (✏️)**: 각 행의 `Output HTML File` 컬럼을 더블클릭하여 `index.html`, `MyCar.html` 등 원하는 이름을 개별 지정 가능.
  * **원클릭 단축 버튼**: `🏷️ 첫 번째 모델을 index.html로 설정` 클릭 시 첫 번째 파일을 대표 `index.html`로 즉시 지정.
  * **행별 `🌐 Preview` 즉시 미리보기**: 특정 모델의 행에서 버튼 클릭 시 해당 모델만 즉시 빌드 및 브라우저 오픈.
* **STEP 2. 선택 모델 초기 카메라 시점 설정 (2단계 직관적 워크플로우)**:
  * Step 1에서 선택한 모델(`Target Model: FordEscape01.ply ➔ index.html`)의 시점을 독립 설정.
  * **`🌐 1. 브라우저에서 시점 맞추기 (Open Viewer to Adjust)`**: 브라우저 뷰어를 바로 띄워 자유롭게 마우스로 앵글을 잡을 수 있음.
  * **`📋 2. 복사한 시점 적용하기 (Paste Copied View)`**: 브라우저에서 복사한 좌표를 1클릭으로 해당 모델 프로필에 영구 저장.
  * **퀵 프리셋 지원**: `🎯 Front View`, `📐 Quarter (3/4)`, `🚗 Side View`, `🚁 Top-Down`.
* **STEP 3. 출력 디렉토리 및 일괄 패키징**:
  * **출력 폴더 지정**: 기본 `05_web_build` 외에 자유롭게 변경 가능.
  * **`⚡ 선택된 모델 WebGL 일괄 빌드`**: 체크된 모든 모델을 각자의 파일명과 카메라 세팅으로 일괄 패키징.
  * **`🌐 로컬 웹 서버 실행 / 중지`**: 포트 충돌 없이 백그라운드 HTTP 서버 토글.

---

## 🛠️ 3. 코드베이스 아키텍처

```text
Points & Reality Pipeline/
├── main.pyw                         # 애플리케이션 진입점 (High DPI 지원)
├── Run_Points_Reality_Pipeline.bat  # 원클릭 백그라운드 GUI 실행 배치 스크립트
├── config.py                        # 앱 버전(APP_VERSION = v2.222), 다크 테마 QSS, 폴더 상수
├── utils.py                         # FFmpeg 추출 스레드, 폴더 감시 스레드
├── CHANGELOG.md                     # 전체 릴리즈 및 버전 히스토리 영구 기록
├── ui/
│   ├── ui_main_master.py            # 메인 윈도우 컨트롤러, 프리셋 관리, 통합 로그
│   ├── ui_components.py            # ModernStepCard, StatusPill, ElideLeftDelegate 커스텀 위젯
│   ├── ui_translations.py          # 한국어(KO) / 영어(EN) 완전 다국어 사전
│   ├── tabs/
│   │   ├── capture_sections/       # Tab 1 세부 섹션 (프로젝트, 인제스트, 런처, 와처)
│   │   ├── tab_cleanup.py          # Tab 2 스플랫 클린업 컨트롤러
│   │   └── tab_webgl.py            # Tab 3 WebGL 빌더 & HTTP 서버 스레드
│   └── templates/
│       ├── supersplat_template.html # SuperSplat 독립 실행 엔진 템플릿 (카메라 동기화 HUD 포함)
│       └── libs/                   # Three.js (0.164.0), GaussianSplats3D (0.4.5) 오프라인 모듈
```

---

## 🛡️ 4. 개발 및 코드 수정 3단계 검증 체크리스트 (Quality Gate)

모든 코드 수정 및 리팩토링 시 다음 3단계 검증 체크리스트를 필수적으로 통과해야 합니다.

### 1️⃣ 누락 검증 (Omission Verification)
> **"수정 전의 기존 코드에 있던 모든 함수와 변수(예: `log_signal`, `init_ui`, 시그널 핸들러, 설정값 등)가 새 코드에 100% 포함되었는가?"**
* 리팩토링이나 UI 컴포넌트 재배치 시, 기존에 작동하던 메서드, 시그널 바인딩, 슬롯, 예외 처리 블록이 누락 없이 보존되었는지 전수 확인.
* 변경된 컴포넌트를 참조하는 다른 모듈(예: 다국어 번역 `update_language`, 메인 컨트롤러 이벤트)의 참조가 깨지지 않았는지 교차 검증.

### 2️⃣ 생명주기(Lifecycle) 검증 (Lifecycle Safety)
> **"초기화 시점(`__init__`)에 발생하는 이벤트(`resizeEvent`, `showEvent` 등)로 인해 아직 생성되지 않은 위젯에 접근하여 발생하는 크래시(`AttributeError`) 방어 코드(`hasattr` 등)를 넣었는가?"**
* UI 위젯 생성 순서에 따른 종속성 문제를 차단.
* 위젯이 완전히 인스턴스화되기 전에 호출될 수 있는 이벤트 핸들러에는 반드시 `hasattr(self, 'widget_name')` 또는 `is not None` 가드를 배치하여 런타임 크래시를 원천 차단.

### 3️⃣ 정공법 검증 (Standard/Official Pattern Verification)
> **"프레임워크(Qt 등)의 렌더링 엔진을 억지로 속이거나 무력화하는 꼼수(Hack, ProxyStyle 덮어쓰기 등)를 사용하지 않고, 공식 API와 순정 속성만으로 해결했는가?"**
* 임시방편의 하드코딩이나 불안정한 오버라이드 대신, 프레임워크가 공식적으로 권장하는 표준 레이아웃(`QHBoxLayout(alignment=Qt.AlignCenter)`), 공식 속성(`setFocusPolicy(Qt.NoFocus)`), 표준 QSS 명세(`outline: none; border: none;`)를 준수.
* OS 간 크로스 플랫폼(Windows, macOS, Linux) 호환성과 High DPI 환경에서도 왜곡 없이 일관된 렌더링을 보장.

---

## 🏷️ 5. 버전업 및 릴리즈 규칙 (Versioning Rules)

Points & Reality 파이프라인은 시맨틱 버저닝(Semantic Versioning)을 준용하며 다음과 같은 규칙으로 버전을 갱신합니다:

* **Major Release (`vX.000` / `+1.000`)**: 
  * 파이프라인의 핵심 아키텍처 전면 개편 또는 하위 호환성이 변경되는 대규모 업그레이드.
* **Minor Release (`v2.X00` / `+0.100`)**: 
  * 새로운 탭 추가, 핵심 엔진(SuperSplat, Houdini, AI Trainer) 연동, 대형 기능군 신규 도입.
* **Patch / Revision (`v2.20X` / `+0.001`)**: 
  * **0.001 단위로 버전업 (`+0.001`)**: UI/UX 레이아웃 개선, 버그 픽스, 컴포넌트 정밀 튜닝, 단축 워크플로우 최적화 등 모든 코드 수정 시 `0.001` 단위로 순차 증가 (예: `v2.200` ➔ `v2.201` ➔ `v2.205` ➔ `v2.206` ➔ `v2.207` ➔ `v2.208` ➔ `v2.209` 등).
* **버전 동기화 원칙 (Version Synchronization)**:
  * 버전 변경 시 [`config.py`](file:///d:/SPLATIAL/Postshot_Pipeline/config.py)의 `APP_VERSION`, [`README.md`](file:///d:/SPLATIAL/Postshot_Pipeline/README.md)의 헤더 타이틀, [`CHANGELOG.md`](file:///d:/SPLATIAL/Postshot_Pipeline/CHANGELOG.md)의 히스토리 내역을 반드시 동시에 일치시켜 갱신.

---

## 📋 6. 버전 및 릴리즈 내역 (Release Information)

* **Current Version**: `v2.231`
* **주요 변경 요약**:
  * **3DGS 트레이너 런처 버튼 재배치 및 'Launch Trainer' 간소화 (`v2.231`)**: `Launch Trainer` 및 `Open Exports` 버튼을 `Target Trainer` 콤보박스 바로 우측으로 이동 배치하여 드롭다운 선택 즉시 1클릭 실행 가능한 동선 최적화 및 텍스트 간소화 완료.
  * **상단 메인 탭바 폰트 잘림 근본적 영구 해결 및 High-DPI 완벽 대응 (`v2.228~v2.229`)**: 네이티브 `QTabBar`를 세그먼트 버튼 그룹(`QButtonGroup` + `QPushButton`)으로 전면 교체하고 가중치를 `font-weight: 600`으로 고정하여 어떤 해상도/배율에서도 폰트 잘림 없는 깨끗한 렌더링 보장.
  * **프로젝트 디렉토리 최근 5개 히스토리 드롭다운 및 스튜디오 저채도 테마 개편 (`v2.225`)**: 작업 폴더 최근 목록 선택 기능 및 눈의 피로를 덜어주는 슬레이트 네이비/세이지 올리브 전문 스튜디오 테마 적용.

> 📄 **전체 세부 릴리즈 히스토리 및 버전별 상세 변경 내역은 [CHANGELOG.md (전체 내역 보기)](./CHANGELOG.md) 파일에서 확인하실 수 있습니다.**
