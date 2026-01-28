import os


def draw_entity(entity_id, name, attributes, x, y, width=200, row_height=28):
    cells = []

    total_height = row_height * (len(attributes) + 1)

    # Container (entity box)
    container_style = (
        "rounded=0;"
        "whiteSpace=wrap;"
        "html=1;"
        "fillColor=none;"
        "strokeColor=#000000;"
    )

    cells.append(f"""
    <mxCell id="{entity_id}_container"
        style="{container_style}"
        vertex="1"
        connectable="0"
        parent="0">
        <mxGeometry x="{x}" y="{y}"
            width="{width}" height="{total_height}"
            as="geometry"/>
    </mxCell>
    """)

    # Header
    header_style = (
        "rounded=0;"
        "whiteSpace=wrap;"
        "html=1;"
        "fillColor=#ffffff;"
        "strokeColor=#000000;"
        "fontStyle=1;"
        "align=center;"
    )

    cells.append(f"""
    <mxCell id="{entity_id}_header"
        value="{name}"
        style="{header_style}"
        vertex="1"
        parent="{entity_id}_container">
        <mxGeometry x="0" y="0"
            width="{width}" height="{row_height}"
            as="geometry"/>
    </mxCell>
    """)

    # Attributes
    attr_style = (
        "rounded=0;"
        "whiteSpace=wrap;"
        "html=1;"
        "fillColor=#ffffff;"
        "strokeColor=#000000;"
        "align=left;"
        "spacingLeft=10;"
    )

    for i, attr in enumerate(attributes):
        cells.append(f"""
        <mxCell id="{entity_id}_attr_{i}"
            value="{attr}"
            style="{attr_style}"
            vertex="1"
            parent="{entity_id}_container">
            <mxGeometry x="0" y="{row_height * (i + 1)}"
                width="{width}" height="{row_height}"
                as="geometry"/>
        </mxCell>
        """)

    return "".join(cells)


def generate_drawio(filename):
    entities = []

    # DEPARTMENTS
    entities.append(draw_entity(
        "Departments", "DEPARTMENTS",
        [
            "department_id (PK)",
            "department_name",
            "office_location"
        ],
        50, 50
    ))

    # PROGRAMS
    entities.append(draw_entity(
        "Programs", "PROGRAMS",
        [
            "program_id (PK)",
            "program_name",
            "department_id (FK)",
            "degree_level"
        ],
        320, 50
    ))

    # STUDENTS
    entities.append(draw_entity(
        "Students", "STUDENTS",
        [
            "student_id (PK)",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "email",
            "phone",
            "program_id (FK)"
        ],
        600, 50
    ))

    # COURSES
    entities.append(draw_entity(
        "Courses", "COURSES",
        [
            "course_id (PK)",
            "course_title",
            "credits",
            "department_id (FK)"
        ],
        50, 300
    ))

    # INSTRUCTORS
    entities.append(draw_entity(
        "Instructors", "INSTRUCTORS",
        [
            "instructor_id (PK)",
            "first_name",
            "last_name",
            "email",
            "department_id (FK)"
        ],
        320, 300
    ))

    # CLASSROOMS
    entities.append(draw_entity(
        "Classrooms", "CLASSROOMS",
        [
            "classroom_id (PK)",
            "building",
            "room_number",
            "capacity"
        ],
        600, 300
    ))

    # SEMESTERS
    entities.append(draw_entity(
        "Semesters", "SEMESTERS",
        [
            "semester_id (PK)",
            "term",
            "year",
            "start_date",
            "end_date"
        ],
        50, 560
    ))

    # COURSE_OFFERINGS
    entities.append(draw_entity(
        "CourseOfferings", "COURSE_OFFERINGS",
        [
            "offering_id (PK)",
            "course_id (FK)",
            "instructor_id (FK)",
            "semester_id (FK)",
            "classroom_id (FK)",
            "section_code",
            "meeting_days",
            "meeting_time"
        ],
        320, 560
    ))

    # ENROLLMENTS
    entities.append(draw_entity(
        "Enrollments", "ENROLLMENTS",
        [
            "enrollment_id (PK)",
            "student_id (FK)",
            "offering_id (FK)",
            "enrollment_date"
        ],
        650, 560
    ))

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram name="School ER Diagram">
    <mxGraphModel dx="1200" dy="900" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        {''.join(entities)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml)

    print("draw.io file generated at:")
    print(output_path)


if __name__ == "__main__":
    generate_drawio("school_er.drawio")