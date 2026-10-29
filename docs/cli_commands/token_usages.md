# 토큰 사용량 및 구독 할당량 조회

## 개요

`tokscale`는 Codex, Claude, Gemini, Cursor 등 20개 이상의 AI 코딩 도구의 토큰 사용량과 구독 할당량을 추적하는 CLI 도구입니다.

- **프로젝트**: [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) (⭐ 3.3k stars)
- **설치**: `npx tokscale@latest` (전역 설치 불필요)
- **홈페이지**: [tokscale.ai](https://tokscale.ai)

---

## 설치

```bash
# 즉시 실행 (npx)
npx tokscale@latest

# 전역 설치 (선택사항)
npm install -g tokscale
```

---

## 구독 할당량 조회

### 기본 명령어

```bash
# 구독 할당량 확인 (가벼운 터미널 출력)
npx tokscale@latest usage --light

# JSON 출력 (스크립트/자동화용)
npx tokscale@latest usage --json

# TUI 인터랙티브 모드
npx tokscale@latest usage
```

### 예시 출력 (Codex Pro)

```
╭──────────────────────────────────────────────────────────────╮
│ Codex                                                        │
│ Session       100% left  [============]resets in 4h 59m      │
│ Weekly        0% left    [------------]resets Sat 8pm        │
│ Account   rus2232@gmail.com                                  │
│ Plan      Pro                                                │
╰──────────────────────────────────────────────────────────────╯
```

### 지원되는 프로바이더

| 프로바이더 | 확인 가능한 한도 | 인증 방식 |
|------------|-----------------|-----------|
| **Claude** | 세션(5hr), 주간, Opus 할당량 | OAuth (Keychain/credentials) |
| **Codex** | 세션, 주간 할당량 | `~/.codex/auth.json` |
| **GitHub Copilot** | Premium 상호작용, Chat 할당량 | GitHub token |
| **Amp** | Free tier 잔여량, Credits | API key |
| **Kimi** | 세션, 주간 할당량 | OAuth |
| **Z.ai** | 토큰 한도, 웹 검색 | `ZAI_API_KEY` |
| **MiniMax** | 모델별 프롬프트 할당량 | `MINIMAX_API_KEY` |

> **참고**: 숫자들은 프로바이더가 보고하는 그대로 표시됩니다. tokscale이 독립적으로 검증하지는 않습니다.

---

## 토큰 사용량 조회

### 모델별 사용량

```bash
# 모델별 사용량 테이블
npx tokscale@latest models --light

# JSON 출력
npx tokscale@latest models --json
```

### 월별 사용량

```bash
# 월별 사용량
npx tokscale@latest monthly --light

# JSON 출력
npx tokscale@latest monthly --json
```

### 시간별 사용량

```bash
# 시간별 사용량
npx tokscale@latest hourly --light
```

### 전체 사용량 요약

```bash
# 전체 요약 (TUI)
npx tokscale@latest

# 기여도 그래프 (GitHub 스타일)
npx tokscale@latest stats

# 분별 사용량 (고급)
npx tokscale@latest minutely --light
```

---

## TUI 인터랙티브 모드

```bash
npx tokscale@latest
```

### 키보드 단축키

| 키 | 동작 |
|----|------|
| `←/→/Tab` | 탭 전환 |
| `↑/↓` | 목록 탐색 |
| `Enter` | 상세 보기 |
| `Esc` | 뒤로가기 |
| `c/d/t` | 비용/날짜/토큰 정렬 |
| `j` | 오늘로 이동 |
| `s` | 소스 선택 |
| `g` | 그룹화 선택 |
| `p` | 색상 테마 변경 |
| `r` | 데이터 새로고침 |
| `e` | JSON 내보내기 |
| `q` | 종료 |

### 탭 목록

1. **Overview** — 차트 + 상위 모델
2. **Usage** — 구독 할당량
3. **Models** — 모델별 분해
4. **Daily** — 일별 사용량
5. **Hourly** — 시간별 사용량
6. **Stats** — 기여도 그래프
7. **Agents** — 에이전트별 사용량

---

## 데이터 소스

tokscale는 각 AI 코딩 도구의 로컬 데이터베이스에서 사용량 정보를 읽습니다:

| 도구 | 데이터 경로 |
|------|-------------|
| **Codex** | `~/.codex/state_5.sqlite` (threads 테이블) |
| **Claude Code** | `~/.claude/projects/` + `~/.claude/transcripts/` |
| **OpenCode** | `~/.local/share/opencode/opencode.db` |
| **Hermes Agent** | `$HERMES_HOME/state.db` |
| **Gemini CLI** | `~/.gemini/tmp/*/chats/*.json` |
| **Cursor IDE** | Cursor API export (`~/.config/tokscale/cursor-cache/`) |

---

## JSON 출력 예시 (Codex 구독)

```json
[
  {
    "provider": "Codex",
    "plan": "Pro",
    "email": "rus2232@gmail.com",
    "metrics": [
      {
        "label": "Session",
        "used_percent": 0.0,
        "remaining_percent": 100.0,
        "resets_at": "2026-05-29T18:46:20+00:00"
      },
      {
        "label": "Weekly",
        "used_percent": 100.0,
        "remaining_percent": 0.0,
        "resets_at": "2026-05-30T20:28:15+00:00"
      }
    ]
  }
]
```

---

## 자동화 예시

### 할당량 모니터링 스크립트

```bash
#!/bin/bash
# codex_quota_check.sh

QUOTA=$(npx tokscale@latest usage --json 2>/dev/null)
WEEKLY_LEFT=$(echo "$QUOTA" | jq '.[0].metrics[] | select(.label=="Weekly") | .remaining_percent')

if (( $(echo "$WEEKLY_LEFT < 20" | bc -l) )); then
  echo "⚠️  Codex 주간 할당량이 20% 미만입니다: ${WEEKLY_LEFT}%"
fi
```

### 정기 모니터링 (cron)

```bash
# 매일 아침 9시에 할당량 확인
0 9 * * * npx tokscale@latest usage --json >> ~/.logs/codex_quota.log
```

---

## 참고

- **가격 데이터**: [LiteLLM pricing](https://github.com/BerriAI/litellm)에서 실시간 가져옴 (1시간 캐시)
- **소셜 플랫폼**: `npx tokscale@latest submit`으로 리더보드에 제출 가능
- **Wrapped**: `npx tokscale@latest wrapped`으로 연도별 요약 생성
- **Frontend**: [tokscale.ai](https://tokscale.ai)에서 2D/3D 기여도 그래프 확인
