🌐 **Language / 言語**: [English](../../README.md) | [简体中文](README_ZH.md) | [繁體中文](README_TW.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Русский](README_RU.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [हिन्दी](README_HI.md)

[![Python](https://img.shields.io/badge/python-3.13+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](../../LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-blueviolet?style=flat)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/issues)
[![Last Commit](https://img.shields.io/github/last-commit/rmc8/py-obsidian-tools?style=flat)](https://github.com/rmc8/py-obsidian-tools/commits)

# py-obsidian-tools

Local REST API 커뮤니티 플러그인을 통해 Obsidian과 상호작용하는 MCP 서버입니다.

## 구성 요소

### 도구

서버는 Obsidian과 상호작용하기 위한 여러 도구를 구현합니다:

| 도구 | 설명 |
|------|------|
| `list_notes` | 볼트 또는 특정 디렉토리의 모든 노트 목록 |
| `read_note` | 특정 노트의 내용 읽기 |
| `search_notes` | 특정 텍스트를 포함한 노트 검색 |
| `create_note` | 선택적 frontmatter를 포함한 새 노트 생성 |
| `update_note` | 노트의 전체 내용 업데이트(교체) |
| `append_note` | 노트 끝에 내용 추가 |
| `delete_note` | 볼트에서 노트 삭제 |
| `patch_note` | 특정 섹션(제목/블록/frontmatter) 업데이트 |
| `list_commands` | 사용 가능한 모든 Obsidian 명령 목록 |
| `execute_command` | Obsidian 명령 실행 |
| `batch_read_notes` | 여러 노트를 한 번에 읽기 |
| `complex_search` | 고급 필터링을 위한 JsonLogic 쿼리 검색 |
| `get_recent_changes` | 최근 수정된 파일 가져오기 (Dataview 플러그인 필요) |
| `get_periodic_note` | 오늘의 일간/주간/월간 노트 가져오기 (Periodic Notes 플러그인 필요) |
| `open_note` | Obsidian UI에서 노트 열기 |
| `get_active_note` | 현재 활성 노트 가져오기 |
| `update_active_note` | 활성 노트의 내용 업데이트 |
| `append_active_note` | 활성 노트에 내용 추가 |
| `patch_active_note` | 활성 노트의 특정 섹션 업데이트 |
| `delete_active_note` | 현재 활성 노트 삭제 |
| `server_status` | Obsidian Local REST API 서버 상태 가져오기 |
| `dataview_query` | Dataview DQL 쿼리 실행 (Dataview 플러그인 필요) |
| `vector_search` | 자연어를 사용한 의미 검색 (vector extras 필요) |
| `find_similar_notes` | 지정된 노트와 유사한 노트 찾기 (vector extras 필요) |
| `vector_status` | 벡터 검색 인덱스 상태 가져오기 (vector extras 필요) |

### 예시 프롬프트

먼저 Claude에게 Obsidian을 사용하도록 지시하는 것이 좋습니다. 그러면 항상 도구를 호출합니다.

다음과 같은 프롬프트를 사용할 수 있습니다:
- "'Daily' 폴더의 모든 노트를 나열해줘"
- "'프로젝트 X'를 언급하는 모든 노트를 검색하고 요약해줘"
- "우리 토론 내용으로 '회의 노트'라는 새 노트를 만들어줘"
- "내 일일 노트에 'TODO: PR 검토'를 추가해줘"
- "활성 노트의 내용을 가져와서 비평해줘"
- "complex search를 사용하여 Work 폴더의 모든 markdown 파일을 찾아줘"
- "의미 검색을 사용하여 머신러닝에 관한 노트를 검색해줘"
- "내 프로젝트 계획과 비슷한 노트를 찾아줘"
- "Dataview 쿼리를 실행하여 #project 태그가 있는 모든 노트를 나열해줘"
- "오늘의 일일 노트를 가져와줘"
- "활성 노트의 '작업' 섹션을 업데이트해줘"
- "Obsidian API 서버 상태를 확인해줘"

## 설정

### Obsidian REST API 키

Obsidian REST API 키로 환경을 설정하는 두 가지 방법이 있습니다.

1. 서버 설정에 추가 (권장)

```json
{
  "mcpServers": {
    "obsidian-tools": {
      "command": "uvx",
      "args": ["py-obsidian-tools"],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
}
```

2. 작업 디렉토리에 다음 필수 변수를 포함한 `.env` 파일 생성:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27124
```

참고:
- Obsidian 플러그인 설정에서 API 키를 찾을 수 있습니다 (설정 > Local REST API > 보안)
- 기본 포트는 27124입니다
- 기본 호스트는 127.0.0.1 (localhost)입니다

## 빠른 시작

### 설치

#### Obsidian REST API

Obsidian REST API 커뮤니티 플러그인이 실행 중이어야 합니다: https://github.com/coddingtonbear/obsidian-local-rest-api

설정에서 설치하고 활성화한 후 API 키를 복사하세요.

#### Claude Desktop

MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

Windows: `%APPDATA%/Claude/claude_desktop_config.json`

**권장: PyPI에서 설치 (uvx)**

```json
{
  "mcpServers": {
    "obsidian-tools": {
      "command": "uvx",
      "args": ["py-obsidian-tools"],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
}
```

<details>
  <summary>개발/미게시 서버 설정</summary>

```json
{
  "mcpServers": {
    "obsidian-tools": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/py-obsidian-tools",
        "run",
        "py-obsidian-tools"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>"
      }
    }
  }
}
```
</details>

<details>
  <summary>GitHub에서 설치 (uvx)</summary>

```json
{
  "mcpServers": {
    "obsidian-tools": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/rmc8/py-obsidian-tools",
        "py-obsidian-tools"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>"
      }
    }
  }
}
```
</details>

## 벡터 검색 (선택 사항)

ChromaDB를 사용한 의미 검색 기능입니다. 이 기능을 사용하면 볼트 전체에서 자연어 쿼리가 가능합니다.

### 설치

**uvx 사용 (권장)**:

```bash
# 설치 불필요 - uvx로 직접 실행
uvx --from 'py-obsidian-tools[vector]' pyobsidian-index full --verbose

# 외부 임베딩 제공자 사용
uvx --from 'py-obsidian-tools[vector-openai]' pyobsidian-index full --verbose
uvx --from 'py-obsidian-tools[vector-google]' pyobsidian-index full --verbose
uvx --from 'py-obsidian-tools[vector-cohere]' pyobsidian-index full --verbose
```

**uv 사용 (개발용)**:

```bash
# 기본 (로컬 임베딩 - API 키 불필요)
uv sync

# 외부 임베딩 제공자 사용
uv sync --extra vector-openai
uv sync --extra vector-google
uv sync --extra vector-cohere
uv sync --extra vector-all

# 인덱서 실행
uv run pyobsidian-index full --verbose
```

**pip 사용**:

```bash
# 기본 (로컬 임베딩 - API 키 불필요)
pip install "py-obsidian-tools[vector]"

# 외부 임베딩 제공자 사용
pip install "py-obsidian-tools[vector-openai]"
pip install "py-obsidian-tools[vector-google]"
pip install "py-obsidian-tools[vector-cohere]"
pip install "py-obsidian-tools[vector-all]"
```

### 인덱스 생성

벡터 검색을 사용하기 전에 볼트의 인덱스를 생성해야 합니다:

```bash
# uvx 사용 (권장 - 설치 불필요)
uvx --from 'py-obsidian-tools[vector]' pyobsidian-index full --verbose

# uv 사용 (개발용)
uv run pyobsidian-index full --verbose

# pip로 설치된 경우
pyobsidian-index full --verbose
```

> **참고**: `pyobsidian-index` 명령에는 `[vector]` extras가 필요합니다. uvx를 사용할 때 패키지 사양에 `[vector]`를 포함해야 합니다. `[vector]` 없이 `uvx --from py-obsidian-tools pyobsidian-index`를 실행하면 실패합니다.

### CLI 명령

```bash
# uvx 사용
uvx --from 'py-obsidian-tools[vector]' pyobsidian-index <명령>

# uv 사용 (개발용)
uv run pyobsidian-index <명령>

# pip 설치 사용
pyobsidian-index <명령>
```

| 명령 | 설명 |
|------|------|
| `full` | 볼트의 모든 노트 인덱싱 |
| `update` | 증분 업데이트 (신규/수정된 노트만) |
| `clear` | 전체 인덱스 삭제 |
| `status` | 인덱스 상태 표시 |

### 환경 변수

```bash
VECTOR_PROVIDER=default          # default, ollama, openai, google, cohere
VECTOR_CHROMA_PATH=~/.obsidian-vector
VECTOR_CHUNK_SIZE=512

# Ollama용
VECTOR_OLLAMA_HOST=http://localhost:11434
VECTOR_OLLAMA_MODEL=nomic-embed-text

# OpenAI용
VECTOR_OPENAI_API_KEY=sk-xxx
VECTOR_OPENAI_MODEL=text-embedding-3-small

# Google용
VECTOR_GOOGLE_API_KEY=xxx
VECTOR_GOOGLE_MODEL=embedding-001

# Cohere용
VECTOR_COHERE_API_KEY=xxx
VECTOR_COHERE_MODEL=embed-multilingual-v3.0
```

### 임베딩 제공자

| 제공자 | 모델 | 최적 용도 |
|--------|------|----------|
| default | all-MiniLM-L6-v2 | 빠름, 무료, 완전 로컬 |
| ollama | nomic-embed-text | 고품질, 로컬 |
| openai | text-embedding-3-small | 최고 품질, 다국어 |
| google | embedding-001 | Google AI 통합 |
| cohere | embed-multilingual-v3.0 | 다국어 전문 |

## 개발

### 빌드

패키지 배포 준비:

1. 의존성 동기화 및 잠금 파일 업데이트:
```bash
uv sync
```

### 디버깅

MCP 서버는 stdio를 통해 실행되므로 디버깅이 어려울 수 있습니다. 최상의 디버깅 경험을 위해 [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 사용을 강력히 권장합니다.

다음 명령으로 `npx`를 통해 MCP Inspector를 시작할 수 있습니다:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/py-obsidian-tools run py-obsidian-tools
```

시작 후 Inspector가 브라우저에서 접속하여 디버깅을 시작할 수 있는 URL을 표시합니다.

서버 로그를 확인하거나 (설정된 경우) 표준 Python 로깅을 사용할 수도 있습니다.
