import xml.etree.ElementTree as ET
import base64


tables = {
    "Users": ["id", "username", "email"],
    "Orders": ["order_id", "user_id", "amount", "date"],
    "Products": ["product_id", "name", "price"]
}



def create_cell(id, value, x, y, width=120, height=20, style=None, parent="1"):
    attrib = {
        'id': str(id),
        'value': value,
        'style': style or "shape=swimlane;startSize=20;",
        'vertex': "1",
        'parent': parent
    }
    cell = ET.Element('mxCell', attrib)
    geometry = ET.SubElement(cell, 'mxGeometry', {
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

    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    x, y = 40, 40
    id_counter = 2

    for table, cols in tables.items():
        # Header cell
        height = 30 + 20 * len(cols)
        label = f"<b>{table}</b><br>" + "<br>".join(cols)
        cell = create_cell(id_counter, label, x, y, 160, height)
        root.append(cell)
        id_counter += 1
        x += 200  # move x for next shape

    xml_str = ET.tostring(diagram, encoding='utf-8')
    return xml_str


with open("er_diagram.drawio", "wb") as f:
    f.write(generate_drawio_xml(tables))