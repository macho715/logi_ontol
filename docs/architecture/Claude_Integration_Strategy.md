# 🏗️ C:\logi_ontol ↔ Claude 시스템 통합 마스터플랜
## MACHO-GPT v3.4-mini Enhanced Integration Strategy

**작성일**: 2025-10-24
**버전**: 1.0
**프로젝트**: HVDC Project - Samsung C&T Logistics (ADNOC·DSV Partnership)

---

## 📊 EXECUTIVE SUMMARY

C:\logi_ontol은 HVDC 프로젝트를 위한 **물류 온톨로지 시스템**으로, 현재 Python 기반으로 구축되어 있습니다. 본 통합 전략은 이를 Claude의 네이티브 도구들과 완전히 통합하여 **자동화된 지능형 물류 관리 시스템**을 구축하는 것을 목표로 합니다.

### 핵심 목표
1. **완전 자동화**: logi_ontol → Claude Tools → Automated Workflows
2. **실시간 OCR**: PDF/Image → AI-OCR → Knowledge Graph → Decision
3. **지식 통합**: RDF Ontology + Claude RAG + Google Drive + Web Search
4. **운영 최적화**: Manual 60%↓, Error 85%↓, Response Time 70%↓

---

## 🗺️ 현재 시스템 구조 분석

### C:\logi_ontol 디렉토리 맵

```
C:\logi_ontol/ (117MB compressed)
├── logiontology/                    # 🎯 핵심 온톨로지 엔진
│   ├── src/
│   │   ├── core/                    # 도메인 모델 & 계약
│   │   ├── mapping/                 # 온톨로지 매핑 (v2.6)
│   │   ├── validation/              # SHACL 스키마 검증
│   │   ├── ingest/                  # Excel 데이터 수집
│   │   ├── rdfio/                   # RDF 읽기/쓰기
│   │   ├── reasoning/               # AI 추론 엔진
│   │   └── pipeline/                # 워크플로우 파이프라인
│   ├── configs/                     # ⚙️ 설정
│   │   ├── mapping_rules.v2.6.yaml  # 매핑 규칙
│   │   ├── lightning_sparql_queries.sparql
│   │   ├── abu_sparql_queries.sparql
│   │   └── shacl_shapes.ttl         # 검증 스키마
│   ├── tests/ (92% coverage)        # ✅ 테스트
│   └── docs/                        # 📚 아키텍처 문서
│
├── JPT71/                           # 🚢 Jopetwil 71 선박 운영 데이터
│   ├── ADNOC-TR *.pdf              # ADNOC 운송 문서 (20+)
│   ├── IMG-*.jpg (400+ files)      # WhatsApp 현장 이미지
│   ├── Manifest *.pdf              # 선박 매니페스트
│   ├── *선원명*.pdf                 # 선원 문서 (HARJOT, SOHAN, JAGBIR 등)
│   └── WhatsApp 대화.txt/zip       # 운영 로그 (357KB, 완전한 대화 기록)
│
├── HVDC Project Lightning/          # ⚡ Lightning 서브시스템
│   ├── whatsapp_output/
│   ├── IMG-*.jpg (50+ files)       # 현장 사진
│   ├── Logistics_Entities__Summary_.csv
│   └── Guideline_HVDC_Project_lightning.md
│
├── data/                            # 📂 입력 데이터
│   └── *.xlsx                       # Excel 물류 데이터
│
├── output/                          # 📤 RDF 출력
│   ├── final/
│   │   ├── abu_final.ttl
│   │   └── lightning_final.ttl
│   └── versions/                    # 버전 아카이브
│
├── reports/                         # 📊 시스템 보고서
│   ├── final/
│   │   ├── SYSTEM_ARCHITECTURE_COMPREHENSIVE.md
│   │   ├── HVDC_MASTER_INTEGRATION_REPORT.md
│   │   ├── ABU_SYSTEM_ARCHITECTURE.md
│   │   └── LIGHTNING_FINAL_INTEGRATION_REPORT.md
│   ├── architecture/
│   ├── analysis/
│   └── operations/
│
├── scripts/                         # 🔧 처리 스크립트
│   ├── process_hvdc_excel.py
│   ├── integrate_lightning_images.py
│   ├── build_lightning_cross_references.py
│   ├── generate_final_lightning_report.py
│   └── compare_abu_lightning.py
│
├── ontology_unified/                # 🧬 통합 온톨로지
├── ABU/                             # 아부다비 특화 데이터
├── cursor_ontology_first_pack_v1/   # Cursor 통합 시도 (v1)
└── archive/                         # 아카이브

⚠️ 접근 제약: C:\logi_ontol은 Claude filesystem 도구로 직접 접근 불가
✅ 해결 방안: Windows-MCP PowerShell 또는 심볼릭 링크/복사 필요
```

### 기존 시스템 강점
- ✅ **92% 테스트 커버리지** - 안정적인 코드베이스
- ✅ **RDF 기반 온톨로지** - 표준화된 지식 표현
- ✅ **SHACL 검증** - 데이터 품질 보장
- ✅ **SPARQL 쿼리** - 강력한 지식 검색
- ✅ **실제 운영 데이터** - JPT71, Lightning 프로젝트
- ✅ **완전한 문서화** - 아키텍처 보고서 완비

### 기존 시스템 한계
- ⚠️ **수동 프로세스** - 스크립트 수동 실행 필요
- ⚠️ **제한적 OCR** - PDF/이미지 자동 처리 부족
- ⚠️ **파편화된 데이터** - WhatsApp, Excel, PDF 분산
- ⚠️ **단방향 워크플로우** - 피드백 루프 부족
- ⚠️ **제한적 AI** - 추론 엔진 활용도 낮음

---

## 🎯 통합 전략: 3-Phase Roadmap

### **PHASE 1: 브릿징 & 인덱싱 (2주)**
#### 목표: C:\logi_ontol을 Claude 생태계로 연결

**1.1 디렉토리 브릿징**

**Option A: 심볼릭 링크 생성 (권장)**
```powershell
# 관리자 권한 PowerShell에서 실행
New-Item -ItemType SymbolicLink `
  -Path "C:\cursor-mcp\logi_ontol_link" `
  -Target "C:\logi_ontol"
```

