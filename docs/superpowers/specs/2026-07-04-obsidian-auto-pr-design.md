# Obsidian Main Sync 설계

## 개요

- 대상 Vault: `C:\Users\User\Documents\Obsidian Vault`
- 원격 저장소: `ChangwooHan-hub/obsidian-vault`
- 목적: Obsidian 노트 변경을 주기적으로 자동 커밋하고 `origin/main`에 직접 push한다.
- 기준 브랜치: `main`
- 실행 주기: 15분

## 확정된 요구사항

1. Vault의 표준 작업 브랜치는 항상 `main`이다.
2. 자동화는 PR을 생성하지 않는다.
3. 변경 파일이 없으면 커밋과 push를 모두 건너뛴다.
4. 변경이 있으면 `main`에서 `add -> commit -> push origin main`만 수행한다.
5. 충돌이나 push 실패가 나면 자동 머지는 하지 않고 로그만 남긴다.
6. Obsidian에서 `pull`할 때는 `main`만 보면 최신 상태를 받을 수 있어야 한다.

## 비목표

- 드래프트 PR 자동 생성
- 별도 자동화 브랜치 유지
- 자동 merge 또는 rebase
- 실시간 파일 감시

## 선택안

`Windows Task Scheduler + PowerShell` 조합을 유지하되, 흐름을 `main` 직행 push로 단순화한다.

선정 이유:

- Obsidian 사용자가 이해하기 가장 쉽다.
- `pull` 기준 브랜치가 `main` 하나로 고정되어 혼선이 없다.
- 기존 `git`/`gh` 인증과 예약 작업 구성을 거의 그대로 재사용할 수 있다.

## 구성요소

1. PowerShell 자동화 스크립트 1개
   - Vault 변경 감지
   - `main` 브랜치 확인
   - 커밋 및 `origin/main` push
   - 로그 기록
2. Windows 예약 작업 1개
   - 15분마다 실행
3. 로그 파일 1개
   - 성공, 변경 없음, 실패 사유 기록
4. 잠금 파일 1개
   - 중복 실행 방지

## 파일 배치

- 스크립트: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.ps1`
- 로그: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.log`
- 잠금 파일: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.lock`

## 데이터 흐름

1. 예약 작업이 15분마다 스크립트를 실행한다.
2. 스크립트는 잠금 파일을 확인하고 중복 실행이면 종료한다.
3. `git status --porcelain`로 변경 여부를 검사한다.
4. 변경이 없으면 로그만 남기고 종료한다.
5. 현재 브랜치가 `main`인지 확인한다.
6. 변경 파일을 스테이징하고 자동 커밋한다.
7. `origin/main`으로 push한다.
8. 결과를 로그에 남기고 잠금 파일을 해제한다.

## 브랜치 규칙

- 작업 브랜치와 원격 추적 브랜치는 모두 `main`이다.
- 과거 `obsidian/auto-sync` 브랜치와 드래프트 PR은 제거한다.
- 사용자가 수동으로 다른 브랜치로 이동했다면, 변경 사항이 없는 경우에만 자동화가 `main`으로 되돌릴 수 있다.
- 다른 브랜치에서 변경이 감지되면 자동화는 실패 로그를 남기고 종료한다.

## 커밋 규칙

- 커밋 메시지는 시간 기반 자동 메시지를 사용한다.
- 예시: `Auto sync Obsidian notes 2026-07-04 14:30`
- 한 주기 내 모든 변경은 하나의 커밋으로 묶는다.

## 오류 처리

- `git` 명령 실패: 로그 남기고 종료
- 브랜치 전환 실패: 로그 남기고 종료
- push 실패: 로그 남기고 종료
- 자동 conflict resolution은 수행하지 않음

## 제외 파일 정책

다음 파일은 계속 Git 추적 제외 상태를 유지한다.

- `.obsidian/workspace.json`
- `.obsidian/workspace-mobile.json`
- `.obsidian/cache`
- `.obsidian/plugins/obsidian-git/data.json`
- `.obsidian/automation/*.log`
- `.obsidian/automation/*.lock`

## 관찰 가능성

로그에는 아래 정보를 남긴다.

- 실행 시작 시각
- 변경 없음 여부
- 커밋 SHA
- `origin/main` push 성공 여부
- 실패 메시지

## 테스트 계획

### 시나리오 1. 변경 없음

- Vault 수정 없음
- 기대 결과
  - 커밋 없음
  - push 없음
  - 로그에 `No changes detected.`

### 시나리오 2. 노트 변경

- 노트 파일 1개 수정
- 기대 결과
  - `main`에서 자동 커밋
  - `origin/main` direct push
  - Obsidian `pull`과 GitHub `main`이 동일한 최신 상태

### 시나리오 3. 원격 실패

- 네트워크 또는 인증 문제 유도
- 기대 결과
  - 로그에 실패 원인 기록
  - 로컬 변경 유지

## 완료 기준

1. 예약 작업이 15분마다 실행된다.
2. Vault가 `main` 브랜치에 있다.
3. 자동화 스크립트가 `main`에서 변경을 커밋하고 `origin/main`에 push한다.
4. `obsidian/auto-sync` 브랜치와 드래프트 PR이 제거된다.
5. Obsidian에서 `pull`했을 때 `main` 기준 최신 상태가 반영된다.
