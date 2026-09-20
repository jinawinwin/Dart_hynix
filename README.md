# OpenDART 재무분석 GitHub 스타터

이 저장소는 OpenDART의 공식 API에서 재무제표를 받아 다음 위치에 보관합니다.

- `data/raw`: OpenDART 원본 JSON
- `data/processed`: 계산된 핵심 재무수치와 비율
- `reports`: 사람이 읽는 Markdown 분석보고서
- `docs`: 재무제표·재무비율 실무 가이드 Word 및 PowerPoint

현재 예시는 SK하이닉스(`000660`)입니다. Notion 연동 전에 GitHub 데이터 수집이 정상적으로 작동하는지 확인하기 위한 1단계 스타터입니다.

## 1. 준비물

1. GitHub 계정
2. Git 설치
3. Python 3.11 이상
4. OpenDART API 인증키

OpenDART 인증키는 OpenDART 사이트에서 로그인한 후 `인증키 신청/관리` 메뉴에서 발급합니다.

## 2. GitHub 저장소 만들기

GitHub에서 다음과 같이 만듭니다.

1. 우측 상단 `+` → `New repository`
2. Repository name: `financial-analysis`
3. 공개 범위 선택
   - 코드와 보고서를 공개하려면 `Public`
   - 개인 분석용이면 `Private`
4. `Create repository` 선택

새 저장소 주소가 아래와 같다고 가정합니다.

```text
https://github.com/내계정/financial-analysis.git
```

## 3. 이 스타터를 GitHub에 올리기

PowerShell에서 이 폴더로 이동합니다.

```powershell
cd "스타터를 내려받은 경로\financial-analysis-starter"
git init
git add .
git commit -m "Initial OpenDART financial analysis starter"
git branch -M main
git remote add origin https://github.com/내계정/financial-analysis.git
git push -u origin main
```

GitHub 로그인이 필요하면 화면의 안내에 따라 브라우저 인증을 진행합니다.

## 4. 로컬 실행 환경 만들기

PowerShell에서 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

PowerShell이 가상환경 스크립트 실행을 막는 경우 현재 창에서만 다음 명령을 먼저 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 5. OpenDART API 키를 넣고 실행하기

API 키를 Git 저장소의 파일에 기록하지 않습니다. 현재 PowerShell 창의 환경변수에만 입력합니다.

```powershell
$env:DART_API_KEY = "발급받은_OPEN_DART_API_KEY"
python -m src.main --year 2025 --report-code 11011 --fs-div CFS
```

보고서 코드는 다음과 같습니다.

| 코드 | 보고서 |
|---|---|
| `11011` | 사업보고서 |
| `11012` | 반기보고서 |
| `11013` | 1분기보고서 |
| `11014` | 3분기보고서 |

실행 후 다음 파일이 생깁니다.

```text
data/raw/000660/2025/11011-CFS.json
data/processed/000660/2025-11011-CFS.json
reports/000660/2025-11011-CFS.md
```

OpenDART에 해당 연도·보고서 자료가 아직 없다면 존재하는 최근 사업연도로 다시 실행합니다.

## 6. 분석 기업 추가하기

`config/companies.json`에 종목코드를 추가합니다.

```json
{
  "companies": [
    {"name": "SK하이닉스", "stock_code": "000660", "enabled": true},
    {"name": "삼성전자", "stock_code": "005930", "enabled": true}
  ]
}
```

`corp_code`는 직접 찾을 필요가 없습니다. 프로그램이 OpenDART 기업 고유번호 파일에서 종목코드에 맞는 값을 자동으로 찾습니다.

## 7. GitHub Actions에 API 키 등록하기

GitHub 저장소 화면에서 다음 순서로 이동합니다.

1. `Settings`
2. `Secrets and variables`
3. `Actions`
4. `New repository secret`
5. Name: `DART_API_KEY`
6. Secret: 발급받은 OpenDART API 키
7. `Add secret`

API 키는 코드나 `companies.json`에 입력하지 않습니다.

## 8. GitHub Actions를 처음 수동 실행하기

1. 저장소의 `Actions` 탭 선택
2. 좌측 `OpenDART financial sync` 선택
3. `Run workflow` 선택
4. 사업연도와 보고서 코드 입력
5. 실행이 끝난 후 `data`와 `reports` 폴더 확인

워크플로는 평일 UTC 23:00, 한국시간 오전 8시에 자동 실행됩니다. 예약 실행은 실행 시점의 전년도 사업보고서를 확인합니다. 분기·반기보고서까지 자동 탐지하려면 이후 단계에서 공시목록 API를 연결합니다.

## 9. 생성된 파일을 직접 GitHub에 반영하기

로컬에서 실행한 결과를 올릴 때 사용합니다.

```powershell
git add data reports
git commit -m "data: add SK hynix financial report"
git push
```

## 10. 기존 Word·PowerPoint 문서 공개하기

`docs` 폴더에 다음 문서가 포함되어 있습니다.

- `재무제표_재무비율_실무가이드.docx`
- `재무제표_재무비율_실무가이드_최종.pptx`

GitHub에서는 Office 파일을 바로 읽기 불편할 수 있으므로 나중에 PDF와 주요 슬라이드 PNG도 추가하는 것을 권장합니다.

## 11. Notion 연결을 위한 다음 단계

GitHub 수집이 정상 작동한 다음 아래 항목을 추가합니다.

1. Notion에서 `기업`, `분석 리포트`, `KPI 스냅샷`, `업데이트 로그` 데이터베이스 생성
2. Notion Integration 생성
3. 원본 데이터베이스를 Integration에 연결
4. GitHub Secrets에 다음 값 등록
   - `NOTION_TOKEN`
   - `NOTION_COMPANY_DATA_SOURCE_ID`
   - `NOTION_REPORT_DATA_SOURCE_ID`
   - `NOTION_KPI_DATA_SOURCE_ID`
5. `src/publish_notion.py`를 추가해 `data/processed`의 결과를 upsert

Notion 페이지는 GitHub를 직접 읽는 구조보다 GitHub Actions가 계산 결과를 Notion API로 보내는 구조가 안정적입니다.

## 12. 운영 전에 보완할 항목

이 스타터의 비율 계산은 동작 확인을 위한 최소 예제입니다. 실제 투자·여신·기업분석에 사용하려면 다음을 추가해야 합니다.

- `account_id` 중심의 계정 매핑
- 연결재무제표가 없을 때 별도재무제표 대체
- 누적 분기 수치를 단독 분기로 변환
- 정정공시 및 접수번호 버전 관리
- 평균자산·평균자본 기반 ROA·ROE
- CAPEX, FCF, 순차입금, EBITDA 및 ROIC 계산
- 단위·통화·결산기 변경 검증
- 시장가격 데이터 연결 후 PER·PBR·EV/EBITDA 계산

먼저 한 기업과 한 사업보고서로 끝까지 실행한 후 계산식을 확장하는 순서가 가장 안전합니다.
