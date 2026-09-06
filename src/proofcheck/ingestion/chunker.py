import re

from proofcheck.ingestion.parser import ParsedDocument
from proofcheck.models.schemas import DocumentType, RetrievalChunk


def chunk_document(
    document: ParsedDocument,
    project_id: str,
    document_type: DocumentType,
) -> list[RetrievalChunk]:
    """Create document-aware retrieval chunks."""

    if document_type == DocumentType.CONTRACT:
        return _chunk_contract(document, project_id)

    if document_type == DocumentType.BOQ:
        return _chunk_boq(document, project_id)

    if document_type == DocumentType.APPROVED_CHANGE:
        return _chunk_approved_change(document, project_id)

    if document_type == DocumentType.WORK_RECORD:
        return _chunk_work_record(document, project_id)

    if document_type == DocumentType.INVOICE:
        return _chunk_invoice(document, project_id)

    if document_type == DocumentType.CHANGE_REQUEST:
        return _chunk_change_request(document, project_id)

    if document_type == DocumentType.CORRESPONDENCE:
        return _chunk_correspondence(document, project_id)

    return _chunk_by_page(document, project_id, document_type)


def _chunk_by_page(
    document: ParsedDocument,
    project_id: str,
    document_type: DocumentType,
) -> list[RetrievalChunk]:
    """Temporary fallback: one non-empty page becomes one chunk."""

    chunks: list[RetrievalChunk] = []

    for page in document.pages:
        text = page.text.strip()

        if not text:
            continue

        chunks.append(
            RetrievalChunk(
                chunk_id=f"{document.document_id}-P{page.page_number}-C1",
                document_id=document.document_id,
                project_id=project_id,
                document_type=document_type,
                chunk_type="PAGE",
                text=text,
                page=page.page_number,
                metadata={
                    "source": document.filename,
                },
            )
        )

    return chunks


def _chunk_contract(
    document: ParsedDocument,
    project_id: str,
) -> list[RetrievalChunk]:
    """Split contract text into logical contract sections and clauses."""

    chunks: list[RetrievalChunk] = []

    for page in document.pages:
        text = page.text.strip()

        if not text:
            continue

        matches = list(re.finditer(r"Clause \d+\s+—", text))

        if not matches:
            chunks.append(
                RetrievalChunk(
                    chunk_id=f"{document.document_id}-P{page.page_number}-C1",
                    document_id=document.document_id,
                    project_id=project_id,
                    document_type=DocumentType.CONTRACT,
                    chunk_type="SECTION",
                    text=text,
                    page=page.page_number,
                    metadata={"source": document.filename},
                )
            )
            continue

        first_clause_start = matches[0].start()

        if first_clause_start > 0:
            context_text = text[:first_clause_start].strip()

            if context_text:
                chunks.append(
                    RetrievalChunk(
                        chunk_id=f"{document.document_id}-P{page.page_number}-C1",
                        document_id=document.document_id,
                        project_id=project_id,
                        document_type=DocumentType.CONTRACT,
                        chunk_type="SECTION",
                        text=context_text,
                        page=page.page_number,
                        metadata={"source": document.filename},
                    )
                )

        for index, match in enumerate(matches):
            start = match.start()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
                clause_text = text[start:end].strip()
            else:
                clause_text = text[start:].strip()

            clause_number = re.search(r"Clause (\d+)", clause_text)

            number = clause_number.group(1) if clause_number else str(index + 1)

            chunks.append(
                RetrievalChunk(
                    chunk_id=(
                        f"{document.document_id}-"
                        f"P{page.page_number}-CLAUSE-{number}"
                    ),
                    document_id=document.document_id,
                    project_id=project_id,
                    document_type=DocumentType.CONTRACT,
                    chunk_type="CLAUSE",
                    text=clause_text,
                    page=page.page_number,
                    section=f"Clause {number}",
                    metadata={
                        "source": document.filename,
                        "clause_number": number,
                    },
                )
            )

    return chunks

