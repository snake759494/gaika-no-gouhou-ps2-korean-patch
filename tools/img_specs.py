"""이미지별 글자 교체 사양: 번호 → [(box(x0,y0,x1,y1), 한글, 옵션), ...]"""
from retext import chars
S = 'serifeb'
TITLE = dict(font_name='serif', erase='inpaint', bright_thr=95, height=19, fill=(205, 205, 205), outline=(30, 30, 30))
CAMO = dict(font_name='serif', erase='inpaint', bright_thr=95, fill=(165, 165, 165), outline=(40, 40, 40), height=16)
GRAY = dict(font_name='serif', erase='diff', bright_thr=22, fill=(150, 150, 150), outline=(45, 42, 40))
L16 = dict(font_name='serifm', height=16)
L16L = dict(font_name='serifm', height=16, align='left')
SPECS = {
    # 타이틀 메뉴 항목
    206: [((10, 112, 166, 145), '이어서 하기', dict(font_name=S)),
          ((10, 147, 166, 177), '처음부터', dict(font_name=S)),
          ((10, 180, 166, 210), '환경 설정', dict(font_name=S)),
          ((6, 212, 170, 246), '게임 정보 설정', dict(font_name=S))],
    # 전장 명령 메뉴(어두운 줄무늬 배경)
    167: [((18, 32 * k + 1, 192, 32 * k + 31), t, dict(font_name=S, erase='rowmed', bright_thr=60, height=22))
          for k, t in enumerate(['행동 종료', '전장 정보', '군단 일람', '레이더 맵', '데이터 저장', '데이터 로드', '환경 설정', '게임 정보 설정'])],
    # 환경 설정 화면
    155: [((194, 36, 256, 63), '환경', dict(font_name=S, erase='inpaint', bright_thr=100, align='right', height=19)),
          ((0, 72, 66, 100), '설정', dict(font_name=S, erase='inpaint', bright_thr=100, align='left', height=19)),
          ((0, 105, 80, 125), '스테레오', L16), ((0, 125, 80, 145), '모노럴', L16),
          ((80, 105, 256, 125), '음악 볼륨:', L16L), ((80, 125, 256, 145), '효과음 볼륨:', L16L),
          ((80, 145, 176, 165), '음성 출력:', L16L), ((80, 165, 176, 185), '진동 기능:', L16L),
          ((80, 185, 176, 205), '화면 조정', L16L),
          ((0, 186, 40, 206), '있음', L16), ((0, 206, 40, 226), '없음', L16),
          ((112, 226, 256, 246), '초기 상태로 복원', L16)],
    # 게임 정보 설정 화면
    156: [((0, 0, 61, 20), '컬러', L16), ((62, 0, 126, 20), '리얼', L16),
          ((168, 36, 256, 63), '게임 정', dict(font_name=S, erase='inpaint', bright_thr=100, align='right', height=19)),
          ((0, 72, 90, 100), '보 설정', dict(font_name=S, erase='inpaint', bright_thr=100, align='left', height=19)),
          ((0, 105, 200, 125), '병기 행동 종료 확인:', L16L), ((0, 125, 240, 145), '전투 맵 격자 표시:', L16L),
          ((0, 145, 256, 165), '전투 맵 병기 그래픽:', L16L), ((0, 165, 40, 185), '', L16L),
          ((40, 165, 225, 185), '플레이어 공격 시', L16L), ((0, 185, 40, 205), '있음', L16),
          ((40, 185, 225, 205), '플레이어 방어 시', L16L), ((0, 205, 40, 225), '없음', L16),
          ((40, 205, 240, 225), '컴퓨터끼리의', L16L), ((0, 226, 105, 246), '전투 장면', L16L),
          ((105, 226, 256, 246), '초기 상태로 복원', L16)],
    # 공용 UI 조각(예/아니요/다음/뒤로/파괴)
    153: [((0, 64, 25, 89), '파', dict(font_name='serifeb', height=20, fill=(80, 0, 0), outline=(201, 201, 201))),
          ((84, 68, 140, 92), '예', dict(font_name=S, height=17)),
          ((172, 68, 244, 92), '아니요', dict(font_name=S, height=17)),
          ((194, 98, 244, 124), '다음', dict(font_name=S, height=17)),
          ((34, 178, 84, 202), '뒤로', dict(font_name=S, height=17))],
    # PLAYER軍 / ENEMY軍 / 破 아이콘
    154: [((200, 0, 220, 20), '군', dict(font_name='gothic', height=17)),
          ((220, 0, 240, 20), '파', dict(font_name='serifeb', height=19, fill=(80, 0, 0), outline=(201, 201, 201))),
          ((140, 40, 160, 60), '군', dict(font_name='gothic', height=17))],
    # 화면 조정
    157: [((58, 2, 186, 32), '화면 조정', dict(font_name=S, erase='inpaint', bright_thr=100, height=20))] +
         [(b, t, L16L) for b, t in [((64, 104, 256, 123), '방향키 상하좌우로 화면'), ((64, 124, 240, 143), '위치를 조정할 수'),
                                    ((64, 143, 208, 162), '있습니다.'), ((64, 163, 256, 182), '라인 아래쪽의 바가'),
                                    ((64, 183, 240, 202), '보이지 않도록 TV의'), ((64, 203, 256, 222), '밝기를 조정해'),
                                    ((64, 223, 192, 242), '주십시오.')]],
    # 데이터 저장/불러오기 화면
    160: [((0, 0, 62, 22), '시작 현', dict(font_name=S, height=17)),
          ((63, 0, 168, 22), '수행 작전 수', dict(font_name=S, height=17)),
          ((0, 31, 241, 56), '게임 데이터가 없습니다', dict(font_name=S, height=19)),
          ((71, 127, 129, 149), '데이터', dict(font_name=S, height=17)),
          ((160, 172, 256, 200), '게임 데이', dict(font_name=S, erase='inpaint', bright_thr=100, align='right', height=19)),
          ((0, 212, 96, 240), '터 목록', dict(font_name=S, erase='inpaint', bright_thr=100, align='left', height=19))],
    # 작전 개시 타이틀(두 줄로 이어 붙여 표시)
    175: [((0, 0, 256, 91), '작전', dict(align='right', font_name='gothic', erase='key', out_w=3, height=72, tracking=6)),
          ((0, 91, 256, 200), '개시', dict(align='left', font_name='gothic', erase='key', out_w=3, height=72, tracking=6))],
    # 전투 기록 제목
    161: [((28, 6, 152, 34), '전투 기록', dict(font_name=S, erase='inpaint', bright_thr=95, height=19))],
    # 전과 결과 항목
    162: [((10, y, 100, y + 20), t, dict(font_name='serif', erase='rowmed', bright_thr=70, align='left', height=17, fill=(150, 150, 150), outline=(45, 42, 40)))
          for y, t in zip([49, 77, 105, 133, 160], ['아군 손해', '적군 격파', '작전 평가점', '누계 평가점', '계급'])],
    # 병기 상세 능력치 패널(텍스처 경계를 넘어 이어지는 글자는 한 글자씩 교체)
    170: [lambda t: chars(t, [(84, 3, '대'), (104, 3, '공'),
                              (16, 22, '공'), (32, 22, '격'), (48, 22, '력'), (118, 22, '방'), (134, 22, '어'), (150, 22, '력'),
                              (220, 22, '공'), (236, 22, '격'), (252, 22, '력'),
                              (16, 44, '탄'), (32, 44, '수'), (134, 44, '사'), (150, 44, '정'), (220, 44, '탄'), (236, 44, '수'),
                              (32, 101, '대'), (52, 101, '지'), (236, 101, '대'),
                              (-4, 122, '력'), (67, 122, '방'), (83, 122, '어'), (99, 122, '력'),
                              (168, 122, '공'), (184, 122, '격'), (200, 122, '력'),
                              (82, 144, '사'), (98, 144, '정'), (168, 144, '탄'), (184, 144, '수'),
                              (0, 199, '함'), (14, 222, '방'), (30, 222, '어'), (46, 222, '력'), (30, 246, '사'), (46, 246, '정'), (134, 188, '사'), (150, 188, '정')],
                         **GRAY)],
    # 병종 목록(작은 고딕)
    171: [((0, 0, 192, 240), '', dict(erase='key'))] +
         [((x, y, x + 96, y + 20), t, dict(font_name='gothic', erase='key', align='left', height=16, fill=(208, 208, 208), outline=(32, 24, 24)))
          for x, col in ((0, ['전투기', '공격기', '전투헬기', '보병헬기', '수송기', '전차', '장갑차', '정찰차', '자주포', '대공포']),
                         (96, ['대공미사일', '보병전투차', '보병', '전투함', '수송함', '항공모함', '잠수함', '상륙함']))
          for y, t in zip([2, 27, 51, 75, 99, 124, 148, 172, 196, 220], col)],
    # 병종 목록(갈색 명조)
    193: [((0, 0, 192, 240), '', dict(erase='key'))] +
         [((x0, y - 10, x1, y + 10), t, dict(font_name=S, erase='key', height=17, fill=(144, 88, 40), outline=(40, 24, 16)))
          for x0, x1, col in ((10, 90, ['전투기', '공격기', '전투헬기', '보병헬기', '수송기', '전차', '장갑차', '정찰차', '자주포', '대공포']),
                              (100, 192, ['대공미사일', '보병전투차', '보병', '전투함', '수송함', '항공모함', '잠수함', '상륙함']))
          for y, t in zip([12, 37, 61, 85, 110, 133, 158, 182, 207, 230], col)],
    # 일차 표시 / 수송·탑재 병기 / 무장
    172: [((74, 138, 112, 158), '일째', dict(GRAY, height=16)),
          ((4, 164, 76, 186), '수송 병기', dict(GRAY, height=16)),
          ((4, 188, 76, 210), '탑재 병기', dict(GRAY, height=16)),
          ((4, 209, 76, 230), '무장', dict(GRAY, height=16))],
    # 점령 완료 / 내구력 / 작전 기간 / 세력 상황
    173: [((40, 5, 190, 35), '점령 완료', dict(font_name=S, erase='rowmed', bright_thr=75, height=24, tracking=6, fill=(215, 225, 250), outline=(16, 16, 56), out_w=2)),
          ((13, 48, 64, 68), '내구력', dict(font_name='gothic', erase='key', height=16)),
          ((72, 50, 160, 70), '작전 기간', dict(GRAY, align='left', height=17)),
          ((72, 108, 160, 130), '세력 상황', dict(GRAY, align='left', height=17)),
          ((196, 108, 248, 130), '병기 수', dict(GRAY, height=16))],
    # 보급 회복 표시 / 턴 개시 배너
    174: [((0, 0, 44, 19), '일째', dict(font_name='gothic', erase='key', height=15)),
          ((42, 0, 128, 19), '보급 물자', dict(font_name='gothic', erase='key', height=15)),
          ((128, 0, 172, 19), '회복', dict(font_name='gothic', erase='key', height=15)),
          ((121, 90, 252, 120), '군 턴 개시', dict(font_name='gothic', erase='rowmed', bright_thr=60, height=24, align='left')),
          ((111, 154, 252, 184), '군 턴 개시', dict(font_name='gothic', erase='rowmed', bright_thr=60, height=24, align='left')),
          ((119, 218, 252, 248), '군 턴 개시', dict(font_name='gothic', erase='rowmed', bright_thr=60, height=24, align='left'))],
    # 병기 배치
    178: [((28, 4, 152, 32), '병기 배치', TITLE),
          ((97, 129, 143, 148), '배치', dict(font_name='gothic', erase='key', height=15)),
          ((97, 148, 143, 167), '불가', dict(font_name='gothic', erase='key', height=15)),
          ((16, 224, 104, 248), '보급 물자', dict(GRAY, height=16))],
    # 군단 일람표
    179: [((28, 3, 152, 32), '군단 일람표', TITLE),
          ((60, 46, 144, 68), '병기 명칭', CAMO), ((34, 76, 116, 98), '병기 타입', CAMO),
          ((142, 76, 184, 98), '국적', CAMO), ((196, 76, 252, 98), '레벨', CAMO),
          ((10, 108, 54, 130), '상태', CAMO), ((88, 108, 146, 130), '편성 수', CAMO),
          ((22, 138, 78, 158), '공격력', CAMO), ((120, 138, 178, 158), '방어력', CAMO),
          ((28, 172, 84, 194), '이동력', CAMO), ((88, 172, 158, 194), '필요 물자', CAMO),
          lambda t: chars(t, [(228, 141, '연'), (244, 141, '료'), (-12, 175, '료')], **dict(CAMO, height=16))],
    # 전장 정보
    180: [((28, 3, 152, 32), '전장 정보', TITLE),
          ((167, 0, 207, 19), '동맹', dict(font_name='gothic', erase='key', height=15)),
          ((207, 0, 248, 19), '전멸', dict(font_name='gothic', erase='key', height=15)),
          ((167, 21, 209, 41), '까지', dict(font_name='gothic', erase='key', height=15)),
          ((69, 40, 88, 56), '군', dict(font_name='gothic', erase='key', height=14)),
          ((59, 56, 79, 72), '군', dict(font_name='gothic', erase='key', height=14)),
          ((68, 72, 88, 88), '군', dict(font_name='gothic', erase='key', height=14)),
          ((74, 140, 112, 162), '일째', dict(font_name='gothic', erase='key', height=15))],
    # 전투 개시 / 공격 불가능 / 전투 화면 항목
    181: [((192, 3, 254, 32), '전투', dict(TITLE, height=21)),
          ((0, 38, 60, 66), '개시', dict(TITLE, height=21)),
          ((0, 72, 168, 108), '공격 불가능', dict(font_name=S, erase='key', height=28, fill=(168, 32, 32), outline=(40, 16, 16))),
          ((70, 193, 130, 210), '레벨', dict(GRAY, height=15)),
          ((156, 193, 218, 210), '편성 수', dict(GRAY, height=15)),
          ((8, 228, 50, 244), '지형', dict(GRAY, height=15)),
          ((124, 228, 198, 244), '방어 효과', dict(GRAY, height=15))],
    # 재행동(색 변형 8종)
    186: [(b, '재행동', dict(font_name='gothic', erase='key', height=19)) for b in
          [(4, 84, 60, 106), (68, 76, 124, 98), (132, 74, 188, 96), (196, 72, 252, 94),
           (4, 134, 60, 158), (68, 134, 124, 158), (132, 134, 188, 158), (196, 134, 252, 158)]],
    # 군비 메뉴 항목(붓글씨)
    187: [((38, y, 214, y + 28), t, dict(font_name=S, erase='key', align='left', height=21, tracking=3)) for y, t in
          [(5, '진격지 선택'), (87, '병기 구입'), (127, '병기 수리'), (167, '외교 투자'), (207, '병기 매각')]],
    # 화면 제목 판
    190: [((28, 3, 152, 32), '진격지 선택', TITLE)],
    192: [((28, 3, 152, 32), '군단 편성', TITLE)],
    195: [((10, 226, 110, 248), '군자금 총액', dict(GRAY, height=17)), ((28, 3, 152, 32), '병기 구입', TITLE), ((0, 166, 30, 194), '신', dict(font_name='gothic', erase='key', height=20))],
    196: [((10, 226, 110, 248), '군자금 총액', dict(GRAY, height=17)), ((28, 3, 152, 32), '병기 수리', TITLE)],
    197: [((0, 96, 150, 218), '', dict(erase='key'))] +
         [((0, y, 122, y + 20), t, dict(font_name='gothic', erase='key', align='left', height=16, fill=(184, 120, 48), outline=(56, 32, 8)))
          for y, t in zip([97, 117, 137, 156, 176, 195], ['미국 육공군', '미국 해군', '러시아', '독일', '영국', '일본'])] + [((10, 226, 110, 248), '군자금 총액', dict(GRAY, height=17)), ((28, 3, 152, 32), '외교 투자', TITLE)],
    198: [((10, 226, 110, 248), '군자금 총액', dict(GRAY, height=17)), ((28, 3, 152, 32), '병기 매각', TITLE)],
    200: [((28, 3, 152, 32), '병기 상세', TITLE)],
    203: [((28, 3, 152, 32), '시작 현 선택', TITLE)],
    204: [((14, 3, 248, 34), '개시 시 무기 공여국 선택', TITLE)],
    # 편성 가능 병기 없음(두 줄로 이어짐)
    194: [lambda t: chars(t, [(224, 20, '편'), (248, 20, '성'), (-8, 84, '성'), (16, 84, '가'), (40, 84, '능'), (64, 84, '병'),
                              (88, 84, '기'), (112, 84, '없'), (136, 84, '음')], h=21, w=22, **dict(GRAY, height=18))],
    # 적 세력 / 승리 조건
    199: [((4, 2, 70, 28), '적 세력', dict(GRAY, fill=(176, 104, 96), height=19)),
          ((104, 162, 186, 190), '승리 조건', dict(GRAY, fill=(176, 104, 96), height=19))],
    # 계급(큰 붓글씨) + 결과 항목
    202: [((x, y, x + 72, y + 40), t, dict(font_name=S, erase='key', height=32, tracking=2, fill=(120, 64, 24), outline=(32, 32, 24), out_w=2)) for (x, y), t in [
              ((0, 0), '소위'), ((72, 0), '소장'), ((0, 40), '중위'), ((72, 40), '중장'), ((0, 80), '대위'), ((72, 80), '대장'),
              ((0, 120), '소령'), ((72, 120), '원수'), ((0, 158), '중령'), ((0, 198), '대령')]] +
         [((144, 0, 256, 194), '', dict(erase='key'))] +
         [((144, y, 256, y + 23), t, dict(font_name='gothic', erase='key', align='left', height=17, fill=(200, 200, 200), outline=(40, 40, 40))) for y, t in zip(
              [1, 25, 50, 74, 98, 123, 147, 170],
              ['적 병기 격파 수', '아군 병기 손해 수', '획득 군자금', '이번 평가점', '종합 평가점', '최종 계급', '현재 계급', '부대'])],
    # 작전 실패 / 작전 완료(큰 글자는 칸 단위로 이어짐)
    201: [((0, 0, 256, 54), '', dict(erase='key')), ((0, 56, 50, 104), '', dict(erase='key')),
          ((0, 108, 256, 166), '', dict(erase='key')), ((0, 166, 48, 220), '', dict(erase='key')),
          lambda t: chars(t, [(48, 0, '작'), (110, 0, '전'), (172, 0, '실'), (-6, 56, '패')], h=52, w=60, keep_key=False,
                          font_name='serifeb', erase='key', fill=(200, 72, 24), outline=(48, 56, 40), out_w=3, height=44),
          lambda t: chars(t, [(52, 112, '작'), (112, 112, '전'), (170, 112, '완'), (-8, 168, '료')], h=52, w=58, keep_key=False,
                          font_name='serifeb', erase='key', fill=(232, 120, 40), outline=(240, 230, 200), out_w=3, height=44),
          ((96, 56, 254, 104), '작전 실패', dict(font_name='serifm', erase='key', height=38, fill=(200, 90, 30), outline=(110, 40, 16))),
          ((96, 166, 250, 214), '작전 완료', dict(font_name='serifm', erase='key', height=38, fill=(220, 120, 30), outline=(120, 60, 16)))],
    # 난이도 선택(로고는 원본 유지)
    205: [((148, 226, 252, 251), '난이도 선택', dict(font_name='gothic', erase='key', height=18)),
          ((50, 86, 96, 98), '개가의', dict(font_name='pixel', erase='diff', bright_thr=40, height=10, fill=(24, 24, 24), out_w=0)),
          ((34, 216, 82, 226), '호포', dict(font_name='pixel', erase='diff', bright_thr=40, height=10, fill=(24, 24, 24), out_w=0)),
          # 부제 エアランドフォース → 에어랜드 포스 (윗줄 오른쪽 끝 → 아랫줄 왼쪽으로 이어짐)
          ((112, 100, 256, 121), '', dict(erase='diff', bright_thr=45)),
          ((0, 227, 34, 248), '', dict(erase='diff', bright_thr=45)),
          lambda t: chars(t, [(120, 102, '에'), (143, 102, '어'), (166, 102, '랜'), (189, 102, '드'), (228, 102, '포'), (4, 230, '스')],
                          h=17, w=20, font_name='gothic', erase='none', height=15, fill=(20, 20, 20), out_w=0)],
    # 로드/세이브 화면 안내문(배경)
    6: [((150, 56, 490, 80), '로드할 데이터를 선택해 주십시오', dict(GRAY, font_name='serifm', bright_thr=30, height=20, fill=(185, 185, 185)))],
    7: [((150, 56, 490, 80), '세이브할 장소를 선택해 주십시오', dict(GRAY, font_name='serifm', bright_thr=30, height=20, fill=(185, 185, 185)))],
    # 전장 정보 배경
    40: [(b, t, dict(GRAY, font_name='serifm', bright_thr=30, height=h, fill=(175, 175, 175))) for b, t, h in [
            ((290, 68, 372, 90), '작전 기간', 20), ((290, 103, 372, 125), '현재 시각', 20),
            ((92, 141, 170, 164), '승리 조건', 20), ((48, 225, 124, 248), '세력 상황', 20),
            ((142, 236, 222, 255), '거점/도시', 17), ((226, 236, 268, 255), '공항', 17), ((290, 236, 320, 255), '항구', 17),
            ((336, 236, 478, 255), '턴당 보급 물자', 17), ((494, 236, 606, 255), '현재 보급 물자', 17)]],
    # 외교 화면 배경
    54: [(b, t, dict(GRAY, font_name='serifm', bright_thr=30, height=19, fill=(175, 175, 175))) for b, t in [
            ((222, 62, 312, 82), '외교 레벨'), ((478, 62, 590, 82), '다음 레벨까지')]],
    # 병기 상세 배경
    57: [((x0 - 3, y0 - 2, x1 + 3, y1 + 2), t, dict(GRAY, font_name='serifm', bright_thr=30, height=19, fill=(165, 165, 165), align=a))
         for (x0, y0, x1, y1), t, a in [
            ((171, 107, 220, 123), '편성 수', 'center'), ((40, 150, 88, 166), '경험치', 'left'),
            ((202, 151, 248, 166), '레벨', 'center'), ((306, 167, 420, 184), '카테고리 특성', 'left'),
            ((97, 190, 129, 206), '대공', 'center'), ((164, 190, 195, 206), '대지', 'center'), ((230, 190, 261, 206), '대함', 'center'),
            ((40, 211, 73, 226), '공격', 'left'), ((40, 240, 73, 256), '방어', 'left'), ((40, 267, 73, 284), '사정', 'left'),
            ((40, 296, 73, 312), '탄수', 'left'), ((40, 334, 89, 350), '이동력', 'left'), ((40, 361, 73, 377), '연료', 'left'),
            ((40, 389, 150, 405), '필요 보급 물자', 'left'), ((306, 287, 380, 303), '병기 특성', 'left')]],
    # 거점 정보 바 / 하단 항목
    169: [((98, 3, 142, 24), '방어', dict(GRAY, height=17)),
          ((168, 35, 220, 57), '내구력', dict(GRAY, height=17))] +
         [(b, t, dict(font_name='gothic', erase='key', height=15, fill=(200, 200, 200), outline=(32, 32, 32))) for b, t in [
             ((0, 235, 50, 255), '레벨'), ((54, 235, 94, 255), '연료'), ((116, 235, 156, 255), '편성'), ((162, 235, 234, 255), '전과 예측')]],
}

