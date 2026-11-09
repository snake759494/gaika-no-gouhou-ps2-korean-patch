# 개가의 호포 에어랜드 포스 (PS2) 비공식 한글패치

PS2 일본판 **凱歌の号砲 エアランドフォース (개가의 호포 에어랜드 포스, SLPM-65260)** 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일(xdelta)은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.

## 적용 방법
1. 아래 해시와 일치하는 **원본 `.iso`** (Redump 형식)를 준비합니다. (CSO·CHD 등으로 변환한 이미지에는 적용할 수 없습니다.)
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\Gaika no Gouhou - Air Land Force (Japan).iso'`
2. xdeltaUI 같은 도구로 원본 `.iso` 에 `GaikaNoGouhou_KO_v1.0.xdelta` 를 적용합니다. (Patch = xdelta, Source File = 원본 ISO, Output File = 새 파일명)
   - 명령줄: `xdelta3 -d -s "Gaika no Gouhou - Air Land Force (Japan).iso" GaikaNoGouhou_KO_v1.0.xdelta "Gaika no Gouhou - Air Land Force (Korean).iso"`
3. 만들어진 `.iso` 를 PCSX2 등 PS2 에뮬레이터나 OPL 등에서 실행합니다.

| 항목 | 값 |
| --- | --- |
| 원본 ISO 크기 | 4,697,489,408 바이트 |
| 원본 ISO MD5 | `2465a03044d434f3a060949b3b5cfeeb` |
| 원본 ISO SHA-256 | `04dd6bc97c4122e172d8cecff8c7a6e17806eca7b3ddabb26506c77406d46be7` |
| xdelta SHA-256 | `5067589f6cec49a8c46a5bd0bfb8ac1b971e1f14155229bd5a33afb9adcc83b0` |
| 결과 ISO 크기 | 4,697,489,408 바이트 |
| 결과 ISO SHA-256 | `063a64e491a8cc1781307c13f18e53a5118cfc54b1aa03a919581eb7b2206c66` |

## 주의
- 원본에서 만든 **상태저장(세이브 스테이트)** 은 불러오지 마세요. 글꼴·데이터 배치가 달라 글자가 깨지거나 멈출 수 있습니다. 메모리 카드 세이브는 그대로 쓸 수 있습니다.
- xdelta는 압축하지 않은 형식(`-0`)입니다(약 35MB, 대부분 동영상 자막 교체분).

## 한글화 내용
- 시나리오·브리핑·튜토리얼·확인창 메시지 등 문자열 2,041개 전수 직접 번역 — 브리핑 창 폭·줄 수에 맞춰 줄 재배치, 대사창은 3줄 단위로 문장이 페이지 중간에 끊기지 않게 정리
- 메뉴·부대·병기·지명 등 실행 파일과 데이터의 고정 길이 문자열 번역
- 그림 글자 64종 — 타이틀 「개가의 / 호포」와 부제 「에어랜드 포스」, 메뉴·화면 제목, 명령 버튼, 튜토리얼 화면 등
- 오프닝·엔딩 동영상의 일본어 자막을 지우고 한글 자막을 원래 스크롤·투명도로 다시 입힘
- 게임 글꼴(22×22)에 한글 2,350자(KS X 1001) 추가
- 글꼴: 본문 나눔스퀘어 네오, 타이틀·제목·자막 서울한강체, 아주 작은 그림 글자 갈무리11

## 그대로 둔 것
- 음성, 「凱歌の号砲」 로고 붓글씨, 영문 표기(AIR LAND FORCE 등), 저작권 표기

## 검증 범위
PCSX2에서 타이틀, 오프닝·엔딩 동영상, 처음부터 시작한 프롤로그와 초반 시나리오·브리핑·튜토리얼, 메뉴 화면을 직접 플레이하며 확인했습니다. 모든 문자열 파일을 전수 검사해 번역 누락과 창 폭·줄 수 넘침이 없음을 확인했습니다. 모든 시나리오를 끝까지 플레이해 확인하지는 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/TRANSLATION_GUIDE.md](docs/TRANSLATION_GUIDE.md) — 번역 지침
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
