import xml.etree.ElementTree as ET






def create_cell(id, value, x, y, width=160, height=100, style=None, parent="1"):
    attrib = {
        'id': str(id),
        'value': value,
        'style': style or "shape=swimlane;startSize=30;",
        'vertex': "1",
        'parent': parent
    }
    cell = ET.Element('mxCell', attrib)
    ET.SubElement(cell, 'mxGeometry', {
        'x': str(x),
        'y': str(y),
        'width': str(width),
        'height': str(height),
        'as': 'geometry'
    })
    return cell

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

    for table, cols in tables.items():
        table_id = str(id_counter)
        id_counter += 1

        # Main container with swimlane
        swimlane_style = "shape=swimlane;startSize=30;swimlaneLine=1;"
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
            'width': "160",
            'height': str(30 + 20 * len(cols)),
            'as': 'geometry'
        })
        root.append(swimlane)

        # Body text inside the swimlane
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
            'y': "0",
            'width': "160",
            'height': str(20 * len(cols)),
            'as': 'geometry'
        })
        root.append(body)

        x += 220  # next shape position

    xml_str = ET.tostring(diagram, encoding='utf-8', method='xml')
    return xml_str

tables = {
    "Users": ["id", "username", "email"],
    "Orders": ["order_id", "user_id", "amount", "date"],
    "Products": ["product_id", "name", "price"]
}


with open("er_diagram1.drawio", "wb") as f:
    f.write(generate_drawio_xml(tables))