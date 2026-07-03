# Obsidian 자동 PR 설계

## 개요

- 대상 Vault: `C:\Users\User\Documents\Obsidian Vault`
- 원격 저장소: `ChangwooHan-hub/obsidian-vault`
- 목적: Obsidian에서 작성한 노트 변경을 사람이 직접 Git/GitHub를 조작하지 않아도 주기적으로 수집하고, 하나의 장기 드래프트 PR에 누적한다.
- 기준 브랜치: `main`
- 자동화 브랜치: `obsidian/auto-sync`
- 실행 주기: 15분

## 확정된 요구사항

1. PR은 항상 `main <- obsidian/auto-sync` 조합으로 유지한다.
2. 열린 드래프트 PR이 이미 있으면 새 PR을 만들지 않고 해당 PR에 커밋만 누적한다.
3. 기존 PR이 닫혔거나 머지된 경우 다음 변경 감지 시 새 드래프트 PR을 다시 만든다.
4. 변경 파일이 없으면 커밋, 푸시, PR 생성 모두 건너뛴다.
5. 자동화는 Windows에서 안정적으로 동작해야 하며 Obsidian 플러그인 내부 로직에 과도하게 의존하지 않는다.

## 비목표

- 머지 자동화
- 충돌 자동 해결
- 노트 단위 PR 분리
- 저장 직후 실시간 반응
- 여러 자동화 브랜치 운영

## 접근 방식 비교

### 1. Windows Task Scheduler + PowerShell

- 장점
  - 현재 사용자 환경에서 가장 단순하다.
  - Obsidian이 실행 중이어도 독립적으로 동작한다.
  - `git`과 `gh` 인증 상태를 그대로 활용할 수 있다.
- 단점
  - 예약 작업과 스크립트 파일을 직접 관리해야 한다.

### 2. Obsidian Git 플러그인 + 외부 PR 스크립트

- 장점
  - 사용자가 Obsidian UI에서 Git 상태를 더 직접 볼 수 있다.
- 단점
  - PR 생성 규칙을 플러그인만으로 완결하기 어렵다.
  - 핵심 자동화는 여전히 외부 스크립트가 필요하다.

### 3. 상시 파일 감시 데몬

- 장점
  - 반응 속도가 빠르다.
- 단점
  - Windows 상주 프로세스 관리가 번거롭다.
  - 저장 중간 상태나 파일 잠금 이슈를 더 자주 만날 수 있다.

## 선택안

`Windows Task Scheduler + PowerShell` 조합을 사용한다.

선정 이유:

- 요구된 15분 주기 검사와 가장 잘 맞는다.
- 장기 드래프트 PR 1개 유지 규칙을 구현하기 쉽다.
- 현재 PC에서 이미 확인된 `git`, `gh`, GitHub HTTPS 인증 구성을 그대로 쓸 수 있다.

## 아키텍처

### 구성요소

1. PowerShell 자동화 스크립트 1개
   - Vault 변경 감지
   - 브랜치 준비
   - 커밋 및 푸시
   - 기존 드래프트 PR 조회
   - 필요 시 새 드래프트 PR 생성
   - 로그 기록
2. Windows 예약 작업 1개
   - 15분마다 실행
   - 사용자 로그인 상태에서 동작
3. 로그 파일 1개
   - 성공, 변경 없음, 실패 사유 기록
4. 잠금 파일 1개
   - 중복 실행 방지

### 파일 배치 제안

- 스크립트: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.ps1`
- 로그: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.log`
- 잠금 파일: `C:\Users\User\Documents\Obsidian Vault\.obsidian\automation\obsidian-auto-pr.lock`

## 데이터 흐름

1. 예약 작업이 15분마다 PowerShell 스크립트를 실행한다.
2. 스크립트는 잠금 파일을 확인해 중복 실행이면 즉시 종료한다.
3. Vault에서 `git status --porcelain`로 변경 여부를 검사한다.
4. 변경이 없으면 로그만 남기고 종료한다.
5. 변경이 있으면 `obsidian/auto-sync` 브랜치로 이동한다.
6. 변경 파일을 스테이징하고 자동 커밋한다.
7. `origin/obsidian/auto-sync`로 푸시한다.
8. GitHub에서 `main <- obsidian/auto-sync` 열린 드래프트 PR을 조회한다.
9. 기존 PR이 있으면 그대로 유지한다.
10. 기존 PR이 없으면 새 드래프트 PR을 생성한다.
11. 결과를 로그에 남기고 잠금 파일을 해제한다.