def _chunk_boq(
    document: ParsedDocument,
    project_id: str,
) -> list[RetrievalChunk]:
    """Split BOQ text into coherent line-item and context chunks."""

    chunks: list[RetrievalChunk] = []

    for page in document.pages:
        text = page.text.strip()

        if not text:
            continue

        matches = list(re.finditer(r"(?m)^F-\d+\s*$", text))

        if not matches:
            chunks.append(
                RetrievalChunk(
                    chunk_id=f"{document.document_id}-P{page.page_number}-C1",
                    document_id=document.document_id,
                    project_id=project_id,
                    document_type=DocumentType.BOQ,
                    chunk_type="SECTION",
                    text=text,
                    page=page.page_number,
                    metadata={"source": document.filename},
                )
            )
            continue

        # Content before the first line item.
        first_item_start = matches[0].start()

        if first_item_start > 0:
            context_text = text[:first_item_start].strip()

            if context_text:
                chunks.append(
                    RetrievalChunk(
                        chunk_id=(
                            f"{document.document_id}-"
                            f"P{page.page_number}-CONTEXT"
                        ),
                        document_id=document.document_id,
                        project_id=project_id,
                        document_type=DocumentType.BOQ,
                        chunk_type="SECTION",
                        text=context_text,
                        page=page.page_number,
                        metadata={"source": document.filename},
                    )
                )

        trailing_start = None

        for index, match in enumerate(matches):
            start = match.start()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                # Stop the final line item before document-level content.
                remainder = text[start:]

                boundary_match = re.search(
                    r"(?m)^(Total|BOQ Note)\s*$",
                    remainder,
                )

                if boundary_match:
                    end = start + boundary_match.start()
                    trailing_start = start + boundary_match.start()
                else:
                    end = len(text)

            item_text = text[start:end].strip()

            item_match = re.match(r"F-(\d+)", item_text)
            item_number = (
                item_match.group(1)
                if item_match
                else str(index + 1)
            )

            chunks.append(
                RetrievalChunk(
                    chunk_id=(
                        f"{document.document_id}-"
                        f"P{page.page_number}-ITEM-{item_number}"
                    ),
                    document_id=document.document_id,
                    project_id=project_id,
                    document_type=DocumentType.BOQ,
                    chunk_type="LINE_ITEM",
                    text=item_text,
                    page=page.page_number,
                    section=f"Item F-{item_number}",
                    metadata={
                        "source": document.filename,
                        "item_number": f"F-{item_number}",
                    },
                )
            )

        # Preserve Total / BOQ Note as separate document-level context.
        if trailing_start is not None:
            trailing_text = text[trailing_start:].strip()

            if trailing_text:
                chunks.append(
                    RetrievalChunk(
                        chunk_id=(
                            f"{document.document_id}-"
                            f"P{page.page_number}-TRAILING"
                        ),
                        document_id=document.document_id,
                        project_id=project_id,
                        document_type=DocumentType.BOQ,
                        chunk_type="SECTION",
                        text=trailing_text,
                        page=page.page_number,
                        metadata={"source": document.filename},
                    )
                )

    return chunks

def _chunk_approved_change(
    document: ParsedDocument,
    project_id: str,
) -> list[RetrievalChunk]:
    """Create a coherent chunk for an approved change order."""

    chunks: list[RetrievalChunk] = []

    for page in document.pages:
        text = page.text.strip()

        if not text:
            continue

        chunks.append(
            RetrievalChunk(
                chunk_id=f"{document.document_id}-P{page.page_number}-CHANGE",
                document_id=document.document_id,
                project_id=project_id,
                document_type=DocumentType.APPROVED_CHANGE,
                chunk_type="LINE_ITEM",
                text=text,
                page=page.page_number,
                section="Approved Change",
                metadata={
                    "source": document.filename,
                    "approval_status": "APPROVED",
                },
            )
        )

    return chunks


def _chunk_work_record(
    document: ParsedDocument,
    project_id: str,
) -> list[RetrievalChunk]:
    """Create a coherent evidence chunk for a work measurement record."""

    chunks: list[RetrievalChunk] = []

    for page in document.pages:
        text = page.text.strip()

        if not text:
            continue

        chunks.append(
            RetrievalChunk(
                chunk_id=f"{document.document_id}-P{page.page_number}-MEASUREMENT",
                document_id=document.document_id,
                project_id=project_id,
                document_type=DocumentType.WORK_RECORD,
                chunk_type="LINE_ITEM",
                text=text,
                page=page.page_number,
                section="Work Measurement",
                metadata={
                    "source": document.filename,
                    "record_type": "VERIFIED_MEASUREMENT",
                },
            )
        )

    return chunks

