from googleapiclient.discovery import build
from auth import get_credentials

def get_docs_service():
    creds = get_credentials()
    return build('docs', 'v1', credentials=creds)

def get_document_url(document_id: str) -> str:
    """Returns the URL of the Google Doc."""
    return f"https://docs.google.com/document/d/{document_id}"

def get_heading_link(document_id: str, heading_id: str) -> str:
    """Returns the deep link to a specific heading in the document."""
    return f"https://docs.google.com/document/d/{document_id}/edit#heading=h.{heading_id}"

def find_heading(document_id: str, heading_text: str) -> str:
    """Fetches the doc structure and returns the internal heading_id matching heading_text."""
    service = get_docs_service()
    doc = service.documents().get(documentId=document_id).execute()
    
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            paragraph = element['paragraph']
            if 'paragraphStyle' in paragraph and 'headingId' in paragraph['paragraphStyle']:
                text_content = ""
                for p_element in paragraph.get('elements', []):
                    if 'textRun' in p_element:
                        text_content += p_element['textRun']['content']
                
                # Google Docs adds newlines to the end of paragraph texts
                if text_content.strip() == heading_text:
                    return paragraph['paragraphStyle']['headingId']
                    
    return ""

def append_section(document_id: str, heading_text: str, heading_level: int, body_content: list) -> dict:
    """
    Uses the batchUpdate API to append a new section at the end of the document.
    """
    service = get_docs_service()
    doc = service.documents().get(documentId=document_id).execute()
    
    content = doc.get('body', {}).get('content', [])
    if not content:
        end_index = 1
    else:
        end_index = content[-1]['endIndex'] - 1

    requests = []
    current_index = end_index

    def add_text(text: str, style: str = None):
        nonlocal current_index
        requests.append({
            'insertText': {
                'location': {'index': current_index},
                'text': text
            }
        })
        start_idx = current_index
        current_index += len(text)
        
        if style:
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start_idx,
                        'endIndex': current_index
                    },
                    'paragraphStyle': {
                        'namedStyleType': style
                    },
                    'fields': 'namedStyleType'
                }
            })

    # Insert the main section heading
    add_text(f"\n{heading_text}\n", f"HEADING_{heading_level}")

    # Process body content
    for item in body_content:
        item_type = item.get("type")
        
        if item_type == "paragraph":
            text = item.get("text", "")
            add_text(f"{text}\n", "NORMAL_TEXT")
            
        elif item_type == "heading":
            text = item.get("text", "")
            level = item.get("level", 2)
            add_text(f"{text}\n", f"HEADING_{level}")
            
        elif item_type == "horizontal_rule":
            add_text("---\n", "NORMAL_TEXT")
            
        elif item_type == "bullet_list":
            items = item.get("items", [])
            if items:
                start_idx = current_index
                list_text = "".join([f"{li}\n" for li in items])
                add_text(list_text, "NORMAL_TEXT")
                
                requests.append({
                    'createParagraphBullets': {
                        'range': {
                            'startIndex': start_idx,
                            'endIndex': current_index
                        },
                        'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                    }
                })
                
        elif item_type == "table":
            rows = item.get("rows", [])
            if rows:
                num_rows = len(rows)
                num_cols = max((len(row) for row in rows), default=1)
                
                # Execute pending requests before creating the table
                if requests:
                    service.documents().batchUpdate(
                        documentId=document_id,
                        body={'requests': requests}
                    ).execute()
                    requests.clear()
                
                # Create the table in its own batchUpdate
                service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': [{
                        'insertTable': {
                            'location': {'index': current_index},
                            'rows': num_rows,
                            'columns': num_cols
                        }
                    }]}
                ).execute()
                
                # Fetch the document to find the newly created table's exact indices
                doc_after = service.documents().get(documentId=document_id).execute()
                content_after = doc_after.get('body', {}).get('content', [])
                
                # Find the last table in the document
                last_table = None
                for element in reversed(content_after):
                    if 'table' in element:
                        last_table = element['table']
                        break
                        
                if last_table:
                    cell_inserts = []
                    for r_idx, row in enumerate(rows):
                        if r_idx < len(last_table['tableRows']):
                            table_row = last_table['tableRows'][r_idx]
                            for c_idx, cell_text in enumerate(row):
                                if cell_text and c_idx < len(table_row['tableCells']):
                                    table_cell = table_row['tableCells'][c_idx]
                                    # The paragraph inside the cell starts at cell['startIndex'] + 1
                                    insert_idx = table_cell['startIndex'] + 1
                                    cell_inserts.append((insert_idx, str(cell_text)))
                    
                    # Sort inserts in reverse order to avoid index shifting problems
                    cell_inserts.sort(key=lambda x: x[0], reverse=True)
                    for idx, text in cell_inserts:
                        requests.append({
                            'insertText': {
                                'location': {'index': idx},
                                'text': text
                            }
                        })
                        
                    # Execute cell inserts immediately
                    if requests:
                        service.documents().batchUpdate(
                            documentId=document_id,
                            body={'requests': requests}
                        ).execute()
                        requests.clear()
                        
                    # Fetch document again to get the new end_index so current_index is accurate for subsequent items
                    doc_final = service.documents().get(documentId=document_id).execute()
                    current_index = doc_final.get('body', {}).get('content', [])[-1]['endIndex'] - 1

    # Execute all requests
    if requests:
        service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

    return {"status": "success", "message": f"Appended section '{heading_text}'"}
