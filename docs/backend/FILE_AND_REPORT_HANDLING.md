# HeartXAI 2.0 — File & Clinical Report Handling Specification

**Document ID:** `HX2-BE-012`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Application Security Architect & Backend Lead Engineer  
**Traceability:** FR-050–FR-054, NFR-001–NFR-028, ADR-001, ADR-005  

---

## 1. File Handling Security Principles

Handling patient health summaries and medical license credential uploads requires stringent security controls to prevent **Remote Code Execution (RCE)**, **Arbitrary File Overwrite**, **Server-Side Request Forgery (SSRF)**, and **Unauthorized Protected Health Information (PHI) Exposure**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   FILE SECURITY ARCHITECTURAL RULES                    │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Memory-Only PDF Compilation (Zero Unencrypted Disk Spooling)       │
│ 2. Strict Magic Byte MIME Verification (No Reliance on File Extension) │
│ 3. Storage Outside Web Root with Non-Guessable UUID File Paths         │
│ 4. Mandatory Object-Level Authorization on Every Download Request      │
│ 5. Automated Temporary File Sanitization & 10MB Upload Clamps          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Clinical Consultation Summary PDF Generation

### 2.1 Server-Side Compilation via WeasyPrint
Instead of relying on fragile client-side PDF libraries that inflate JavaScript bundles, HeartXAI 2.0 compiles consultation summaries server-side:

```python
import io
from weasyprint import HTML, CSS
from app.core.exceptions import EntityNotFoundException, AuthorizationException

class ReportService:
    @staticmethod
    def compile_pdf(assessment_data: dict) -> io.BytesIO:
        # 1. Render HTML from Jinja2 template
        rendered_html = template_env.get_template("clinical_report.html").render(
            assessment=assessment_data,
            disclaimer="EDUCATIONAL MODEL: Derived from observational clinical study cohorts. Informational estimation, not a medical diagnosis."
        )

        # 2. Compile to PDF directly into an in-memory buffer
        pdf_buffer = io.BytesIO()
        HTML(string=rendered_html).write_pdf(
            target=pdf_buffer,
            stylesheets=[CSS(filename="app/templates/report_styles.css")]
        )
        pdf_buffer.seek(0)
        return pdf_buffer
```

### 2.2 Streaming Delivery Endpoint (`GET /api/v1/reports/assessments/:id/pdf`)
```python
from fastapi.responses import StreamingResponse

@router.get("/assessments/{id}/pdf")
async def download_clinical_report(
    id: str,
    current_user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow)
):
    # 1. Ownership & Authorization Check
    assessment = await uow.assessments.get_by_id_with_inference(id)
    if not assessment:
        raise EntityNotFoundException("Assessment", id)
        
    if current_user.role == "PATIENT" and assessment.patient_id != current_user.id:
        raise EntityNotFoundException("Assessment", id)
    elif current_user.role == "CLINICIAN":
        await verify_clinician_patient_access(current_user.id, assessment.patient_id, uow)

    # 2. Generate PDF in memory
    pdf_buffer = await asyncio.to_thread(ReportService.compile_pdf, assessment)
    
    # 3. Stream Response
    filename = f"HeartXAI-Clinical-Report-{id[:8]}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache"
        }
    )
```

---

## 3. Clinician Credential Document Uploads

When healthcare practitioners apply for verified clinician status, they submit PDF or image scans of their medical diplomas and government licensure.

### 3.1 Security Validation Pipeline
1. **File Size Enforcement:** Maximum upload size is strictly clamped at **$10\text{ MB}$** (`10 * 1024 * 1024` bytes). Payloads exceeding this limit are terminated before full memory buffering (`HTTP 413 Payload Too Large`).
2. **MIME-Type Magic Byte Sniffing:**
   - Client-provided `Content-Type` headers are untrusted.
   - The file's first 2048 bytes are inspected via magic byte analysis (verifying `%PDF-1.` header for PDFs, or `\xFF\xD8\xFF` for JPEGs).
   - Executable scripts (`.php`, `.py`, `.sh`, `.exe`, `.html`, `.svg`) are strictly rejected.
3. **Storage Isolation:**
   - Files are stored on a private filesystem path outside the web server root: `/var/storage/credentials/{year}/{month}/{random_uuid4}.enc`.
   - Files are saved with AES-256 server-side encryption at rest.
4. **Access Control:** Only authenticated `ADMINISTRATOR` users can retrieve and view uploaded credential documents through the verification queue endpoint.
