# Trustboard 프로젝트 지침

## 공통 규칙 로딩
- 현재 세션에 CODEX COMMON OPTIMIZATION v1이 이미 로딩되었으면 중복해서 읽지 않는다.
- 로딩되지 않았으면 작업 전에 다음 고정 버전의 원본을 GitHub 도구 또는 읽기 전용 HTTP로 읽고 적용한다:
  https://raw.githubusercontent.com/zeix83-maker/quant/c776da8e017e93b7595d2dedb6e53e7e6244cbc3/codex-common/COMMON.md
- 원본 저장소: zeix83-maker/quant, 경로: codex-common/COMMON.md, 커밋: c776da8e017e93b7595d2dedb6e53e7e6244cbc3.
- 이 링크는 자동 상속을 의미하지 않는다. 원본 접근에 실패하면 공통 지침을 확인하지 못했음을 보고하고 적용 완료라고 하지 않는다.
- 공통 본문을 저장소에 복제하지 않는다. 전역 설치 방법은 quant의 codex-common/README.md를 참고한다.
- 전역 규칙과 프로젝트 규칙이 충돌하면 적용되는 지침 우선순위를 따르고 충돌을 보고한다.

## 구조와 실행
- 개발 컨테이너의 Python 버전은 3.11이다.
- 앱 진입점: `trust_dual_platform.py`; 의존성: `requirements.txt`; 저장소 DB 파일명: `trust_quant_clean.db`.
- 설치: `python -m pip install -r requirements.txt`.
- 실행: `python -m streamlit run trust_dual_platform.py`.
- 컨테이너 설정의 보안 관련 실행 옵션은 일반 실행 명령에 자동 복제하지 않는다.

## 변경별 필수 검증
- Python 코드 변경: `python -m py_compile trust_dual_platform.py`.
- 앱 동작 변경: 임시 작업 디렉터리에서 절대 경로로 앱을 구동해 운영 DB와 분리하고, 변경한 UI 경로와 SQLite 반영을 확인한다. HTTP 상태만으로 UI 동작 성공을 단정하지 않는다.
- 증권사 API 로직 변경: 모의 응답으로 정상·인증 실패·타임아웃·비정상/빈 응답 경로를 검증한다. 사용자 계정으로 실제 API를 호출하는 것을 기본 검사로 삼지 않는다.
- DB 로직 변경: 임시 DB로 검증하고 기존 데이터의 파괴적 초기화·덮어쓰기를 피한다.
- 지침 문서만 변경하면 참조 URL·고정 버전·지침 중복을 검사한다.
- 현재 자동 테스트 모음은 없다. 미실행 검증과 제한을 구분해 보고한다.

## 프로젝트 고유 경계
- 모의 계좌·실전 계좌·샘플 데이터가 구분되어야 한다. 코드에 하드코딩된 지표를 실측 검증 결과로 보고하지 않는다.
- 앱 실행에는 DB 생성·샘플 삽입·방문 로그 기록이 따른다. 검증 시 기존 DB를 사용하지 않는다.
- 계좌 인증정보와 토큰을 테스트 데이터·로그·커밋에 포함하지 않는다.