## 브랜치 및 PR 규칙

### 브랜치 규칙

- 기본 작업 기준은 `main`이다.
- 자동화 스크립트는 커밋 직전 `obsidian/auto-sync` 브랜치에 있어야 한다.
- 원격 브랜치가 없으면 최초 푸시 시 생성한다.

### PR 규칙

- PR 제목은 고정 문자열 `Obsidian auto sync`를 기본값으로 사용한다.
- PR 본문은 자동 생성 텍스트로 충분하며, 최근 실행 시각과 목적만 포함한다.
- 열린 드래프트 PR이 있으면 재사용한다.
- 닫힌 PR은 재사용하지 않는다.
- 머지 완료 후 다음 변경이 생기면 새 드래프트 PR을 만든다.

## 커밋 규칙

- 커밋 메시지는 시간 기반 자동 메시지를 사용한다.
- 예시: `Auto sync Obsidian notes 2026-07-04 14:30`
- 한 주기 내 모든 변경은 하나의 커밋으로 묶는다.

## 오류 처리

### 실패 시 동작

- `git` 명령 실패: 로그 남기고 종료
- `gh` 명령 실패: 로그 남기고 종료
- 브랜치 체크아웃 실패: 로그 남기고 종료
- 푸시 실패: 로그 남기고 종료
- PR 생성 실패: 로그 남기고 종료

### 충돌 정책

- 자동 rebase, merge, conflict resolution은 하지 않는다.
- 충돌 또는 비정상 상태를 감지하면 로그에 남기고 다음 주기에서 다시 시도한다.

## 제외 파일 정책

다음 파일은 계속 Git 추적 제외 상태를 유지한다.

- `.obsidian/workspace.json`
- `.obsidian/workspace-mobile.json`
- `.obsidian/cache`
- `.obsidian/plugins/obsidian-git/data.json`

이 정책은 사용자의 개인 UI 상태와 플러그인 런타임 상태가 PR에 섞이지 않도록 하기 위함이다.

## 관찰 가능성

로그에는 최소한 아래 정보를 남긴다.

- 실행 시작 시각
- 변경 없음 여부
- 커밋 SHA
- 푸시 성공 여부
- PR 재사용 또는 신규 생성 여부
- 실패 메시지

## 테스트 계획

### 시나리오 1. 최초 변경

- 노트 파일 1개 수정
- 다음 주기 실행
- 기대 결과
  - `obsidian/auto-sync` 브랜치 생성
  - 자동 커밋 및 푸시
  - 새 드래프트 PR 생성

### 시나리오 2. 후속 변경

- 다른 노트 또는 동일 노트 추가 수정
- 다음 주기 실행
- 기대 결과
  - 기존 드래프트 PR 유지
  - 새 커밋만 기존 PR에 누적

### 시나리오 3. 변경 없음

- Vault 미수정 상태 유지
- 다음 주기 실행
- 기대 결과
  - 커밋 없음
  - 푸시 없음
  - PR 생성 없음
  - 로그에 `no changes` 기록

### 시나리오 4. 원격 실패

- 네트워크 또는 인증 문제를 인위적으로 발생
- 기대 결과
  - 로그에 실패 원인 기록
  - 로컬 변경은 유지
  - 다음 주기 재시도 가능

## 구현 시 주의점

- PowerShell 스크립트는 Git 작업 디렉터리를 Vault 루트로 고정해야 한다.
- 예약 작업은 `gh auth status`가 이미 유효한 현재 사용자 컨텍스트로 실행되어야 한다.
- 자동화가 사용자의 수동 Git 작업과 충돌하지 않도록 잠금 파일과 브랜치 상태 검사를 반드시 둔다.
- 사용자가 수동으로 Obsidian Git 플러그인을 사용할 수는 있지만, 자동 PR 생성의 기준 상태는 스크립트가 관리한다.

## 구현 후 완료 기준

아래가 모두 충족되면 완료로 본다.

1. 15분 예약 작업이 생성되어 있다.
2. 자동화 스크립트가 Vault에 배치되어 있다.
3. 최초 변경 시 드래프트 PR이 자동 생성된다.
4. 후속 변경 시 같은 PR에 커밋이 누적된다.
5. 변경 없음 시 불필요한 GitHub 작업이 발생하지 않는다.
