"""
Retail Sales Analytics - Data Cleaning & Exploratory Data Analysis (EDA)
Performs data cleaning, feature engineering, and generates publication-grade visualizations.
Saves the cleaned dataset to data/processed/retail_sales_cleaned.csv and charts to charts/ and reports/figures/.
"""

import sys
from pathlib import Path
import shutil
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import seaborn as sns

try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.utils import get_project_root, setup_logger, print_section

logger = setup_logger("eda_cleaning")

# Styling configurations
sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def clean_and_enrich_data(raw_csv_path: Path) -> pd.DataFrame:
    """
    Cleans raw retail sales data, parses dates, derives temporal and financial features,
    and flags statistical anomalies.
    """
    logger.info(f"Loading raw dataset from: {raw_csv_path}")
    df = pd.read_csv(raw_csv_path)
    
    # 1. Datetime Parsing & Temporal Feature Extraction
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["year_month"] = df["date"].dt.strftime("%Y-%m")
    df["day"] = df["date"].dt.day
    df["day_name"] = df["date"].dt.strftime("%A")
    df["day_of_week"] = df["date"].dt.dayofweek  # 0=Monday, 6=Sunday
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    
    # 2. Financial Breakdown Metrics
    df["gross_amount"] = (df["quantity"] * df["unit_price"]).round(2)
    df["net_amount"] = (df["gross_amount"] - df["discount_amount"]).round(2)
    
    # 3. Customer Demographic Segmentation
    age_bins = [17, 25, 35, 50, 65, 100]
    age_labels = ["18-25 (Gen Z)", "26-35 (Millennial)", "36-50 (Gen X)", "51-65 (Boomer)", "65+ (Senior)"]
    df["age_group"] = pd.cut(df["customer_age"], bins=age_bins, labels=age_labels)
    
    # 4. Outlier Flagging via IQR Method on total_amount
    q1 = df["total_amount"].quantile(0.25)
    q3 = df["total_amount"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = max(0, q1 - 1.5 * iqr)
    upper_bound = q3 + 1.5 * iqr
    df["is_outlier"] = ((df["total_amount"] < lower_bound) | (df["total_amount"] > upper_bound)).astype(int)
    
    logger.info(f"Data enrichment complete. Total records: {len(df)}. Total columns: {len(df.columns)}")
    logger.info(f"IQR Outlier bounds for Total Amount: [${lower_bound:.2f}, ${upper_bound:.2f}]. Outlier rows: {df['is_outlier'].sum()}")
    return df


def generate_all_charts(df: pd.DataFrame, output_dirs: list[Path]) -> list[Path]:
    """
    Produces 8 publication-grade visualization charts and saves them to designated directories.
    """
    generated_charts = []
    
    # -------------------------------------------------------------
    # Chart 1: Monthly Revenue & Order Volume Trend
    # -------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(12, 6))
    monthly = df.groupby("year_month").agg(
        revenue=("total_amount", "sum"),
        order_count=("transaction_id", "count")
    ).reset_index()
    
    color_rev = "#1f77b4"
    color_vol = "#ff7f0e"
    
    bars = ax1.bar(monthly["year_month"], monthly["revenue"] / 1000, color=color_rev, alpha=0.82, label="Revenue ($K)", width=0.55)
    ax1.set_ylabel("Monthly Revenue ($ in Thousands)", color=color_rev, fontsize=12, fontweight="bold")
    ax1.set_xlabel("Year-Month (2024)", fontsize=12, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color_rev)
    ax1.set_ylim(0, max(monthly["revenue"] / 1000) * 1.25)
    
    # Annotate bar values
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f"${height:.1f}K",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold", color="#333333")
        
    ax2 = ax1.twinx()
    ax2.plot(monthly["year_month"], monthly["order_count"], color=color_vol, marker="o", linewidth=2.5, markersize=7, label="Order Count")
    ax2.set_ylabel("Total Orders Count", color=color_vol, fontsize=12, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=color_vol)
    ax2.set_ylim(0, max(monthly["order_count"]) * 1.25)
    ax2.grid(False)
    
    plt.title("Monthly Retail Revenue and Order Volume (2024 Seasonality)", fontsize=14, fontweight="bold", pad=15)
    fig.tight_layout()
    chart_name = "01_monthly_sales_trend.png"
    for d in output_dirs:
        p = d / chart_name
        plt.savefig(p, dpi=300, bbox_inches="tight")
        generated_charts.append(p)
    plt.close()

    # -------------------------------------------------------------
    # Chart 2: Revenue and Order Count by Product Category
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    cat_summary = df.groupby("product_category").agg(
        revenue=("total_amount", "sum"),
        aov=("total_amount", "mean"),
        count=("transaction_id", "count")
    ).sort_values("revenue", ascending=True)
    
    colors = sns.color_palette("mako", len(cat_summary))
    y_pos = np.arange(len(cat_summary))
    
    # Subplot A: Total Revenue
    bars_rev = ax1.barh(y_pos, cat_summary["revenue"] / 1000, color=colors, height=0.6)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(cat_summary.index, fontsize=11, fontweight="bold")
    ax1.set_xlabel("Total Revenue ($ in Thousands)", fontsize=11, fontweight="bold")
    ax1.set_title("Total Revenue by Category ($K)", fontsize=12, fontweight="bold")
    for bar in bars_rev:
        width = bar.get_width()
        ax1.annotate(f"${width:.1f}K",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=9, fontweight="bold")
    ax1.set_xlim(0, max(cat_summary["revenue"] / 1000) * 1.22)
    
    # Subplot B: Average Order Value (AOV)
    bars_aov = ax2.barh(y_pos, cat_summary["aov"], color=sns.color_palette("flare", len(cat_summary)), height=0.6)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([])
    ax2.set_xlabel("Average Order Value ($)", fontsize=11, fontweight="bold")
    ax2.set_title("Average Order Value (AOV) by Category", fontsize=12, fontweight="bold")
    for bar in bars_aov:
        width = bar.get_width()
        ax2.annotate(f"${width:.2f}",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=9, fontweight="bold")
    ax2.set_xlim(0, max(cat_summary["aov"]) * 1.25)
    
    fig.suptitle("Product Category Performance: Total Revenue vs. Average Order Value", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    chart_name = "02_revenue_by_category.png"
    for d in output_dirs:
        p = d / chart_name
        plt.savefig(p, dpi=300, bbox_inches="tight")
        generated_charts.append(p)
    plt.close()

    # -------------------------------------------------------------
    # Chart 3: Sales Channel Performance (Revenue & Volume)
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    channel_summary = df.groupby("sales_channel").agg(
        revenue=("total_amount", "sum"),
        count=("transaction_id", "count")
    )
    
    palette = ["#2b5c8f", "#d95f02", "#7570b3"]
    # Donut chart for Revenue
    wedges1, texts1, autotexts1 = ax1.pie(
        channel_summary["revenue"],
        labels=channel_summary.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=palette,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        pctdistance=0.75
    )
    for at in autotexts1:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("white")
    ax1.set_title("Revenue Share by Channel", fontsize=12, fontweight="bold")
    
    # Donut chart for Order Volume
    wedges2, texts2, autotexts2 = ax2.pie(
        channel_summary["count"],
        labels=channel_summary.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=palette,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        pctdistance=0.75
    )
    for at in autotexts2:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("white")
    ax2.set_title("Transaction Volume Share by Channel", fontsize=12, fontweight="bold")
    
    fig.suptitle("Multi-Channel Distribution (Online vs. In-Store vs. Mobile App)", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    chart_name = "03_sales_channel_distribution.png"
    for d in output_dirs:
        p = d / chart_name
        plt.savefig(p, dpi=300, bbox_inches="tight")
        generated_charts.append(p)
    plt.close()

    # -------------------------------------------------------------
    # Chart 4: Customer Age Distribution & Age Group Revenue
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Subplot A: Age Histogram with KDE
    sns.histplot(df["customer_age"], bins=20, kde=True, color="#2b5c8f", ax=ax1, edgecolor="white")
    ax1.set_title("Customer Age Distribution", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Customer Age (Years)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Customer Count", fontsize=11, fontweight="bold")
    median_age = df["customer_age"].median()
    mean_age = df["customer_age"].mean()
    ax1.axvline(median_age, color="red", linestyle="--", linewidth=1.8, label=f"Median: {median_age:.0f} yrs")
    ax1.axvline(mean_age, color="green", linestyle=":", linewidth=1.8, label=f"Mean: {mean_age:.1f} yrs")
    ax1.legend(loc="upper right")
    
    # Subplot B: Revenue by Age Group
    age_rev = df.groupby("age_group", observed=False)["total_amount"].sum() / 1000
    colors_age = sns.color_palette("crest", len(age_rev))
    bars_age = ax2.bar(range(len(age_rev)), age_rev, color=colors_age, width=0.55)
    ax2.set_xticks(range(len(age_rev)))
    ax2.set_xticklabels(age_rev.index, rotation=25, ha="right", fontsize=9, fontweight="bold")
    ax2.set_ylabel("Total Revenue ($ in Thousands)", fontsize=11, fontweight="bold")
    ax2.set_title("Revenue by Age Group Cohort ($K)", fontsize=12, fontweight="bold")
    for bar in bars_age:
        height = bar.get_height()
        ax2.annotate(f"${height:.1f}K",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax2.set_ylim(0, max(age_rev) * 1.20)
    
    fig.suptitle("Customer Demographics: Age Distribution and Cohort Contribution", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    chart_name = "04_customer_age_distribution.png"
    for d in output_dirs:
        p = d / chart_name
        plt.savefig(p, dpi=300, bbox_inches="tight")
        generated_charts.append(p)
    plt.close()

    # -------------------------------------------------------------
    # Chart 5: Discount Tiers vs. Order Value and Volume
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Subplot A: Boxplot of Total Amount by Discount Tier
    df["discount_tier_label"] = (df["discount_percent"] * 100).astype(int).astype(str) + "%"
    ordered_tiers = ["0%", "5%", "10%", "15%", "20%", "25%"]
    tier_palette = sns.color_palette("viridis", len(ordered_tiers))
    
    sns.boxplot(
        data=df,
        x="discount_tier_label",
        y="total_amount",
        order=ordered_tiers,
        palette=tier_palette,
        ax=ax1,
        showfliers=False,
        width=0.5
    )
    ax1.set_title("Order Value Distribution by Discount Tier (No Outliers)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Discount Tier Applied", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Order Total Amount ($)", fontsize=11, fontweight="bold")
    
    # Subplot B: Average Quantity by Discount Tier
    tier_stats = df.groupby("discount_tier_label", observed=False).agg(
        avg_qty=("quantity", "mean"),
        count=("transaction_id", "count")
    ).reindex(ordered_tiers)
    
    bars_tier = ax2.bar(range(len(tier_stats)), tier_stats["avg_qty"], color=tier_palette, width=0.55)
    ax2.set_xticks(range(len(tier_stats)))
    ax2.set_xticklabels(tier_stats.index, fontsize=10, fontweight="bold")
    ax2.set_xlabel("Discount Tier", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Average Units Purchased per Order", fontsize=11, fontweight="bold")
    ax2.set_title("Average Basket Size (Units) by Discount Tier", fontsize=12, fontweight="bold")
    for bar in bars_tier:
        height = bar.get_height()
        ax2.annotate(f"{height:.2f} pcs",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax2.set_ylim(0, max(tier_stats["avg_qty"]) * 1.30)
    
    fig.suptitle("Impact of Discount Tiers on Basket Value and Purchasing Volume", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    chart_name = "05_discount_vs_order_value.png"
    for d in output_dirs:
        p = d / chart_name
        plt.savefig(p, dpi=300, bbox_inches="tight")
        generated_charts.append(p)
    plt.close()

    # -------------------------------------------------------------
    # Chart 6: Regional Performance Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    region_stats = df.groupby("customer_region").agg(
        revenue=("total_amount", "sum"),
        order_count=("transaction_id", "count"),
        aov=("total_amount", "mean")
    ).sort_values("revenue", ascending=False)
    
    colors_reg = sns.color_palette("Blues_r", len(region_stats))
    bars_reg = ax.bar(region_stats.index, region_stats["revenue"] / 1000, color=colors_reg, width=0.55)
    ax.set_ylabel("Total Revenue ($ in Thousands)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Customer Geographic Region", fontsize=11, fontweight="bold")
    ax.set_title("Geographic Performance: Total Revenue and AOV by Region", fontsize=13, fontweight="bold", pad=15)
    
    for i, bar in enumerate(bars_reg):
        reg = region_stats.index[i]
        rev = bar.get_height()
        aov = region_stats.loc[reg, "aov"]
        orders = region_stats.loc[reg, "order_count"]
        ax.annotate(f"${rev:.1f}K\n({orders} txns)\nAOV: ${aov:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, rev),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold", color="#222222")
    ax.set_ylim(0, max(region_stats["revenue"] / 1000) * 1.32)
    
    fig.tight_layout()
    chart_name = "06_regional_performance.png"
    for d in output_dirs:
        p = d / chart_name
        plt.savefig(p, dpi=300, bbox_inches="tight")
        generated_charts.append(p)
    plt.close()

    # -------------------------------------------------------------
    # Chart 7: Order Fulfillment Status & Loss Leakage
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    status_counts = df["order_status"].value_counts()
    status_palette = {"Completed": "#2ca02c", "Returned": "#d62728", "Cancelled": "#ff7f0e", "Pending": "#1f77b4"}
    ordered_statuses = ["Completed", "Returned", "Cancelled", "Pending"]
    
    # Donut chart of Status
    wedges, texts, autotexts = ax1.pie(
        [status_counts.get(s, 0) for s in ordered_statuses],
        labels=ordered_statuses,
        autopct="%1.1f%%",
        startangle=140,
        colors=[status_palette[s] for s in ordered_statuses],
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
        pctdistance=0.75
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("white")
    ax1.set_title("Order Fulfillment Status Breakdown (%)", fontsize=12, fontweight="bold")
    
    # Bar chart of Revenue Realized vs. Lost
    status_rev = df.groupby("order_status")["total_amount"].sum().reindex(ordered_statuses) / 1000
    bars_st = ax2.bar(ordered_statuses, status_rev, color=[status_palette[s] for s in ordered_statuses], width=0.55)
    ax2.set_ylabel("Monetary Volume ($ in Thousands)", fontsize=11, fontweight="bold")
    ax2.set_title("Monetary Impact by Fulfillment Status ($K)", fontsize=12, fontweight="bold")
    for bar in bars_st:
        height = bar.get_height()
        ax2.annotate(f"${height:.1f}K",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax2.set_ylim(0, max(status_rev) * 1.22)
    
    fig.suptitle("Fulfillment Pipeline Analysis: Realized Revenue vs. Returns & Cancellations", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    chart_name = "07_order_status_breakdown.png"
    for d in output_dirs:
        p = d / chart_name
        plt.savefig(p, dpi=300, bbox_inches="tight")
        generated_charts.append(p)
    plt.close()

    # -------------------------------------------------------------
    # Chart 8: Numeric Correlation Heatmap
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 7))
    num_cols = ["quantity", "unit_price", "discount_percent", "discount_amount", "tax_amount", "total_amount", "customer_age"]
    corr_matrix = df[num_cols].corr()
    
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.7,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )
    ax.set_title("Feature Correlation Heatmap (Pearson Correlation Coefficients)", fontsize=13, fontweight="bold", pad=15)
    fig.tight_layout()
    chart_name = "08_correlation_heatmap.png"
    for d in output_dirs:
        p = d / chart_name
        plt.savefig(p, dpi=300, bbox_inches="tight")
        generated_charts.append(p)
    plt.close()

    logger.info(f"Successfully generated and saved all 8 visualizations to {[str(d) for d in output_dirs]}")
    return generated_charts


def main():
    root = get_project_root()
    raw_path = root / "data" / "raw" / "retail_sales.csv"
    processed_dir = root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    cleaned_csv_path = processed_dir / "retail_sales_cleaned.csv"
    
    reports_fig_dir = root / "reports" / "figures"
    reports_fig_dir.mkdir(parents=True, exist_ok=True)
    charts_dir = root / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    
    print_section("Retail Sales Data Cleaning & Exploratory Data Analysis")
    
    # 1. Clean and Enrich Data
    cleaned_df = clean_and_enrich_data(raw_path)
    cleaned_df.to_csv(cleaned_csv_path, index=False)
    logger.info(f"Cleaned dataset saved to: {cleaned_csv_path}")
    
    # 2. Generate Visualizations
    generate_all_charts(cleaned_df, [reports_fig_dir, charts_dir])
    
    # 3. Print Key Verification Statistics
    print("\n--- DATA CLEANING & EDA EXECUTION SUMMARY ---")
    print(f"  * Raw Records Processed      : {len(cleaned_df)}")
    print(f"  * Cleaned Columns Count      : {len(cleaned_df.columns)} (enriched with 11 derived features)")
    print(f"  * Output Cleaned CSV         : {cleaned_csv_path}")
    print(f"  * Missing Values Detected    : {cleaned_df.isnull().sum().sum()}")
    print(f"  * Total Revenue Analyzed     : ${cleaned_df['total_amount'].sum():,.2f}")
    print(f"  * Realized Revenue (Complete): ${cleaned_df[cleaned_df['order_status']=='Completed']['total_amount'].sum():,.2f}")
    print(f"  * Return Loss (Refunds)      : ${cleaned_df[cleaned_df['order_status']=='Returned']['total_amount'].sum():,.2f}")
    print(f"  * Outlier Records Flagged    : {cleaned_df['is_outlier'].sum()} records (preserved for completeness)")
    print(f"  * Charts Generated           : 8 figures in reports/figures/ and charts/")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