**Option B: 자동 동기화 스크립트**
```powershell
# C:\cursor-mcp\scripts\sync_logi_ontol.ps1
$source = "C:\logi_ontol"
$dest = "C:\cursor-mcp\logi_ontol_sync"
$exclude = @("node_modules", ".git", "__pycache__", "venv", ".ruff_cache")

# 미러 동기화 (변경사항만 복사)
robocopy $source $dest /MIR /XD $exclude /MT:8 /LOG+:sync.log

# 스케줄러 등록 (매 시간 자동 동기화)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\cursor-mcp\scripts\sync_logi_ontol.ps1"
Register-ScheduledTask -TaskName "LogiOntolSync" -Trigger $trigger -Action $action
```

**1.2 MCP 서버 통합**
```javascript
// C:\cursor-mcp\mcp\servers\logi-ontol-server.js
const MCPServer = require('@modelcontextprotocol/sdk/server/index.js');
const { exec } = require('child_process');
const fs = require('fs');

const server = new MCPServer({
  name: "logi-ontol",
  version: "1.0.0",
  capabilities: {
    tools: {
      "read_ontology": {
        description: "Read RDF ontology files (.ttl) from logi_ontol",
        inputSchema: {
          type: "object",
          properties: {
            path: { type: "string", description: "Relative path in logi_ontol" }
          },
          required: ["path"]
        }
      },
      "query_sparql": {
        description: "Execute SPARQL queries on HVDC knowledge graph",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "SPARQL query" }
          },
          required: ["query"]
        }
      },
      "validate_shacl": {
        description: "Validate logistics data against SHACL shapes",
        inputSchema: {
          type: "object",
          properties: {
            data_uri: { type: "string" },
            shape_uri: { type: "string" }
          }
        }
      },
      "process_invoice": {
        description: "Process invoice PDF through OCR pipeline",
        inputSchema: {
          type: "object",
          properties: {
            pdf_path: { type: "string" }
          },
          required: ["pdf_path"]
        }
      }
    }
  }
});

// Tool implementations
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  switch(name) {
    case 'read_ontology':
      const ttlPath = `C:/logi_ontol/${args.path}`;
      return { content: fs.readFileSync(ttlPath, 'utf8') };

    case 'query_sparql':
      // Execute Python script with SPARQL query
      return new Promise((resolve) => {
        exec(`python C:/logi_ontol/scripts/query_sparql.py "${args.query}"`,
          (error, stdout) => {
            resolve({ results: JSON.parse(stdout) });
          });
      });

    case 'validate_shacl':
      // Run SHACL validation
      return new Promise((resolve) => {
        exec(`python -m logiontology.validation --data ${args.data_uri} --shape ${args.shape_uri}`,
          { cwd: 'C:/logi_ontol/logiontology' },
          (error, stdout) => {
            resolve({ validation: JSON.parse(stdout) });
          });
      });

    case 'process_invoice':
      // Trigger OCR pipeline
      return new Promise((resolve) => {
        exec(`python C:/cursor-mcp/hvdc_automation/ocr_pipeline.py "${args.pdf_path}"`,
          (error, stdout) => {
            resolve({ entities: JSON.parse(stdout) });
          });
      });
  }
});

server.listen();
```

**1.3 인덱싱 & 메타데이터 생성**
```python
# C:\cursor-mcp\scripts\index_logi_ontol.py
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

def create_comprehensive_index():
    """Create searchable index of logi_ontol contents"""
    index = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_files": 0,
            "total_size_mb": 0,
            "ontologies": 0,
            "pdfs": 0,
            "images": 0,
            "scripts": 0
        },
        "ontologies": [],
        "scripts": [],
        "data_files": [],
        "reports": [],
        "operational_data": {
            "jpt71": {},
            "lightning": {}
        }
    }

    base_path = Path("C:/logi_ontol")

    # 1. Scan ontology files
    for ttl_file in (base_path / "output" / "final").glob("*.ttl"):
        file_info = {
            "path": str(ttl_file.relative_to(base_path)),
            "size": ttl_file.stat().st_size,
            "modified": datetime.fromtimestamp(ttl_file.stat().st_mtime).isoformat(),
            "checksum": calculate_checksum(ttl_file)
        }
        index["ontologies"].append(file_info)
        index["summary"]["total_files"] += 1
        index["summary"]["total_size_mb"] += file_info["size"] / (1024*1024)
        index["summary"]["ontologies"] += 1

    # 2. Scan JPT71 operational data
    jpt71_path = base_path / "JPT71"
    jpt71_index = {
        "pdfs": [],
        "images": [],
        "whatsapp_chat": None,
        "crew_documents": []
    }

    for pdf_file in jpt71_path.glob("*.pdf"):
        file_info = {
            "filename": pdf_file.name,
            "path": str(pdf_file.relative_to(base_path)),
            "size": pdf_file.stat().st_size,
            "type": classify_document(pdf_file.name)
        }

        if "ADNOC-TR" in pdf_file.name:
            file_info["document_type"] = "transport_request"
        elif "Manifest" in pdf_file.name:
            file_info["document_type"] = "manifest"
        elif pdf_file.name in ["HARJOT.pdf", "SOHAN.pdf", "JAGBIR.pdf"]:
            jpt71_index["crew_documents"].append(file_info)

        jpt71_index["pdfs"].append(file_info)
        index["summary"]["pdfs"] += 1

    # Count images
    jpt71_index["image_count"] = len(list(jpt71_path.glob("IMG-*.jpg")))
    index["summary"]["images"] += jpt71_index["image_count"]

    # WhatsApp chat
    chat_file = jpt71_path / "Jopetwil 71 Group님과의 WhatsApp 대화.txt"
    if chat_file.exists():
        jpt71_index["whatsapp_chat"] = {
            "path": str(chat_file.relative_to(base_path)),
            "size": chat_file.stat().st_size,
            "message_count": count_whatsapp_messages(chat_file)
        }

    index["operational_data"]["jpt71"] = jpt71_index

    # 3. Scan Lightning data
    lightning_path = base_path / "HVDC Project Lightning"
    lightning_index = {
        "csv_summary": None,
        "images": len(list(lightning_path.glob("IMG-*.jpg"))),
        "guideline": str(lightning_path / "Guideline_HVDC_Project_lightning (1).md")
    }

    csv_file = lightning_path / "Logistics_Entities__Summary_.csv"
    if csv_file.exists():
        lightning_index["csv_summary"] = {
            "path": str(csv_file.relative_to(base_path)),
            "size": csv_file.stat().st_size
        }

    index["operational_data"]["lightning"] = lightning_index
    index["summary"]["images"] += lightning_index["images"]

    # 4. Scan scripts
    scripts_path = base_path / "scripts"
    for py_file in scripts_path.glob("*.py"):
        index["scripts"].append({
            "name": py_file.name,
            "path": str(py_file.relative_to(base_path)),
            "purpose": extract_script_purpose(py_file)
        })
        index["summary"]["scripts"] += 1

    # 5. Scan reports
    reports_path = base_path / "reports" / "final"
    for md_file in reports_path.glob("*.md"):
        index["reports"].append({
            "title": md_file.stem,
            "path": str(md_file.relative_to(base_path)),
            "size": md_file.stat().st_size
        })

    # Save index
    output_path = Path("C:/cursor-mcp/logi_ontol_index.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"✅ Index created successfully!")
    print(f"   Total files: {index['summary']['total_files']}")
    print(f"   Total size: {index['summary']['total_size_mb']:.2f} MB")
    print(f"   Ontologies: {index['summary']['ontologies']}")
    print(f"   PDFs: {index['summary']['pdfs']}")
    print(f"   Images: {index['summary']['images']}")
    print(f"   Scripts: {index['summary']['scripts']}")

    return index

def calculate_checksum(file_path):
    """Calculate MD5 checksum of file"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def classify_document(filename):
    """Classify document type based on filename"""
    filename_lower = filename.lower()
    if 'invoice' in filename_lower:
        return 'invoice'
    elif 'manifest' in filename_lower:
        return 'manifest'
    elif 'tr' in filename_lower or 'transport' in filename_lower:
        return 'transport_request'
    else:
        return 'general'

def count_whatsapp_messages(chat_file):
    """Count messages in WhatsApp chat export"""
    with open(chat_file, 'r', encoding='utf-8') as f:
        content = f.read()
    import re
    # Pattern: [DD/MM/YYYY, HH:MM:SS] Sender: Message
    pattern = r'\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}\]'
    return len(re.findall(pattern, content))

def extract_script_purpose(py_file):
    """Extract purpose from script docstring"""
    with open(py_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) > 1 and '"""' in lines[0]:
            # Extract docstring
            for i, line in enumerate(lines[1:], 1):
                if '"""' in line:
                    return lines[1:i][0].strip()
    return py_file.stem.replace('_', ' ').title()

if __name__ == "__main__":
    create_comprehensive_index()
```

