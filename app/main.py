import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db import get_companies, get_finished_goods, get_raw_materials


st.set_page_config(page_title="Company Visualizer", page_icon="📊", layout="wide")


@st.cache_data(show_spinner=False)
def load_companies() -> list[dict]:
    return get_companies()


@st.cache_data(show_spinner=False)
def load_finished_goods(company_id: int) -> list[dict]:
    return get_finished_goods(company_id)


@st.cache_data(show_spinner=False)
def load_raw_materials(company_id: int) -> list[dict]:
    return get_raw_materials(company_id)


st.title("Company Visualizer")
st.caption("Start by selecting a company, then explore products and raw materials.")

companies = load_companies()
if not companies:
    st.warning("No companies found in the database.")
    st.stop()

selected_company = st.selectbox(
    "Choose company",
    companies,
    format_func=lambda company: company["Name"],
    index=0,
)

company_id = selected_company["Id"]
company_name = selected_company["Name"]

products = load_finished_goods(company_id)
raw_materials = load_raw_materials(company_id)

metric_col_1, metric_col_2 = st.columns(2)
metric_col_1.metric("Products", len(products))
metric_col_2.metric("Raw materials", len(raw_materials))

tab_products, tab_raw_materials = st.tabs(["Products", "Raw Materials"])

with tab_products:
    st.subheader(f"Products for {company_name}")
    if products:
        products_df = pd.DataFrame(products).rename(
            columns={
                "Id": "Product ID",
                "SKU": "SKU",
                "Type": "Product type",
                "raw_material_count": "Raw material count",
            }
        )
        st.dataframe(products_df, hide_index=True, width="stretch")
    else:
        st.info("No products found for this company.")

with tab_raw_materials:
    st.subheader(f"Raw materials for {company_name}")
    if raw_materials:
        raw_materials_df = pd.DataFrame(raw_materials).rename(
            columns={
                "Id": "Material ID",
                "SKU": "SKU",
                "Type": "Material type",
                "supplier_count": "Supplier count",
            }
        )
        st.dataframe(raw_materials_df, hide_index=True, width="stretch")
    else:
        st.info("No raw materials found for this company.")
