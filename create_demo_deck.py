"""Build an editable PowerPoint deck using only Python stdlib and Pillow."""

from __future__ import annotations

import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "presentations"
EMU = 914400
SW, SH = 13.333 * EMU, 7.5 * EMU
NAVY, GREEN, MINT, WHITE, TEXT, MUTED, PANEL = "10243A", "22B573", "DDF7EA", "FFFFFF", "17324D", "63788E", "F1F6F8"


def terminal_image() -> Path:
    """Render real current CLI output and label the unavailable menu workflow honestly."""
    try:
        run = subprocess.run(
            [sys.executable, str(ROOT / "main.py")], input="0\nc\n", text=True,
            capture_output=True, cwd=ROOT, timeout=10,
        )
        output = run.stdout + run.stderr
    except Exception as exc:  # the slide still builds if CLI cannot launch
        output = f"Không chạy được CLI: {exc}"
    lines = output.splitlines()[:23]
    out = OUT / "screenshots" / "cli_menu.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1320, 760), "#111827")
    draw = ImageDraw.Draw(image)
    font_path = Path("C:/Windows/Fonts/consola.ttf")
    font = ImageFont.truetype(str(font_path), 20) if font_path.exists() else ImageFont.load_default()
    draw.rounded_rectangle((22, 22, 1298, 738), radius=18, fill="#111827", outline="#334155", width=2)
    draw.ellipse((48, 42, 64, 58), fill="#F87171")
    draw.ellipse((74, 42, 90, 58), fill="#FBBF24")
    draw.ellipse((100, 42, 116, 58), fill="#34D399")
    draw.text((142, 38), "Product Inventory Management System · CLI", font=font, fill="#94A3B8")
    y = 94
    for line in lines:
        draw.text((52, y), line[:94], font=font, fill="#D1FAE5" if "HỆ THỐNG" in line else "#E2E8F0")
        y += 27
    draw.text((52, 688), "Ảnh được dựng từ output CLI hiện tại; menu nghiệp vụ đang chờ tích hợp service.", font=ImageFont.load_default(), fill="#FBBF24")
    image.save(out)
    return out


def run_slide(shapes: list[str], slide_num: int, image_rel: bool = False) -> str:
    bg = f'<p:bg><p:bgPr><a:solidFill><a:srgbClr val="{WHITE}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
    image = ""
    if image_rel:
        image = f'''<p:pic><p:nvPicPr><p:cNvPr id="90" name="CLI screenshot"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="rId2"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{int(6.55*EMU)}" y="{int(1.65*EMU)}"/><a:ext cx="{int(6.1*EMU)}" cy="{int(3.52*EMU)}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'''
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld>{bg}<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>{''.join(shapes)}{image}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'''


def box(text: str, x: float, y: float, w: float, h: float, size: int = 18, color: str = TEXT,
        fill: str | None = None, bold: bool = False, align: str = "l", shape_id: int = 2) -> str:
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
    paragraphs = []
    for line in text.split("\n"):
        paragraphs.append(f'<a:p><a:pPr algn="{align}"/><a:r><a:rPr lang="vi-VN" sz="{size*100}" b="{1 if bold else 0}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Aptos"/></a:rPr><a:t>{escape(line)}</a:t></a:r><a:endParaRPr lang="vi-VN" sz="{size*100}"/></a:p>')
    return f'''<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="Text {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x*EMU)}" y="{int(y*EMU)}"/><a:ext cx="{int(w*EMU)}" cy="{int(h*EMU)}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>{fill_xml}<a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="120000" tIns="90000" rIns="120000" bIns="70000"/><a:lstStyle/>{''.join(paragraphs)}</p:txBody></p:sp>'''


