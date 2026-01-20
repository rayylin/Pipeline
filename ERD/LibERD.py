def draw_entity(entity_id, name, attributes, x, y, width=200, row_height=28):
    cells = []

    header_style = (
        "rounded=0;whiteSpace=wrap;html=1;"
        "fillColor=#ffffff;strokeColor=#000000;"
        "fontStyle=1;align=center;"
    )

    attr_style = (
        "rounded=0;whiteSpace=wrap;html=1;"
        "fillColor=#ffffff;strokeColor=#000000;"
        "align=left;spacingLeft=10;"
    )

    # Header
    cells.append(f"""
    <mxCell id="{entity_id}" value="{name}" style="{header_style}"
        vertex="1" parent="0">
        <mxGeometry x="{x}" y="{y}" width="{width}" height="{row_height}" as="geometry"/>
    </mxCell>
    """)

    # Attributes
    for i, attr in enumerate(attributes):
        cells.append(f"""
        <mxCell id="{entity_id}_{i}" value="{attr}" style="{attr_style}"
            vertex="1" parent="0">
            <mxGeometry x="{x}" y="{y + row_height * (i + 1)}"
                width="{width}" height="{row_height}" as="geometry"/>
        </mxCell>
        """)

    return "".join(cells)


def generate_drawio(filename):
    entities = []

    entities.append(draw_entity(
        "Book", "Book",
        ["book_id (PK)", "title", "genre", "publication_year"],
        50, 50
    ))

    entities.append(draw_entity(
        "BookCopy", "BookCopy",
        ["copy_id (PK)", "book_id (FK)", "purchase_date", "status"],
        300, 50
    ))

    entities.append(draw_entity(
        "Author", "Author",
        ["author_id (PK)", "name", "created_time"],
        50, 250
    ))

    entities.append(draw_entity(
        "BookAuthor", "BookAuthor",
        ["book_id (FK)", "author_id (FK)"],
        300, 250
    ))

    entities.append(draw_entity(
        "Patron", "Patron",
        [
            "patron_id (PK)",
            "ssn (UNIQUE, NOT NULL)",
            "name",
            "phone",
            "address",
            "status",
            "violation_count",
            "outstanding_balance",
            "join_date",
            "termination_date"
        ],
        600, 50
    ))

    entities.append(draw_entity(
        "Employee", "Employee",
        [
            "employee_id (PK)",
            "name",
            "phone",
            "address",
            "status",
            "join_date",
            "termination_date"
        ],
        600, 300
    ))

    entities.append(draw_entity(
        "BorrowTransaction", "BorrowTransaction",
        [
            "transaction_id (PK)",
            "copy_id (FK)",
            "patron_id (FK)",
            "employee_id (FK)",
            "borrow_date",
            "return_date",
            "status"
        ],
        900, 150
    ))

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram name="Library ER Diagram">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        {''.join(entities)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml)


if __name__ == "__main__":
    generate_drawio("library_er.drawio")