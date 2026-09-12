# Running on remote compute

Long tree builds and thorough queries should run on the machine that hosts Ollama. This
avoids laptop-local forwarding and lets jobs survive sleep, lid closure, and disconnects.

## One-time setup

```bash
ssh <user>@<compute-host>
git clone https://github.com/asharma395/treerag.git
cd treerag
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[build,test]'
ollama pull gpt-oss:120b
curl -fsS http://127.0.0.1:11434/api/version
```

Do not bind Ollama to an internet-facing interface. Keep the corpus, caches, code, and
model endpoint inside the same approved trust boundary.

## Persistent session

```bash
tmux new -s treerag
cd ~/treerag
source .venv/bin/activate
export TREERAG_OLLAMA_URL=http://127.0.0.1:11434
export TREERAG_MODEL=gpt-oss:120b
./scripts/build_tree.sh
```

Detach with `Ctrl-b`, then `d`. Reconnect later with `tmux attach -t treerag`.
The job remains on the compute host after SSH disconnects or the laptop sleeps.

## Query the committed tree

```bash
tmux new -s treerag-query
cd ~/treerag
source .venv/bin/activate
export TREERAG_OLLAMA_URL=http://127.0.0.1:11434
./scripts/query_single_question.sh "Your question"
```

For shared production service, replace `tmux` with the site's scheduler or a supervised
service account. Never store passwords or tokens in shell scripts, `.env`, Git history,
job logs, or command-line arguments.
