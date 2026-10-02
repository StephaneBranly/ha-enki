import re
import os
import json
import sys


# Add parent directory to path
sys.path.insert(1, os.path.join(sys.path[0], '../custom_components/enki'))
from const import ENKI_CAPABILITY
RAW_GITHUB_URL = "https://raw.githubusercontent.com/StephaneBranly/ha-enki/refs/heads/main"


# Lire le contenu du fichier


def update_anchor(current_page: str, tag: str, new_content: str) -> str:
    updated_page = re.sub(
        f"<!-- start {tag} -->.*?<!-- end -->",
        f"<!-- start {tag} -->\n{new_content}<!-- end -->",
        current_page,
        flags=re.DOTALL  # To match multiple lines
    )

    return updated_page

def compute_coverage(device: dict[str, any], capabilities: list[ENKI_CAPABILITY]) -> int:
    dcs = device.get('capabilities', [])
    coverage = 0
    if not (len(dcs)):
        return 100
    
    for dc in dcs:
        caps = [cap for cap in capabilities if cap.name == dc]
        if len(caps):
            coverage+=caps[0].coverage
    return int(coverage/len(dcs))

if __name__ == '__main__':
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    capabilities = ENKI_CAPABILITY.__subclasses__()

    supported_capabilities = '| Capability | Coverage (%) |\n|---|---|\n'
    for capability in capabilities:
        if not (coverage:=capability.coverage):
            continue
        name = capability.name if capability.name else str(capability.__name__)
        supported_capabilities += f"|{name}|![{coverage}%](https://progress-bar.xyz/{coverage})|\n"

    devices_cells = []
    NCOLS = 4

    for device_name in os.listdir("./doc/devices"):
        if not device_name.endswith(".json"):
            continue

        with open(f"./doc/devices/{device_name}") as dev_file:
            device = json.load(dev_file)

        if not (coverage := compute_coverage(device, capabilities)):
            continue

        img = (
            f"<img src='{RAW_GITHUB_URL}/doc/devices/{device.get('image', '')}' width='120' height='120'>"
            if device.get("image")
            else ""
        )

        tested = "✅ Tested" if device.get("tested", False) else "❌ Not tested"

        url = f'{RAW_GITHUB_URL}/doc/devices/{device_name}'
        cell = f"""
    <td align="center" width="{100//NCOLS}%"><a href="{url}" target="_blank">
    {img}<br>
    <b>{device.get('name', 'na')}</b><br>
    {device.get('manufacturer', 'na')}<br>
    {tested}</a>
    </td>
    """

        devices_cells.append(cell.strip())

    supported_devices = "<table>\n"

    for i in range(0, len(devices_cells), NCOLS):
        supported_devices += "<tr>\n"

        row = devices_cells[i:i+NCOLS]

        while len(row) < NCOLS:
            row.append(f"""<td width="{100//NCOLS}%"></td>""")

        supported_devices += "\n".join(row)
        supported_devices += "\n</tr>\n"

    supported_devices += "</table>"
    content = update_anchor(content, 'devices', supported_devices)
    content = update_anchor(content, 'capabilities', supported_capabilities)

    # Écrire le contenu mis à jour dans le fichier
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(update_anchor(content, 'devices', supported_devices)
    )