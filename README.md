# SK하이닉스 재무분석

OpenDART 공시를 수집해 SK하이닉스(`000660`)의 장기 재무 흐름을 보여주는 GitHub Pages 프로젝트입니다.

## [대시보드 바로가기 →](https://jinawinwin.github.io/Dart_hynix/)

대시보드 상단은 최근 핵심 지표와 연간 추이 그래프로 구성되고, 하단은 다음 세 분류의 수치 테이블을 제공합니다.

- **Annual**: 사업보고서 (`11011`)
- **Half-year**: 반기보고서 (`11012`)
- **Quarterly**: 1분기 (`11013`) 및 3분기보고서 (`11014`)

## 동작 구조

```text
OpenDART API
   │  DART_API_KEY (GitHub Actions Secret)
   ▼
src/main.py ──▶ data/raw + data/processed + reports
   │
   ▼
src/build_dashboard.py ──▶ docs/dashboard-data.js
   │
   ▼
GitHub Pages ──▶ https://jinawinwin.github.io/Dart_hynix/
```

`src/main.py`는 2010년부터 현재 연도까지 네 보고서 코드를 조회합니다. 연결재무제표(`CFS`)를 우선 사용하고, 자료가 없으면 별도재무제표(`OFS`)를 시도합니다. OpenDART 표준 재무제표 API에 존재하지 않는 과거 기간은 실패로 중단하지 않고 `missing`으로 기록합니다.

## 자동 업데이트

`.github/workflows/dart-sync.yml`은 매월 1일 00:15 UTC(한국시간 09:15)에 실행됩니다.

1. 2010년부터 현재 연도까지 사업·반기·분기보고서를 조회
2. 원본·가공 데이터와 Markdown 보고서 갱신
3. 대시보드 데이터 재생성
4. 변경 파일을 `financial-data-bot` 명의로 커밋
5. `docs` 디렉터리를 GitHub Pages에 배포

처음 설정할 때 저장소의 `Settings → Secrets and variables → Actions`에 `DART_API_KEY`를 등록하고, `Settings → Pages → Build and deployment`의 Source를 **GitHub Actions**로 선택합니다. 이후 Actions 탭의 **OpenDART data and dashboard**를 한 번 수동 실행하면 전체 기간을 백필할 수 있습니다.

## 로컬 실행

Python 3.11 이상과 OpenDART 인증키가 필요합니다. 외부 Python 패키지는 사용하지 않습니다.

```powershell
$env:DART_API_KEY = "발급받은_OPEN_DART_API_KEY"
python -m src.main --from-year 2010 --to-year 2026 --all-reports --fs-div AUTO --continue-on-error
python -m src.build_dashboard
```

단일 기간만 확인하려면 기존 형식도 사용할 수 있습니다.

```powershell
python -m src.main --year 2025 --report-code 11011 --fs-div CFS
```

## 디렉터리

| 경로 | 내용 |
|---|---|
| `data/raw` | OpenDART 원본 JSON |
| `data/processed` | 핵심 재무수치와 비율 |
| `reports` | 사람이 읽는 기간별 Markdown 분석 |
| `docs` | GitHub Pages 대시보드와 실무 가이드 |
| `src` | API 클라이언트, 수집기, 지표 및 대시보드 빌더 |

## 인증과 토큰

저장소는 사용자 로그인 기능을 제공하지 않습니다. 외부 자격 증명은 실행 환경에서만 주입되며 코드·데이터·대시보드에는 포함되지 않습니다.

- `DART_API_KEY`: OpenDART 요청의 `crtfc_key` 쿼리 파라미터로만 사용되는 Repository Secret
- `GITHUB_TOKEN`: Actions 실행마다 GitHub가 자동 발급하는 단기 토큰. 데이터 커밋과 Pages 배포에 최소 권한으로 사용
- 로컬 GitHub 로그인: 개발자가 `git push`할 때 사용하는 Git 자격 증명이며 애플리케이션이 읽지 않음

구성요소별 요청 흐름, 권한 범위, 비밀정보 취급 원칙은 [인증 구조 문서](docs/AUTHENTICATION.md)를 참고하세요.

## 데이터 해석 주의

분기·반기 손익 수치는 공시의 누적 금액입니다. 이 프로젝트는 `account_nm` 별칭으로 대표 계정을 매핑하므로, 투자·여신 판단 전에는 원문 공시, 정정공시, 계정 ID와 단위·연결범위를 함께 확인해야 합니다.
