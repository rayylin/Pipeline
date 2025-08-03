import xml.etree.ElementTree as ET
import html

def estimate_width(text, min_width=160, char_width=7):
    return max(min_width, len(text) * char_width)

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
        # Parse table name and optional description
        if "(" in raw_table:
            name = raw_table.split("(")[0].strip()
            desc = raw_table[raw_table.find("("):].strip()
        else:
            name = raw_table
            desc = ""

        # Proper HTML escape
        escaped_name = html.escape(name)
        escaped_desc = html.escape(desc)
        full_header = f"<b>{escaped_name}</b>" + (f"<br><i>{escaped_desc}</i>" if desc else "")

        table_id = str(id_counter)
        id_counter += 1
        total_height = header_height + row_height * len(cols)
        max_text = max([name, desc] + cols, key=len)
        width = estimate_width(max_text)

        # Swimlane cell
        swimlane = ET.Element('mxCell', {
            'id': table_id,
            'value': full_header,
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

        # Add column cells
        for i, col in enumerate(cols):
            cell_id = str(id_counter)
            id_counter += 1
            col_cell = ET.Element('mxCell', {
                'id': cell_id,
                'value': html.escape(col),
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

tables = ["Users", "Orders", "Products", "Orders11111"]

descDic = {"Users": "DB1.dbo.user", "Orders": "DB2.sales.orders", "Products":"", "Orders11111": "DB222.sales.orders"}

tableList = {"Users": ["id", "username", "email"],
    "Orders": ["order_id", "user_id", "amount", "date"],
    "Products": ["product_id", "name", "price"],
    "Orders11111": ["order_id", "user_id", "amount", "date", "user_id", "amount", "date", "user_id", "amount", "date", "user_id", "amount", "date"]}

tablesDic =  {f"{i} {"(" +descDic[i]+")" if descDic[i] != "" else ""} " : tableList[i] for i in tables}

# format_desc = lambda s: f"({s})" if s else ""
# tablesDic = {f"{i} {format_desc(descDic[i])}": tableList[i] for i in tables}

#tablesDic = {f"{i} {(fmt := (lambda s: f'({s})' if s else ''))(descDic[i])}": tableList[i] for i in tables}



with open("er_diagram13.drawio", "wb") as f:
    f.write(generate_drawio_xml(tablesDic))