**산출물 (Phase 1):**
- ✅ C:\cursor-mcp\logi_ontol_sync/ (동기화된 데이터)
- ✅ logi_ontol_index.json (검색 인덱스)
- ✅ MCP 서버 logi-ontol 구성 완료
- ✅ 자동 동기화 스케줄러 등록

---

### **PHASE 2: AI-OCR & 지식 통합 (3주)**
#### 목표: 비정형 데이터를 구조화된 지식으로 변환

**2.1 AI-OCR 파이프라인 구축**

```python
# C:\cursor-mcp\hvdc_automation\ocr_pipeline.py
import os
import json
import base64
from pathlib import Path
from PIL import Image
import pytesseract
import anthropic
from pdf2image import convert_from_path

class LogisticsOCRPipeline:
    """
    Advanced OCR pipeline for logistics documents
    Target: 90%+ entity extraction accuracy
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.confidence_threshold = 0.90

    def process_document(self, file_path):
        """
        Main processing pipeline
        PDF/Image → Text + Entities → RDF
        """
        print(f"🔍 Processing: {file_path}")

        # 1. Extract text based on file type
        if file_path.endswith('.pdf'):
            text, images = self.extract_pdf(file_path)
        else:
            text = self.extract_image(file_path)
            images = [file_path]

        # 2. Classify document type
        doc_type = self.classify_document(text, images[0] if images else None)
        print(f"📄 Document type: {doc_type}")

        # 3. Extract entities using Claude
        entities = self.extract_entities_with_claude(text, doc_type, images)

        # 4. Validate extraction confidence
        confidence = self.calculate_confidence(entities)
        print(f"📊 Confidence: {confidence:.2%}")

        # 5. Convert to RDF if high confidence
        if confidence >= self.confidence_threshold:
            rdf_data = self.convert_to_rdf(entities, doc_type)
            status = "✅ AUTO_PROCESSED"
        else:
            rdf_data = None
            status = "⚠️ NEEDS_REVIEW"

        return {
            "file_path": file_path,
            "doc_type": doc_type,
            "entities": entities,
            "confidence": confidence,
            "rdf": rdf_data,
            "status": status
        }

    def extract_pdf(self, pdf_path):
        """Extract text and images from PDF"""
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300)

        # OCR each page
        text_parts = []
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang='eng')
            text_parts.append(text)

        full_text = "\n\n".join(text_parts)

        # Save first page as image for Claude vision
        image_paths = []
        if images:
            img_path = f"/tmp/{Path(pdf_path).stem}_page1.jpg"
            images[0].save(img_path, 'JPEG')
            image_paths.append(img_path)

        return full_text, image_paths

    def extract_image(self, image_path):
        """Extract text from image using Tesseract"""
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='eng')
        return text

    def classify_document(self, text, image_path=None):
        """Classify document type using Claude"""
        prompt = f"""
        Classify this logistics document into one of these types:
        - INVOICE
        - MANIFEST
        - TRANSPORT_REQUEST
        - DELIVERY_NOTE
        - BILL_OF_LADING
        - PACKING_LIST
        - OTHER

        Document text (first 500 chars):
        {text[:500]}

        Return only the document type.
        """

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()

    def extract_entities_with_claude(self, text, doc_type, images=None):
        """
        Extract structured entities using Claude
        Returns entities with confidence scores
        """

        # Prepare prompt based on document type
        if doc_type == "INVOICE":
            fields_to_extract = """
            - invoice_number
            - invoice_date
            - trn (Tax Registration Number)
            - supplier_name
            - customer_name
            - total_amount
            - currency
            - line_items (description, quantity, unit_price, amount)
            - payment_terms
            """
        elif doc_type == "TRANSPORT_REQUEST":
            fields_to_extract = """
            - request_number
            - date
            - vessel_name
            - origin_port
            - destination_port
            - eta (Estimated Time of Arrival)
            - etd (Estimated Time of Departure)
            - cargo_description
            - weight
            - container_numbers
            """
        else:
            fields_to_extract = """
            - document_number
            - date
            - relevant_parties (sender, receiver, etc.)
            - key_amounts
            - important_dates
            - container/shipment identifiers
            """

        prompt = f"""
        You are an expert logistics data extraction AI. Extract structured information from this {doc_type} document.

        Document text:
        {text}

        Fields to extract:
        {fields_to_extract}

        **CRITICAL REQUIREMENTS:**
        1. Return ONLY valid JSON
        2. Include a "confidence" score (0.0-1.0) for EACH field
        3. If a field is not found, set value to null and confidence to 0.0
        4. Use exact field names provided above
        5. For dates, use ISO format (YYYY-MM-DD)
        6. For amounts, extract as numbers without currency symbols

        Example response format:
        {{
          "invoice_number": {{"value": "INV-2025-001", "confidence": 0.95}},
          "invoice_date": {{"value": "2025-10-24", "confidence": 1.0}},
          "total_amount": {{"value": 15000.00, "confidence": 0.90}},
          ...
        }}

        DO NOT include any text outside the JSON object.
        """

        # Add image if available (for better accuracy)
        if images and len(images) > 0:
            with open(images[0], 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {"type": "text", "text": prompt}
            ]
        else:
            content = prompt

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": content}]
        )

        # Parse JSON response
        response_text = response.content[0].text

        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        entities = json.loads(response_text.strip())
        return entities

    def calculate_confidence(self, entities):
        """Calculate overall confidence score"""
        if not entities:
            return 0.0

        confidences = []
        for field, data in entities.items():
            if isinstance(data, dict) and 'confidence' in data:
                if data['value'] is not None:  # Only count non-null values
                    confidences.append(data['confidence'])

        if not confidences:
            return 0.0

        return sum(confidences) / len(confidences)

    def convert_to_rdf(self, entities, doc_type):
        """Convert extracted entities to RDF triples"""
        from rdflib import Graph, Namespace, Literal, URIRef
        from rdflib.namespace import RDF, XSD

        g = Graph()
        LOGI = Namespace("http://hvdc.samsung.com/logistics#")
        g.bind("logi", LOGI)

        # Create document URI
        doc_id = entities.get('invoice_number', {}).get('value') or \
                 entities.get('document_number', {}).get('value') or \
                 f"DOC_{hash(str(entities))}"

        doc_uri = URIRef(LOGI[doc_id.replace('-', '_')])

        # Add document type
        g.add((doc_uri, RDF.type, LOGI[doc_type]))

        # Add all extracted fields
        for field, data in entities.items():
            if isinstance(data, dict) and data.get('value') is not None:
                value = data['value']

                # Determine datatype
                if isinstance(value, (int, float)):
                    literal = Literal(value, datatype=XSD.decimal)
                elif field.endswith('_date') or field == 'date':
                    literal = Literal(value, datatype=XSD.date)
                else:
                    literal = Literal(value)

                g.add((doc_uri, LOGI[field], literal))
                g.add((doc_uri, LOGI[f"{field}_confidence"], Literal(data['confidence'], datatype=XSD.float)))

        return g.serialize(format='turtle')

# Integration with /logi-master invoice-audit
def audit_invoice_with_ocr(invoice_path):
    """
    Slash command integration: /logi-master invoice-audit
    """
    pipeline = LogisticsOCRPipeline()
    result = pipeline.process_document(invoice_path)

    if result["confidence"] >= 0.90:
        # High confidence - auto-update knowledge graph
        print("✅ High confidence extraction - updating knowledge graph")

        # Save RDF to knowledge graph
        from rdflib import Graph
        kg = Graph()
        kg.parse(data=result["rdf"], format="turtle")

        # Merge with existing ontology
        abu_ontology = Graph()
        abu_ontology.parse("C:/logi_ontol/output/final/abu_final.ttl", format="turtle")
        abu_ontology += kg

        # Save updated ontology
        abu_ontology.serialize("C:/logi_ontol/output/final/abu_final.ttl", format="turtle")

        return {
            "status": "✅ APPROVED - AUTO-UPDATED",
            "confidence": result["confidence"],
            "entities": {k: v['value'] for k, v in result["entities"].items() if v.get('value')}
        }
    else:
        # Low confidence - flag for manual review
        print(f"⚠️ Low confidence ({result['confidence']:.2%}) - manual review required")

        # Save to review queue
        review_path = f"C:/logi_ontol/output/review/{Path(invoice_path).stem}_review.json"
        os.makedirs(os.path.dirname(review_path), exist_ok=True)
        with open(review_path, 'w') as f:
            json.dump(result, f, indent=2)

        return {
            "status": "⚠️ REVIEW_REQUIRED",
            "confidence": result["confidence"],
            "review_file": review_path,
            "entities": result["entities"]
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = audit_invoice_with_ocr(sys.argv[1])
        print(json.dumps(result, indent=2))
```

