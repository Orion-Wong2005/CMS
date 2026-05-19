from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from flask import make_response, Response
import io

def export_to_excel(headers, data, filename):
    """
    通用 Excel 导出工具
    :param headers: 表头列表，例如 ['学号', '姓名', '成绩']
    :param data: 数据列表，二维数组
    :param filename: 导出文件名
    :return: Response 对象
    """
    # 创建工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = "数据导出"

    # 样式
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    center_alignment = Alignment(horizontal="center", vertical="center")

    # 写入表头
    ws.append(headers)
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_alignment

    # 写入数据
    for row in data:
        ws.append(row)

    # 自动调整列宽
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    # 保存到内存
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # 构建响应
    response = make_response(output.read())
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"

    return response
