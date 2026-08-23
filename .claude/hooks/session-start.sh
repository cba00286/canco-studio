#!/bin/bash
# 세션이 시작될 때 저장소 상태를 세션에 넘긴다.
# 여기서 출력한 내용이 그대로 Claude Code의 첫 컨텍스트가 된다 —
# 새 세션이 «어디까지 했고 다음에 뭘 해야 하는지»를 묻지 않고 알게 하는 것이 목적이다.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0

# 생성 파이프라인용 의존성. 페이지 빌드와 검사 스크립트는 표준 라이브러리만 쓰므로
# 설치가 실패해도 세션을 막지 않는다.
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ] && [ -f requirements.txt ]; then
  python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt >/dev/null 2>&1 \
    || echo "· 의존성 설치를 건너뛰었습니다(네트워크). 페이지 빌드와 규격 검사는 그대로 됩니다."
fi

echo "=============================================================="
echo " 쿵쿵이와 친구들 — 제작 저장소"
echo "=============================================================="
echo
echo "먼저 CLAUDE.md 를 읽어라. 절대 어기면 안 되는 규칙이 거기 있다."
echo

if [ -f episodes/ep1/PROGRESS.md ]; then
  echo "── 진행 상황 ─────────────────────────────────────────────────"
  sed -n '/## 지금 어디까지/,/^## /p' episodes/ep1/PROGRESS.md | sed '$d' | sed '/^$/d' | head -20
  echo
fi

echo "── 1화 규격 검사 ─────────────────────────────────────────────"
python3 scripts/check_episode.py ep1 2>&1 | tail -22 || true
echo

echo "── OST ──────────────────────────────────────────────────────"
python3 scripts/check_ost.py ep1 2>&1 | tail -n +2 | sed '/^$/d' | tail -12 || true
echo

echo "── 아직 안 정해진 것 (사용자 결정 필요) ──────────────────────"
sed -n '/## 아직 안 정해진 것/,$p' CLAUDE.md | tail -n +2 | sed '/^$/d' || true
echo
echo "── 자주 쓰는 명령 ────────────────────────────────────────────"
echo "  python3 scripts/build_ref_prompts.py --episode ep1   프롬프트 재생성"
echo "  python3 scripts/check_episode.py ep1                 규격 검사"
echo "  python3 site/build.py ep1                            사이트 3페이지"
echo "  python3 scripts/sync_from_page.py <page.html>        페이지 편집 → JSON"
echo "=============================================================="
