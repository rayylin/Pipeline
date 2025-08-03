import xml.etree.ElementTree as ET

def estimate_width(text, min_width=160, char_width=7):
    return max(min_width, len(text) * char_width)

def html_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def wrap_html(value):
    return f"<![CDATA[<div>{value}</div>]]>"

def generate_drawio_xml(tables):
    diagram = ET.Element('mxfile')
    diagram_doc = ET.SubElement(diagram, 'diagram', name="ERD")
    mxGraphModel = ET.SubElement(diagram_doc, 'mxGraphModel')
    root = ET.SubElement(mxGraphModel, 'root')

    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    x, y = 40, 40
    id_counter = 2
    row_height = 20
    header_rows = 2
    header_height = row_height * header_rows

    for raw_table, cols in tables.items():
        # Parse table name and description
        if "(" in raw_table:
            name = raw_table.split("(")[0].strip()
            desc = raw_table[raw_table.find("("):].strip()
        else:
            name = raw_table
            desc = ""

        # Format header using HTML
        escaped_name = html_escape(name)
        escaped_desc = html_escape(desc)
        full_header = f"<b>{escaped_name}</b>" + (f"<br><i>{escaped_desc}</i>" if desc else "")
        header_value = wrap_html(full_header)

        table_id = str(id_counter)
        id_counter += 1
        total_height = header_height + row_height * len(cols)
        max_text = max([name, desc] + cols, key=len)
        width = estimate_width(max_text)

        # Swimlane with HTML header
        swimlane = ET.Element('mxCell', {
            'id': table_id,
            'value': header_value,
            'style': f"shape=swimlane;startSize={header_height};swimlaneLine=1;html=1;whiteSpace=wrap;",
            'vertex': "1",
            'parent': "1"
        })
        ET.SubElement(swimlane, 'mxGeometry', {
            'x': str(x),
            'y': str(y),
            'width': str(width),
            'height': str(total_height),
            'as': 'geometry'
        })
        root.append(swimlane)

        # Add individual column lines
        for i, col in enumerate(cols):
            cell_id = str(id_counter)
            id_counter += 1
            col_cell = ET.Element('mxCell', {
                'id': cell_id,
                'value': html_escape(col),
                'style': "text;html=1;align=left;verticalAlign=middle;spacingLeft=4;",
                'vertex': "1",
                'parent': table_id
            })
            ET.SubElement(col_cell, 'mxGeometry', {
                'x': "0",
                'y': str(header_height + i * row_height),
                'width': str(width),
                'height': str(row_height),
                'as': 'geometry'
            })
            root.append(col_cell)

        x += width + 60

    return ET.tostring(diagram, encoding='utf-8', method='xml')

tables = {
    "Users (DB1.dbo.user)": ["id", "username", "email"],
    "Orders (DB2.sales.orders)": ["order_id", "user_id", "amount", "date"],
    "Products": ["product_id", "name", "price"]
}


with open("er_diagram7.drawio", "wb") as f:
    f.write(generate_drawio_xml(tables))