**2.2 WhatsApp 데이터 통합**

```python
# C:\cursor-mcp\hvdc_automation\whatsapp_processor.py
import re
import json
from datetime import datetime
from pathlib import Path
import anthropic

class WhatsAppLogisticsProcessor:
    """
    Process WhatsApp chat logs for logistics entities
    Extracts: Container numbers, ETAs, amounts, vessel names, etc.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.entity_patterns = {
            'container': r'[A-Z]{4}\d{7}',
            'eta_date': r'ETA[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'etd_date': r'ETD[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'amount': r'AED\s*([\d,]+\.?\d*)',
            'invoice_ref': r'INV[-\s]?\d{4,}',
        }

    def parse_chat(self, chat_file_path):
        """Parse WhatsApp chat export"""
        with open(chat_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract messages with pattern: [DD/MM/YYYY, HH:MM:SS] Sender: Message
        pattern = r'\[(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2})\] ([^:]+): (.+?)(?=\n\[|\n$|$)'
        messages = re.findall(pattern, content, re.DOTALL)

        processed_messages = []
        for timestamp, sender, message in messages:
            # Skip system messages
            if '<Media omitted>' in message or 'changed the subject' in message:
                continue

            # Basic regex extraction
            basic_entities = self.extract_basic_entities(message)

            # Enhanced extraction with Claude for complex cases
            if self.requires_advanced_extraction(message):
                enhanced_entities = self.extract_with_claude(message)
                basic_entities.update(enhanced_entities)

            processed_messages.append({
                "timestamp": datetime.strptime(timestamp, "%d/%m/%Y, %H:%M:%S").isoformat(),
                "sender": sender.strip(),
                "message": message.strip(),
                "entities": basic_entities
            })

        return processed_messages

    def extract_basic_entities(self, text):
        """Extract entities using regex patterns"""
        entities = {}

        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches if len(matches) > 1 else matches[0]

        return entities

    def requires_advanced_extraction(self, message):
        """Determine if message needs Claude extraction"""
        keywords = ['vessel', 'ship', 'cargo', 'container', 'delivery', 'pickup', 'customs']
        return any(keyword in message.lower() for keyword in keywords)

    def extract_with_claude(self, message):
        """Use Claude for complex entity extraction"""
        prompt = f"""
        Extract logistics entities from this WhatsApp message:

        "{message}"

        Extract if present:
        - vessel_name
        - cargo_type
        - location (origin/destination)
        - status_update
        - action_required

        Return as JSON. If entity not found, omit it.
        Example: {{"vessel_name": "JPT71", "status_update": "departed"}}
        """

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            return json.loads(response.content[0].text)
        except:
            return {}

    def convert_to_rdf(self, messages):
        """Convert WhatsApp messages to RDF triples"""
        from rdflib import Graph, Namespace, Literal, URIRef
        from rdflib.namespace import RDF, XSD

        g = Graph()
        LOGI = Namespace("http://hvdc.samsung.com/logistics#")
        CHAT = Namespace("http://hvdc.samsung.com/chat#")
        g.bind("logi", LOGI)
        g.bind("chat", CHAT)

        for i, msg in enumerate(messages):
            msg_uri = URIRef(CHAT[f"msg_{i}"])

            g.add((msg_uri, RDF.type, CHAT.Message))
            g.add((msg_uri, CHAT.timestamp, Literal(msg['timestamp'], datatype=XSD.dateTime)))
            g.add((msg_uri, CHAT.sender, Literal(msg['sender'])))
            g.add((msg_uri, CHAT.content, Literal(msg['message'])))

            # Add extracted entities
            for entity_type, value in msg['entities'].items():
                if isinstance(value, list):
                    for v in value:
                        g.add((msg_uri, LOGI[entity_type], Literal(v)))
                else:
                    g.add((msg_uri, LOGI[entity_type], Literal(value)))

        return g.serialize(format='turtle')

def process_jpt71_chat():
    """Process JPT71 WhatsApp chat and add to knowledge graph"""
    processor = WhatsAppLogisticsProcessor()

    chat_file = "C:/logi_ontol/JPT71/Jopetwil 71 Group님과의 WhatsApp 대화.txt"
    print(f"🔍 Processing WhatsApp chat: {chat_file}")

    messages = processor.parse_chat(chat_file)
    print(f"📊 Extracted {len(messages)} messages")

    # Convert to RDF
    rdf_data = processor.convert_to_rdf(messages)

    # Save to knowledge graph
    output_file = "C:/logi_ontol/output/final/jpt71_whatsapp.ttl"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rdf_data)

    print(f"✅ WhatsApp data saved to: {output_file}")

    # Merge with main ontology
    from rdflib import Graph
    main_kg = Graph()
    main_kg.parse("C:/logi_ontol/output/final/abu_final.ttl", format="turtle")
    main_kg.parse(output_file, format="turtle")
    main_kg.serialize("C:/logi_ontol/output/final/abu_final.ttl", format="turtle")

    print("✅ Merged with abu_final.ttl")

    return len(messages)

if __name__ == "__main__":
    process_jpt71_chat()
```