def common(title: str, eyebrow: str, index: int, content: list[tuple[str, float, float, float, float, int, str, str | None, bool]]) -> list[str]:
    shapes = [box(eyebrow.upper(), .56, .35, 7, .32, 11, GREEN, bold=True, shape_id=2),
              box(title, .52, .78, 12, .58, 29, NAVY, bold=True, shape_id=3),
              box("PYTHON OOP  ·  CONSOLE CLI  ·  JSON / CSV", .55, 7.07, 9, .23, 9, MUTED, shape_id=88),
              box(f"{index:02d}", 12.25, 7.02, .55, .3, 10, GREEN, bold=True, align="r", shape_id=89)]
    for i, (txt, x, y, w, h, size, color, fill, bold) in enumerate(content, 10):
        shapes.append(box(txt, x, y, w, h, size, color, fill, bold, shape_id=i))
    return shapes


def build_deck() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    screenshot = terminal_image()
    slides: list[list[str]] = []
    slides.append([
        box("PRODUCT\nINVENTORY", .72, 1.0, 5.5, 1.8, 34, WHITE, bold=True, shape_id=2),
        box("MANAGEMENT SYSTEM", .75, 2.8, 5.8, .65, 24, GREEN, bold=True, shape_id=3),
        box("Quản lý kho sản phẩm bằng Python hướng đối tượng", .8, 3.6, 6.0, .8, 20, WHITE, shape_id=4),
        box("ĐỒ ÁN NHÓM  ·  06/11/2026 — 25/11/2026", .82, 5.85, 6, .45, 13, "B6C6D5", shape_id=5),
        box("01", 12.0, 6.8, .7, .35, 12, GREEN, bold=True, align="r", shape_id=6),
        box("INVENTORY\nIN  /  OUT\nREPORTS", 8.2, 1.25, 3.4, 3.4, 30, WHITE, "173A55", True, "ctr", 7),
    ])
    slides.append(common("Bài toán & mục tiêu", "01 / TỔNG QUAN", 2, [
        ("QUẢN LÝ TẬP TRUNG", .7, 1.7, 3.7, .65, 17, WHITE, NAVY, True),
        ("Sản phẩm · Nhà cung cấp\nNhập / xuất · Tồn kho", .7, 2.45, 3.7, 1.15, 19, TEXT, PANEL, False),
        ("KIỂM SOÁT NGHIỆP VỤ", 4.8, 1.7, 3.7, .65, 17, WHITE, NAVY, True),
        ("Không xuất vượt tồn\nKiểm tra hạn dùng / bảo hành", 4.8, 2.45, 3.7, 1.15, 19, TEXT, PANEL, False),
        ("DỮ LIỆU DỄ DÙNG", 8.9, 1.7, 3.7, .65, 17, WHITE, GREEN, True),
        ("JSON lưu trữ\nCSV mở bằng Excel", 8.9, 2.45, 3.7, 1.15, 19, TEXT, MINT, False),
        ("Mục tiêu OOP: đóng gói · kế thừa · đa hình", 1.1, 4.6, 10.8, .75, 24, NAVY, "EAF5F0", True),
    ]))
    slides.append(common("Kiến trúc phân tầng", "02 / THIẾT KẾ", 3, [
        ("NGƯỜI DÙNG", .65, 2.2, 2.2, .8, 18, WHITE, NAVY, True),
        ("Console CLI", 3.35, 2.2, 2.2, .8, 18, NAVY, MINT, True),
        ("Service nghiệp vụ\nInventory · Stock · Report", 6.05, 1.95, 3.0, 1.3, 16, WHITE, GREEN, True),
        ("Product models", 9.65, 1.95, 2.5, .8, 16, NAVY, PANEL, True),
        ("Storage", 9.65, 3.05, 2.5, .8, 16, NAVY, PANEL, True),
        ("JSON", 10.0, 4.35, 1.2, .65, 16, TEXT, MINT, True),
        ("CSV", 11.35, 4.35, 1.2, .65, 16, TEXT, MINT, True),
        ("Luồng: CLI điều phối → service xử lý nghiệp vụ → model / storage", 1.15, 5.65, 10.8, .7, 20, MUTED, None, False),
    ]))
    slides.append(common("UML lớp cốt lõi", "03 / OOP", 4, [
        ("Product\nproduct_id · name\nprice · quantity\nget_inventory_value()", .65, 2.0, 2.8, 1.75, 15, NAVY, "EAF5F0", True),
        ("FoodProduct\nexpiry_date\nis_valid()", 4.05, 1.55, 2.5, 1.25, 15, NAVY, PANEL, True),
        ("ElectronicProduct\nwarranty_months\nis_valid()", 4.05, 3.1, 2.5, 1.25, 15, NAVY, PANEL, True),
        ("InventoryManager\nCRUD · tìm · sắp xếp", 7.1, 1.55, 2.45, 1.15, 15, NAVY, PANEL, True),
        ("StockService\nnhập / xuất · lịch sử", 7.1, 3.0, 2.45, 1.15, 15, NAVY, PANEL, True),
        ("ReportService\nthống kê · nhà cung cấp", 10.05, 1.55, 2.55, 1.15, 15, NAVY, MINT, True),
        ("Storage\nJSON · CSV", 10.05, 3.0, 2.55, 1.15, 15, NAVY, MINT, True),
        ("FoodProduct và ElectronicProduct kế thừa Product; service dùng chung InventoryManager.", .8, 5.25, 11.8, .8, 18, MUTED, None, False),
    ]))
    slides.append(common("Workflow demo", "04 / QUY TRÌNH", 5, [
        ("01\nTạo sản phẩm", .65, 2.2, 2.4, 1.35, 20, NAVY, MINT, True),
        ("02\nNhập kho", 3.45, 2.2, 2.2, 1.35, 20, NAVY, PANEL, True),
        ("03\nXuất kho", 6.05, 2.2, 2.2, 1.35, 20, NAVY, PANEL, True),
        ("04\nLưu JSON", 8.65, 2.2, 2.0, 1.35, 20, NAVY, MINT, True),
        ("05\nXuất CSV", 11.05, 2.2, 1.8, 1.35, 20, NAVY, PANEL, True),
        ("Kiểm tra bổ sung: xuất vượt số lượng tồn phải bị từ chối và không làm thay đổi kho.", 1.1, 4.55, 11.2, .85, 21, WHITE, NAVY, True),
    ]))
    slides.append(common("Ảnh CLI hiện tại", "05 / DEMO", 6, [
        ("Chạy menu chính và chọn thoát an toàn", .65, 1.8, 5.6, .8, 20, NAVY, MINT, True),
        ("Menu hiện có; các menu nghiệp vụ chờ service được tích hợp.", .65, 3.0, 5.3, 1.1, 17, MUTED, PANEL, False),
    ]))
    slides.append(common("JSON & báo cáo CSV", "06 / DỮ LIỆU", 7, [
        ("ĐỊNH DẠNG JSON · MINH HỌA", .7, 1.8, 4.8, .55, 16, WHITE, NAVY, True),
        ('[{"type":"Product",\n  "product_id":"IT-001",\n  "quantity":6}]', .7, 2.45, 5.3, 1.55, 16, TEXT, PANEL, False),
        ("ĐỊNH DẠNG CSV · MINH HỌA", 6.7, 1.8, 4.8, .55, 16, WHITE, GREEN, True),
        ("type, product_id, name, price, quantity\nProduct, IT-001, Sản phẩm kiểm thử, 125000, 6", 6.7, 2.45, 5.7, 1.55, 15, TEXT, MINT, False),
        ("Ví dụ cấu trúc đầu ra; workflow tích hợp cần chạy sau khi các service được hoàn thiện.", 1.1, 5.1, 11.2, .7, 17, MUTED, None, False),
    ]))
    slides.append(common("Kiểm thử & bước tiếp theo", "07 / KẾT QUẢ", 8, [
        ("13 ca unit test lưu trữ\nJSON · subtype · lỗi dữ liệu · CSV", .8, 2.0, 5.4, 1.3, 20, NAVY, MINT, True),
        ("Workflow tích hợp\nTạo → nhập/xuất → JSON → CSV", 6.8, 2.0, 5.6, 1.3, 20, NAVY, PANEL, True),
        ("Tích hợp đầu-cuối cần chạy sau khi Product / InventoryManager / StockService được triển khai.", 1.0, 4.45, 11.4, .9, 18, "8A5A00", "FFF3CD", True),
        ("Cảm ơn!", 4.0, 5.8, 5.3, .6, 30, GREEN, None, True),
    ]))

    # Compose a minimal editable Office Open XML package.
    content_types = ['<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>', '<Default Extension="xml" ContentType="application/xml"/>', '<Default Extension="png" ContentType="image/png"/>', '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>', '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>', '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>', '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>']
    for i in range(1, len(slides) + 1):
        content_types.append(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    presentation_ids = ''.join(f'<p:sldId id="{255+i}" r:id="rId{i+1}"/>' for i in range(len(slides)))
    presentation_rels = '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>' + ''.join(f'<Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>' for i in range(1, len(slides)+1))
    out_file = OUT / "product_inventory_demo.pptx"
    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as z:
        def write(path: str, body: str):
            z.writestr(path, body.encode("utf-8"))
        write("[Content_Types].xml", f'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">{"".join(content_types)}</Types>')
        write("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>')
        write("ppt/presentation.xml", f'<?xml version="1.0" encoding="UTF-8"?><p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>{presentation_ids}</p:sldIdLst><p:sldSz cx="{int(SW)}" cy="{int(SH)}" type="screen16x9"/><p:notesSz cx="{int(7.5*EMU)}" cy="{int(10*EMU)}"/></p:presentation>')
        write("ppt/_rels/presentation.xml.rels", f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{presentation_rels}</Relationships>')
        master = '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
        write("ppt/slideMasters/slideMaster1.xml", master)
        write("ppt/slideMasters/_rels/slideMaster1.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>')
        layout = '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
        write("ppt/slideLayouts/slideLayout1.xml", layout)
        write("ppt/slideLayouts/_rels/slideLayout1.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>')
        write("ppt/theme/theme1.xml", '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Inventory"><a:themeElements><a:clrScheme name="Inventory"><a:dk1><a:srgbClr val="10243A"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="17324D"/></a:dk2><a:lt2><a:srgbClr val="F1F6F8"/></a:lt2><a:accent1><a:srgbClr val="22B573"/></a:accent1><a:accent2><a:srgbClr val="DDF7EA"/></a:accent2><a:accent3><a:srgbClr val="63788E"/></a:accent3><a:accent4><a:srgbClr val="FBBF24"/></a:accent4><a:accent5><a:srgbClr val="60A5FA"/></a:accent5><a:accent6><a:srgbClr val="F87171"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme><a:fontScheme name="Aptos"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements></a:theme>')
        for i, shapes in enumerate(slides, 1):
            # Dark navy cover and screenshot picture slide.
            if i == 1:
                shapes.insert(0, f'<p:sp><p:nvSpPr><p:cNvPr id="99" name="Cover background"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{int(SW)}" cy="{int(SH)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr></p:sp>')
                shapes = [shapes[0]] + shapes[1:]
            has_img = i == 6
            write(f"ppt/slides/slide{i}.xml", run_slide(shapes, i, has_img))
            rel = '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
            if has_img:
                rel += '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/cli_menu.png"/>'
            write(f"ppt/slides/_rels/slide{i}.xml.rels", f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rel}</Relationships>')
        z.write(screenshot, "ppt/media/cli_menu.png")
    return out_file


if __name__ == "__main__":
    print(build_deck())
