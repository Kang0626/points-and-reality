# main.pyw
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.ui_main_master import PointsAndRealityController 

if __name__ == "__main__":
    # [v2.130] 4K / High DPI 모니터 스케일링 강제 활성화
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
    app = QApplication(sys.argv)
    
    # 윈도우 인스턴스 생성 및 실행
    window = PointsAndRealityController()
    window.show()
    
    sys.exit(app.exec_())