def _chunk_invoice(
    document: ParsedDocument,
    project_id: str,
) -> list[RetrievalChunk]:
    """Create a coherent evidence chunk for an invoice claim."""

    chunks: list[RetrievalChunk] = []

    for page in document.pages:
        text = page.text.strip()

        if not text:
            continue

        chunks.append(
            RetrievalChunk(
                chunk_id=f"{document.document_id}-P{page.page_number}-LINE-1",
                document_id=document.document_id,
                project_id=project_id,
                document_type=DocumentType.INVOICE,
                chunk_type="LINE_ITEM",
                text=text,
                page=page.page_number,
                section="Invoice Line Item",
                metadata={
                    "source": document.filename,
                    "claim_type": "INVOICE_LINE_ITEM",
                },
            )
        )

    return chunks

def _chunk_change_request(
    document: ParsedDocument,
    project_id: str,
) -> list[RetrievalChunk]:
    """Create a coherent evidence chunk for a change request."""

    chunks: list[RetrievalChunk] = []

    for page in document.pages:
        text = page.text.strip()

        if not text:
            continue

        chunks.append(
            RetrievalChunk(
                chunk_id=f"{document.document_id}-P{page.page_number}-CHANGE-REQUEST",
                document_id=document.document_id,
                project_id=project_id,
                document_type=DocumentType.CHANGE_REQUEST,
                chunk_type="LINE_ITEM",
                text=text,
                page=page.page_number,
                section="Change Request",
                metadata={
                    "source": document.filename,
                    "approval_status": "SUBMITTED_FOR_APPROVAL",
                },
            )
        )

    return chunks

def _chunk_correspondence(
    document: ParsedDocument,
    project_id: str,
) -> list[RetrievalChunk]:
    """Split correspondence into logical message chunks."""

    chunks: list[RetrievalChunk] = []

    for page in document.pages:
        text = page.text.strip()

        if not text:
            continue

        matches = list(
            re.finditer(
                r"(?m)^Message\s+\d+\s+—",
                text,
            )
        )

        if not matches:
            chunks.append(
                RetrievalChunk(
                    chunk_id=f"{document.document_id}-P{page.page_number}-C1",
                    document_id=document.document_id,
                    project_id=project_id,
                    document_type=DocumentType.CORRESPONDENCE,
                    chunk_type="SECTION",
                    text=text,
                    page=page.page_number,
                    section="Correspondence",
                    metadata={"source": document.filename},
                )
            )
            continue

        # Preserve document-level context before the first message.
        first_message_start = matches[0].start()

        if first_message_start > 0:
            header_text = text[:first_message_start].strip()

            if header_text:
                chunks.append(
                    RetrievalChunk(
                        chunk_id=(
                            f"{document.document_id}-"
                            f"P{page.page_number}-HEADER"
                        ),
                        document_id=document.document_id,
                        project_id=project_id,
                        document_type=DocumentType.CORRESPONDENCE,
                        chunk_type="SECTION",
                        text=header_text,
                        page=page.page_number,
                        section="Correspondence",
                        metadata={"source": document.filename},
                    )
                )

        # Create one chunk per logical message.
        for index, match in enumerate(matches):
            start = match.start()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(text)

            message_text = text[start:end].strip()

            if not message_text:
                continue

            message_number_match = re.match(
                r"Message\s+(\d+)",
                message_text,
            )

            message_number = (
                message_number_match.group(1)
                if message_number_match
                else str(index + 1)
            )

            chunks.append(
                RetrievalChunk(
                    chunk_id=(
                        f"{document.document_id}-"
                        f"P{page.page_number}-MESSAGE-{message_number}"
                    ),
                    document_id=document.document_id,
                    project_id=project_id,
                    document_type=DocumentType.CORRESPONDENCE,
                    chunk_type="MESSAGE",
                    text=message_text,
                    page=page.page_number,
                    section="Correspondence",
                    metadata={
                        "source": document.filename,
                        "message_number": message_number,
                        "content_type": "PROJECT_MESSAGE",
                    },
                )
            )

    return chunks


