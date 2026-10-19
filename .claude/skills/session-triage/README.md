# session-triage（取り込み版）

出典: https://github.com/chaenmasahiro0425/claude-session-triage （MIT, commit 7308dfd）
`SKILL.md` と `LICENSE` は原本のまま。`config.example.json` だけこのリポジトリ用に変えている。

- `folder_rules`: `D:\MyDocument\ClaudeApp\GadgetTerminal` 配下を【GT】【GT記事】【GT特集】にする（`\` と `/` の両方に当たる）
- `notify`: false（通知は macOS 専用で Windows では出ないため）

## 動く条件

Claude デスクトップアプリの **Codeタブ** でだけ動く（`mcp__ccd_session_mgmt__*` を使うため）。
クラウドのセッションや GitHub Actions からは動かない。

プロジェクトのスキルなので、作業フォルダがこのリポジトリのセッションで読み込まれる。
どのフォルダからでも使いたい場合は、このフォルダを `%USERPROFILE%\.claude\skills\session-triage` にコピーする。

## 使い方

1. 設定を自分用に変えたいときは `config.example.json` を `%USERPROFILE%\.claude\session-triage\config.json` にコピーして直す（無ければこのフォルダの値を使う）
2. Codeタブで「セッションを整理して」で1回動く
3. 「session-triage を15分おきに定期実行して」で定期実行に載る（アプリが開いている間だけ動く）

`state.json` / `log.md` / `latest.md` は `%USERPROFILE%\.claude\session-triage\` に書かれ、リポジトリには入らない。
