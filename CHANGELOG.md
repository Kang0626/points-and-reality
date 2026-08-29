# 📋 Points & Reality 3DGS Controller - Version History & Changelog

Points & Reality 3DGS Pipeline Controller의 릴리즈 내역 및 변경 사항 기록 문서입니다.  
버전 번호는 시맨틱 버저닝(Semantic Versioning) 규칙을 따르며, 모든 수정/패치는 **`0.001` 단위 (`+0.001`)**로 순차 갱신됩니다.

---

## 🚀 Version Details

### 🔹 v2.248 (Current)
* **웹 쇼룸(showroom.html & index.html) JavaScript ReferenceError 런타임 크래시 핫픽스 및 이벤트 위임 렌더링 엔진 고도화 (`v2.248`) ([`showroom.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/showroom.html), [`index.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/index.html), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **전역 변수 스코프 및 초기화 순서 정상화**: `showroom.html` 시작 시 `applyLanguage()` 호출 과정에서 발생하던 `Uncaught ReferenceError: allLoadedModels is not defined` 오류를 최상단 전역 상태 변수 명시 및 방어 로직으로 완전 해결 (페이지가 `Scanning Deliverables...` 상태 및 검은 화면으로 영구 정지되던 핵심 원인 해소).
  * **표준 이벤트 위임(Event Delegation) 기반 카드 인터랙션 구축**: 취약한 인라인 `onclick='setActiveStage(...)'` 패턴을 제거하고 그리드 레벨의 `data-idx` 기반 이벤트 리스너를 도입하여 안전한 3D 스테이지 로드 보장.
  * **다국어 실시간 전환 및 메타데이터 동기화**: 언어 전환(EN/KO/ZH/MI) 시 모델 개수 라벨(`N Active Models` / `N개 활성 모델`), 카드 그리드, 활성 스테이지 타이틀이 즉각 동기화되도록 라이프사이클 최적화.
  * **UI 고대비 스타일 보강**: `.page-title` 컬러 토큰(`color: var(--text-primary); text-shadow: ...`)을 명시하여 모든 브라우저 및 다크 테마 배경에서 최상의 가독성 확보.

### 🔹 v2.247
* **Tab 3 WebGL 모듈 QDoubleSpinBox 임포트 핫픽스 및 쇼룸/포털 최신 파일 우선 정렬 전수 반영 (`v2.247`) ([`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`dialog_web_publish.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/dialog_web_publish.py), [`index.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/index.html), [`showroom.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/showroom.html), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **PyQt5 QDoubleSpinBox 임포트 추가**: Tab 3 카메라 거리 제약(Min/Max Distance) 위젯에 사용된 `QDoubleSpinBox`가 모듈 상단 `PyQt5.QtWidgets` import 목록에서 누락되어 앱 시작 시 발생하던 `NameError` 런타임 오류 즉시 해결.
  * **쇼룸 배포 다이얼로그 & 웹 포털 정렬 일원화**: `dialog_web_publish.py`의 로컬/클라우드 파일 목록, `index.html` 및 `showroom.html`의 모델 카드 렌더링에 모두 최신 파일 우선(`mtime` 내림차순) 정렬과 최신 배포 뱃지(`⭐ Latest`)를 100% 동기화 적용.
  * **3단계 품질 게이트 전수 통과**: `py_compile` 컴파일, UI 라이프사이클 및 위젯 안전성 검증 완료.

### 🔹 v2.246
* **Tab 3 WebGL 뷰어 지면 하단 회전 방지(Ground Lock) 및 최소/최대 접근 거리 제한 기능 추가 (`v2.246`) ([`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`supersplat_template.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/templates/supersplat_template.html), [`ui_translations.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_translations.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **지면 하단 회전 방지 (`🛡️ Ground Lock`)**: 마우스 드래그 시 카메라가 바닥(지평선) 아래로 파고들거나 밑에서 위를 올려다보는 왜곡을 방지하도록 고도각(Pitch)을 `-89° ~ 0°` (수평 지면)로 안전하게 고정(SuperSplat `pitchRange` 및 GaussianSplats3D `maxPolarAngle = Math.PI / 2` 100% 동시 적용).
  * **최소 접근 거리 제약 (`🔍 Min Distance`, 기본값: `0.8m`)**: 마우스 휠 줌인 시 피사체 내부로 뚫고 들어가지 않도록 최소 궤도 반경을 고정하여 자연스러운 외관 감상 유지(SuperSplat `zoomRange` 및 GaussianSplats3D `minDistance` 동시 적용).
  * **최대 후퇴 거리 제약 (`🔭 Max Distance`, 기본값: `50.0m`)**: 휠 줌아웃 시 피사체가 화면 밖으로 과도하게 멀어지는 것을 차단.
  * **Tab 3 Card 2 UI 2-Tier 정밀 레이아웃 & 다국어 완비**: 좌표/FOV 입력줄 하단에 `Ground Lock` 체크박스와 `Min/Max Distance` 스핀박스를 2열로 배치하고, 모델별 카메라 프로필 저장/로드 및 다국어(KO/EN) 1:1 동기화 완료.

### 🔹 v2.245
* **쇼룸 배포 테이블 최신 파일 우선 정렬 (`v2.245`) ([`tab_showroom.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_showroom.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **Local Package 및 Live Cloud 테이블 정렬 기준 변경**: 기존 알파벳순(`sorted(files)`) → 파일 수정시간 내림차순(`os.path.getmtime`, `reverse=True`)으로 전환하여 가장 최근 빌드/배포 파일이 항상 테이블 최상단에 위치.

### 🔹 v2.244
* **뷰어 HUD 오버레이 4대 개선 — 브랜드 타이틀, 조작 가이드, 어트리뷰션 Fade 동기화, 워터마크 읽기 순서 교정 (`v2.244`) ([`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`supersplat_template.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/templates/supersplat_template.html), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **브랜드/모델 타이틀 중복 해소**: `✨ Points & Reality | {모델파일명}` 형식으로 통일. 기존 `display_title`(Points & Reality 3DGS - ...) 중복 삽입 문제를 `base_name` 직접 참조로 교정.
  * **조작 가이드 시야 방해 최소화**: 배경 투명도를 `0.55`로 낮추고, 초기 `opacity: 0.5` + 호버 시 `0.95` 복원. 4초 비활동 시 자동 페이드아웃 적용.
  * **엔진 어트리뷰션 전체화면 버튼 Fade 동기화**: SuperSplat 뷰어는 `.points-reality-hud` 클래스를 부여하여 `controlsHidden:changed` 이벤트 기반 fade-in/out을 전체화면 버튼과 100% 동기화. PLY 뷰어도 동일한 `showHUD()` 타이머 루프로 통합.
  * **워터마크 읽기 순서 교정 (POINTS&REALITY)**: 타일링 캔버스를 `left: -65%`로 좌측 시프트하고, 가로 폭을 `440vw`로 확장하며, 행당 `<span>` 8개로 증설하여 `-24deg` 회전 시에도 반드시 "POINTS&REALITY" 순서로 가독.

### 🔹 v2.243
* **엔진 어트리뷰션 뱃지 초경량 무반응 순수 텍스트 라벨 전환 및 전체화면 버튼 밀착 수직 중앙 정렬 (`v2.243`) ([`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **초경량 무반응 순수 텍스트 라벨 (`pointer-events: none;`)**: 불필요한 하이퍼링크(`<a>`), 링크 색상 및 호버 반응을 모두 제거하고 마우스 이벤트가 3D 씬으로 바로 통과되도록 처리하여 조작 방해를 원천 차단.
  * **전체화면 버튼 수직 중앙 정렬 (`bottom: 24px; right: 60px; height: 24px;`)**: 전체화면 버튼과 완벽하게 수직 중앙(`y = 36px`)을 일치시키고 4px 여백으로 밀착시켜 조화롭고 완성도 높은 단일 툴바 클러스터 디자인 구현.

### 🔹 v2.242
* **엔진 어트리뷰션 뱃지 전체화면 버튼 좌측 정렬 재배치 및 워터마크 행간-자간 2:1 황금비 최적화 ([`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **전체화면 버튼 좌측 독립 정렬**: 우측 하단 전체화면(`Fullscreen`) 버튼과 겹치지 않도록 전체화면 버튼 바로 좌측 라인에 배치하여 UI 겹침 현상을 원천 해소.
  * **워터마크 행간:자간 2:1 황금비율 적용**: 기존의 과도하게 넓었던 행간을 개편하여, 수평 어간(`word_gap`) 대비 행간(`row_gap = word_gap * 2`)을 정확히 2배로 유지하고 `line-height: 0.95` 및 18행 캔버스 풀 커버리지를 적용하여 세련되고 밀도 높은 컨펌용 워터마크 완성.

### 🔹 v2.241
* **엔진 어트리뷰션 뱃지 우측 하단 초슬림/고투명도(Subtle/High-Transparency) 재배치 ([`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **우측 하단 코너 배치**: 시각적 시야를 가리지 않도록 뱃지 위치를 화면 중앙에서 **우측 하단(`bottom: 16px; right: 16px;`)**으로 이동 배치.
  * **고투명도 및 호버 반응형 UI**: 기본 투명도를 35%(`opacity: 0.35`) 및 초슬림 패딩(`3px 10px`, `font-size: 10px`)으로 극대화하여 3D 씬 감상을 전혀 방해하지 않도록 처리하고, 마우스 호버 시 부드럽게 강조(`opacity: 0.9`)되어 링크 접근성을 동시에 확보.
  * **MIT 라이선스 완벽 준수**: SuperSplat(PlayCanvas & SuperSplat) 및 Three.js(Three.js & GaussianSplats3D) 뷰어 모두에 균형 잡힌 저작권 표기를 적용.

### 🔹 v2.240
* **SuperSplat Orbit 카메라 모드 완전 잠금(Fly 모드 영구 비활성화) ([`supersplat_template.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/templates/supersplat_template.html), [`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **Orbit 카메라 모드 절대 고정 & Fly 모드 영구 차단**: 바운딩 박스 위치 계산, 키보드 축 입력(WASD/방향키), 이벤트 전환 등 모든 경로에서 Fly 모드로 전환되는 동작을 원천 봉쇄하고, `FlyController`를 `OrbitController`로 강제 매핑하여 100% 영구적인 Orbit 조작 환경을 보장.

### 🔹 v2.239
* **SuperSplat 뷰어 Orbit 기본 모드 고정, 디바이스별(마우스/터치) 조작 가이드 자동 감지 및 툴바 간소화 & MIT 라이선스 공식 표기 ([`supersplat_template.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/templates/supersplat_template.html), [`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **기본 궤도(Orbit) 카메라 고정 및 디바이스 자동 감지**: 뷰어 실행 시 Orbit 카메라 모드로 자동 시작되며, 사용자의 디바이스 환경(PC/마우스 vs 모바일/태블릿 터치)을 런타임에 자동 감지하여 상단 조작 안내(`🖱️ Left/Right/Wheel` ↔ `👆 1-Finger/✌️ 2-Finger`)를 동적으로 전환.
  * **하단 우측 툴바 불필요 아이콘 숨김 및 전체화면 버튼만 보존**: 불필요한 Orbit/Fly 전환, Info, Settings 아이콘을 숨기고, 사용자가 가장 필요로 하는 **`⛶ 전체화면(Fullscreen)`** 버튼만 우측 하단에 단독 유지하여 압도적인 시각적 몰입감 제공.
  * **저작권 및 오픈소스 라이선스(MIT) 법적 안전성 확보**: 중앙 하단에 초슬림 글래스모피즘 **`⚡ Powered by PlayCanvas & SuperSplat`** (PLY 뷰어: `Three.js & GaussianSplats3D`) 공식 어트리뷰션 뱃지를 배치하여 MIT 라이선스 준수 및 저작권 분쟁 소지를 완벽하게 예방.

### 🔹 v2.238
* **Cloud Showroom 탭 배포 버튼 텍스트 간소화('▼ 쇼룸으로 업로드') 및 중앙 정렬 배치 ([`tab_showroom.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_showroom.py), [`dialog_web_publish.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/dialog_web_publish.py), [`ui_translations.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_translations.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **버튼 텍스트 간소화 및 직관적 방향 아이콘**: 기존의 길었던 `"🚀 Upload Selected Packages to Vercel"` 문구를 하향 화살표와 간결한 문구인 **`"▼ 쇼룸으로 업로드"`** (영문: `"▼ Upload to Showroom"`)로 개편하여 시각적 전달력 극대화.
  * **하단 중앙 정렬 배치**: 우측 치우침에서 벗어나 상단 로컬 패키지 카드(Card 1)와 하단 클라우드 쇼룸 카드(Card 2)의 정중앙에 배치하여, 로컬 모델이 하단 클라우드 쇼룸으로 내려가는 흐름을 명확히 시각화.

### 🔹 v2.237
* **Client Review Watermark 활성화 시 'Review_' 파일명 접두사 자동 연동 ([`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **워터마크 활성화 시 `Review_` 프리픽스 자동 부여**: `Client Review Watermark` 체크 시 WebGL 모델 목록의 `Output HTML File` 컬럼 및 단일/일괄 빌드 출력 파일명에 자동으로 `'Review_'` 접두사(예: `FordEscape.html` ➔ `Review_FordEscape.html`, `index.html` ➔ `Review_index.html`)가 부여되도록 연동.
  * **체크 해제 시 원복**: 워터마크 체크박스를 해제하면 즉시 원래 파일명으로 안전하게 원복되며, 빌드 시에도 정품 릴리즈 파일명으로 생성.

### 🔹 v2.236
* **Cloud Showroom 탭 상하 카드 위치 스왑 및 액션 버튼(Open/URL) 텍스트 잘림 해결 ([`tab_showroom.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_showroom.py), [`dialog_web_publish.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/dialog_web_publish.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **상하 카드 위치 재배치 (자연스러운 빌드➔배포 워크플로우)**: 상단에 **Card 1: `Local Package Deployment & Selective Upload` (로컬 패키지 배포 및 선택적 업로드)**를 배치하고, 하단에 **Card 2: `Live Cloud Showroom & Vercel Resources` (실시간 클라우드 쇼룸 및 자산 관리)**를 배치하여 빌드 후 배포, 배포 후 라이브 확인으로 이어지는 자연스러운 시각적 흐름 완성.
  * **Actions 컬럼 버튼 잘림 원천 해결**: 행 높이를 `36px`로 확장하고 Actions 컬럼 너비를 `160px Fixed`로 고정하여 `🌐 Open` 및 `📋 URL` 버튼이 어떤 DPI나 창 크기에서도 잘림 없이 깨끗하게 렌더링되도록 최적화.

### 🔹 v2.235
* **Client Review Watermark 글자 크기 및 오퍼시티 조절 컨트롤 도입 & Tab 3 중복 Upload 버튼 정리 ([`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`ui_translations.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_translations.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **워터마크 크기(Size) 및 불투명도(Opacity) 실시간 설정**: 고객 컨펌용 워터마크 입력란 옆에 `Size (40~300 px, 기본: 140px)` 및 `Opacity (1~100 %, 기본: 6%)` 스핀박스 컨트롤을 배치하고, SuperSplat 및 PLY WebGL 뷰어 생성 시 선택한 크기/불투명도가 정밀하게 반영되도록 파이프라인 연동.
  * **Tab 3 액션바 간소화**: 클라우드 쇼룸 기능이 전용 4번째 탭(`Cloud Showroom`)으로 정식 이전됨에 따라, Tab 3 하단 액션바에서 중복되던 `Upload & Cloud Showroom` 버튼을 제거하여 빌드/폴더 열기 중심의 깔끔한 워크플로우로 최적화.

### 🔹 v2.234
* **상단 네비게이션 4번째 전용 탭 'Cloud Showroom' 정식 신설 및 로컬 서버 토글 크래시 버그 완벽 수정 ([`tab_showroom.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_showroom.py), [`ui_main_master.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_main_master.py), [`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`ui_translations.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_translations.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **전용 탭 4 'Cloud Showroom' 신설**: WebGL Build 탭 옆에 4번째 독립 탭(`Cloud Showroom` / `클라우드 쇼룸`)을 신설하여, 실시간 클라우드 배포 현황 확인, 라이브 쇼룸 접속, 선택적 로컬 패키지 배포 및 원격 모델 삭제를 한곳에서 영구 관리.
  * **로컬 서버 토글 버튼 크래시 수정**: `WebGLTab.toggle_preview_server` 실행 시 누락되었던 `_start_server_sync` 메서드를 표준 스레드 생명주기 안전 패턴(`try-except`, `pyqtSignal`)으로 구현하여 "Off" 버튼 클릭 시 앱이 비정상 종료되던 버그를 완전 해결.
  * **3단계 품질 검증 게이트 통과**: 누락 검증, 생명주기 안전성 검증, 정공법 렌더링 검증 완료.

### 🔹 v2.233
* **웹 배포 및 클라우드 쇼룸 관리자 모달(선택적 업로드 & 실시간 웹 뷰어/삭제) 도입 및 로컬 서버 원형 인디케이터 최적화 ([`dialog_web_publish.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/dialog_web_publish.py), [`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`ui_translations.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_translations.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **로컬 서버 제어 버튼 최적화**: 하단 액션바를 차지하던 거대한 `Stop Local Server` 버튼을 제거하고, Card 3 상단 헤더에 작고 세련된 **원형/컴팩트 상태 인디케이터 버튼(`🟢 8080` / `⚪ Off`)**으로 전환하여 공간 활용도 극대화.
  * **선택적 웹 업로드(Selective Upload to Vercel)**: `Upload & Cloud Showroom` 클릭 시 전용 대화상자에서 로컬 `05_web_build`의 파일(HTML, 3DGS 스플랫 모델, 용량, 수정일)을 목록으로 확인하고 원하는 모델만 선별하여 GitHub/Vercel로 안전하게 업로드.
  * **실시간 웹 배포 뷰어 및 클라우드 삭제 관리자**: GitHub/Vercel에 배포된 실시간 모델 목록과 라이브 접속 URL 확인, 원클릭 브라우저 열기, 선택 모델 클라우드 영구 삭제(Purge from Cloud) 및 Git 자동 동기화 기능 구현.

### 🔹 v2.232
* **3단계 검증 체크리스트(Quality Gate) 현재 프로세스 기반 전면 고도화 ([`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py))**:
  * **디스크 실반영 2중 검증 체계화**: 코드 누락 검증 외에도 수정 툴의 덮어쓰기 누락을 방어하기 위한 `view_file`/`git diff` 실반영 확인 절차 명문화.
  * **High-DPI 텍스트 래스터라이징 무왜곡 원칙 수립**: 폰트 가중치(`font-weight: 600`) 일관성 유지 및 앰퍼샌드(`&&`) 이스케이프 강제 규칙 추가.
  * **비동기 스레드 및 디바운스 생명주기 안전성 가이드 강화**: UI 블로킹 방지를 위한 `QThread`/`subprocess.Popen` 비동기 패턴 및 다중 클릭 방지 가드 표준화.

### 🔹 v2.231
* **3DGS 트레이너 런처 버튼 재배치 실반영 및 버튼 텍스트 'Launch Trainer' 간소화 ([`section_launcher.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/capture_sections/section_launcher.py), [`ui_translations.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_translations.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`README.md`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/README.md))**:
  * **트레이너 드롭다운 우측 일렬 액션바 실반영**: `Launch Trainer` 및 `Open Exports` 버튼을 `Target Trainer` 콤보박스 바로 우측(`top_row`)으로 완전히 재배치하고 하단 중복 행을 제거하여 즉시 1클릭 실행 가능한 직관적 UX 구축.
  * **버튼 텍스트 간소화**: 다국어 사전(EN/KO) 및 위젯 텍스트를 직관적인 `Launch Trainer`(트레이너 실행)로 간소화.
  * **3단계 품질 검증 게이트 통과**: 누락 검증(기존 시그널/슬롯/메서드 100% 보존), 생명주기 검증(가드 배치), 정공법 검증(표준 Qt 레이아웃 엔진) 완료.

### 🔹 v2.229
* **선택(Checked) 탭 폰트 가중치(Font-weight) 일치화 및 앰퍼샌드(&) 이스케이프 수정 ([`ui_main_master.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_main_master.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py))**:
  * **선택 시 글자 잘림 완벽 해결**: 활성 탭(`QPushButton:checked`)에서 `font-weight: 700(Bold)`으로 변경될 때 Windows DirectWrite 폰트 래스터라이저가 가로/세로 어드밴스 너비를 초과하여 글자를 뭉개던 현상을 `font-weight: 600` 고정 및 여유 있는 패딩(`padding: 2px 20px;`)으로 수정.
  * **앰퍼샌드(`&`) 단축키 파싱 방지**: `Capture & Ingest`에서 `&`가 Windows 단축키(Mnemonic)로 오인되어 밑줄/누락되던 문제를 `&&` 이스케이프 처리로 완벽 해결.

### 🔹 v2.228
* **메인 상단 네비게이션 탭을 QTabBar에서 세그먼트 버튼 그룹(QButtonGroup + QPushButton)으로 전면 교체하여 폰트 잘림 근본적 영구 해결 ([`ui_main_master.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_main_master.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py))**:
  * **근본 원인 제거**: Windows High-DPI 환경에서 QSS와 충돌하여 텍스트 상하단 및 첫 글자 좌측을 잘라내던 결함 있는 네이티브 `QTabBar` 페인팅 엔진을 완전히 걷어냄.
  * **전문가용 세그먼트 버튼 탭 적용**: 픽셀 정밀도로 텍스트를 수직/수평 정중앙 정렬하는 독점적 `QPushButton` 그룹(`Capture & Ingest`, `Splat Cleanup`, `WebGL Build`)을 구축하여, 어떤 해상도/배율에서도 단 1픽셀의 글자 잘림 없이 시원하고 선명한 텍스트 렌더링 및 또렷한 로열 블루 활성 상태를 완벽하게 보장.

### 🔹 v2.227
* **메인 탭바 폰트 높이/선명도 개선, 전 탭 체크박스 스타일 통일 및 WebGL Preview 버튼 충돌 해결 ([`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`ui_main_master.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_main_master.py), [`section_ingest.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/capture_sections/section_ingest.py), [`tab_cleanup.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_cleanup.py), [`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py))**:
  * **전체 탭바 텍스트 높이(36px / 32px) 확보 및 선명한 로열 블루 컬러 적용**: `self.tab_bar.setMinimumHeight(36)` 및 `QTabBar::tab` 높이 `32px` 고정으로 글자 하단 잘림을 완전히 해소하고, 선택 탭에 선명한 스튜디오 로열 블루(`#1d4ed8`) 적용.
  * **전체 탭 파일선택 체크박스 디자인 100% 통일 및 고시인성 블루 체크 적용**: 탭별로 상이하던 체크박스 인라인 스타일을 전면 제거하고, 전역 QSS 기반 선명한 슬레이트 테두리(`#64748b`) 및 체크 시 선명한 로열 블루(`#2563eb`) + 고대비 화이트 체크마크로 일괄 통일.
  * **WebGL 모델 목록 Preview 버튼 셀 마진/크기 최적화**: Preview 버튼을 전용 컨테이너 셀 위젯(`preview_cell`)에 패딩과 함께 격리 배치하고 높이를 `20~22px`로 최적화하여 인접 행 간의 버튼 침범 및 겹침 현상 완벽 해결.

### 🔹 v2.226
* **전체 UI 텍스트 상하/좌우 잘림(Font Clipping) 전면 수정 및 High-DPI 대응 ([`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`ui_main_master.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_main_master.py), [`ui_components.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_components.py), [`section_project.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/capture_sections/section_project.py))**:
  * **탭바 텍스트 하단 잘림 해결**: `QTabBar::tab`에 명시적 `min-height: 28px;` 및 여유 있는 패딩(`padding: 3px 16px;`)을 적용하여 'g', 'p', 'y' 등 글자 디센더가 잘리던 문제 해결.
  * **프로젝트 디렉토리 콤보박스 텍스트 잘림 해결**: `QComboBox` 및 내부 `QLineEdit`에 `min-height: 28px / 22px` 및 적정 패딩을 부여하여 폰트 상하가 눌리던 현상 완벽 수정.
  * **버튼, 카드 헤더, 테이블 헤더 및 체크박스 여백 최적화**: 전역 `min-height: 28px;` 표준화 및 헤더 텍스트 수직 중앙 정렬(`Qt.AlignVCenter`) 적용.

### 🔹 v2.225
* **프로젝트 디렉토리 최근 목록(최대 5개) 드롭다운 히스토리 및 저채도(Low-Saturation) 스튜디오 룩앤필 적용 ([`section_project.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/capture_sections/section_project.py), [`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`ui_components.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_components.py), [`section_ingest.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/capture_sections/section_ingest.py))**:
  * **최근 프로젝트 디렉토리 히스토리(최대 5개) 드롭다운**: 단일 텍스트 입력창 대신 편집 가능한 콤보박스(`QComboBox`)를 적용하여 최근에 선택 및 생성한 작업 디렉토리를 최대 5개까지 드롭다운으로 표시하고, 1클릭으로 즉시 작업 공간 전환 가능.
  * **저채도(Low-Saturation) 전문 스튜디오 컬러 팔레트 전면 개편**: 고채도/형광 버튼 컬러를 눈의 피로가 적은 차분한 슬레이트 네이비(`#283344`, `#324056`), 세이지 올리브(`#24352c`), 뮤티드 크림슨(`#3a2224`)으로 재조정하여 VFX/3D 스튜디오 수준의 고급스럽고 매트한 룩앤필 구현.
  * **QComboBox 드롭다운 화살표 SVG 정돈**: 윈도우 기본 붉은색 마커/화살표 대신 정갈한 미니멀 슬레이트 그레이 SVG 화살표 적용.

### 🔹 v2.224
* **데스크톱 앱(PyQt5) UI/UX 전면 개편: AI틱한 네온/이모지 배제 및 전문가용 프로덕션 스튜디오 스타일 구축 ([`config.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/config.py), [`ui_translations.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_translations.py), [`ui_main_master.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_main_master.py), [`ui_components.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_components.py))**:
  * **불필요한 이모지 및 장식적 요소 100% 제거**: 버튼, 타이틀, 카드 헤더, 테이블 헤더, 콘솔창 등에 남발되던 이모지(`✨`, `🚀`, `🎬`, `⚡`, `📂`, `💾`, `🗑`, `🎯`, `📐`, `🚗`, `🚁`, `🛡️`, `📟` 등)를 전면 제거하고 직관적이고 정갈한 프로페셔널 텍스트로 정돈.
  * **하이엔드 스튜디오 다크 테마(Pro Studio Neutral Dark QSS)**: 인위적이고 유치한 네온 사이언 테두리와 형광 컬러를 배제하고, Houdini/Nuke/Resolve 스타일의 정밀 슬레이트 차콜 팔레트(`#101216`, `#15181f`, `#232732`, `#2563eb`)로 전면 개편.
  * **헤더, 탭바, 콘솔창 및 카드 컴포넌트 레이아웃 정돈**: 미니멀 브랜드 타이포그래피(`POINTS & REALITY`), 군더더기 없는 프리셋 툴바, 심플한 상태 칩(StatusPill), 접이식 카드(ModernStepCard)로 가독성 극대화.

### 🔹 v2.223
* **05_web_build ➔ 웹 뷰어 실시간 자동 연결 및 Vercel/GitHub 원클릭 클라우드 업로드 파이프라인 구현 ([`tab_webgl.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/tabs/tab_webgl.py), [`ui_translations.py`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/ui/ui_translations.py), [`index.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/index.html))**:
  * **05_web_build ➔ 웹 뷰어 즉시 연결 & 모델 매니페스트(`models.json`) 자동화**: WebGL 패키징 시 `05_web_build/models.json` 매니페스트가 자동 생성/업데이트되며, 메인 웹 쇼케이스 포털([`index.html`](file:///d:/Points%20&%20Reality/Points%20&%20Reality%20Pipeline/index.html))이 실시간 감지하여 3D 모델 갤러리 카드와 "Launch Viewer" 버튼으로 즉시 연결.
  * **원클릭 클라우드 업로드 버튼 (`🚀 Upload to Web (Vercel)`) 추가**: Tab 3 툴바에 전용 업로드 버튼을 추가하여, 클릭 1번으로 `05_web_build` 결과물 동기화 및 GitHub 자동 커밋 & 푸시 실행 (`VercelUploadThread`). Vercel을 통해 전 세계 고객에게 약 15초 내 자동 라이브 배포 완료.
  * **글로벌 스튜디오 영문 기본값 & 4개 국어 실시간 스위처**: English (NZ)를 기본으로 한국어, 中文, Te Reo Māori 언어 즉시 전환 지원.

### 🔹 v2.222
* **정식 비즈니스 브랜드 명칭 "Points & Reality" 전면 일괄 통일 및 디렉토리 개편**:
  * **앱 및 UI 브랜드 통일**: 기존 임시 명칭(SPLATIAL)을 정식 비즈니스 브랜드 명칭인 **Points & Reality**로 전체 코드베이스, 윈도우 타이틀, 최상단 헤더 로고(`✨ Points & Reality`), 번역 사전(`app_title`, `tab3_placeholder_watermark`), 기본 워터마크, WebGL 뷰어 HUD 및 오버레이 헤더까지 완벽하게 통일.
  * **컨트롤러 클래스 및 설정 마이그레이션**: 메인 컨트롤러 클래스명을 `PointsAndRealityController`로 변경하고, `QSettings("PointsAndReality", "3DGSController")` 및 프리셋 저장 경로(`~/.points_and_reality`)로 업그레이드하면서 기존 설정/프리셋 데이터를 자동 승계하도록 하위 호환성 지원.
  * **실행 스크립트 및 디렉토리 갱신**: 신규 런처 스크립트 `Run_Points_Reality_Pipeline.bat` 생성, `houdini_builder.py` 환경변수(`POINTS_REALITY_TARGET_PLY`) 지원, 상위 작업 디렉토리 명칭(`D:\Points & Reality\Points & Reality Pipeline`) 정렬.

### 🔹 v2.221
* **부모 컨테이너 프레임의 하위 스타일 오염 방지(ID 스코핑) 및 롤오버 호버 색상 전환 100% 정상화 ([`section_launcher.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/capture_sections/section_launcher.py), [`section_ingest.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/capture_sections/section_ingest.py), [`tab_cleanup.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_cleanup.py), [`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py), [`config.py`](file:///d:/SPLATIAL/Postshot_Pipeline/config.py))**:
  * **근본 원인 해결 (QFrame 무선택자 전파 차단)**: 부모 `QFrame`(`rc_card`, `trainer_card`, `cam_frame` 등)에 선택자 없이 지정되었던 배경 스타일(`background-color: #141619`)이 하위 자식 버튼들에 전파되어 버튼의 글로벌 호버 색상 변화를 덮어쓰고 있던 문제를 `QFrame#rcCard`, `QFrame#trainerCard` 등 ID 스코핑으로 완벽 격리.
  * **버튼 호버(Hover) 색상 변화 실시간 작동**: 마우스 롤오버 시 `PrimaryBtn`(`🚀 RealityCapture 실행` 등)은 `#0284c7` ➔ `#0ea5e9` (스카이블루), `SuccessBtn`(`🚀 자동 로드 & 트레이너 실행` 등)은 `#059669` ➔ `#10b981` (에메랄드 그린)으로 선명하게 색상이 전환되도록 수정.

### 🔹 v2.220
* **전체 액션 버튼 마우스 롤오버(Hover) 비주얼 이펙트 강화 및 포인팅 커서 일괄 적용 ([`config.py`](file:///d:/SPLATIAL/Postshot_Pipeline/config.py), [`section_launcher.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/capture_sections/section_launcher.py), [`section_ingest.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/capture_sections/section_ingest.py), [`tab_cleanup.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_cleanup.py), [`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py))**:
  * **스타일시트 상속 차단 해제**: 버튼 인스턴스에 직접 적용되어 글로벌 QSS 상속을 가로막던 인라인 `setStyleSheet`을 제거하여 `PrimaryBtn`(스카이블루) 및 `SuccessBtn`(에메랄드그린)의 생동감 넘치는 배경색과 호버 상태가 100% 정상 발현되도록 수정.
  * **다크 테마 롤오버(Hover) 이펙트 업그레이드**:
    * **PrimaryBtn (`RealityCapture 실행`, `프레임 추출`, `WebGL 빌드` 등)**: 일반 `#0284c7` ➔ 롤오버 시 밝은 스카이블루 `#0ea5e9` 및 네온 발광 테두리 `#bae6fd`.
    * **SuccessBtn (`트레이너 실행`, `후디니 클린업`, `웹서버 실행` 등)**: 일반 `#059669` ➔ 롤오버 시 생동감 있는 에메랄드 `#10b981` 및 발광 테두리 `#a7f3d0`.
    * **Standard Buttons (`폴더 열기`, `경로 복사`, `새로고침` 등)**: 롤오버 시 `#2b313e` 배경 및 선명한 `#38bdf8` 하이라이트 테두리.
  * **마우스 손가락 포인팅 커서(`PointingHandCursor`) 일괄 적용**: 툴바 및 모든 액션 버튼에 마우스 오버 시 직관적인 손가락 포인터 피드백 제공.

### 🔹 v2.219
* **UI 전체 불필요한 넘버링 & STEP 배지 완전 제거 및 테이블 수직 헤더(행 번호) 일괄 통일 ([`ui_components.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/ui_components.py), [`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py), [`section_launcher.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/capture_sections/section_launcher.py), [`ui_translations.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/ui_translations.py), [`ui_main_master.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/ui_main_master.py))**:
  * **전체 테이블 수직 헤더(행 번호 열) 일괄 숨김**: WebGL 모델 테이블(`table_models`)에 남아있던 행 번호(1, 2, 3...) 열을 숨김 처리(`verticalHeader().setVisible(False)`)하여 비디오 인제스트(Tab 1), 스플랫 클린업(Tab 2), WebGL 빌드(Tab 3)의 모든 테이블이 동일한 1열 체크박스 그리드로 완벽 통일.
  * **의미 없는 STEP 배지 완전 제거**: 카드 헤더에 일괄 표시되던 파란색 `STEP 1`, `STEP 2`, `STEP 3` 배지를 카드 레이아웃에서 완전히 제거하여 깔끔하고 세련된 미니멀 모던 카드 디자인 구현.
  * **탭 및 버튼 텍스트의 불필요한 번호 접두사 정리**: 상단 탭 바(`캡처 & 인제스트`, `스플랫 클린업`, `WebGL 빌드`) 및 액션 버튼(`1. RealityCapture 실행` ➔ `RealityCapture 실행`, `1. Open Viewer...` ➔ `Open Viewer...` 등)의 번호 접두사를 모두 제거하여 직관적이고 군더더기 없는 UI 완성.

### 🔹 v2.218
* **전체 탭 체크박스 UI 디자인 & 비주얼 스타일 일괄 통일 ([`config.py`](file:///d:/SPLATIAL/Postshot_Pipeline/config.py), [`tab_cleanup.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_cleanup.py), [`section_ingest.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/capture_sections/section_ingest.py), [`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py))**:
  * **글로벌 다크 테마 QCheckBox 스타일 통합**: `DARK_THEME_CSS`에 라운드 코너(`border-radius: 3px`), 다크 베이스(`background-color: #1a1d24`), 테두리 호버(`#38bdf8`), 체크 시 스카이블루 채움(`#0284c7`) 및 선명한 화이트 벡터 SVG 체크 아이콘(`polyline stroke='white'`) 규칙을 앱 전역으로 확장.
  * **Tab 1, Tab 2, Tab 3 테이블 체크박스 100% 동일화**: 비디오 인제스트(Tab 1), 스플랫 클린업(Tab 2), WebGL 빌드(Tab 3)의 모든 테이블에 동일한 현대적 체크박스 렌더링 스타일을 일괄 적용하여 시각적 통일감과 프리미엄 UX 완성.

### 🔹 v2.217
* **스플랫 클린업(Tab 2) 테이블 선택/해제 체크박스 및 선택 삭제/전체 비우기 UI 구현 ([`tab_cleanup.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_cleanup.py), [`ui_translations.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/ui_translations.py))**:
  * **개별 체크박스 열 추가 (`☑️ Clean`)**: 스플랫 목록의 1번째 열에 중앙 정렬된 체크박스 위젯을 배치하여 클린업을 진행할 대상 모델을 개별적으로 선택/해제 가능.
  * **전체 선택/해제 토글 (`☑️ Toggle All`)**: 툴바의 `☑️ Toggle All` 버튼 및 테이블 헤더 클릭을 통해 모든 스플랫 모델의 선택 상태를 1클릭으로 일괄 전환.
  * **선택 삭제 (`🗑 Remove`) & 전체 비우기 (`🧹 Clear All`)**: 테이블에서 선택/체크된 항목들만 깔끔하게 제거하거나 전체 목록을 초기화하는 배치 관리 기능 제공.
  * **동적 상태 알약 연동**: `0 Splats`, `X Splats`, `X/Y Selected` 등 실시간 선택 상태 피드백 표시.

### 🔹 v2.216
* **Tab 1 슬림화(Step 4 제거) 및 스플랫 클린업(Tab 2) 학습 데이터 자동 로드/스캔 파이프라인 구현 ([`tab_cleanup.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_cleanup.py), [`ui_main_master.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/ui_main_master.py), [`section_launcher.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/capture_sections/section_launcher.py))**:
  * **Tab 1 슬림화 (3단계 직관적 구성)**: 실효성이 떨어지던 수동 감시 카드(Step 4: Export Watcher)를 완전히 제거하여 Tab 1을 `Step 1 (프로젝트 설정) ➔ Step 2 (비디오 인제스트 & 프레임 추출) ➔ Step 3 (카메라 정렬 & AI 트레이너 런처)` 3단계로 심플하게 개편.
  * **스플랫 클린업(Tab 2) 자동 스캔 & 로딩 (`scan_exported_splats`)**: 프로젝트 폴더 설정 시 및 탭 전환(`Tab 1 ➔ Tab 2`) 시 `03_splats_exports`에 생성된 `.ply` / `.splat` / `.sog` 모델을 실시간 자동 감지하여 클린업 테이블에 즉시 로드.
  * **Tab 2 `🔄 Scan Folder` 버튼 추가**: 언제든 원클릭으로 최신 훈련 산출물을 재스캔할 수 있도록 툴바에 스캔 버튼 추가 및 `+ Add Splat` 파일 탐색기 기본 경로를 `03_splats_exports`로 자동 리디렉션.
  * **Step 3 트레이너 런처에 `📂 Open 03_splats_exports` 퀵 버튼 추가**: AI 트레이닝 출력 폴더로 즉시 이동할 수 있는 바로가기 제공.

### 🔹 v2.215
* **카메라 시점 프리셋 영구 저장 & 불러오기/기억 기능 구현 ([`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py), [`ui_translations.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/ui_translations.py))**:
  * **커스텀 카메라 프리셋 저장 (`💾 Save View`)**: 브라우저 프리뷰에서 복사한 좌표나 직접 수정한 카메라 위치/타겟/화각을 원하는 이름(예: `⭐ Hero Angle`, `⭐ Close-up Front`)으로 영구 저장.
  * **저장된 시점 드롭다운 (`⭐ Saved Views:`)**: 저장된 카메라 시점들을 콤보박스에서 즉시 선택하여 다른 모델에 1클릭으로 동일하게 적용. 불필요한 프리셋 삭제(`🗑 Del`) 기능 지원.
  * **프로젝트별 모델 카메라 설정 자동 저장 & 복원**: 프로젝트 폴더(`05_web_build/camera_configs.json`)에 모델별 커스텀 시점 및 HTML 파일명 매핑을 자동 저장하여, 앱 재실행 또는 폴더 재스캔 시에도 사용자가 맞춘 시점을 완벽하게 기억/복원.
  * 글로벌 프리셋(`~/.splatial/camera_presets.json`) 연동을 통해 프로젝트 간 재사용 가능.

### 🔹 v2.214
* **퀵 프리셋(Quick Presets) 버튼 활성/선택 비주얼 피드백 동적 연동 ([`section_ingest.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/capture_sections/section_ingest.py), [`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py))**:
  * **비디오 인제스트 프리셋 피드백 구현**: `🎯 Standard`, `⚡ Fast`, `💎 Ultra` 클릭 또는 파라미터(FPS, 포맷, 스케일) 변경 시 현재 적용된 프리셋 버튼에 하이라이트 활성 테두리(`border: 1px solid #0284c7`, `background: #1e3a5f`, `color: #38bdf8`)가 실시간으로 동기화되도록 개선.
  * **마우스 호버(Hover) 인터랙션 추가**: 비활성 프리셋 버튼 호버 시 밝은 색상(`background: #2d323c`) 피드백 제공.
  * **WebGL 카메라 퀵 프리셋 동적 피드백 연동**: Step 2 카메라 시점 프리셋(`정면`, `쿼터`, `측면`, `탑뷰`) 선택 시에도 활성 버튼 하이라이트 실시간 갱신.

### 🔹 v2.213
* **워터마크 스케일 초대형 확장 및 전방위(360°/우측하단 포함) 완벽 풀스크린 커버리지 ([`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py))**:
  * **초대형 타이포그래피 스케일업 (`clamp(120px, 14vw, 220px)`)**: 차량/주요 오브젝트의 전체 측면을 웅장하게 가로지르는 대형 사이즈로 워터마크 크기 추가 확대.
  * **340vw x 340vh 중앙 대칭 캔버스 기반 100% 뷰포트 커버리지**: 화면 정중앙(`top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-24deg);`)을 축으로 12개 행의 엇갈림 타일 패턴을 배치하여 우측 하단 및 네 모서리 전체에 빈틈없이 균일하게 워터마크가 배치되도록 보정.
  * 초밀착 자간(`letter-spacing: -4px`)과 6% 미세 투명도(`opacity: 0.06`) 유지.

### 🔹 v2.212
* **워터마크 스케일 400% 확대, 울트라 블랙 폰트 & 6% 미세 투명도 튜닝 ([`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py))**:
  * **폰트 두께 및 자간 최적화**: 가장 두꺼운 울트라 볼드 폰트 패밀리(`'Arial Black', 'Impact', 'Montserrat'`)와 촘촘한 자간(`letter-spacing: -3px`) 적용.
  * **워터마크 크기 4배 확대**: 기존 대비 4배 이상 커진 초대형 타이포그래피(`clamp(80px, 10vw, 150px)`)로 대각선 영역을 웅장하게 커버.
  * **미세 투명도 6% (`opacity: 0.06`) 적용**: 3DGS 스플랫 오브젝트의 색감과 텍스처를 94% 투명하게 투과시켜 감상 방해를 원천 차단하면서도 고급스러운 보안 워터마크 효과 완성.

### 🔹 v2.211
* **워터마크 가시성 및 렌더링 스타일 전면 개선 ([`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py))**:
  * **검정 그림자/블러 효과 전면 제거**: 3DGS 스플랫 오브젝트를 가리던 어두운 블러(`text-shadow`)를 완전 제거하여 배경과 모델의 세부 디테일이 투명하게 유지되도록 개선.
  * **SPLATIAL 반복 대각선 패턴 오버레이**: 화면 전체에 균일한 간격으로 `SPLATIAL` 텍스트가 대각선으로 은은하게 반복 배열되도록 패턴화 (`_generate_watermark_html`).
  * **순백색 + 투명도 20% (`opacity: 0.20`, `#ffffff`) 고정**: 시각적 방해 없이 3D 뷰어 감상과 저작권 보호/클라이언트 컨펌 목적을 동시에 달성.
  * Step 3 기본 워터마크 문구 디폴트값을 `SPLATIAL`로 최적화.

### 🔹 v2.210
* **프리뷰 vs 최종 빌드 시점 뷰포트 분리 및 카메라 HUD 조건부 렌더링**:
  * **프리뷰 모드 (`🌐 Preview` / `1. Open Viewer to Adjust Camera`)**: 브라우저에서 카메라 좌표를 실시간 추적하고 클립보드에 복사할 수 있는 `#splatial-cam-hud` 활성화.
  * **Step 3 WebGL 최종 빌드 모드 (`⚡ Build Selected Models WebGL`)**: 최종 클라이언트 배포용이므로 카메라 복사 옵션은 완전 비활성화되며, 대신 좌상단에 프리미엄 **`✨ SPLATIAL 3DGS | [모델명]` 브랜드 로고 & 타이틀 헤더**와 우상단 내비게이션 힌트가 깔끔하게 노출.
* **고객 컨펌용 워터마크 (Client Confirmation Watermark) 옵션 신설**:
  * Step 3 카드에 `🛡️ Client Review Watermark (고객 컨펌용 워터마크)` 체크박스 및 문구 입력란(`QLineEdit`) 추가.
  * 체크 후 빌드 시 브라우저 화면 중앙에 반투명 회전 워터마크 오버레이(`CONFIDENTIAL - CLIENT REVIEW ONLY` 등)가 렌더링되어 고객 피드백/컨펌용으로 안전하게 전달 가능.
* **SuperSplat (`.sog`) 및 GaussianSplats3D (`.ply` / `.splat`) 양방향 엔진 동시 지원**:
  * `.sog` 스탠드얼론 템플릿과 `.ply` 오프라인 뷰어 모두 동일한 브랜딩 헤더 및 고객 컨펌용 워터마크 오버레이 로직 적용.

### 🔹 v2.209
* **프로젝트 폴더 기본 경로 "Works" 폴더 고정 ([`section_project.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/capture_sections/section_project.py))**:
  * `📁 Browse...` 및 `+ New Project` 클릭 시 프로젝트 탐색창이 소스코드 폴더 대신 항상 **`"Works"` 작업 폴더(`D:\SPLATIAL\Works`)를 기본 디폴트 경로**로 열리도록 개선.
* **버전 히스토리 독립 분리 (`CHANGELOG.md`)**:
  * `README.md`의 비대화를 방지하고 깔끔한 메인 문서를 유지하기 위해 전체 버전 변경 기록을 별도의 [`CHANGELOG.md`](file:///d:/SPLATIAL/Postshot_Pipeline/CHANGELOG.md)로 분리 관리.

### 🔹 v2.208
* **전체 탭 반응형 스크롤 영역(`QScrollArea`) 래핑 ([`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py), [`tab_cleanup.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_cleanup.py))**:
  * UI 높이/너비 축소 시 모델 목록 및 전체 카드 내용이 잘리지 않도록 WebGL 빌드 탭과 스플랫 클린업 탭에 `QScrollArea(widgetResizable=True)`를 전면 적용.
* **고대비 스크롤바 디자인 및 테이블 스크롤 정책 최적화 ([`config.py`](file:///d:/SPLATIAL/Postshot_Pipeline/config.py))**:
  * 스크롤바 너비를 8px로 확대하고 고대비 핸들 색상(`background: #333842;`, hover 시 `#0284c7`)을 적용하여 가시성 개선.
  * 테이블에 `ScrollBarAsNeeded` 정책을 적용하여 수직/수평 목록 확인 보장.

### 🔹 v2.207
* **최상단 글로벌 헤더 상하 2단(2-Tier) 구조 분리 ([`ui_main_master.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/ui_main_master.py))**:
  * **1단 (상단)**: 브랜드 타이틀(`✨ SPLATIAL 3DGS Pipeline Controller`) 및 유틸리티 컨트롤(프리셋 관리 + 언어 전환).
  * **2단 (하단)**: 파이프라인 3단계 내비게이션 탭(`1. 캡처 & 인제스트`, `2. 스플랫 클린업`, `3. WebGL 빌드`) 전용 독립 행 배치.
  * 창(UI) 너비를 좁혀도 3단계 탭 버튼과 프리셋 UI가 서로 겹치거나 잘리지 않는 반응형 내구성 확보.

### 🔹 v2.206
* **`Toggle All` 기능을 `Build` 헤더 컬럼으로 직관적 일체화 ([`tab_webgl.py`](file:///d:/SPLATIAL/Postshot_Pipeline/ui/tabs/tab_webgl.py))**:
  * 상단 툴바의 중복 버튼을 제거하고, `Build` 컬럼 헤더(`☑️ Build` / `☐ Build`) 클릭 시 전체 모델 일괄 선택/해제 토글 연동.
* **체크박스 완벽한 중앙 정렬 및 포커스 점선 사각형 제거**:
  * 체크박스 컬럼을 `Qt.AlignCenter` 레이아웃 위젯으로 전면 교체.
  * 포커스 점선 박스 제거 (`outline: none; border: none;`, `setFocusPolicy(Qt.NoFocus)`).
* **개발 3단계 검증 체크리스트(누락·생명주기·정공법) 및 버전업 규칙 문서화**.

### 🔹 v2.205
* **테이블 다크 테마 일체화**:
  * 테이블 좌상단 코너의 흰색 바탕 제거 및 완벽한 다크 테마 일체화 (`QTableCornerButton`).
* **다국어 실시간 번역 지원**:
  * WebGL 빌드 탭(Tab 3) 전체 한글/영문(`KO`/`EN`) 다국어 실시간 번역 지원.
* **개별 출력 경로 대화상자 연동**:
  * WebGL 빌드 실행 시 사용자가 저장 위치와 HTML 파일명을 직접 지정할 수 있는 대화상자 연동.

### 🔹 v2.204
* **WebGL 빌드(Tab 3) 네이밍 및 프리뷰 UX 전면 개편**:
  * 모호하고 중복되던 전역 라디오 버튼을 완전 제거하고, 테이블 내에서 각 모델별 출력 파일명(`Output HTML File`)을 인라인으로 직접 더블클릭 편집할 수 있도록 개선.
  * `🏷️ 첫 번째 모델을 index.html로 설정` 단축 버튼 추가.
  * 각 행별 `🌐 Preview` 버튼 및 Step 2의 `🌐 1. 브라우저에서 시점 맞추기` ➔ `📋 2. 복사한 시점 적용하기` 2단계 직관적 카메라 튜닝 워크플로우 확립.

### 🔹 v2.203
* **60 FPS 실시간 카메라 인스펙터 HUD**:
  * 정밀 3D 전방 레이캐스팅 수식 연동 및 뷰어 실시간 동기화.

### 🔹 v2.202
* **멀티파일 / 배치(Batch) WebGL 빌드 큐 시스템 최초 탑재**.

### 🔹 v2.201
* **초기 카메라 시점 완벽 동기화**:
  * 강제 턴테이블 회전 비활성화 및 네이티브 `calcFocusPoint` 연동.
  * `*.sog` 확장자 브라우즈 필터 및 자동 엔진 라우팅 지원.
  * 100% 오프라인 WebGL 라이브러리(`libs/`) 번들링.

### 🔹 v2.200
* **4단계 복합 파이프라인 UI 대개편 (Capture, Ingest, Cleanup, WebGL)**.