# 튜토리얼 스크린샷: 우하단 '튜토리얼' 표시 + 큰 자막/배너
TUT = ((480, 402, 628, 430), '튜토리얼', dict(font_name='gothic', erase='diff', bright_thr=40, align='right', height=15,
                                            fill=(176, 112, 24), out_w=0))
BAN = dict(font_name='gothic', erase='rowmed', bright_thr=60, height=18, align='left')
TOP = dict(font_name='gothic', erase='diff', bright_thr=40, height=12, fill=(200, 200, 210), out_w=0)
CAP = dict(font_name='gothic', erase='diff', bright_thr=40, height=17, fill=(235, 235, 235), out_w=0)
for _i in range(10, 31):
    SPECS[_i] = [TUT]
SPECS[16] += [((112, 181, 536, 206), '싸움에서 이기기 위한 기초 지식 1', CAP),
              ((318, 129, 450, 155), '군 턴 개시', BAN),
              ((200, 106, 236, 122), '일째', TOP), ((306, 106, 366, 122), '보급 물자', TOP), ((416, 106, 450, 122), '회복', TOP)]
SPECS[27] += [((112, 173, 536, 196), '싸움에서 이기기 위한 기초 지식 2', CAP)]
SPECS[20] += [((318, 125, 450, 152), '군 턴 개시', BAN),
              ((203, 103, 234, 119), '일째', TOP), ((306, 103, 366, 119), '보급 물자', TOP), ((416, 103, 448, 119), '회복', TOP)]

from tut_specs import get as _tut_get
for _k, _v in _tut_get().items(): SPECS[_k] = SPECS.get(_k, []) + _v
