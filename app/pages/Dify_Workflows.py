import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import (
    DIFY_API_KEY,
    DIFY_BASE_URL,
    DIFY_INPUT_KEY_RAW_MATERIALS_LIST,
    DIFY_USER_PREFIX,
)
from app.db import get_companies, get_raw_materials
from app.dify_client import DifyAPIError, run_workflow


st.set_page_config(page_title="Dify Workflows", page_icon="🤖", layout="wide")


@st.cache_data(show_spinner=False)
def load_companies() -> list[dict]:
    return get_companies()


@st.cache_data(show_spinner=False)
def load_raw_materials(company_id: int) -> list[dict]:
    return get_raw_materials(company_id)


def build_dify_inputs(company_raw_materials: list[dict]) -> dict:
    materials = [material["SKU"] for material in company_raw_materials]
    raw_materials_payload = {
        "materials": materials,
        "count": len(materials),
    }
    return {
        DIFY_INPUT_KEY_RAW_MATERIALS_LIST: raw_materials_payload,
    }


st.title("Dify Workflow: Raw Material Compatibility")
st.caption(
    "Runs your real Dify workflow using raw materials from the selected company and your knowledge documents."
)

if st.button("← Back to main page", key="back_to_main"):
    st.switch_page("main.py")

companies = load_companies()
if not companies:
    st.warning("No companies found in the database.")
    st.stop()

companies_by_id = {int(company["Id"]): company for company in companies}
selected_company_id = st.session_state.get("selected_dify_company_id")

if selected_company_id not in companies_by_id:
    st.warning("No selected company found from Company View. Choose a company to continue.")
    fallback_company = st.selectbox(
        "Choose company",
        companies,
        format_func=lambda company: company["Name"],
        key="dify_fallback_company_select",
    )
    selected_company = fallback_company
    st.session_state["selected_dify_company_id"] = int(fallback_company["Id"])
    st.session_state["selected_dify_company_name"] = fallback_company["Name"]
else:
    selected_company = companies_by_id[int(selected_company_id)]

st.subheader(f"Company: {selected_company['Name']}")

company_raw_materials = load_raw_materials(int(selected_company["Id"]))
material_skus = [material["SKU"] for material in company_raw_materials]

st.write("Raw materials sent to Dify")
if material_skus:
    st.dataframe(
        pd.DataFrame(
            {
                "Material SKU": material_skus,
                "Material type": [material["Type"] for material in company_raw_materials],
            }
        ),
        hide_index=True,
        width="stretch",
    )
else:
    st.warning("No raw materials found for this company.")

st.subheader("Connection status")
api_key_ready = bool(DIFY_API_KEY.strip())

if api_key_ready:
    st.success("Dify API key is loaded from .env or environment variable.")
else:
    st.error(
        "Dify API key is not configured. Set DIFY_API_KEY in .env (or env var) and rerun."
    )

st.caption(f"Dify base URL: {DIFY_BASE_URL}")

st.caption(
    "Current workflow input payload uses the selected company's full raw-material list."
)

if material_skus:
    preview_materials = [material["SKU"] for material in company_raw_materials]
    preview_payload = {
        DIFY_INPUT_KEY_RAW_MATERIALS_LIST: {
            "materials": preview_materials,
            "count": len(preview_materials),
        },
    }
    st.json(preview_payload)

should_auto_run = st.session_state.pop("auto_run_dify_workflow", False)
run_now = should_auto_run or st.button(
    "Run Dify compatibility check", key="run_workflow_now"
)

if run_now:
    if not material_skus:
        st.error("No raw materials found for this company, so there is nothing to send to Dify.")
        st.stop()

    if not api_key_ready:
        st.error("Set DIFY_API_KEY in .env before running the workflow.")
        st.stop()

    with st.spinner(f"Running Dify workflow for {selected_company['Name']}..."):
        try:
            analysis_text, full_payload = run_workflow(
                api_key=DIFY_API_KEY.strip(),
                base_url=DIFY_BASE_URL.strip(),
                user_id=f"{DIFY_USER_PREFIX}-{selected_company['Id']}",
                inputs=build_dify_inputs(company_raw_materials=company_raw_materials),
            )
        except DifyAPIError as exc:
            st.error(str(exc))
            st.stop()

    st.success("Dify workflow completed.")

    st.subheader("Compatibility assessment")
    st.markdown(analysis_text)

    st.subheader("Request summary")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Company": selected_company["Name"],
                    "Raw material count": len(material_skus),
                    "Dify endpoint": f"{DIFY_BASE_URL.rstrip('/')}/workflows/run",
                }
            ]
        ),
        hide_index=True,
        width="stretch",
    )

    with st.expander("Show full Dify response payload"):
        st.json(full_payload)
else:
    st.info("Click 'Run Dify compatibility check' to evaluate material fit based on your Dify knowledge.")
