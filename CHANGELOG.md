# 📋 Points & Reality 3DGS Controller - Version History & Changelog

Points & Reality 3DGS Pipeline Controller의 릴리즈 내역 및 변경 사항 기록 문서입니다.  
버전 번호는 시맨틱 버저닝(Semantic Versioning) 규칙을 따르며, 모든 수정/패치는 **`0.001` 단위 (`+0.001`)**로 순차 갱신됩니다.

---

## 🚀 Version Details

### 🔹 v2.223 (Current)
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
