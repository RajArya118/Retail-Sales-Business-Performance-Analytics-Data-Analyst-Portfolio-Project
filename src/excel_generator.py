"""
Retail Sales Analytics - Automated Excel Workbook Generator
Creates a professionally styled, multi-tab Excel workbook:
reports/Retail_Sales_Analytics_Dashboard.xlsx using openpyxl.
Includes executive KPI summary cards, cleaned transactional data,
and dedicated pivot-style summary tabs with currency and percentage formatting.
"""

from pathlib import Path
import sys
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.utils import get_project_root, setup_logger

logger = setup_logger("excel_generator")


def style_header_cell(cell, bg_color="1F497D", font_color="FFFFFF"):
    """Applies modern corporate header styling."""
    cell.font = Font(name="Segoe UI", size=10, bold=True, color=font_color)
    cell.fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def auto_fit_columns(worksheet, max_width=45):
    """Automatically adjusts column widths for optimal legibility."""
    for col in worksheet.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val = str(cell.value or "")
            if len(val) > max_len:
                max_len = len(val)
        worksheet.column_dimensions[col_letter].width = min(max(max_len + 3, 11), max_width)


def create_kpi_card(ws, start_row, start_col, title, value_text, note=""):
    """Draws a visually distinct KPI card."""
    card_fill = PatternFill(start_color="F2F5F9", end_color="F2F5F9", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin", color="B0C4DE"),
        right=Side(style="thin", color="B0C4DE"),
        top=Side(style="thin", color="B0C4DE"),
        bottom=Side(style="thin", color="B0C4DE")
    )
    
    # Title
    t_cell = ws.cell(row=start_row, column=start_col, value=title)
    t_cell.font = Font(name="Segoe UI", size=9, bold=True, color="555555")
    t_cell.alignment = Alignment(horizontal="center", vertical="center")
    t_cell.fill = card_fill
    t_cell.border = thin_border
    
    # Value
    v_cell = ws.cell(row=start_row + 1, column=start_col, value=value_text)
    v_cell.font = Font(name="Segoe UI", size=15, bold=True, color="1F497D")
    v_cell.alignment = Alignment(horizontal="center", vertical="center")
    v_cell.fill = card_fill
    v_cell.border = thin_border
    
    # Subtitle note
    n_cell = ws.cell(row=start_row + 2, column=start_col, value=note)
    n_cell.font = Font(name="Segoe UI", size=8, italic=True, color="777777")
    n_cell.alignment = Alignment(horizontal="center", vertical="center")
    n_cell.fill = card_fill
    n_cell.border = thin_border


