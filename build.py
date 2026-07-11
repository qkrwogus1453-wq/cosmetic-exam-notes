#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
맞춤형화장품 조제관리사 — 사용한도 성분 퀴즈 빌더

성분 데이터(INGREDIENTS)를 수정한 뒤 이 파일을 실행하면
index.html이 새로 생성됩니다.

    python3 build.py

문제 생성 방식:
  1) 단일 한도 성분 → "X의 사용한도는?"  (오답은 같은 카테고리 다른 성분의 실제 수치)
  2) 조건부 한도 성분 → "X를 [조건]에 사용할 때 한도는?" (오답은 같은 성분의 다른 조건 수치 + 유사 성분 수치)
  3) 손으로 쓴 부정형/복합형 문제(HANDWRITTEN)
보기 순서는 실행할 때마다 브라우저에서 자동으로 섞입니다.
"""

import json
import random
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# 1. 단일 한도 성분: (카테고리, 성분명, 한도문자열, 비고)
#    한도문자열은 그대로 정답 보기가 됩니다.
# ─────────────────────────────────────────────────────────────
SIMPLE = [
    # ── 보존제 ──
    ("보존제", "글루타랄", "0.1%", "스프레이형 에어로졸 제품에는 사용금지"),
    ("보존제", "데하이드로아세틱애씨드 및 그 염류", "0.6%", "데하이드로아세틱애씨드로서. 스프레이형 에어로졸 사용금지"),
    ("보존제", "4,4-디메칠-1,3-옥사졸리딘(디메칠옥사졸리딘)", "0.05%", "제품의 pH는 6을 넘어야 함"),
    ("보존제", "디브로모헥사미딘 및 그 염류", "0.1%", "디브로모헥사미딘으로서"),
    ("보존제", "디아졸리디닐우레아", "0.5%", ""),
    ("보존제", "이미다졸리디닐우레아", "0.6%", ""),
    ("보존제", "엠디엠하이단토인", "0.2%", ""),
    ("보존제", "다이엠디엠하이단토인", "0.6%", ""),
    ("보존제", "2,4-디클로로벤질알코올", "0.15%", ""),
    ("보존제", "3,4-디클로로벤질알코올", "0.15%", ""),
    ("보존제", "메텐아민(헥사메칠렌테트라민)", "0.15%", ""),
    ("보존제", "무기설파이트 및 하이드로젠설파이트류", "0.2%", "유리 SO₂로서"),
    ("보존제", "벤제토늄클로라이드", "0.1%", "점막에 사용되는 제품에는 사용금지"),
    ("보존제", "벤질헤미포르말", "0.15%", "사용 후 씻어내는 제품에 한함. 기타 제품 사용금지"),
    ("보존제", "보레이트류(소듐보레이트, 테트라보레이트)", "0.76%", "밀납·백납 유화 목적. 밀납·백납 배합량의 1/2 초과 불가"),
    ("보존제", "2-브로모-2-나이트로프로판-1,3-디올(브로노폴)", "0.1%", "아민류·아마이드류 함유 제품에는 사용금지"),
    ("보존제", "브로모클로로펜", "0.1%", ""),
    ("보존제", "비페닐-2-올(o-페닐페놀) 및 그 염류", "0.15%", "페놀로서"),
    ("보존제", "세틸피리디늄클로라이드", "0.08%", ""),
    ("보존제", "소듐이오데이트", "0.1%", "사용 후 씻어내는 제품에 한함"),
    ("보존제", "소듐하이드록시메칠아미노아세테이트", "0.5%", ""),
    ("보존제", "소르빅애씨드 및 그 염류", "0.6%", "소르빅애씨드로서"),
    ("보존제", "알킬이소퀴놀리늄브로마이드", "0.05%", "사용 후 씻어내지 않는 제품에 한함"),
    ("보존제", "알킬(C12~C22)트리메칠암모늄 브로마이드 및 클로라이드", "0.1%", "두발용 제품류를 제외한 화장품"),
    ("보존제", "에칠라우로일알지네이트 하이드로클로라이드", "0.4%", "입술·에어로졸(스프레이) 제품 사용금지"),
    ("보존제", "알킬디아미노에칠글라이신하이드로클로라이드액(30%)", "0.3%", ""),
    ("보존제", "운데실레닉애씨드 및 그 염류", "0.2%", "씻어내는 제품에 산으로서. 기타 제품 사용금지"),
    ("보존제", "이소프로필메칠페놀", "0.1%", ""),
    ("보존제", "쿼터늄-15", "0.2%", "에어로졸(스프레이) 제품에는 사용금지"),
    ("보존제", "클로로부탄올", "0.5%", ""),
    ("보존제", "클로로자이레놀", "0.5%", "점막에 사용되는 제품에는 사용금지"),
    ("보존제", "p-클로로-m-크레솔", "0.04%", ""),
    ("보존제", "클로로펜", "0.05%", ""),
    ("보존제", "클로페네신", "0.3%", ""),
    ("보존제", "테트라브로모-o-크레솔", "0.3%", ""),
    ("보존제", "트리클로카반(트리클로카바닐리드)", "0.2%", "테트라클로로아조벤젠 1ppm 미만 등 불순물 기준 있음"),
    ("보존제", "페녹시에탄올", "1.0%", ""),
    ("보존제", "페녹시아이소프로판올", "1.0%", "사용 후 씻어내는 제품에 한함. 기타 제품 사용금지"),
    ("보존제", "포믹애씨드 및 소듐포메이트", "0.5%", "포믹애씨드로서"),
    ("보존제", "폴리아미노프로필비구아니드", "0.05%", "에어로졸(스프레이) 제품에는 사용금지"),
    ("보존제", "프로피오닉애씨드 및 그 염류", "0.9%", "프로피오닉애씨드로서"),
    ("보존제", "피리딘-2-올 1-옥사이드", "0.5%", ""),
    ("보존제", "헥세티딘", "0.1%", "사용 후 씻어내는 제품에 한함. 기타 제품 사용금지"),
    ("보존제", "헥사미딘 및 그 염류", "0.1%", "헥사미딘으로서"),
    ("보존제", "5-브로모-5-나이트로-1,3-디옥산", "0.1%", "씻어내는 제품에 한함. 아민류·아마이드류 함유 제품 사용금지"),
    ("보존제", "메칠이소치아졸리논", "0.0015%", "씻어내는 제품에 한함. MCI/MI 혼합물과 병행 사용 금지"),
    ("보존제", "메칠클로로이소치아졸리논과 메칠이소치아졸리논 혼합물", "0.0015%", "씻어내는 제품에 3:1 혼합물로서. 기타 제품 사용금지"),

    # ── 자외선 차단 ──
    ("자외선차단", "드로메트리졸트리실록산", "15%", ""),
    ("자외선차단", "드로메트리졸", "1.0%", ""),
    ("자외선차단", "디갈로일트리올레이트", "5%", ""),
    ("자외선차단", "디소듐페닐디벤즈이미다졸테트라설포네이트", "10%", "산으로서"),
    ("자외선차단", "디에칠헥실부타미도트리아존", "10%", ""),
    ("자외선차단", "디에칠아미노하이드록시벤조일헥실벤조에이트", "10%", ""),
    ("자외선차단", "메칠렌비스-벤조트리아졸릴테트라메칠부틸페놀", "10%", ""),
    ("자외선차단", "4-메칠벤질리덴캠퍼", "4%", ""),
    ("자외선차단", "메톡시시네마미도프로필C8-알킬디메칠암모늄토실레이트", "3%", "흡입 노출 제품·니트로사민 함유 제품 사용금지"),
    ("자외선차단", "멘틸안트라니레이트", "5%", ""),
    ("자외선차단", "벤조페논-4", "5%", ""),
    ("자외선차단", "벤조페논-8(디옥시벤존)", "3%", ""),
    ("자외선차단", "부틸메톡시디벤조일메탄", "5%", ""),
    ("자외선차단", "비스-에칠헥실옥시페놀메톡시페닐트리아진", "10%", ""),
    ("자외선차단", "시노세이트", "5%", ""),
    ("자외선차단", "에칠헥실다이메칠파바", "8%", ""),
    ("자외선차단", "에칠헥실메톡시신나메이트", "7.5%", ""),
    ("자외선차단", "에칠헥실살리실레이트", "5%", ""),
    ("자외선차단", "에칠헥실트리아존", "5%", ""),
    ("자외선차단", "이소아밀-p-메톡시신나메이트", "10%", ""),
    ("자외선차단", "폴리실리콘-15", "10%", ""),
    ("자외선차단", "징크옥사이드", "25%", "무기 자외선차단제"),
    ("자외선차단", "티타늄디옥사이드", "25%", "무기 자외선차단제"),
    ("자외선차단", "테레프탈릴리덴디캠퍼설포닉애씨드 및 그 염류", "10%", "산으로서"),
    ("자외선차단", "트리스-비페닐 트리아진", "10%", "에어로졸(펌프스프레이 포함) 사용금지"),
    ("자외선차단", "티에이이-살리실레이트", "12%", ""),
    ("자외선차단", "페닐벤즈이미다졸설포닉애씨드", "4%", ""),
    ("자외선차단", "호모살레이트", "10%", ""),

    # ── 염모제 (전부 산화염모제 기준) ──
    ("염모제", "p-니트로-o-페닐렌디아민", "1.5%", "산화염모제. 기타 제품 사용금지"),
    ("염모제", "2-메칠-5-하이드록시에칠아미노페놀", "0.5%", "산화염모제"),
    ("염모제", "2-아미노-3-하이드록시피리딘", "1.0%", "산화염모제"),
    ("염모제", "4-아미노-m-크레솔", "1.5%", "산화염모제"),
    ("염모제", "5-아미노-o-크레솔", "1.0%", "산화염모제"),
    ("염모제", "m-아미노페놀", "2.0%", "산화염모제"),
    ("염모제", "p-아미노페놀", "0.9%", "산화염모제"),
    ("염모제", "염산 2,4-디아미노페녹시에탄올", "0.5%", "산화염모제"),
    ("염모제", "염산 톨루엔-2,5-디아민", "3.2%", "산화염모제"),
    ("염모제", "염산 p-페닐렌디아민", "3.3%", "산화염모제"),
    ("염모제", "염산 하이드록시프로필비스(N-하이드록시에칠-p-페닐렌디아민)", "0.4%", "산화염모제"),
    ("염모제", "톨루엔-2,5-디아민", "2.0%", "산화염모제"),
    ("염모제", "p-페닐렌디아민", "2.0%", "산화염모제"),
    ("염모제", "N-페닐-p-페닐렌디아민 및 그 염류", "2.0%", "산화염모제. N-페닐-p-페닐렌디아민으로서"),
    ("염모제", "피크라민산", "0.6%", "산화염모제"),
    ("염모제", "황산 p-니트로-o-페닐렌디아민", "2.0%", "산화염모제"),
    ("염모제", "황산 p-메칠아미노페놀", "0.68%", "산화염모제"),
    ("염모제", "황산 5-아미노-o-크레솔", "4.5%", "산화염모제"),
    ("염모제", "황산 m-아미노페놀", "2.0%", "산화염모제"),
    ("염모제", "황산 p-아미노페놀", "1.3%", "산화염모제"),
    ("염모제", "황산 톨루엔-2,5-디아민", "3.6%", "산화염모제"),
    ("염모제", "황산 p-페닐렌디아민", "3.8%", "산화염모제"),
    ("염모제", "황산 N,N-비스(2-하이드록시에칠)-p-페닐렌디아민", "2.9%", "산화염모제"),
    ("염모제", "2,6-디아미노피리딘", "0.15%", "산화염모제"),
    ("염모제", "염산 2,4-디아미노페놀", "0.02%", "산화염모제. 염모제 성분 중 한도가 가장 낮음"),
    ("염모제", "1,5-디하이드록시나프탈렌", "0.5%", "산화염모제"),
    ("염모제", "피크라민산 나트륨", "0.6%", "산화염모제"),
    ("염모제", "황산 1-하이드록시에칠-4,5-디아미노피라졸", "3.0%", "산화염모제"),
    ("염모제", "히드록시벤조모르폴린", "1.0%", "산화염모제"),
    ("염모제", "6-히드록시인돌", "0.5%", "산화염모제"),
    ("염모제", "1-나프톨(α-나프톨)", "2.0%", "산화염모제"),
    ("염모제", "2-메칠레조시놀", "0.5%", "산화염모제"),
    ("염모제", "유산자산", "4.0%", "산화염모제"),
    ("염모제", "염기성 등색 31호", "0.5%", "산화염모제"),
    ("염모제", "염기성 적색 51호", "0.5%", "산화염모제"),
    ("염모제", "염기성 황색 87호", "1.0%", "산화염모제"),
    ("염모제", "인디고페라 엽가루", "25%", "비산화염모제. 기타 제품 사용금지"),
    ("염모제", "황산철수화물", "6%", "비산화염모제. 산화염모제 사용금지"),
    ("염모제", "황산은", "0.4%", "비산화염모제. 산화염모제 사용금지"),
    ("염모제", "헤마테인", "0.1%", "비산화염모제. 산화염모제 사용금지"),

    # ── 기타 성분 ──
    ("기타성분", "감광소(101·201·301·401호 등) 합계량", "0.002%", ""),
    ("기타성분", "건강틴크·칸타리스틴크·고추틴크 합계량", "1%", ""),
    ("기타성분", "글라이옥살", "0.01%", ""),
    ("기타성분", "노녹시놀-9", "17.2%", ""),
    ("기타성분", "α-다마스콘(시스-로즈 케톤-1)", "0.02%", ""),
    ("기타성분", "다이아미노피리미딘옥사이드", "1.5%", "두발용 제품류"),
    ("기타성분", "라우레스-8 / 9 / 10", "2%", "각각"),
    ("기타성분", "로즈 케톤류(3·4·5, 시스-2, 트랜스-1·2·3·5)", "0.02%", "각각"),
    ("기타성분", "3-메칠-2-부텐니트릴", "0.2%", ""),
    ("기타성분", "메칠 2-옥티노에이트(메칠헵틴카보네이트)", "0.01%", "메칠옥티노에이트와 병용 시 합 0.01%"),
    ("기타성분", "메칠옥티노에이트", "0.002%", ""),
    ("기타성분", "p-메칠하이드로신남알데하이드", "0.2%", ""),
    ("기타성분", "메톡시디시클로펜타디엔카르복스알데하이드", "0.5%", ""),
    ("기타성분", "4-tert-부틸디하이드로신남알데하이드", "0.6%", ""),
    ("기타성분", "부틸페닐메칠프로피오날", "0.14%", ""),
    ("기타성분", "1,3-비스(하이드록시메칠)이미다졸리딘-2-치온", "2%", "두발용·손톱용. 에어로졸 사용금지"),
    ("기타성분", "비타민E(토코페롤)", "20%", ""),
    ("기타성분", "사이클로테트라실록세인", "8.7%", ""),
    ("기타성분", "사이클로펜타실록세인", "19.7%", ""),
    ("기타성분", "소듐나이트라이트", "0.2%", "2급·3급 아민류 함유 제품 사용금지"),
    ("기타성분", "소합향나무 발삼오일 및 추출물", "0.6%", ""),
    ("기타성분", "수용성 징크 염류", "1%", "징크로서. 아세테이트·벤젠설포네이트·피리치온 제외"),
    ("기타성분", "실버나이트레이트", "4%", "속눈썹·눈썹 착색용도"),
    ("기타성분", "아밀비닐카르비닐아세테이트", "0.3%", ""),
    ("기타성분", "아밀시클로펜텐원", "0.1%", ""),
    ("기타성분", "아세틸헥사메틸인단", "2%", "사용 후 씻어내지 않는 제품"),
    ("기타성분", "알리에이치피 올리고펩타이드-1(상피세포성장인자)", "0.001%", "사용한도 성분 중 가장 낮은 축"),
    ("기타성분", "알만토인클로로하이드록시알루미늄(알클로사)", "1%", ""),
    ("기타성분", "알킬헵틴카보네이트", "0.002%", "2-알키노익애씨드 에스텔 함유 제품 사용금지"),
    ("기타성분", "알칼리금속의 염소산염", "3%", ""),
    ("기타성분", "암모니아", "6%", ""),
    ("기타성분", "에칠라우로일알지네이트 하이드로클로라이드(샴푸)", "0.8%", "비듬·가려움 완화용 씻어내는 샴푸"),
    ("기타성분", "에탄올·붕사·라우릴황산나트륨(4:1:1) 혼합물", "12%", "외음부세정제"),
    ("기타성분", "오포파낙스", "0.6%", ""),
    ("기타성분", "옥살릭애씨드, 그 에스테르 및 알칼리염류", "5%", "두발용 제품류"),
    ("기타성분", "우레아", "10%", ""),
    ("기타성분", "이소베르가메이트", "0.1%", ""),
    ("기타성분", "이소사이클로제라니움", "0.5%", ""),
    ("기타성분", "징크페놀설포네이트", "2%", "사용 후 씻어내지 않는 제품"),
    ("기타성분", "클로라민T", "0.2%", ""),
    ("기타성분", "톨루엔", "25%", "손톱용 제품류. 기타 제품 사용금지"),
    ("기타성분", "쿠민알데하이드 및 추출물", "0.4%", "사용 후 씻어내지 않는 제품. 쿠민알데하이드로서"),
    ("기타성분", "페닐알데하이드", "0.1%", ""),
    ("기타성분", "페루발삼 추출물·페루발삼·증류물", "0.4%", ""),
    ("기타성분", "풍나무 발삼오일 및 추출물", "0.6%", ""),
    ("기타성분", "프로필리덴프탈라이드", "0.01%", ""),
    ("기타성분", "트랜스-2-헥세날", "0.002%", ""),
    ("기타성분", "2-헥실리덴사이클로펜탄온", "0.06%", ""),
    ("기타성분", "무기설파이트 및 하이드로젠설파이트류(염모제용)", "0.67%", "산화염모제에서 유리 SO₂로서"),
    ("기타성분", "트리클로카반(기능성 유효성분)", "1.5%", "사용 후 씻어내는 제품류"),
]

# ─────────────────────────────────────────────────────────────
# 2. 조건부 한도 성분
#    conditions: [(조건 설명, 한도), ...]  → 조건별로 문제 1개씩 생성
# ─────────────────────────────────────────────────────────────
CONDITIONAL = [
    {"cat": "보존제", "name": "벤질알코올",
     "conditions": [("일반 제품", "1.0%"), ("두발 염색용 제품류에 용제로 사용할 경우", "10%")],
     "note": "용제 목적일 때만 10배 높은 한도가 적용돼요."},

    {"cat": "보존제", "name": "벤조익애씨드, 그 염류 및 에스테르류",
     "conditions": [("일반 제품(산으로서)", "0.5%"), ("벤조익애씨드 및 그 소듐염을 씻어내는 제품에 사용할 경우", "2.5%")],
     "note": "'소듐염 + 씻어내는 제품' 두 조건이 모두 맞아야 2.5%예요."},

    {"cat": "보존제", "name": "벤잘코늄클로라이드, 브로마이드 및 사카리네이트",
     "conditions": [("사용 후 씻어내는 제품", "0.1%"), ("기타 제품", "0.05%")],
     "note": "분사형 제품에 벤잘코늄클로라이드는 사용금지예요."},

    {"cat": "보존제", "name": "클로르헥시딘 및 그 염류",
     "conditions": [("점막에 사용하지 않고 씻어내는 제품", "0.1%"), ("기타 제품", "0.05%"), ("두발용 제품", "0.5%")],
     "note": "3단계로 갈리며 두발용이 가장 높아요."},

    {"cat": "보존제", "name": "아이오도프로피닐부틸카바메이트(IPBC)",
     "conditions": [("사용 후 씻어내는 제품", "0.02%"), ("사용 후 씻어내지 않는 제품", "0.01%"), ("데오도란트에 배합할 경우", "0.0075%")],
     "note": "데오도란트만 별도로 더 낮은 0.0075%예요."},

    {"cat": "보존제", "name": "징크피리치온(보존제 기준)",
     "conditions": [("사용 후 씻어내는 일반 제품", "0.5%"), ("샴푸·린스·탈모기능성화장품", "1.0%")],
     "note": "기타(씻어내지 않는) 제품에는 사용금지예요."},

    {"cat": "보존제", "name": "피록톤올아민",
     "conditions": [("사용 후 씻어내는 제품", "1.0%"), ("기타 제품", "0.5%")],
     "note": ""},

    {"cat": "보존제", "name": "p-하이드록시벤조익애씨드, 그 염류 및 에스테르류",
     "conditions": [("단일성분일 경우(산으로서)", "0.4%"), ("혼합사용의 경우(산으로서)", "0.8%")],
     "note": "단일 : 혼합 = 1 : 2 관계로 기억하면 편해요."},

    {"cat": "보존제", "name": "클림바졸",
     "conditions": [("일반 제품", "0.3%"), ("두발용 제품", "0.5%")],
     "note": ""},

    {"cat": "보존제", "name": "살리실릭애씨드 및 그 염류(보존제 목적)",
     "conditions": [("보존제 목적으로 사용할 경우", "0.5%")],
     "note": "영유아용 또는 만 13세 이하 어린이 대상 제품에는 사용금지(샴푸는 제외). 기능성 유효성분 목적일 땐 인체세정용 2%, 씻어내는 두발용 3%로 완전히 다른 기준이에요."},

    {"cat": "자외선차단", "name": "벤조페논-3(옥시벤존)",
     "conditions": [("일반 제품", "2.4%"), ("얼굴·손·입술에 사용되는 제품", "5%")],
     "note": "노출 부위가 더 좁은 제품에 오히려 더 높은 한도가 붙는 예외 케이스예요."},

    {"cat": "염모제", "name": "5-아미노-6-클로로-o-크레솔",
     "conditions": [("산화염모제", "1.0%"), ("비산화염모제", "0.5%")],
     "note": "산화/비산화 양쪽에 모두 쓸 수 있는 드문 성분이에요."},

    {"cat": "염모제", "name": "레조시놀",
     "conditions": [("산화염모제의 염모성분으로 사용할 경우", "2.0%"), ("기타 제품", "0.1%")],
     "note": "20배 차이가 나므로 반드시 구분해야 해요."},

    {"cat": "염모제", "name": "과붕산나트륨·과붕산나트륨일수화물",
     "conditions": [("염모제(탈염·탈색 포함)에서 과산화수소로서", "7.0%")],
     "note": "과산화수소수·과산화수소 자체는 12.0%로 더 높아요."},

    {"cat": "염모제", "name": "과산화수소수·과산화수소(염모제용)",
     "conditions": [("염모제(탈염·탈색 포함)에서 과산화수소로서", "12.0%")],
     "note": "과붕산나트륨(7.0%)과 헷갈리지 마세요."},

    {"cat": "기타성분", "name": "과산화수소 및 과산화수소 생성물질",
     "conditions": [("두발용 제품류에 과산화수소로서", "3%"), ("손톱경화용 제품에 과산화수소로서", "2%")],
     "note": "염모제(탈염·탈색)에서는 12%까지 허용되는 것과 구분해야 해요."},

    {"cat": "기타성분", "name": "베헨트리모늄 클로라이드",
     "conditions": [("사용 후 씻어내는 두발용·염색용 제품류", "5.0%"), ("사용 후 씻어내지 않는 두발용·염색용 제품류", "3.0%")],
     "note": "세트리모늄·스테아트리모늄 클로라이드(2.5% / 1.0%)와 숫자가 비슷해 혼동하기 쉬워요."},

    {"cat": "기타성분", "name": "세트리모늄 클로라이드·스테아트리모늄 클로라이드",
     "conditions": [("사용 후 씻어내는 두발용·염색용 제품류", "2.5%"), ("사용 후 씻어내지 않는 두발용·염색용 제품류", "1.0%")],
     "note": "베헨트리모늄 클로라이드(5.0% / 3.0%)의 정확히 절반 수준이에요."},

    {"cat": "기타성분", "name": "리튬하이드록사이드",
     "conditions": [("헤어스트레이트너 제품", "4.5%")],
     "note": "제모제에서 pH조정 목적일 땐 최종 제품 pH 12.7 이하 조건이 붙어요. 칼슘하이드록사이드는 7%예요."},

    {"cat": "기타성분", "name": "칼슘하이드록사이드",
     "conditions": [("헤어스트레이트너 제품", "7%")],
     "note": "리튬하이드록사이드(4.5%)와 짝으로 외우세요. 둘 다 제모제 pH조정 시 최종 pH 12.7 이하."},

    {"cat": "기타성분", "name": "치오글라이콜릭애씨드, 그 염류 및 에스테르류",
     "conditions": [("퍼머넌트웨이브용·헤어스트레이트너 제품(일반)", "11%"),
                    ("가온2욕식 헤어스트레이트너 제품", "5%"),
                    ("발열2욕식 퍼머넌트웨이브용 제품", "19%"),
                    ("제모제 제품", "5%"),
                    ("샴푸용 제품", "1%"),
                    ("사용 후 씻어내는 두발용 제품류", "2%")],
     "note": "용도별로 1%~19%까지 폭이 가장 넓은 성분이에요."},

    {"cat": "기타성분", "name": "살리실릭애씨드(기능성 유효성분 목적)",
     "conditions": [("인체 세정용 제품류", "2%"), ("사용 후 씻어내는 두발용 제품류", "3%")],
     "note": "보존제 목적(0.5%)과 완전히 다른 기준이에요."},

    {"cat": "기타성분", "name": "에티드로닉애씨드 및 그 염류",
     "conditions": [("두발용·두발염색용 제품류(산으로서)", "1.5%"), ("인체 세정용 제품류(산으로서)", "0.2%")],
     "note": ""},

    {"cat": "기타성분", "name": "퀴닌 및 그 염류",
     "conditions": [("샴푸(퀴닌염으로서)", "0.5%"), ("헤어로션(퀴닌염으로서)", "0.2%")],
     "note": ""},

    {"cat": "기타성분", "name": "머스크자일렌",
     "conditions": [("향수류로서 향료원액을 8% 초과 함유하는 제품", "1.0%"),
                    ("향료원액을 8% 이하로 함유하는 제품", "0.4%"),
                    ("기타 제품", "0.03%")],
     "note": "머스크케톤(1.4% / 0.56% / 0.042%)과 세트로 비교해서 외우세요."},

    {"cat": "기타성분", "name": "머스크케톤",
     "conditions": [("향수류로서 향료원액을 8% 초과 함유하는 제품", "1.4%"),
                    ("향료원액을 8% 이하로 함유하는 제품", "0.56%"),
                    ("기타 제품", "0.042%")],
     "note": "머스크자일렌(1.0% / 0.4% / 0.03%)보다 모든 구간에서 조금씩 높아요."},

    {"cat": "기타성분", "name": "만수국꽃·만수국아재비꽃 추출물 또는 오일",
     "conditions": [("사용 후 씻어내는 제품", "0.1%"), ("사용 후 씻어내지 않는 제품", "0.01%")],
     "note": "원료 중 알파 터티에닐 함량은 0.35% 이하여야 하고, 자외선차단·태닝 목적 제품에는 사용금지예요."},

    {"cat": "기타성분", "name": "아세틸헥사메틸테트라린",
     "conditions": [("사용 후 씻어내지 않는 일반 제품", "0.1%"),
                    ("하이드로알콜성 제품", "1%"),
                    ("순수향료 제품", "2.5%"),
                    ("방향크림", "0.5%"),
                    ("사용 후 씻어내는 제품", "0.2%")],
     "note": ""},

    {"cat": "기타성분", "name": "트리알킬아민 및 그 염류",
     "conditions": [("사용 후 씻어내지 않는 제품", "2.5%"), ("사용 후 씻어내는 제품류", "0.3%")],
     "note": "기능성화장품 유효성분 목적에 한정돼요."},

    {"cat": "기타성분", "name": "폴리아크릴아마이드류",
     "conditions": [("사용 후 씻어내지 않는 바디화장품(잔류 아크릴아마이드로서)", "0.00001%"),
                    ("기타 제품(잔류 아크릴아마이드로서)", "0.00005%")],
     "note": "화장품 사용한도 중 가장 작은 자릿수예요."},

    {"cat": "기타성분", "name": "포타슘하이드록사이드·소듐하이드록사이드",
     "conditions": [("손톱표피 용해 목적", "5%")],
     "note": "pH 조정 목적이면 최종 제품 pH 11 이하, 제모제에서 pH조정 목적이면 최종 pH 12.7 이하예요."},

    {"cat": "기타성분", "name": "징크피리치온(기능성 목적)",
     "conditions": [("비듬·가려움 완화 씻어내는 제품(샴푸·린스), 탈모증상 완화 화장품", "1.0%")],
     "note": "보존제 목적으로 씻어내는 일반 제품에 쓸 땐 0.5%예요."},

    {"cat": "기타성분", "name": "시스테인, 아세틸시스테인 및 그 염류",
     "conditions": [("퍼머넌트 웨이브용 제품(시스테인으로서)", "3.0~7.5%"),
                    ("가온2욕식 퍼머넌트웨이브용 제품(시스테인으로서)", "1.5~5.5%"),
                    ("속눈썹·눈썹 착색용도의 제품", "4%")],
     "note": "안정제로 치오글라이콜릭애씨드 1.0%를 배합할 수 있으나, 주성분 시스테인의 양은 6.5%를 초과할 수 없어요."},
]

# ─────────────────────────────────────────────────────────────
# 3. 손으로 쓴 부정형·복합형 문제
# ─────────────────────────────────────────────────────────────
HANDWRITTEN = [
    {"cat": "보존제", "type": "부정형",
     "q": "다음 중 사용한도가 <b>잘못</b> 연결된 것은?",
     "opts": ["페녹시에탄올 — 1.0%", "클로페네신 — 0.3%", "세틸피리디늄클로라이드 — 0.8%", "p-클로로-m-크레솔 — 0.04%"],
     "answer": 2,
     "explain": "세틸피리디늄클로라이드는 <b>0.08%</b>예요. 0.8%가 아닙니다. 소수점 자리를 바꿔 놓는 것이 대표적인 함정 유형이에요.",
     "compare": [["세틸피리디늄클로라이드", "0.08%"], ["페녹시에탄올", "1.0%"], ["클로페네신", "0.3%"], ["p-클로로-m-크레솔", "0.04%"]]},

    {"cat": "보존제", "type": "부정형",
     "q": "다음 중 <b>스프레이형 에어로졸 제품에 사용할 수 있는</b> 보존제는?",
     "opts": ["글루타랄", "데하이드로아세틱애씨드", "쿼터늄-15", "클로로부탄올"],
     "answer": 3,
     "explain": "글루타랄·데하이드로아세틱애씨드·쿼터늄-15·폴리아미노프로필비구아니드는 모두 에어로졸(스프레이) 사용금지예요. 클로로부탄올(0.5%)에는 그런 제한이 없습니다.",
     "compare": [["글루타랄", "0.1% · 에어로졸 금지"], ["데하이드로아세틱애씨드", "0.6% · 에어로졸 금지"], ["쿼터늄-15", "0.2% · 에어로졸 금지"], ["클로로부탄올", "0.5% · 제한 없음"]]},

    {"cat": "보존제", "type": "복합",
     "q": "메칠이소치아졸리논(MIT)과 MCI/MI 혼합물에 대한 설명으로 옳은 것은?",
     "opts": ["둘 다 씻어내는 제품에 0.0015%까지 허용되나, 병행 사용은 금지된다",
              "둘 다 모든 제품에 0.0015%까지 허용된다",
              "MIT는 0.0015%, MCI/MI 혼합물은 0.01%까지 허용된다",
              "MCI/MI 혼합물의 혼합비는 1:3이다"],
     "answer": 0,
     "explain": "둘 다 씻어내는 제품에 0.0015%가 한도이고, 기타 제품에는 사용금지예요. 혼합비는 MCI:MI = <b>3:1</b>이며, MIT 단독과 혼합물의 <b>병행 사용은 금지</b>됩니다.",
     "compare": [["MIT 단독", "씻어내는 제품 0.0015%"], ["MCI/MI 혼합물(3:1)", "씻어내는 제품 0.0015%"], ["병행 사용", "금지"]]},

    {"cat": "보존제", "type": "복합",
     "q": "IPBC(아이오도프로피닐부틸카바메이트)의 사용금지 대상이 <b>아닌</b> 제품은?",
     "opts": ["입술에 사용되는 제품", "바디로션 및 바디크림", "에어로졸(스프레이) 제품", "샤워젤류"],
     "answer": 3,
     "explain": "IPBC는 입술 제품·에어로졸(스프레이)·바디로션/바디크림에 사용금지예요. 영유아·만 13세 이하 대상 제품도 금지지만 <b>목욕용제품류·샤워젤류·샴푸류는 예외</b>입니다.",
     "compare": [["씻어내는 제품", "0.02%"], ["안 씻어내는 제품", "0.01%"], ["데오도란트", "0.0075%"], ["예외 허용", "목욕용·샤워젤·샴푸"]]},

    {"cat": "보존제", "type": "복합",
     "q": "영유아용 제품류 또는 만 13세 이하 어린이 대상 제품에 사용이 금지되지만, <b>샴푸는 예외</b>로 허용되는 성분은?",
     "opts": ["살리실릭애씨드 및 그 염류", "페녹시에탄올", "벤질알코올", "클로페네신"],
     "answer": 0,
     "explain": "살리실릭애씨드는 영유아·13세 이하 대상 제품 금지지만 샴푸는 예외예요. IPBC도 비슷한 구조지만 예외 범위가 '목욕용제품류·샤워젤류·샴푸류'로 더 넓다는 점이 다릅니다.",
     "compare": [["살리실릭애씨드", "예외: 샴푸"], ["IPBC", "예외: 목욕용·샤워젤·샴푸"]]},

    {"cat": "자외선차단", "type": "부정형",
     "q": "다음 중 사용한도가 <b>잘못</b> 연결된 것은?",
     "opts": ["징크옥사이드 — 25%", "에칠헥실메톡시신나메이트 — 7.5%", "드로메트리졸 — 15%", "호모살레이트 — 10%"],
     "answer": 2,
     "explain": "드로메트리졸은 <b>1.0%</b>예요. 15%는 <b>드로메트리졸트리실록산</b>의 한도입니다. 이름이 비슷한 두 성분을 바꿔치기하는 것이 대표적인 함정이에요.",
     "compare": [["드로메트리졸", "1.0%"], ["드로메트리졸트리실록산", "15%"], ["징크옥사이드", "25%"], ["호모살레이트", "10%"]]},

    {"cat": "자외선차단", "type": "복합",
     "q": "자외선 차단 성분에 관한 설명으로 옳지 <b>않은</b> 것은?",
     "opts": ["징크옥사이드와 티타늄디옥사이드는 무기 차단제로 한도가 각각 25%다",
              "벤조페논-3은 얼굴·손·입술 제품에 5%까지 허용된다",
              "변색방지 목적으로 사용농도가 0.5% 미만이면 자외선 차단 제품으로 인정하지 않는다",
              "트리스-비페닐 트리아진은 펌프스프레이 형태라면 에어로졸 제품에도 사용할 수 있다"],
     "answer": 3,
     "explain": "트리스-비페닐 트리아진은 <b>펌프스프레이를 포함해</b> 에어로졸 제품에 전면 사용금지예요. 나머지 셋은 모두 맞는 설명입니다.",
     "compare": [["트리스-비페닐 트리아진", "10% · 에어로졸(펌프스프레이 포함) 금지"], ["나노입자 조건", "입도 중앙값 80nm 초과, 순도 98% 이상"]]},

    {"cat": "자외선차단", "type": "복합",
     "q": "다음 자외선 차단 성분 중 사용한도가 <b>가장 낮은</b> 것은?",
     "opts": ["드로메트리졸", "메톡시시네마미도프로필C8-알킬디메칠암모늄토실레이트", "벤조페논-8", "4-메칠벤질리덴캠퍼"],
     "answer": 0,
     "explain": "드로메트리졸이 1.0%로 가장 낮아요. 메톡시시네마미도프로필...은 3%, 벤조페논-8은 3%, 4-메칠벤질리덴캠퍼는 4%입니다.",
     "compare": [["드로메트리졸", "1.0%"], ["벤조페논-3(일반)", "2.4%"], ["벤조페논-8", "3%"], ["메톡시시네마미도프로필...", "3%"], ["4-메칠벤질리덴캠퍼", "4%"]]},

    {"cat": "염모제", "type": "복합",
     "q": "톨루엔-2,5-디아민 계열의 산화염모제 한도를 <b>낮은 것부터</b> 바르게 나열한 것은?",
     "opts": ["톨루엔-2,5-디아민 < 염산염 < 황산염",
              "염산염 < 톨루엔-2,5-디아민 < 황산염",
              "황산염 < 염산염 < 톨루엔-2,5-디아민",
              "톨루엔-2,5-디아민 < 황산염 < 염산염"],
     "answer": 0,
     "explain": "순수형 2.0% → 염산염 3.2% → 황산염 3.6% 순이에요. p-페닐렌디아민 계열(2.0 → 3.3 → 3.8)도 같은 순서를 따릅니다.",
     "compare": [["톨루엔-2,5-디아민", "2.0%"], ["염산 톨루엔-2,5-디아민", "3.2%"], ["황산 톨루엔-2,5-디아민", "3.6%"]]},

    {"cat": "염모제", "type": "부정형",
     "q": "다음 중 산화염모제 한도가 <b>잘못</b> 연결된 것은?",
     "opts": ["p-페닐렌디아민 — 2.0%", "황산 p-페닐렌디아민 — 3.8%", "염산 p-페닐렌디아민 — 2.0%", "p-아미노페놀 — 0.9%"],
     "answer": 2,
     "explain": "염산 p-페닐렌디아민은 <b>3.3%</b>예요. 2.0%는 순수형 p-페닐렌디아민의 한도입니다.",
     "compare": [["p-페닐렌디아민", "2.0%"], ["염산 p-페닐렌디아민", "3.3%"], ["황산 p-페닐렌디아민", "3.8%"], ["p-아미노페놀", "0.9%"]]},

    {"cat": "염모제", "type": "복합",
     "q": "다음 중 <b>비산화염모제</b>에 사용하는 성분끼리 바르게 묶인 것은?",
     "opts": ["인디고페라 엽가루, 황산철수화물, 황산은, 헤마테인",
              "p-페닐렌디아민, 레조시놀, 1-나프톨",
              "과산화수소수, 과붕산나트륨, 과황산나트륨",
              "톨루엔-2,5-디아민, 피크라민산, 2,6-디아미노피리딘"],
     "answer": 0,
     "explain": "인디고페라 엽가루(25%), 황산철수화물(6%), 황산은(0.4%), 헤마테인(0.1%)은 모두 <b>비산화염모제</b>용이며 산화염모제에는 사용금지예요.",
     "compare": [["인디고페라 엽가루", "비산화 25%"], ["황산철수화물", "비산화 6%"], ["황산은", "비산화 0.4%"], ["헤마테인", "비산화 0.1%"]]},

    {"cat": "염모제", "type": "복합",
     "q": "염모제(탈염·탈색 포함)에서 <b>산화보조제</b>로 사용되는 성분은?",
     "opts": ["과산화수소수", "과붕산나트륨", "과황산나트륨·과황산암모늄·과황산칼륨", "황산철수화물"],
     "answer": 2,
     "explain": "과황산나트륨·과황산암모늄·과황산칼륨은 별도 농도상한 없이 <b>산화보조제</b> 용도로 규정돼 있어요. 과산화수소수(12.0%)와 과붕산나트륨(7.0%)은 산화제 본체입니다.",
     "compare": [["과붕산나트륨", "과산화수소로서 7.0%"], ["과산화수소수", "과산화수소로서 12.0%"], ["과황산염류", "산화보조제 (한도 미설정)"]]},

    {"cat": "염모제", "type": "복합",
     "q": "다음 염모제 성분 중 산화염모제 한도가 <b>가장 높은</b> 것은?",
     "opts": ["황산 5-아미노-o-크레솔", "황산 p-페닐렌디아민", "유산자산", "황산 톨루엔-2,5-디아민"],
     "answer": 0,
     "explain": "황산 5-아미노-o-크레솔이 4.5%로 가장 높아요. 유산자산 4.0%, 황산 p-페닐렌디아민 3.8%, 황산 톨루엔-2,5-디아민 3.6% 순입니다.",
     "compare": [["황산 5-아미노-o-크레솔", "4.5%"], ["유산자산", "4.0%"], ["황산 p-페닐렌디아민", "3.8%"], ["황산 톨루엔-2,5-디아민", "3.6%"]]},

    {"cat": "기타성분", "type": "부정형",
     "q": "다음 중 사용한도가 <b>잘못</b> 연결된 것은?",
     "opts": ["우레아 — 10%", "암모니아 — 6%", "비타민E(토코페롤) — 20%", "사이클로테트라실록세인 — 19.7%"],
     "answer": 3,
     "explain": "사이클로테트라실록세인은 <b>8.7%</b>예요. 19.7%는 <b>사이클로펜타실록세인</b>의 한도입니다.",
     "compare": [["사이클로테트라실록세인", "8.7%"], ["사이클로펜타실록세인", "19.7%"], ["우레아", "10%"], ["암모니아", "6%"], ["비타민E", "20%"]]},

    {"cat": "기타성분", "type": "복합",
     "q": "치오글라이콜릭애씨드의 용도별 한도로 옳지 <b>않은</b> 것은?",
     "opts": ["퍼머넌트웨이브용 제품(일반) — 11%", "제모제 제품 — 5%", "샴푸용 제품 — 3%", "발열2욕식 퍼머넌트웨이브용 제품 — 19%"],
     "answer": 2,
     "explain": "샴푸용 제품은 <b>1%</b>예요. 3%는 어디에도 해당하지 않습니다. (씻어내는 두발용 제품류는 2%)",
     "compare": [["샴푸용", "1%"], ["씻어내는 두발용", "2%"], ["제모제", "5%"], ["가온2욕식 헤어스트레이트너", "5%"], ["퍼머넌트웨이브용(일반)", "11%"], ["발열2욕식 퍼머넌트웨이브용", "19%"]]},

    {"cat": "기타성분", "type": "복합",
     "q": "제모제에서 pH 조정 목적으로 사용될 때 <b>최종 제품의 pH 12.7 이하</b> 조건이 붙는 성분이 아닌 것은?",
     "opts": ["리튬하이드록사이드", "칼슘하이드록사이드", "포타슘하이드록사이드", "소듐나이트라이트"],
     "answer": 3,
     "explain": "리튬·칼슘·포타슘(소듐)하이드록사이드는 모두 제모제 pH조정 시 최종 pH 12.7 이하 조건이 붙어요. 소듐나이트라이트(0.2%)는 pH와 무관하고, 아민류 함유 제품과의 병행 사용이 금지되는 성분이에요.",
     "compare": [["리튬하이드록사이드", "헤어스트레이트너 4.5% · pH 12.7 이하"], ["칼슘하이드록사이드", "헤어스트레이트너 7% · pH 12.7 이하"], ["포타슘/소듐하이드록사이드", "손톱표피 용해 5% · pH 12.7 이하"], ["소듐나이트라이트", "0.2% · 아민류 병행 금지"]]},

    {"cat": "기타성분", "type": "복합",
     "q": "머스크자일렌과 머스크케톤에 대한 설명으로 옳은 것은?",
     "opts": ["향료원액 8% 초과 함유 제품에서 자일렌 1.0%, 케톤 1.4%다",
              "두 성분의 한도는 모든 구간에서 동일하다",
              "기타 제품에서 자일렌은 0.042%, 케톤은 0.03%다",
              "향료원액 8% 이하 제품에서 자일렌은 0.56%다"],
     "answer": 0,
     "explain": "머스크케톤이 모든 구간에서 머스크자일렌보다 조금씩 높아요. 자일렌(1.0 / 0.4 / 0.03) vs 케톤(1.4 / 0.56 / 0.042) 구조입니다.",
     "compare": [["머스크자일렌", "1.0% / 0.4% / 0.03%"], ["머스크케톤", "1.4% / 0.56% / 0.042%"]]},

    {"cat": "기타성분", "type": "복합",
     "q": "다음 중 <b>사용한도가 가장 낮은</b> 성분은?",
     "opts": ["알리에이치피 올리고펩타이드-1", "폴리아크릴아마이드류(씻어내지 않는 바디화장품)", "감광소 합계량", "트랜스-2-헥세날"],
     "answer": 1,
     "explain": "폴리아크릴아마이드류의 잔류 아크릴아마이드 기준이 <b>0.00001%</b>로 압도적으로 낮아요. 올리고펩타이드-1은 0.001%, 감광소 0.002%, 트랜스-2-헥세날 0.002%입니다.",
     "compare": [["폴리아크릴아마이드(안 씻어내는 바디)", "0.00001%"], ["폴리아크릴아마이드(기타)", "0.00005%"], ["올리고펩타이드-1", "0.001%"], ["감광소 합계량", "0.002%"]]},

    {"cat": "기타성분", "type": "복합",
     "q": "다음 중 <b>손톱용 제품류</b>에 25%까지 사용할 수 있는 성분은?",
     "opts": ["톨루엔", "우레아", "노녹시놀-9", "옥살릭애씨드"],
     "answer": 0,
     "explain": "톨루엔은 손톱용 제품류에 한해 25%까지 허용되고 기타 제품에는 사용금지예요. 옥살릭애씨드는 두발용 5%, 노녹시놀-9는 17.2%, 우레아는 10%입니다.",
     "compare": [["톨루엔", "손톱용 25%"], ["노녹시놀-9", "17.2%"], ["우레아", "10%"], ["옥살릭애씨드", "두발용 5%"]]},

    {"cat": "기타성분", "type": "복합",
     "q": "속눈썹 및 눈썹 착색용도의 제품에 <b>4%</b>까지 사용할 수 있는 성분끼리 묶인 것은?",
     "opts": ["시스테인 계열, 실버나이트레이트", "톨루엔, 우레아", "징크피리치온, 클로라민T", "암모니아, 알만토인클로로하이드록시알루미늄"],
     "answer": 0,
     "explain": "시스테인·아세틸시스테인 및 그 염류와 실버나이트레이트는 모두 속눈썹·눈썹 착색용도 제품에 4%까지 허용돼요.",
     "compare": [["시스테인 계열(속눈썹·눈썹)", "4%"], ["실버나이트레이트(속눈썹·눈썹)", "4%"]]},

    {"cat": "법령", "type": "복합",
     "q": "화장품법 제15조의2(동물실험을 실시한 화장품 등의 유통판매 금지)의 <b>예외 사유가 아닌</b> 것은?",
     "opts": ["동물대체시험법이 존재하지 아니하여 동물실험이 필요한 경우",
              "화장품 수출을 위하여 수출 상대국의 법령에 따라 동물실험이 필요한 경우",
              "제조원가를 절감하기 위하여 동물실험이 필요한 경우",
              "보존제·색소·자외선차단제 등 사용상 제한이 필요한 원료의 위해평가를 위하여 필요한 경우"],
     "answer": 2,
     "explain": "경제적·원가 절감 목적은 예외 사유가 아니에요. 예외는 위해평가, 동물대체시험법 부재, 수출/수입 상대국 법령상 필요, 다른 법령에 따라 개발된 원료 사용, 식약처장이 정하는 경우 총 6가지입니다.",
     "compare": [["예외 1", "위해평가 필요"], ["예외 2", "동물대체시험법 부재"], ["예외 3", "수출 상대국 법령"], ["예외 4", "수입 상대국 법령(제품 개발)"], ["예외 5", "다른 법령에 따라 개발된 원료"], ["예외 6", "식약처장이 정하는 경우"]]},

    {"cat": "법령", "type": "복합",
     "q": "'동물대체시험법'의 정의로 옳은 것은?",
     "opts": ["동물을 전혀 사용하지 않는 실험방법만을 말한다",
              "동물을 사용하지 않거나, 부득이 사용하더라도 개체 수를 감소시키거나 고통을 경감시키는 실험방법으로서 식약처장이 인정하는 것",
              "해외에서 승인받은 모든 in vitro 시험법을 말한다",
              "동물실험 결과를 컴퓨터로 예측하는 시뮬레이션만을 말한다"],
     "answer": 1,
     "explain": "동물을 <b>전혀 안 쓰는 것만</b>이 아니라, 부득이 쓰더라도 개체 수를 줄이거나 고통을 줄이는 방법까지 포함해요. 그리고 <b>식약처장이 인정</b>한 것이어야 합니다.",
     "compare": [["범위", "미사용 + 개체 수 감소 + 고통 경감"], ["인정 주체", "식품의약품안전처장"]]},
]


# ─────────────────────────────────────────────────────────────
# 문제 생성
# ─────────────────────────────────────────────────────────────
def parse_pct(s):
    """'0.5%' → 0.5 (비교/정렬용). 파싱 실패 시 None."""
    try:
        return float(s.replace("%", "").split("~")[0])
    except ValueError:
        return None


def build_questions():
    questions = []

    # 카테고리별 값 풀 (오답 후보 = 같은 카테고리의 실제 수치들)
    by_cat = defaultdict(list)
    for cat, name, limit, note in SIMPLE:
        by_cat[cat].append((name, limit))

    # (1) 단일 한도 문제
    for cat, name, limit, note in SIMPLE:
        pool = [lim for nm, lim in by_cat[cat] if lim != limit]
        target = parse_pct(limit)

        # 오답은 정답과 '가까운 값' 우선 → 훨씬 헷갈림
        if target is not None:
            scored = []
            for lim in set(pool):
                v = parse_pct(lim)
                if v is None or v == target:
                    continue
                scored.append((abs(v - target), lim))
            scored.sort()
            near = [lim for _, lim in scored[:8]]
            distractors = random.sample(near, min(3, len(near))) if near else []
        else:
            distractors = random.sample(list(set(pool)), min(3, len(set(pool))))

        if len(distractors) < 3:
            continue

        # 비교표: 같은 카테고리에서 값이 인접한 성분들
        comp = []
        if target is not None:
            neighbors = sorted(
                [(abs((parse_pct(l) or 0) - target), nm, l) for nm, l in by_cat[cat]
                 if parse_pct(l) is not None],
            )[:4]
            comp = [[nm, l] for _, nm, l in neighbors]
        if not comp:
            comp = [[name, limit]]

        explain = f"<b>{name}</b>의 사용한도는 <b>{limit}</b>예요."
        if note:
            explain += f" ({note})"
        explain += " 아래 표에서 수치가 인접한 같은 계열 성분들과 함께 확인해 보세요."

        questions.append({
            "cat": cat, "type": "한도",
            "q": f"<b>{name}</b>의 사용한도는?",
            "opts": [limit] + distractors,
            "answer": 0,  # 셔플 전 기준. 브라우저에서 섞임
            "explain": explain,
            "compare": comp,
        })

    # (2) 조건부 한도 문제
    for item in CONDITIONAL:
        conds = item["conditions"]
        all_vals = [v for _, v in conds]
        cat_pool = [lim for nm, lim in by_cat.get(item["cat"], [])]

        for cond_text, val in conds:
            # 오답 1순위: 같은 성분의 다른 조건 값 (가장 헷갈림). 중복 값은 제거.
            distractors = []
            for v in all_vals:
                if v != val and v not in distractors:
                    distractors.append(v)
            # 부족하면 같은 카테고리 인접 수치로 채움
            target = parse_pct(val)
            if len(distractors) < 3 and target is not None:
                scored = []
                for lim in set(cat_pool):
                    v = parse_pct(lim)
                    if v is None or v == target or lim in distractors:
                        continue
                    scored.append((abs(v - target), lim))
                scored.sort()
                for _, lim in scored:
                    if len(distractors) >= 3:
                        break
                    distractors.append(lim)
            distractors = distractors[:3]
            if len(distractors) < 3:
                continue

            explain = f"<b>{item['name']}</b>을(를) {cond_text}에 사용할 때의 한도는 <b>{val}</b>예요."
            if item.get("note"):
                explain += f" {item['note']}"

            questions.append({
                "cat": item["cat"], "type": "조건부",
                "q": f"<b>{item['name']}</b>을(를) <u>{cond_text}</u>에 사용할 때의 한도는?",
                "opts": [val] + distractors,
                "answer": 0,
                "explain": explain,
                "compare": [[c, v] for c, v in conds],
            })

    # (3) 손으로 쓴 문제
    for h in HANDWRITTEN:
        questions.append(h)

    return questions


QUESTIONS = build_questions()

# ─────────────────────────────────────────────────────────────
# HTML 출력
# ─────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>사용한도 성분 퀴즈 | 맞춤형화장품 조제관리사</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" rel="stylesheet">
<style>
  :root{
    --paper:#EFF2ED; --paper-dim:#E3E7DF; --ink:#122C2E; --ink-soft:#3E5457;
    --line:#C9D0C4; --amber:#B9832E; --amber-deep:#8C6222;
    --correct:#2E6B4F; --correct-bg:#DEEBE2; --wrong:#B5432E; --wrong-bg:#F3DFD8;
    --mono:'JetBrains Mono',monospace; --sans:'Pretendard',-apple-system,sans-serif;
  }
  *{box-sizing:border-box;}
  body{margin:0;background:var(--paper);
    background-image:repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(18,44,46,.035) 40px);
    color:var(--ink);font-family:var(--sans);min-height:100vh;-webkit-font-smoothing:antialiased;}
  .wrap{max-width:660px;margin:0 auto;padding:28px 18px 80px;}
  header.top{display:flex;align-items:flex-end;justify-content:space-between;
    border-bottom:2px solid var(--ink);padding-bottom:14px;margin-bottom:18px;gap:12px;}
  .doc-id{font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--ink-soft);text-transform:uppercase;}
  h1{font-size:21px;line-height:1.35;margin:4px 0 0;font-weight:800;letter-spacing:-.01em;}
  .badge-count{font-family:var(--mono);font-size:13px;border:1.5px solid var(--ink);
    border-radius:3px;padding:4px 8px;white-space:nowrap;}

  .controls{margin-bottom:16px;}
  .ctl-label{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;
    color:var(--ink-soft);text-transform:uppercase;margin-bottom:6px;}
  .chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;}
  .chip{font-family:var(--mono);font-size:12px;padding:6px 10px;border:1.5px solid var(--ink);
    border-radius:999px;background:transparent;cursor:pointer;color:var(--ink);
    transition:background .15s,color .15s;}
  .chip.active{background:var(--ink);color:var(--paper);}
  .chip.small{font-size:11px;padding:5px 9px;}

  .len-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
  .len-row .chip{font-size:11px;padding:5px 9px;}

  .progress-row{display:flex;align-items:center;gap:10px;margin-bottom:16px;}
  .progress-track{flex:1;height:6px;background:var(--paper-dim);border:1px solid var(--line);
    border-radius:4px;overflow:hidden;}
  .progress-fill{height:100%;background:var(--amber);width:0%;transition:width .3s;}
  .progress-label{font-family:var(--mono);font-size:12px;color:var(--ink-soft);white-space:nowrap;}
  .streak{font-family:var(--mono);font-size:12px;color:var(--amber-deep);white-space:nowrap;}

  .card{background:#FBFBF9;border:1.5px solid var(--ink);border-radius:6px;padding:24px 20px;
    position:relative;box-shadow:4px 4px 0 rgba(18,44,46,.08);}
  .tag-row{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;}
  .cat-tag,.type-tag{display:inline-block;font-family:var(--mono);font-size:11px;
    letter-spacing:.05em;border-radius:3px;padding:2px 7px;}
  .cat-tag{color:var(--amber-deep);border:1px solid var(--amber);}
  .type-tag{color:var(--ink-soft);border:1px solid var(--line);background:var(--paper-dim);}
  .q-text{font-size:16.5px;line-height:1.6;font-weight:600;margin:0 0 18px;word-break:keep-all;}
  .q-text .num{font-family:var(--mono);color:var(--amber-deep);font-weight:700;}
  .q-text u{text-decoration-color:var(--amber);text-underline-offset:3px;}

  .options{display:flex;flex-direction:column;gap:9px;}
  .opt{display:flex;align-items:center;gap:10px;text-align:left;padding:12px 13px;
    border:1.5px solid var(--line);border-radius:5px;background:#fff;cursor:pointer;
    font-size:14.5px;font-family:var(--sans);color:var(--ink);
    transition:border-color .12s,background .12s;line-height:1.45;}
  .opt .letter{font-family:var(--mono);font-weight:700;font-size:13px;width:20px;height:20px;
    flex:none;border:1.5px solid var(--ink);border-radius:50%;display:flex;
    align-items:center;justify-content:center;}
  .opt:hover:not(.locked){border-color:var(--ink);background:var(--paper-dim);}
  .opt.locked{cursor:default;}
  .opt.correct{background:var(--correct-bg);border-color:var(--correct);color:var(--correct);}
  .opt.correct .letter{border-color:var(--correct);}
  .opt.wrong{background:var(--wrong-bg);border-color:var(--wrong);color:var(--wrong);}
  .opt.wrong .letter{border-color:var(--wrong);}
  .opt.dim{opacity:.45;}

  .stamp-row{display:flex;align-items:center;gap:10px;margin-top:2px;margin-bottom:10px;}
  .stamp{font-family:var(--mono);font-weight:800;font-size:13px;letter-spacing:.08em;
    padding:6px 12px;border:2.5px solid currentColor;border-radius:4px;
    transform:rotate(-4deg) scale(.85);opacity:0;animation:stamp-in .28s ease forwards;}
  @keyframes stamp-in{to{transform:rotate(-4deg) scale(1);opacity:1;}}
  @media (prefers-reduced-motion:reduce){.stamp{animation:none;opacity:1;transform:rotate(-4deg);}}
  .stamp.ok{color:var(--correct);}
  .stamp.no{color:var(--wrong);}

  .explain{margin-top:16px;padding-top:16px;border-top:1px dashed var(--line);
    font-size:13.5px;line-height:1.65;color:var(--ink-soft);display:none;}
  .explain.show{display:block;}
  .explain b{color:var(--ink);}
  .compare{margin-top:12px;border:1px solid var(--line);border-radius:5px;overflow:hidden;}
  .compare-title{font-family:var(--mono);font-size:11px;letter-spacing:.05em;
    background:var(--ink);color:var(--paper);padding:6px 10px;}
  .compare table{width:100%;border-collapse:collapse;font-size:13px;}
  .compare td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;}
  .compare tr:last-child td{border-bottom:none;}
  .compare td.label{width:56%;color:var(--ink-soft);font-weight:500;word-break:keep-all;}
  .compare td.val{font-family:var(--mono);font-weight:700;color:var(--amber-deep);}

  .next-btn{margin-top:20px;width:100%;padding:13px;background:var(--ink);color:var(--paper);
    border:none;border-radius:5px;font-family:var(--sans);font-weight:700;font-size:14.5px;
    cursor:pointer;display:none;}
  .next-btn.show{display:block;}
  .next-btn:active{transform:translateY(1px);}
  .next-btn:focus-visible,.opt:focus-visible,.chip:focus-visible,.restart-btn:focus-visible{
    outline:2px solid var(--amber);outline-offset:2px;}

  .result{text-align:center;padding:26px 6px 6px;}
  .result .score{font-family:var(--mono);font-size:44px;font-weight:800;
    color:var(--amber-deep);margin:6px 0;}
  .result p{color:var(--ink-soft);font-size:14px;line-height:1.6;}
  .btn-row{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:14px;}
  .restart-btn{padding:11px 18px;background:transparent;border:2px solid var(--ink);
    border-radius:5px;font-weight:700;font-family:var(--sans);cursor:pointer;
    color:var(--ink);font-size:13.5px;}
  .restart-btn.primary{background:var(--ink);color:var(--paper);}
  .missed-list{text-align:left;margin-top:22px;border-top:1px dashed var(--line);padding-top:16px;}
  .missed-item{font-size:13px;padding:9px 0;border-bottom:1px solid var(--paper-dim);
    color:var(--ink-soft);line-height:1.5;}
  .missed-item .mq{color:var(--ink);}
  .missed-item .ma{font-family:var(--mono);color:var(--correct);font-weight:700;}
  footer{text-align:center;margin-top:26px;font-family:var(--mono);font-size:11px;
    color:var(--ink-soft);opacity:.7;line-height:1.6;}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div>
      <div class="doc-id">MFDS · 화장품 안전기준 등에 관한 규정 별표2</div>
      <h1>사용한도 성분 암기 퀴즈</h1>
    </div>
    <div class="badge-count" id="totalBadge">—</div>
  </header>

  <div class="controls">
    <div class="ctl-label">분류</div>
    <div class="chips" id="chips"></div>
    <div class="ctl-label">출제 문항 수</div>
    <div class="len-row chips" id="lenChips"></div>
  </div>

  <div class="progress-row">
    <div class="progress-track"><div class="progress-fill" id="progressFill"></div></div>
    <div class="progress-label" id="progressLabel">0 / 0</div>
    <div class="streak" id="streak"></div>
  </div>

  <div class="card" id="quizCard"></div>

  <footer>
    보기 순서는 매번 무작위로 섞입니다 · 틀린 문제는 결과 화면에서 다시 풀 수 있습니다
  </footer>
</div>

<script>
const QUESTIONS = __QUESTIONS__;

const LENGTHS = [10, 20, 30, "전체"];
let currentFilter = "전체";
let currentLen = 20;
let order = [], idx = 0, score = 0, answered = false, missed = [], streak = 0, bestStreak = 0;

const categories = ["전체", ...Array.from(new Set(QUESTIONS.map(q => q.cat)))];

function shuffle(arr){
  const a = arr.slice();
  for(let i = a.length - 1; i > 0; i--){
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/* 보기 섞기: 정답 텍스트를 기억해 두고, 섞은 뒤 새 인덱스를 찾음 */
function shuffleOptions(q){
  const correctText = q.opts[q.answer];
  const shuffled = shuffle(q.opts);
  return { ...q, opts: shuffled, answer: shuffled.indexOf(correctText) };
}

function buildChips(){
  const chipsEl = document.getElementById('chips');
  chipsEl.innerHTML = "";
  categories.forEach(cat => {
    const n = cat === "전체" ? QUESTIONS.length : QUESTIONS.filter(q => q.cat === cat).length;
    const b = document.createElement('button');
    b.className = 'chip' + (cat === currentFilter ? ' active' : '');
    b.textContent = cat + " " + n;
    b.onclick = () => { currentFilter = cat; startQuiz(); };
    chipsEl.appendChild(b);
  });

  const lenEl = document.getElementById('lenChips');
  lenEl.innerHTML = "";
  LENGTHS.forEach(len => {
    const b = document.createElement('button');
    b.className = 'chip small' + (len === currentLen ? ' active' : '');
    b.textContent = len === "전체" ? "전체" : len + "문항";
    b.onclick = () => { currentLen = len; startQuiz(); };
    lenEl.appendChild(b);
  });
}

function startQuiz(customPool){
  const base = customPool
    ? customPool
    : (currentFilter === "전체" ? QUESTIONS : QUESTIONS.filter(q => q.cat === currentFilter));

  let picked = shuffle(base);
  if(!customPool && currentLen !== "전체"){
    picked = picked.slice(0, Math.min(currentLen, picked.length));
  }
  order = picked.map(shuffleOptions);

  idx = 0; score = 0; missed = []; streak = 0; bestStreak = 0;
  document.getElementById('totalBadge').textContent = order.length + "문항";
  buildChips();
  renderQuestion();
}

function renderQuestion(){
  answered = false;
  const card = document.getElementById('quizCard');
  if(idx >= order.length){ renderResult(); return; }
  const q = order[idx];

  document.getElementById('progressFill').style.width = (idx / order.length * 100) + "%";
  document.getElementById('progressLabel').textContent = (idx + 1) + " / " + order.length;
  document.getElementById('streak').textContent = streak >= 3 ? "연속 " + streak : "";

  const L = ["A", "B", "C", "D"];
  card.innerHTML = `
    <div class="tag-row">
      <span class="cat-tag">${q.cat}</span>
      <span class="type-tag">${q.type}</span>
    </div>
    <p class="q-text"><span class="num">Q${idx + 1}.</span> ${q.q}</p>
    <div class="options">
      ${q.opts.map((o, i) => `<button class="opt" data-i="${i}"><span class="letter">${L[i]}</span><span>${o}</span></button>`).join("")}
    </div>
    <div class="explain" id="explainBox"></div>
    <button class="next-btn" id="nextBtn">${idx + 1 === order.length ? "결과 보기" : "다음 문제"}</button>
  `;
  card.querySelectorAll('.opt').forEach(btn => btn.addEventListener('click', () => selectOption(btn, q)));
  document.getElementById('nextBtn').addEventListener('click', () => { idx++; renderQuestion(); });
}

function selectOption(btn, q){
  if(answered) return;
  answered = true;
  const chosen = parseInt(btn.dataset.i);
  const isRight = chosen === q.answer;

  if(isRight){
    score++; streak++; if(streak > bestStreak) bestStreak = streak;
  } else {
    streak = 0;
    missed.push({ ...q, chosenText: q.opts[chosen] });
  }
  document.getElementById('streak').textContent = streak >= 3 ? "연속 " + streak : "";

  document.querySelectorAll('.opt').forEach(o => {
    o.classList.add('locked');
    const i = parseInt(o.dataset.i);
    if(i === q.answer) o.classList.add('correct');
    else if(i === chosen) o.classList.add('wrong');
    else o.classList.add('dim');
  });

  let compareHtml = "";
  if(q.compare && q.compare.length){
    compareHtml = `<div class="compare">
      <div class="compare-title">비교표 · 헷갈리기 쉬운 수치</div>
      <table>${q.compare.map(([l, v]) => `<tr><td class="label">${l}</td><td class="val">${v}</td></tr>`).join("")}</table>
    </div>`;
  }
  const box = document.getElementById('explainBox');
  box.innerHTML = `
    <div class="stamp-row"><span class="stamp ${isRight ? 'ok' : 'no'}">${isRight ? '정답' : '오답'}</span></div>
    <div>${q.explain}</div>${compareHtml}`;
  box.classList.add('show');
  document.getElementById('nextBtn').classList.add('show');
}

function renderResult(){
  document.getElementById('progressFill').style.width = "100%";
  document.getElementById('progressLabel').textContent = order.length + " / " + order.length;
  document.getElementById('streak').textContent = bestStreak >= 3 ? "최고 연속 " + bestStreak : "";

  const pct = Math.round(score / order.length * 100);
  let comment = "비교표 위주로 다시 훑어보세요. 숫자보다 '조건'을 먼저 잡으면 정리가 빨라져요.";
  if(pct >= 90) comment = "거의 완벽해요. 이 상태를 유지하면서 오답만 관리하세요.";
  else if(pct >= 75) comment = "합격권이에요. 아래 오답 노트만 한 번 더 짚어보세요.";
  else if(pct >= 55) comment = "절반 이상 잡았어요. 유사 성분 짝(예: 자일렌/케톤)을 세트로 외워보세요.";

  const missedHtml = missed.length ? `
    <div class="missed-list">
      <div class="doc-id">오답 노트 (${missed.length})</div>
      ${missed.map(m => `<div class="missed-item">
        <div class="mq">${m.q.replace(/<[^>]*>/g, "")}</div>
        <div>내 답: ${m.chosenText} → 정답: <span class="ma">${m.opts[m.answer]}</span></div>
      </div>`).join("")}
    </div>` : "";

  document.getElementById('quizCard').innerHTML = `
    <div class="result">
      <div class="doc-id">Result</div>
      <div class="score">${score} / ${order.length}</div>
      <p>${comment}</p>
      <div class="btn-row">
        <button class="restart-btn primary" id="restartBtn">새 문제로 다시 풀기</button>
        ${missed.length ? `<button class="restart-btn" id="retryBtn">틀린 ${missed.length}문제만 다시</button>` : ""}
      </div>
      ${missedHtml}
    </div>`;

  document.getElementById('restartBtn').addEventListener('click', () => startQuiz());
  const retry = document.getElementById('retryBtn');
  if(retry){
    const pool = missed.map(m => QUESTIONS.find(q => q.q === m.q && q.cat === m.cat) || m);
    retry.addEventListener('click', () => startQuiz(pool));
  }
}

startQuiz();
</script>
</body>
</html>
"""


def main():
    html = HTML.replace("__QUESTIONS__", json.dumps(QUESTIONS, ensure_ascii=False, indent=1))
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    counts = defaultdict(int)
    types = defaultdict(int)
    for q in QUESTIONS:
        counts[q["cat"]] += 1
        types[q["type"]] += 1

    print(f"index.html 생성 완료 — 총 {len(QUESTIONS)}문항")
    print("  분류별:", dict(counts))
    print("  유형별:", dict(types))


if __name__ == "__main__":
    main()
