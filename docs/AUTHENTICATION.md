# 인증 구조

이 프로젝트에는 대시보드 사용자 인증이 없습니다. 공개 GitHub Pages는 이미 생성된 정적 파일만 제공하며, OpenDART 인증키나 GitHub 토큰을 브라우저로 전달하지 않습니다.

## 구성요소와 자격 증명

| 구성요소 | 자격 증명 | 저장 위치 | 용도 |
|---|---|---|---|
| 로컬 수집기 | `DART_API_KEY` | 현재 셸 환경변수 | OpenDART API 호출 |
| GitHub Actions 수집 작업 | `DART_API_KEY` | Repository Secret | 예약·수동 OpenDART API 호출 |
| GitHub Actions | `GITHUB_TOKEN` | 실행 시 GitHub가 자동 발급 | 결과 커밋, Pages artifact 업로드·배포 |
| GitHub Pages | 없음 | 해당 없음 | 공개 정적 대시보드 제공 |

## 요청 흐름

1. 워크플로가 `secrets.DART_API_KEY`를 수집 단계의 환경변수로만 전달합니다.
2. `src/main.py`가 환경변수를 읽어 `DartClient`를 만듭니다.
3. `src/dart_client.py`는 키를 OpenDART의 `crtfc_key` 쿼리 파라미터로 넣어 HTTPS 요청을 보냅니다.
4. 응답 JSON은 `data/raw`에 저장되고, 키가 없는 응답 데이터만 `data/processed`와 `reports`로 가공됩니다.
5. `src/build_dashboard.py`가 처리된 재무수치만 `docs/dashboard-data.js`에 씁니다.
6. Actions의 `GITHUB_TOKEN`이 변경 파일을 저장소에 push하고 Pages artifact를 배포합니다.
7. 방문자의 브라우저는 Pages의 HTML/CSS/JavaScript와 공개 재무수치만 내려받습니다.

## 권한 경계

워크플로 권한은 다음으로 한정합니다.

```yaml
permissions:
  contents: write
  pages: write
  id-token: write
```

- `contents: write`: 자동 생성된 `data`, `reports`, `docs/dashboard-data.js` 커밋
- `pages: write`: Pages 배포 생성
- `id-token: write`: Pages 배포가 GitHub OIDC로 실행 신원을 확인하는 데 사용

`GITHUB_TOKEN`은 워크플로 실행마다 자동 발급되고 실행 후 만료됩니다. 개인 액세스 토큰(PAT)을 별도로 저장하지 않습니다.

## 비밀정보 취급

- API 키를 코드, JSON, Markdown, Actions 로그에 출력하지 않습니다.
- `.env`는 `.gitignore`에 포함되어 있습니다.
- GitHub Actions Secret은 `${{ secrets.DART_API_KEY }}`로 필요한 단계에만 주입합니다.
- `DartClient`의 오류 메시지는 OpenDART 상태 코드와 설명만 포함하고 요청 URL이나 키를 포함하지 않습니다.
- 키를 노출했다고 의심되면 OpenDART에서 즉시 재발급하고 GitHub Secret을 교체합니다.

## 신뢰 경계

OpenDART와 GitHub Actions 사이의 통신은 HTTPS를 사용합니다. 공개 대시보드는 읽기 전용이며 API를 직접 호출하지 않으므로 방문자가 키를 추출하거나 수집 권한으로 요청을 보낼 수 없습니다. 저장소 쓰기 권한은 Actions의 단기 토큰과 저장소 관리자에게만 있습니다.
