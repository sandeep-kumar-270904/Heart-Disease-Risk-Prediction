"""HeartXAI 2.0 - Cryptographically Sealed Clinical PDF Dossier Export (Milestone 14)."""

from __future__ import annotations

import hashlib
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas.assessment import AssessmentDetailResponse, ShapExplanationResponse


def generate_assessment_pdf_bytes(
    detail: AssessmentDetailResponse,
    shap_data: ShapExplanationResponse,
) -> tuple[bytes, str]:
    """Render a structured 2-page PDF dossier with SHA-256 integrity seal and zero Task B claims."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=48,
        rightMargin=48,
        topMargin=48,
        bottomMargin=48,
        title=f"HeartXAI Assessment {detail.id}",
    )
    styles = getSampleStyleSheet()
    story = []

    # Page 1: Executive Summary & Mandatory Non-Diagnostic Disclaimers
    story.append(Paragraph("HeartXAI 2.0 — Cardiovascular Assessment Dossier", styles["Title"]))
    story.append(
        Paragraph(
            "<b>SYNTHETIC / EDUCATIONAL DECISION-SUPPORT REPORT (NON-DIAGNOSTIC)</b>",
            styles["Heading3"],
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "NOTICE: This report summarizes an experimental Task A retrospective dataset "
            "similarity score (UCI Cleveland benchmark). It does NOT constitute a medical "
            "diagnosis, clinical prognosis, prescription, or 10-year prospective cardiovascular "
            "event calculation. Review all metrics with a licensed healthcare professional.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 14))

    fbs_display = (
        f"{detail.fasting_blood_sugar:g} mg/dL "
        f"(UCI binary >120 mg/dL: {'Yes' if detail.fasting_blood_sugar_gt_120 else 'No'})"
        if detail.fasting_blood_sugar is not None
        else f"Not recorded numerically (legacy binary >120 mg/dL: {'Yes' if detail.fasting_blood_sugar_gt_120 else 'No'})"
    )
    summary_rows = [
        ["Assessment ID", detail.id],
        ["Persona ID (Synthetic)", detail.patient_id],
        ["Data Provenance", detail.data_provenance],
        ["Model Version", detail.model_version],
        ["Cohort Reference", detail.cohort_name],
        [
            "Experimental Task A Score",
            f"{detail.cad_likelihood_percent:.2f}% (Unstratified Research Score)",
        ],
        ["Fasting Blood Sugar", fbs_display],
        ["Clinical Review Note", "Non-diagnostic synthetic demonstration; no automated triage"],
        ["Created UTC", detail.created_at.isoformat()],
    ]
    summary_table = Table(summary_rows, colWidths=[180, 320])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 16))
    story.append(Paragraph(f"<b>Summary:</b> {detail.plain_language_summary}", styles["BodyText"]))

    # Page 2: TreeSHAP Local Feature Attributions & Integrity Seal
    story.append(PageBreak())
    story.append(Paragraph("Local TreeSHAP Feature Attribution Breakdown", styles["Heading2"]))
    story.append(
        Paragraph(
            "Attributions reflect statistical model margin associations in log-odds units "
            f"(Baseline E[f(x)] = {shap_data.base_value:.4f}, Margin f(x) = {shap_data.final_likelihood:.4f}), "
            "not biological causation.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 12))

    shap_rows = [["Biomarker", "Value", "Cohort Mean", "SHAP (log-odds)", "Direction"]]
    for feat in shap_data.features:
        shap_rows.append(
            [
                feat.feature_name,
                f"{feat.raw_patient_value:g}",
                f"{feat.cohort_average_value:g}",
                f"{feat.shap_value:+.4f}",
                "Increases" if feat.direction == "increases_likelihood" else "Decreases",
            ]
        )
    shap_table = Table(shap_rows, colWidths=[110, 75, 85, 110, 120])
    shap_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(shap_table)
    story.append(Spacer(1, 18))

    canonical_digest_input = f"{detail.id}|{detail.patient_id}|{detail.cad_likelihood_percent}|{shap_data.final_likelihood}"
    seal_hash = hashlib.sha256(canonical_digest_input.encode("utf-8")).hexdigest()
    story.append(
        Paragraph(
            f"<b>Cryptographic Content Seal (SHA-256):</b> <font face='Courier'>{seal_hash}</font>",
            styles["BodyText"],
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    pdf_sha256 = hashlib.sha256(pdf_bytes).hexdigest()
    return pdf_bytes, pdf_sha256