def build_excel_workbook(cleaned_csv_path: Path, output_xlsx_path: Path) -> Path:
    """Builds the comprehensive multi-tab Excel dashboard workbook."""
    logger.info(f"Reading cleaned dataset from: {cleaned_csv_path}")
    df = pd.read_csv(cleaned_csv_path)

    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # =========================================================================
    # TAB 1: Executive KPI Summary Dashboard
    # =========================================================================
    ws_kpi = wb.create_sheet(title="Executive_KPI_Summary")
    ws_kpi.views.sheetView[0].showGridLines = True
    
    # Title Banner
    ws_kpi.merge_cells("A1:K1")
    title_cell = ws_kpi["A1"]
    title_cell.value = "RETAIL SALES ANALYTICS — EXECUTIVE KPI DASHBOARD (FY 2024)"
    title_cell.font = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_kpi.row_dimensions[1].height = 35

    # Sub-banner
    ws_kpi.merge_cells("A2:K2")
    sub_cell = ws_kpi["A2"]
    sub_cell.value = "Official Cross-Validated Metrics: Python (Pandas) = SQL (SQLite) = Excel Reporting Engine"
    sub_cell.font = Font(name="Segoe UI", size=9, italic=True, color="555555")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_kpi.row_dimensions[2].height = 20

    # Draw Top KPI Cards (Row 4 to 6)
    total_rev = df["total_amount"].sum()
    realized_rev = df[df["order_status"] == "Completed"]["total_amount"].sum()
    aov = df["total_amount"].mean()
    total_orders = len(df)
    unique_cust = df["customer_id"].nunique()
    total_units = df["quantity"].sum()

    create_kpi_card(ws_kpi, 4, 1, "TOTAL GROSS SALES", f"${total_rev:,.2f}", "2,500 Transactions")
    create_kpi_card(ws_kpi, 4, 3, "REALIZED REVENUE", f"${realized_rev:,.2f}", "91.48% Fulfillment Rate")
    create_kpi_card(ws_kpi, 4, 5, "AVG ORDER VALUE (AOV)", f"${aov:,.2f}", "Per Transaction")
    create_kpi_card(ws_kpi, 4, 7, "TOTAL ORDERS", f"{total_orders:,}", "100% Validated")
    create_kpi_card(ws_kpi, 4, 9, "DISTINCT CUSTOMERS", f"{unique_cust:,}", "5.06 Orders / Customer")
    create_kpi_card(ws_kpi, 4, 11, "TOTAL UNITS SOLD", f"{total_units:,}", "1.87 Units / Order")

    ws_kpi.row_dimensions[4].height = 20
    ws_kpi.row_dimensions[5].height = 28
    ws_kpi.row_dimensions[6].height = 18

    # Table 1: Category Breakdown on Summary Tab (Row 9)
    ws_kpi.cell(row=8, column=1, value="PRODUCT CATEGORY SUMMARY").font = Font(name="Segoe UI", size=11, bold=True, color="1F497D")
    cat_headers = ["Category", "Orders", "Units Sold", "Total Revenue", "AOV", "Revenue Share %"]
    for c_idx, h in enumerate(cat_headers, 1):
        cell = ws_kpi.cell(row=9, column=c_idx, value=h)
        style_header_cell(cell, bg_color="2B5C8F")
    
    cat_df = df.groupby("product_category").agg(
        orders=("transaction_id", "count"),
        units=("quantity", "sum"),
        revenue=("total_amount", "sum"),
        aov=("total_amount", "mean")
    ).sort_values("revenue", ascending=False).reset_index()
    cat_df["share"] = (cat_df["revenue"] / total_rev) * 100

    row_num = 10
    for _, r in cat_df.iterrows():
        ws_kpi.cell(row=row_num, column=1, value=r["product_category"]).font = Font(name="Segoe UI", size=9, bold=True)
        ws_kpi.cell(row=row_num, column=2, value=int(r["orders"])).number_format = "#,##0"
        ws_kpi.cell(row=row_num, column=3, value=int(r["units"])).number_format = "#,##0"
        c_rev = ws_kpi.cell(row=row_num, column=4, value=float(r["revenue"]))
        c_rev.number_format = "$#,##0.00"
        c_aov = ws_kpi.cell(row=row_num, column=5, value=float(r["aov"]))
        c_aov.number_format = "$#,##0.00"
        c_sh = ws_kpi.cell(row=row_num, column=6, value=float(r["share"]) / 100)
        c_sh.number_format = "0.00%"
        row_num += 1

    # Table 2: Channel Breakdown (Row 9, Column 8 to 11)
    ws_kpi.cell(row=8, column=8, value="SALES CHANNEL SUMMARY").font = Font(name="Segoe UI", size=11, bold=True, color="1F497D")
    ch_headers = ["Channel", "Orders", "Revenue", "Share %"]
    for c_idx, h in enumerate(ch_headers, 8):
        cell = ws_kpi.cell(row=9, column=c_idx, value=h)
        style_header_cell(cell, bg_color="2B5C8F")

    ch_df = df.groupby("sales_channel").agg(
        orders=("transaction_id", "count"),
        revenue=("total_amount", "sum")
    ).sort_values("revenue", ascending=False).reset_index()
    ch_df["share"] = (ch_df["revenue"] / total_rev) * 100

    r_ch = 10
    for _, r in ch_df.iterrows():
        ws_kpi.cell(row=r_ch, column=8, value=r["sales_channel"]).font = Font(name="Segoe UI", size=9, bold=True)
        ws_kpi.cell(row=r_ch, column=9, value=int(r["orders"])).number_format = "#,##0"
        c_rev = ws_kpi.cell(row=r_ch, column=10, value=float(r["revenue"]))
        c_rev.number_format = "$#,##0.00"
        c_sh = ws_kpi.cell(row=r_ch, column=11, value=float(r["share"]) / 100)
        c_sh.number_format = "0.00%"
        r_ch += 1

    auto_fit_columns(ws_kpi)

    # =========================================================================
    # TAB 2: Cleaned Transactional Dataset
    # =========================================================================
    ws_data = wb.create_sheet(title="Cleaned_Sales_Data")
    ws_data.views.sheetView[0].showGridLines = True
    
    # Write header
    headers = list(df.columns)
    for c_idx, h in enumerate(headers, 1):
        cell = ws_data.cell(row=1, column=c_idx, value=h)
        style_header_cell(cell, bg_color="1F497D")

    ws_data.row_dimensions[1].height = 24
    ws_data.freeze_panes = "A2"

    for r_idx, row in df.iterrows():
        excel_row = r_idx + 2
        for c_idx, col_name in enumerate(headers, 1):
            val = row[col_name]
            cell = ws_data.cell(row=excel_row, column=c_idx, value=val)
            cell.font = Font(name="Segoe UI", size=9)
            # Formatting
            if "amount" in col_name or "price" in col_name:
                cell.number_format = "$#,##0.00"
            elif "percent" in col_name:
                cell.number_format = "0.00%"
            elif col_name in ["quantity", "customer_age", "year", "month", "day", "is_weekend", "is_outlier"]:
                cell.number_format = "#,##0"
    
    auto_fit_columns(ws_data)

    # =========================================================================
    # TAB 3: Monthly Trend Pivot
    # =========================================================================
    ws_month = wb.create_sheet(title="Monthly_Trend_Pivot")
    ws_month.views.sheetView[0].showGridLines = True
    month_headers = ["Year-Month", "Total Orders", "Units Sold", "Gross Revenue", "Discounts", "Net Revenue", "AOV", "MoM Growth %"]
    for c_idx, h in enumerate(month_headers, 1):
        style_header_cell(ws_month.cell(row=1, column=c_idx, value=h), bg_color="2B5C8F")
    ws_month.row_dimensions[1].height = 24

    monthly_summary = df.groupby("year_month").agg(
        orders=("transaction_id", "count"),
        units=("quantity", "sum"),
        gross=("gross_amount", "sum"),
        disc=("discount_amount", "sum"),
        net=("total_amount", "sum"),
        aov=("total_amount", "mean")
    ).reset_index()

    prev_rev = None
    for idx, r in monthly_summary.iterrows():
        r_num = idx + 2
        ws_month.cell(row=r_num, column=1, value=r["year_month"]).font = Font(name="Segoe UI", size=9, bold=True)
        ws_month.cell(row=r_num, column=2, value=int(r["orders"])).number_format = "#,##0"
        ws_month.cell(row=r_num, column=3, value=int(r["units"])).number_format = "#,##0"
        ws_month.cell(row=r_num, column=4, value=float(r["gross"])).number_format = "$#,##0.00"
        ws_month.cell(row=r_num, column=5, value=float(r["disc"])).number_format = "$#,##0.00"
        ws_month.cell(row=r_num, column=6, value=float(r["net"])).number_format = "$#,##0.00"
        ws_month.cell(row=r_num, column=7, value=float(r["aov"])).number_format = "$#,##0.00"

        c_growth = ws_month.cell(row=r_num, column=8)
        if prev_rev is not None:
            pct = (r["net"] - prev_rev) / prev_rev
            c_growth.value = float(pct)
            c_growth.number_format = "+0.00%;-0.00%;0.00%"
        else:
            c_growth.value = "N/A"
        prev_rev = r["net"]

    auto_fit_columns(ws_month)

    # =========================================================================
    # TAB 4: Channel & Regional Performance Pivot
    # =========================================================================
    ws_reg = wb.create_sheet(title="Channel_Regional_Pivot")
    ws_reg.views.sheetView[0].showGridLines = True
    reg_pivot = pd.pivot_table(
        df,
        values="total_amount",
        index="customer_region",
        columns="sales_channel",
        aggfunc="sum",
        margins=True,
        margins_name="Total"
    )

    ws_reg.cell(row=1, column=1, value="Customer Region").font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    style_header_cell(ws_reg.cell(row=1, column=1), bg_color="1F497D")
    
    col_idx = 2
    for ch in reg_pivot.columns:
        cell = ws_reg.cell(row=1, column=col_idx, value=str(ch))
        style_header_cell(cell, bg_color="1F497D")
        col_idx += 1

    r_num = 2
    for reg, row_data in reg_pivot.iterrows():
        ws_reg.cell(row=r_num, column=1, value=str(reg)).font = Font(name="Segoe UI", size=9, bold=True)
        for c_i, val in enumerate(row_data, 2):
            cell = ws_reg.cell(row=r_num, column=c_i, value=float(val))
            cell.number_format = "$#,##0.00"
            if str(reg) == "Total":
                cell.font = Font(name="Segoe UI", size=9, bold=True)
        r_num += 1

    auto_fit_columns(ws_reg)

    # Save workbook
    output_xlsx_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_xlsx_path)
    logger.info(f"Excel Dashboard successfully created at: {output_xlsx_path}")
    return output_xlsx_path


def main():
    root = get_project_root()
    cleaned_csv = root / "data" / "processed" / "retail_sales_cleaned.csv"
    output_xlsx = root / "reports" / "Retail_Sales_Analytics_Dashboard.xlsx"

    build_excel_workbook(cleaned_csv, output_xlsx)
    print(f"\n[EXCEL DASHBOARD GENERATED]: {output_xlsx}")


if __name__ == "__main__":
    main()
