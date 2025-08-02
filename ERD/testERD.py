import xml.etree.ElementTree as ET

def generate_drawio_xml(tables):
    diagram = ET.Element('mxfile')
    diagram_doc = ET.SubElement(diagram, 'diagram', name="ERD")
    mxGraphModel = ET.SubElement(diagram_doc, 'mxGraphModel')
    root = ET.SubElement(mxGraphModel, 'root')

    # Root and layer
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    x, y = 40, 40
    id_counter = 2
    start_size = 30
    row_height = 20
    width = 160

    for table, cols in tables.items():
        table_id = str(id_counter)
        id_counter += 1
        total_height = start_size + row_height * len(cols)

        # Swimlane with header (table name)
        swimlane_style = f"shape=swimlane;startSize={start_size};swimlaneLine=1;"
        swimlane = ET.Element('mxCell', {
            'id': table_id,
            'value': table,
            'style': swimlane_style,
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

        # Body cell (columns), starting at Y = start_size
        content_id = str(id_counter)
        id_counter += 1
        body = ET.Element('mxCell', {
            'id': content_id,
            'value': "<br>".join(cols),
            'style': "text;html=1;align=left;verticalAlign=top;spacingLeft=4;",
            'vertex': "1",
            'parent': table_id
        })
        ET.SubElement(body, 'mxGeometry', {
            'x': "0",
            'y': str(start_size),  # Push down to below the header
            'width': str(width),
            'height': str(row_height * len(cols)),
            'as': 'geometry'
        })
        root.append(body)

        x += 220  # Next shape position

    return ET.tostring(diagram, encoding='utf-8', method='xml')

tables = {
    "Users": ["id", "username", "email"],
    "Orders": ["order_id", "user_id", "amount", "date","order_id", "user_id", "amount", "date","order_id", "user_id", "amount", "date"],
    "Products": ["product_id", "name", "price"]
}


with open("er_diagram3.drawio", "wb") as f:
    f.write(generate_drawio_xml(tables))