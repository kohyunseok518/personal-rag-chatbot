# Personal Knowledge RAG Chatbot

개인 문서를 기반으로 질문에 답변하는 로컬 웹 RAG 챗봇입니다.  
문서를 작은 단위로 분할하고 벡터화하여 FAISS에 저장한 뒤, 사용자 질문과 관련된 문서를 검색해 LLM이 근거 기반 답변을 생성합니다.

이 프로젝트는 단순한 기능 구현을 넘어, 실제 서비스 개발처럼 각 계층의 역할과 책임을 명확하게 분리하는 것을 목표로 합니다.

## 1. 프로젝트 목표

- 개인 문서를 기반으로 한 질의응답 기능 구현
- 검색된 문서에 근거한 답변과 출처 제공
- 문서 색인 과정과 사용자 질의 과정을 분리
- FastAPI를 이용한 REST API 제공
- HTML, CSS, JavaScript 기반의 간단한 채팅 화면 제공
- Docker를 이용한 동일한 로컬 실행 환경 구성
- GitHub Actions를 이용한 자동 테스트 및 빌드 검증
- 계층 간 의존성을 낮춰 검색 방식과 LLM을 쉽게 교체할 수 있는 구조 설계

## 2. 전체 동작 구조

```text
[문서 색인 과정]

원문 파일
   ↓
문서 로더
   ↓
전처리 및 청킹
   ↓
OpenAI 임베딩
   ↓
FAISS 인덱스 저장


[질문 응답 과정]

사용자
   ↓
HTML / CSS / JavaScript
   ↓ REST API
FastAPI
   ↓
Chat Use Case
   ↓
FAISS 관련 문서 검색
   ↓
프롬프트 구성
   ↓
OpenAI LLM 답변 생성
   ↓
답변 및 출처 반환
```

## 3. 핵심 설계 원칙

### 역할과 책임 분리

- `api`: HTTP 요청과 응답만 처리합니다.
- `application`: 사용자의 요청을 하나의 업무 흐름으로 조정합니다.
- `domain`: 핵심 데이터 모델과 인터페이스를 정의합니다.
- `infrastructure`: OpenAI, FAISS, 파일 시스템 등 외부 기술을 구현합니다.
- `web`: 사용자에게 보여줄 정적 웹 화면을 담당합니다.

### 의존성 방향

```text
API → Application → Domain
                    ↑
              Infrastructure
```

상위 계층은 FAISS나 OpenAI의 구체적인 사용 방법을 직접 알지 않습니다.  
`domain`에 정의된 인터페이스를 `infrastructure`가 구현하도록 구성하여 외부 기술 교체의 영향을 줄입니다.

예를 들어 FAISS를 다른 벡터 저장소로 변경하더라도, 검색 인터페이스가 유지된다면 API와 애플리케이션 로직은 최대한 수정하지 않습니다.

## 4. 프로젝트 폴더 구조

