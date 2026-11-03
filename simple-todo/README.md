# Simple TODO — Web / API / DB 과제

React + Vite / FastAPI / PostgreSQL. 할 일 추가·조회·수정·완료·삭제, 새로고침 후 데이터 유지.

## 1단계: 로컬에서 직접 실행

PostgreSQL을 로컬에 설치하고 `tododb` DB와 `todouser` 계정을 만듭니다. DB 비밀번호는 직접 정하세요.

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://todouser:YOUR_PASSWORD@localhost:5432/tododb'
uvicorn main:app --reload --port 8000
```

다른 터미널에서:

```bash
cd web
npm install
npm run dev
```

브라우저 `http://localhost:5173`에서 추가 후 새로고침해도 남는지 확인합니다. Vite가 `/api`를 `localhost:8000`으로 프록시합니다.

## 2단계: Ubuntu VM에 직접 배포

1. `git clone`으로 소스를 `/opt/simple-todo`에 배치합니다. `todo` 시스템 사용자에게 디렉터리 소유권을 부여하고, Nginx가 `web/dist`를 읽을 수 있도록 권한을 설정합니다.
2. VM에 `postgresql`, `nginx`, `python3-venv`, `nodejs`, `npm`을 설치합니다. PostgreSQL에서 DB/계정을 만들고 `api/.venv`에 의존성을 설치합니다.
3. `cd web && npm install && npm run build`로 정적 파일을 생성합니다.
4. `/etc/simple-todo/api.env`에 `DATABASE_URL=postgresql+psycopg://todouser:YOUR_PASSWORD@localhost:5432/tododb`를 저장합니다. 해당 파일은 `root`만 읽도록 권한을 제한합니다.
5. `deploy/systemd/todo-api.service`를 `/etc/systemd/system/`에 복사하고 `sudo systemctl daemon-reload && sudo systemctl enable --now todo-api`를 실행합니다.
6. `deploy/nginx/todo.conf`를 `/etc/nginx/sites-available/todo`에 복사해 활성화합니다. 기본 사이트는 비활성화하고 `sudo nginx -t && sudo systemctl reload nginx`를 실행합니다.
7. `curl http://localhost/api/health` 및 브라우저로 검증합니다. VS Code Remote-SSH의 PORTS 탭에서 VM의 80 포트를 포워딩하면 로컬 브라우저로도 확인할 수 있습니다.

VM의 Linux 사용자/설치 경로가 다르면 systemd와 Nginx 설정을 맞춰 수정하세요. VM OS와 포트 충돌을 확인해야 합니다.

## 3단계: Docker Compose

VM에서 **2단계의 호스트 Nginx, API 서비스를 중지**하여 포트 충돌을 방지합니다. DB 데이터 이전이 필요하면 별도 백업/복원 작업이 필요합니다. Compose DB는 새 볼륨을 사용합니다.

```bash
cp .env.example .env
# .env의 POSTGRES_PASSWORD를 안전한 값으로 변경
# .env는 Git에 올리지 않습니다.
docker compose up -d --build
docker compose ps
curl http://localhost:8080/api/health
```

`http://VM_IP:8080`에서 테스트합니다. 포트 변경 시 `.env`의 `WEB_PORT`를 수정하세요. PostgreSQL 포트는 외부에 공개하지 않습니다. 재시작 후에도 `postgres_data` 볼륨에 데이터가 유지됩니다.

## 확인 사항

- 브라우저에서 추가/수정/완료/삭제, 새로고침 후 유지
- `curl /api/health` 응답
- `systemctl status todo-api` 및 `journalctl -u todo-api`
- `docker compose ps`, `docker compose logs api`
- 로컬과 VM은 서로 다른 DB를 사용하므로 데이터가 자동 공유되지 않음

**주의:** 이 코드는 학습용이며 인증 기능이 없습니다. 인터넷에 공개 배포할 경우 접근 제어, HTTPS, DB 백업 등을 추가하세요.
