import math
import re
from pathlib import Path


def load_scad_parameters(path):
    values = {"true": True, "false": False}
    assignment_re = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^;]+);$")

    for raw_line in Path(path).read_text().splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue

        match = assignment_re.match(line)
        if not match:
            continue

        name, expr = match.groups()
        values[name] = eval(expr, {"__builtins__": {}}, values)

    return values


def course_heights(panel_height, featheredge_cover):
    board_count = math.ceil(panel_height / featheredge_cover) + 1
    return [i * featheredge_cover for i in range(1, board_count) if i * featheredge_cover < panel_height]


def main():
    params = load_scad_parameters(Path(__file__).with_name("parameters.scad"))

    front_panel_height = params["front_height"] - params["rail_h"]
    door_height = (
        params["front_height"]
        - params["rail_h"]
        - 2 * params["door_gap"]
        - params["door_head_clearance"]
    )
    left_wall_front_height = params["front_height"]
    left_wall_back_height = params["back_height"]

    panels = {
        "right_front_panel": front_panel_height,
        "door_panel": door_height,
        "left_wall_front_edge": left_wall_front_height,
        "left_wall_back_edge": left_wall_back_height,
    }

    print(f"featheredge_cover = {params['featheredge_cover']} mm")
    print()

    for panel_name, panel_height in panels.items():
        heights = course_heights(panel_height, params["featheredge_cover"])
        print(f"{panel_name}:")
        print(f"  panel_height = {panel_height} mm")
        print(f"  course_boundaries = {heights}")
        print()


if __name__ == "__main__":
    main()