```text
personal-rag-chatbot/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── exception_handlers.py
│   │   └── routes/
│   │       ├── chat.py
│   │       └── health.py
│   │
│   ├── application/
│   │   ├── dto/
│   │   │   ├── chat_request.py
│   │   │   ├── chat_response.py
│   │   │   └── source_response.py
│   │   └── services/
│   │       ├── chat_service.py
│   │       └── indexing_service.py
│   │
│   ├── domain/
│   │   ├── models/
│   │   │   ├── document.py
│   │   │   ├── retrieved_chunk.py
│   │   │   └── generated_answer.py
│   │   └── ports/
│   │       ├── document_loader.py
│   │       ├── chunker.py
│   │       ├── embedding_provider.py
│   │       ├── vector_store.py
│   │       └── answer_generator.py
│   │
│   ├── infrastructure/
│   │   ├── document/
│   │   │   ├── text_document_loader.py
│   │   │   └── recursive_text_chunker.py
│   │   ├── embedding/
│   │   │   └── openai_embedding_provider.py
│   │   ├── vector_store/
│   │   │   └── faiss_vector_store.py
│   │   └── llm/
│   │       ├── openai_answer_generator.py
│   │       └── prompts.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   └── web/
│       ├── index.html
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── chat.js
│
├── data/
│   ├── raw/
│   └── vector_store/
│
├── scripts/
│   └── build_index.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 5. 계층별 책임

### API 계층

FastAPI 라우터를 이용해 외부 요청을 받습니다.

- 요청 데이터 검증
- 애플리케이션 서비스 호출
- HTTP 응답 코드와 응답 형식 결정
- 공통 예외 응답 처리

검색, 임베딩, 프롬프트 생성과 같은 내부 구현은 API 계층에 작성하지 않습니다.

### Application 계층

하나의 사용자 요청이 완료되기까지의 업무 순서를 조정합니다.

`ChatService`의 주요 책임:

1. 질문 검증
2. 관련 문서 검색 요청
3. 검색 결과를 이용한 답변 생성 요청
4. 답변과 출처를 응답 객체로 변환

`IndexingService`의 주요 책임:

1. 문서 로드
2. 문서 전처리 및 청킹
3. 임베딩 생성
4. 벡터 인덱스 저장

### Domain 계층

프로젝트의 핵심 개념과 외부 기술에 의존하지 않는 인터페이스를 정의합니다.

- 문서
- 검색된 청크
- 생성된 답변
- 문서 로더 인터페이스
- 청킹 인터페이스
- 벡터 검색 인터페이스
- 답변 생성 인터페이스

### Infrastructure 계층

도메인 인터페이스의 실제 구현을 담당합니다.

- TXT 파일 로드
- LangChain 텍스트 분할
- OpenAI 임베딩 API 호출
- FAISS 인덱스 저장 및 검색
- OpenAI 모델을 이용한 답변 생성

### Web 계층

별도의 프론트엔드 프레임워크 없이 HTML, CSS, JavaScript로 구성합니다.

- 질문 입력
- `/api/chat` 호출
- 로딩 및 오류 상태 표시
- 답변과 출처 표시

## 6. API 초안

### 상태 확인

```http
GET /api/health
```

응답 예시:

```json
{
  "status": "ok"
}
```

### 문서 기반 질문

```http
POST /api/chat
Content-Type: application/json
```

요청 예시:

```json
{
  "question": "이 문서에서 설명하는 핵심 내용은 무엇인가요?"
}
```

응답 예시:

```json
{
  "answer": "검색된 문서를 기반으로 생성된 답변입니다.",
  "sources": [
    {
      "document_name": "sample.txt",
      "chunk_id": "sample-001",
      "content": "답변의 근거로 사용한 문서 내용"
    }
  ],
  "grounded": true
}
```

## 7. 기술 스택

### Backend

- Python 3.12
- FastAPI
- Uvicorn
- LangChain
- Pydantic

### RAG

- Document Loader
- Recursive text chunking
- OpenAI Embeddings
- FAISS
- OpenAI API

### Frontend

- HTML
- CSS
- JavaScript
- Fetch API

### Development

- Docker
- Docker Compose
- Pytest
- GitHub Actions

## 8. 환경 변수

`.env.example`을 복사하여 `.env` 파일을 생성합니다.

```env
OPENAI_API_KEY=your_api_key
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_PATH=data/vector_store
RAW_DOCUMENT_PATH=data/raw
```

`.env`에는 실제 API 키가 포함되므로 Git에 커밋하지 않습니다.

## 9. 로컬 실행 목표

```bash
docker compose up --build
```

실행 후 브라우저에서 다음 주소로 접속합니다.

```text
http://localhost:8000
```

## 10. 테스트 전략

### 단위 테스트

- 문서 전처리 결과 검증
- 청크 크기와 중첩 검증
- 요청 및 응답 객체 검증
- 검색 결과가 없는 경우의 서비스 동작 검증
- 외부 API를 가짜 객체로 교체한 답변 생성 테스트

### 통합 테스트

- FastAPI 엔드포인트 요청 및 응답 검증
- 테스트 문서를 이용한 FAISS 저장 및 검색 검증
- 검색 결과와 반환된 출처의 일치 여부 검증

실제 OpenAI API 호출 테스트는 일반 테스트와 분리하여 불필요한 비용 발생을 막습니다.

## 11. CI 범위

GitHub Actions는 AWS 배포가 아닌 코드 품질 검증에 사용합니다.

```text
GitHub Push
   ↓
의존성 설치
   ↓
단위 테스트
   ↓
통합 테스트
   ↓
Docker 이미지 빌드 확인
```

## 12. 보안 원칙

- OpenAI API 키는 브라우저 코드에 포함하지 않습니다.
- API 키는 FastAPI 서버의 환경 변수로만 관리합니다.
- `.env`와 생성된 로컬 인덱스는 Git에 올리지 않습니다.
- 사용자 질문과 검색 문서 전체를 불필요하게 로그에 남기지 않습니다.
- 검색된 근거가 없으면 추측성 답변 대신 답변 불가 상태를 반환합니다.

## 13. 개발 단계

- [v] 프로젝트 기본 구조 생성
- [v] 설정 및 공통 예외 처리 구현
- [ ] 문서 로더 구현
- [ ] 청킹 구현
- [ ] 임베딩 및 FAISS 저장 구현
- [ ] 문서 검색 구현
- [ ] RAG 답변 생성 구현
- [ ] FastAPI 엔드포인트 구현
- [ ] 웹 채팅 화면 구현
- [ ] Docker 환경 구성
- [ ] 단위 및 통합 테스트 작성
- [ ] GitHub Actions 구성

## 14. 현재 범위에서 제외하는 기능

- AWS 및 외부 서버 배포
- 사용자 회원가입과 인증
- 대화 내역 데이터베이스 저장
- 문서 업로드 관리 화면
- PDF 및 이미지 OCR
- BM25 하이브리드 검색
- 리랭킹
- 관리자 페이지

위 기능은 기본 RAG 웹 서비스가 안정적으로 동작한 이후 확장합니다.