**2.3 통합 지식 그래프**

```python
# C:\cursor-mcp\hvdc_automation\knowledge_graph.py
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import json

class HVDCKnowledgeGraph:
    """
    Unified knowledge graph for HVDC logistics
    Integrates: abu_final.ttl + lightning_final.ttl + operational data
    """

    def __init__(self):
        self.graph = Graph()
        self.LOGI = Namespace("http://hvdc.samsung.com/logistics#")
        self.graph.bind("logi", self.LOGI)
        self.load_ontologies()

    def load_ontologies(self):
        """Load all existing RDF ontologies"""
        ontology_files = [
            "C:/logi_ontol/output/final/abu_final.ttl",
            "C:/logi_ontol/output/final/lightning_final.ttl",
        ]

        for onto_file in ontology_files:
            try:
                self.graph.parse(onto_file, format="turtle")
                print(f"✅ Loaded: {onto_file}")
            except Exception as e:
                print(f"⚠️ Failed to load {onto_file}: {e}")

    def query_sparql(self, sparql_query):
        """Execute SPARQL query on knowledge graph"""
        return self.graph.query(sparql_query)

    def find_entity(self, entity_type, filters=None):
        """Find entities of specific type with optional filters"""
        query = f"""
        PREFIX logi: <http://hvdc.samsung.com/logistics#>
        SELECT ?entity ?prop ?value
        WHERE {{
            ?entity a logi:{entity_type} .
            ?entity ?prop ?value .
        }}
        """
        return self.query_sparql(query)

    def add_invoice(self, invoice_data):
        """Add invoice entity to knowledge graph"""
        invoice_uri = URIRef(self.LOGI[f"Invoice_{invoice_data['number']}"])

        self.graph.add((invoice_uri, RDF.type, self.LOGI.Invoice))

        for key, value in invoice_data.items():
            if key == 'number':
                continue

            predicate = self.LOGI[key]

            if isinstance(value, (int, float)):
                literal = Literal(value, datatype=XSD.decimal)
            elif 'date' in key:
                literal = Literal(value, datatype=XSD.date)
            else:
                literal = Literal(value)

            self.graph.add((invoice_uri, predicate, literal))

    def get_statistics(self):
        """Get knowledge graph statistics"""
        stats = {
            "total_triples": len(self.graph),
            "entity_counts": {}
        }

        # Count entities by type
        type_query = """
        PREFIX logi: <http://hvdc.samsung.com/logistics#>
        SELECT ?type (COUNT(?entity) as ?count)
        WHERE {
            ?entity a ?type .
            FILTER(STRSTARTS(STR(?type), "http://hvdc.samsung.com/logistics#"))
        }
        GROUP BY ?type
        """

        results = self.query_sparql(type_query)
        for row in results:
            entity_type = str(row.type).split('#')[1]
            stats["entity_counts"][entity_type] = int(row.count)

        return stats

    def save(self, output_path=None):
        """Save knowledge graph to file"""
        if output_path is None:
            output_path = "C:/logi_ontol/output/final/hvdc_unified.ttl"

        self.graph.serialize(output_path, format="turtle")
        print(f"✅ Knowledge graph saved: {output_path}")

# Integration with Claude tools
def query_knowledge_graph_via_claude(user_question):
    """
    Use Claude to generate SPARQL and query knowledge graph
    Integration with /logi-master commands
    """
    from anthropic import Anthropic

    client = Anthropic()
    kg = HVDCKnowledgeGraph()

    # Generate SPARQL with Claude
    prompt = f"""
    Generate a SPARQL query to answer this question about HVDC logistics:
    "{user_question}"

    Available ontology:
    Namespace: http://hvdc.samsung.com/logistics#

    Entity types:
    - Invoice (properties: number, date, amount, trn, supplier, customer)
    - Container (properties: number, size, type, status)
    - Vessel (properties: name, eta, etd, location)
    - Shipment (properties: origin, destination, cargo_type, weight)

    Return ONLY the SPARQL query, no explanation.
    Use PREFIX logi: <http://hvdc.samsung.com/logistics#>
    """

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    sparql_query = response.content[0].text.strip()

    # Remove markdown code blocks if present
    if "```sparql" in sparql_query:
        sparql_query = sparql_query.split("```sparql")[1].split("```")[0].strip()

    # Execute query
    results = kg.query_sparql(sparql_query)

    # Format results
    formatted_results = []
    for row in results:
        formatted_results.append({k: str(v) for k, v in row.asdict().items()})

    return {
        "question": user_question,
        "sparql": sparql_query,
        "results": formatted_results,
        "result_count": len(formatted_results)
    }

