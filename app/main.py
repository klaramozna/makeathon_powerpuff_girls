import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db import (
    get_companies,
    get_finished_goods,
    get_materials_for_supplier,
    get_raw_materials,
    get_raw_material_catalog,
    get_suppliers,
    get_suppliers_for_material,
)


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


@st.cache_data(show_spinner=False)
def load_suppliers() -> list[dict]:
    return get_suppliers()


@st.cache_data(show_spinner=False)
def load_raw_material_catalog() -> list[dict]:
    return get_raw_material_catalog()


@st.cache_data(show_spinner=False)
def load_materials_for_supplier(supplier_id: int) -> list[dict]:
    return get_materials_for_supplier(supplier_id)


@st.cache_data(show_spinner=False)
def load_suppliers_for_material(material_id: int) -> list[dict]:
    return get_suppliers_for_material(material_id)


st.title("Company Visualizer")
st.caption(
    "Use Company View for company-level data, or Supplier Explorer for supplier/material relationships."
)

tab_company_view, tab_supplier_explorer = st.tabs(["Company View", "Supplier Explorer"])

with tab_company_view:
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

    st.divider()
    if st.button("Run Dify workflow for selected company", key="go_to_dify_workflows"):
        st.session_state["selected_dify_company_id"] = int(company_id)
        st.session_state["selected_dify_company_name"] = company_name
        st.session_state["auto_run_dify_workflow"] = True
        st.switch_page("pages/Dify_Workflows.py")

with tab_supplier_explorer:
    st.subheader("Supplier Explorer")
    tab_supplier_to_materials, tab_material_to_suppliers = st.tabs(
        ["Supplier → Materials", "Material → Suppliers"]
    )

    with tab_supplier_to_materials:
        suppliers = load_suppliers()
        if not suppliers:
            st.info("No suppliers found.")
        else:
            selected_supplier = st.selectbox(
                "Choose supplier",
                suppliers,
                format_func=lambda supplier: supplier["Name"],
                key="supplier_explorer_supplier_select",
            )
            supplied_materials = load_materials_for_supplier(selected_supplier["Id"])
            st.metric("Supplied materials", len(supplied_materials))
            if supplied_materials:
                supplied_materials_df = pd.DataFrame(supplied_materials).rename(
                    columns={
                        "material_id": "Material ID",
                        "SKU": "Material SKU",
                        "company_name": "Company",
                        "Type": "Material type",
                    }
                )
                st.dataframe(supplied_materials_df, hide_index=True, width="stretch")
            else:
                st.info("This supplier does not supply any raw materials.")

    with tab_material_to_suppliers:
        materials = load_raw_material_catalog()
        if not materials:
            st.info("No raw materials found.")
        else:
            selected_material = st.selectbox(
                "Choose material",
                materials,
                format_func=lambda material: f"{material['SKU']} ({material['company_name']})",
                key="supplier_explorer_material_select",
            )
            material_suppliers = load_suppliers_for_material(selected_material["Id"])
            st.metric("Suppliers", len(material_suppliers))
            if material_suppliers:
                material_suppliers_df = pd.DataFrame(material_suppliers).rename(
                    columns={
                        "supplier_id": "Supplier ID",
                        "supplier_name": "Supplier",
                    }
                )
                st.dataframe(material_suppliers_df, hide_index=True, width="stretch")
            else:
                st.info("No suppliers found for this material.")
