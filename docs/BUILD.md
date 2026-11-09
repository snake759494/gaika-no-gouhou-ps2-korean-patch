# 빌드 방법

일본어 원문·번역 대본(`translation/`)과 글꼴 파일은 저장소에 없으므로, 아래는 같은 자료를 갖춘 경우의 절차입니다.

## 준비
- Python 3.11 이상, `pip install pillow numpy opencv-python imageio-ffmpeg`
- 원본 `Gaika no Gouhou - Air Land Force (Japan).iso` (README의 해시와 일치)를 저장소 폴더에 둡니다.
- 글꼴(저장소 폴더): `NanumSquareNeo-dEb.ttf` 등 나눔스퀘어 네오, `SeoulHangangEB/B/M.ttf`, `Galmuri11-Bold.ttf`

## 순서
1. 원본 추출: `python tools/extract.py` → `work/ext/`, `work/arc/`, `translation/src/`
2. 번역: `translation/ko/*.tsv` (`docs/TRANSLATION_GUIDE.md`), 누락 검사 `python tools/check_ko.py`, `python tools/coverage.py`, 줄 넘침 검사 `python tools/linecheck.py`
3. 동영상 자막(선택): `python tools/movsub.py OP`, `python tools/movsub.py ED` → `work/mov/*_ko.PSS`
4. 빌드: `python tools/build.py` → `Gaika no Gouhou - Air Land Force (Korean).iso`
5. 차분 파일: `xdelta3 -e -0 -f -s "Gaika no Gouhou - Air Land Force (Japan).iso" "Gaika no Gouhou - Air Land Force (Korean).iso" GaikaNoGouhou_KO_v1.0.xdelta`

`tools/emu.py`는 PCSX2를 백그라운드로 실행해 입력·스크린샷으로 확인하는 보조 도구입니다.
