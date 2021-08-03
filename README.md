# RealTime-Duxcycler
new Duxcycler System (Real-time PCR)


## Requirements<hr>
Windows 10(x64) 환경에서 개발되었습니다.
- python(64-bit) == 3.8.10 
- requirements packages
    - PyQt6==6.1.1
    - PyQt6-Qt6==6.1.1
    - PyQt6-sip==13.1.0
    - hid==1.0.4
        - Window 환경은 https://github.com/libusb/hidapi/releases 에서 동적 라이브러리(hid.dll) 다운로드 후, "C:\Windows\System32" 경로에 넣어야 정상적으로 작동합니다.
        - 해당 패키지 관련 참고는 https://pypi.org/project/hid/ 에서 해주세요.

## Notice<hr>
- 현재 개발단계 입니다.
- 현재 "C:\mPCR\protocol" 경로에 protocol 파일이 없거나 "C:\mPCR"에 "recent_protocol.txt" 파일이 없는경우 정상적으로 작동하지 않을 수 있습니다. 필요한 경우 butter9709@gmail.com 으로 요청 부탁드립니다.

