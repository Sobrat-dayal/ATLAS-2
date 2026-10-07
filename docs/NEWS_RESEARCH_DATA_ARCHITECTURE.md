# News and Research Data Architecture

ATLAS maintains a clear distinction between the real-world events or concepts being described, and the media that describes them.

## News Domain
The `atlas.news` domain package establishes canonical contracts for interacting with News Providers. 

### Key Principles
1. **News Article != News Event**:
   A `NewsArticle` is a canonical, immutable representation of a piece of media published by a specific publisher at a specific time. 
   A `NewsEvent` (from the Stage 20 Entity System) represents a real-world occurrence (e.g., an M&A Announcement) that might be described by many `NewsArticle`s.
   
2. **Offline Validation**:
   Canonical models in `atlas.news.articles` are strict Pydantic V2 definitions that perform offline validation of payloads without database or network connections.

3. **No Ingestion**:
   Stage 36 does not perform content ingestion. The abstractions define how ATLAS asks providers for news metadata, not how it persists or pipelines full-text content.

### Contracts
- `NewsArticle`: The canonical article representation (`title`, `publisher`, `published_at`, `summary`, etc.).
- `NewsDataOrigin`: Provenance for the news metadata extraction, distinct from the global Stage 24 Provenance.
- `NewsProviderCapabilities`: Capability reporting for News functionality.
- `NewsProvider`: The Python Protocol that must be implemented by News providers.

## Research Domain
The `atlas.research` domain package establishes canonical contracts for interacting with Research Document providers (e.g., academic databases, open-access repos).

### Key Principles
1. **Alignment with Stage 20 Entity**:
   The `ResearchMetadata` model mirrors the attributes expected by the `ResearchDocument` entity (`document_kind`, `publication_date`, `language_code`, `abstract_text`).
   
2. **Metadata Focus**:
   The domain models describe research metadata, not the binary contents of the research papers themselves.

3. **Strict Boundaries**:
   Domain packages do not depend on external frameworks like FastAPI, pandas, or specific API clients like arxiv or OpenAlex.

### Contracts
- `ResearchMetadata`: The canonical research document metadata.
- `ResearchDataOrigin`: Provenance for the research metadata extraction.
- `ResearchProviderCapabilities`: Capability reporting for Research functionality.
- `ResearchProvider`: The Python Protocol that must be implemented by Research providers.