if __name__ == "__main__":
    # Example usage
    kg = HVDCKnowledgeGraph()
    stats = kg.get_statistics()
    print(json.dumps(stats, indent=2))
```

**산출물 (Phase 2):**
- ✅ AI-OCR 파이프라인 (Confidence ≥90%)
- ✅ WhatsApp 데이터 통합 (JPT71, Lightning)
- ✅ 통합 지식 그래프 (RDF + 비정형 데이터)
- ✅ SPARQL 쿼리 API
- ✅ Claude-powered 자연어 쿼리

---

### **PHASE 3: 자동화 워크플로우 & 대시보드 (2주)**
#### 목표: End-to-End 자동화 및 실시간 모니터링

**3.1 자동 트리거 시스템**

```python
# C:\cursor-mcp\hvdc_automation\triggers.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import asyncio

class HVDCAutomationTriggers:
    """
    Automated triggers for HVDC logistics operations
    - Daily invoice audit
    - ETA deviation monitoring
    - WhatsApp data sync
    - Knowledge graph backup
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def setup_all_triggers(self):
        """Setup all automated triggers"""

        # 1. Daily invoice audit (8:00 AM)
        self.scheduler.add_job(
            func=self.auto_invoice_audit,
            trigger=CronTrigger(hour=8, minute=0),
            id='invoice_audit',
            name='Daily Invoice Audit'
        )

        # 2. ETA monitoring (every 2 hours)
        self.scheduler.add_job(
            func=self.monitor_eta_deviations,
            trigger='interval',
            hours=2,
            id='eta_monitoring',
            name='ETA Deviation Monitoring'
        )

        # 3. WhatsApp data sync (every 30 minutes)
        self.scheduler.add_job(
            func=self.sync_whatsapp_data,
            trigger='interval',
            minutes=30,
            id='whatsapp_sync',
            name='WhatsApp Data Sync'
        )

        # 4. Knowledge graph backup (daily at midnight)
        self.scheduler.add_job(
            func=self.backup_knowledge_graph,
            trigger=CronTrigger(hour=0, minute=0),
            id='kg_backup',
            name='Knowledge Graph Backup'
        )

        # 5. KPI calculation (every hour)
        self.scheduler.add_job(
            func=self.calculate_kpis,
            trigger='interval',
            hours=1,
            id='kpi_calc',
            name='KPI Calculation'
        )

        print("✅ All triggers setup complete")
        self.scheduler.start()

    def auto_invoice_audit(self):
        """Automatically audit new invoices"""
        from pathlib import Path
        from .ocr_pipeline import audit_invoice_with_ocr

        print(f"🔍 [{datetime.now()}] Running daily invoice audit...")

        # Scan for new PDFs
        jpt71_path = Path("C:/logi_ontol/JPT71")
        new_invoices = [f for f in jpt71_path.glob("*.pdf")
                       if "ADNOC-TR" not in f.name and
                          "Manifest" not in f.name and
                          not self.is_processed(f)]

        results = {"processed": 0, "approved": 0, "review_needed": 0}

        for invoice in new_invoices:
            result = audit_invoice_with_ocr(str(invoice))
            results["processed"] += 1

            if result["status"].startswith("✅"):
                results["approved"] += 1
            else:
                results["review_needed"] += 1
                self.send_alert(f"⚠️ Invoice review needed: {invoice.name}")

        print(f"✅ Audit complete: {results}")
        self.log_trigger_result("invoice_audit", results)

    def monitor_eta_deviations(self):
        """Monitor vessels for ETA deviations > 24h"""
        from .knowledge_graph import HVDCKnowledgeGraph

        print(f"🔍 [{datetime.now()}] Monitoring ETA deviations...")

        kg = HVDCKnowledgeGraph()

        query = """
        PREFIX logi: <http://hvdc.samsung.com/logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?vessel ?name ?scheduled_eta ?current_eta
        WHERE {
            ?vessel a logi:Vessel .
            ?vessel logi:name ?name .
            ?vessel logi:scheduled_eta ?scheduled_eta .
            ?vessel logi:current_eta ?current_eta .
            FILTER (xsd:dateTime(?current_eta) > xsd:dateTime(?scheduled_eta) + "P1D"^^xsd:duration)
        }
        """

        deviations = kg.query_sparql(query)

        for row in deviations:
            delay_hours = (row.current_eta - row.scheduled_eta).total_seconds() / 3600
            self.send_alert(
                f"🚨 ETA Delay Alert\n"
                f"Vessel: {row.name}\n"
                f"Scheduled: {row.scheduled_eta}\n"
                f"Current: {row.current_eta}\n"
                f"Delay: {delay_hours:.1f} hours"
            )

        print(f"✅ ETA monitoring complete: {len(list(deviations))} deviations")

    def sync_whatsapp_data(self):
        """Sync WhatsApp chat data to knowledge graph"""
        from .whatsapp_processor import process_jpt71_chat

        print(f"🔍 [{datetime.now()}] Syncing WhatsApp data...")

        try:
            message_count = process_jpt71_chat()
            print(f"✅ Synced {message_count} messages")
        except Exception as e:
            print(f"⚠️ WhatsApp sync failed: {e}")
            self.send_alert(f"⚠️ WhatsApp sync failed: {e}")

    def backup_knowledge_graph(self):
        """Backup knowledge graph with timestamp"""
        from .knowledge_graph import HVDCKnowledgeGraph
        from shutil import copy2

        print(f"🔍 [{datetime.now()}] Backing up knowledge graph...")

        kg = HVDCKnowledgeGraph()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_path = f"C:/logi_ontol/output/versions/hvdc_unified_{timestamp}.ttl"
        kg.save(backup_path)

        print(f"✅ Backup saved: {backup_path}")

    def calculate_kpis(self):
        """Calculate and cache KPIs"""
        from .knowledge_graph import HVDCKnowledgeGraph
        import json

        print(f"🔍 [{datetime.now()}] Calculating KPIs...")

        kg = HVDCKnowledgeGraph()
        stats = kg.get_statistics()

        # Calculate custom KPIs
        kpis = {
            "timestamp": datetime.now().isoformat(),
            "knowledge_graph_size": stats["total_triples"],
            "entity_counts": stats["entity_counts"],
            "invoice_accuracy": self.calculate_invoice_accuracy(),
            "eta_deviation_avg": self.calculate_eta_deviation(),
            "warehouse_utilization": self.calculate_warehouse_util()
        }

        # Save to cache
        with open("C:/cursor-mcp/data/kpis_cache.json", "w") as f:
            json.dump(kpis, f, indent=2)

        print(f"✅ KPIs calculated and cached")

    def calculate_invoice_accuracy(self):
        """Calculate invoice processing accuracy"""
        # Placeholder - implement based on actual data
        return 92.5

    def calculate_eta_deviation(self):
        """Calculate average ETA deviation"""
        # Placeholder - implement based on actual data
        return 8.3  # hours

    def calculate_warehouse_util(self):
        """Calculate warehouse utilization"""
        # Placeholder - implement based on actual data
        return 78.5  # percent

    def is_processed(self, file_path):
        """Check if file has been processed"""
        import json
        log_file = "C:/cursor-mcp/data/processed_files.json"

        try:
            with open(log_file, 'r') as f:
                processed = json.load(f)
            return str(file_path) in processed
        except:
            return False

    def log_trigger_result(self, trigger_id, result):
        """Log trigger execution result"""
        import json
        log_file = f"C:/cursor-mcp/logs/triggers_{datetime.now().strftime('%Y%m')}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "trigger_id": trigger_id,
            "result": result
        }

        # Append to log file
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def send_alert(self, message):
        """Send alert via Telegram"""
        import os
        import requests

        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not bot_token or not chat_id:
            print(f"⚠️ Telegram not configured: {message}")
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f"✅ Alert sent via Telegram")
        except Exception as e:
            print(f"⚠️ Failed to send Telegram alert: {e}")

if __name__ == "__main__":
    triggers = HVDCAutomationTriggers()
    triggers.setup_all_triggers()

    # Keep running
    try:
        while True:
            import time
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n✅ Shutting down automation triggers...")
```

**산출물 (Phase 3):**
- ✅ 60+ Slash Commands 통합
- ✅ 자동 트리거 시스템 (5개 주요 작업)
- ✅ Telegram 알림 통합
- ✅ KPI 자동 계산 및 캐싱
- ✅ 완전 자동화 파이프라인

---

## 📋 구현 체크리스트

### Phase 1: 브릿징 (Week 1-2)
- [ ] **Week 1**
  - [ ] 심볼릭 링크 생성 또는 동기화 스크립트 구현
  - [ ] MCP 서버 logi-ontol 설정
  - [ ] 전체 파일 인덱스 생성
  - [ ] Claude filesystem 접근 테스트
  - [ ] 디렉토리 구조 문서화

- [ ] **Week 2**
  - [ ] HVDC_PJT와 통합
  - [ ] RoboCopy 자동 동기화 설정
  - [ ] 백업 전략 수립
  - [ ] Slash commands 테스트
  - [ ] 성능 최적화

### Phase 2: AI-OCR & 지식 (Week 3-5)
- [ ] **Week 3**
  - [ ] Tesseract OCR 설치 및 설정
  - [ ] Claude 엔티티 추출 통합
  - [ ] 문서 분류 시스템 구축
  - [ ] JPT71 PDF 테스트
  - [ ] 추출 정확도 검증 (목표: 90%)

- [ ] **Week 4**
  - [ ] WhatsApp 데이터 파서 구현
  - [ ] 지식 그래프 통합
  - [ ] SPARQL 쿼리 생성기
  - [ ] SHACL 검증
  - [ ] End-to-end 파이프라인 테스트

- [ ] **Week 5**
  - [ ] abu_final.ttl + lightning_final.ttl 로드
  - [ ] 엔티티 크로스 레퍼런스
  - [ ] 쿼리 API 구축
  - [ ] 성능 튜닝
  - [ ] 문서화

### Phase 3: 자동화 & 대시보드 (Week 6-7)
- [ ] **Week 6**
  - [ ] 모든 slash commands 구현
  - [ ] 자동 트리거 설정
  - [ ] Telegram 봇 통합
  - [ ] React 대시보드 구축
  - [ ] 실시간 데이터 스트리밍

- [ ] **Week 7**
  - [ ] End-to-end 테스트
  - [ ] 사용자 수용 테스트
  - [ ] 성능 벤치마킹
  - [ ] 교육 자료 제작
  - [ ] Go-live 준비

---

## 🎯 성과 지표

### 정량적 KPI
| 지표 | Before | After | 개선율 |
|------|--------|-------|--------|
| 인보이스 처리 시간 | 15분 | 3분 | **80%↓** |
| OCR 정확도 | 75% | ≥90% | **20%↑** |
| 수동 개입 | 40건/월 | 10건/월 | **75%↓** |
| ETA 편차 탐지 | 수동 | <2시간 자동 | **자동화** |
| 지식 그래프 크기 | 5K triples | 50K triples | **10배↑** |
| 쿼리 응답 시간 | - | <2초 | **신규** |
| 시스템 가동률 | - | 99.5% | **신규** |

### 정성적 성과
- ✅ **Single Source of Truth**: 모든 물류 데이터가 통합 지식 그래프에
- ✅ **사전 대응 알림**: 문제가 커지기 전에 자동 탐지
- ✅ **완전한 감사 추적**: 원본 데이터부터 의사결정까지
- ✅ **확장성**: 새로운 선박, 루트, 파트너 추가 용이
- ✅ **사용자 만족도**: 빠른 응답, 적은 오류

---

## 🔄 롤아웃 계획

### Week 0: 준비
- 팀 킥오프 미팅
- 환경 설정
- 접근 권한 부여
- 기준선 측정

### Week 1-2: Phase 1 (브릿징)
- 1-2명 내부 파일럿
- 동기화 검증
- 버그 수정
- 문서 업데이트

### Week 3-5: Phase 2 (AI-OCR & 지식)
- 5명 파워 유저로 확대
- 과거 데이터 처리 (JPT71)
- OCR 정확도 개선
- 지식 그래프 구축

### Week 6-7: Phase 3 (자동화)
- 전체 팀 롤아웃
- 대시보드 런칭
- 자동 트리거 활성화
- 24/7 모니터링

### Week 8+: 최적화
- 성능 튜닝
- 기능 요청 처리
- 지속적 개선
- 다른 선박으로 확장

---

## 🔧 즉시 실행 가능한 Next Actions

### 이번 주 (Week 0)
1. ✅ **이 마스터플랜 검토** - 이해관계자와 공유
2. ✅ **개발 환경 설정**
   - 의존성 설치
   - MCP 서버 구성
   - Filesystem 접근 테스트
3. ✅ **Phase 1 작업 보드 생성** - Jira/Asana
4. ✅ **킥오프 미팅 스케줄**

### 다음 2주 (Week 1-2)
1. **심볼릭 링크 구현** - C:\logi_ontol → C:\cursor-mcp
2. **MCP 서버 구축** - logi-ontol 접근
3. **/logi-master 명령어 테스트** - 샘플 데이터
4. **장애물 문서화**

### 다음 4주 (Week 3-6)
1. **AI-OCR 파이프라인 배포**
2. **JPT71 과거 데이터 처리**
3. **지식 그래프 구축**
4. **파일럿 대시보드 런칭**

---

## 📊 시스템 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Interface Layer                    │
│  (Web Chat / API / Slack / Telegram / WhatsApp)             │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                MACHO-GPT Command Router                      │
│  /logi-master  /switch_mode  /visualize  /check_KPI         │
└────────────────┬────────────────────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
┌────────▼─────┐  ┌──────▼────────┐
│ Claude Tools │  │  MCP Servers  │
│              │  │               │
│ • filesystem │  │ • logi-ontol  │
│ • web_search │  │ • pdf-tools   │
│ • drive_srch │  │ • vercel      │
│ • web_fetch  │  │ • windows     │
└────────┬─────┘  └──────┬────────┘
         │               │
         └───────┬───────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│              Integration & Processing Layer                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  AI-OCR      │  │  Knowledge   │  │  Data Pipeline  │  │
│  │  Pipeline    │  │  Graph       │  │                 │  │
│  │              │  │              │  │  • Ingest       │  │
│  │ • Tesseract  │  │ • RDFLib     │  │  • Validate     │  │
│  │ • Claude     │  │ • SPARQL     │  │  • Transform    │  │
│  │ • Entity Ext │  │ • SHACL      │  │  • Load         │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                   Data Sources Layer                         │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ logi_ontol │  │ Google     │  │  External APIs       │  │
│  │            │  │ Drive      │  │                      │  │
│  │ • RDF      │  │            │  │  • AIS (vessel)      │  │
│  │ • Excel    │  │ • Docs     │  │  • NOAA (weather)    │  │
│  │ • PDF      │  │ • Sheets   │  │  • Port APIs         │  │
│  │ • WhatsApp │  │ • Templates│  │  • Customs           │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 혁신 기회

### MVP 이후
1. **예측 분석**
   - ML 기반 ETA 예측
   - 비용 예측
   - 리스크 스코어링

2. **모바일 앱**
   - iOS/Android 네이티브 앱
   - 오프라인 모드
   - 푸시 알림

3. **음성 인터페이스**
   - "Alexa, JPT71 상태는?"
   - 일반 작업을 위한 음성 명령

4. **블록체인 통합**
   - 불변 감사 추적
   - 결제용 스마트 계약
   - 분산 지식 그래프

5. **고급 시각화**
   - 3D 컨테이너 적재
   - 실시간 선박 추적
   - 창고 레이아웃용 AR

---

## 📞 연락처 & 지원

**프로젝트 리더**: MACHO-GPT Integration Team
**기술 리더**: [Your Name]
**이해관계자**: Samsung C&T, ADNOC, DSV

**지원 채널**:
- Slack: #hvdc-integration
- Email: hvdc-support@samsung.com
- Telegram: @logi-alert

**업무 시간**: 월-금 9:00-17:00 GST

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-10-24
**다음 검토**: 2025-11-01
**상태**: ✅ 구현 승인됨
