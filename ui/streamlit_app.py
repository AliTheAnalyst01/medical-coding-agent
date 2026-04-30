import json
import streamlit as st
import httpx

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Medical Coding AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Medical Coding AI")
st.caption("Paste a clinical note — get validated ICD-10-CM codes with full agent trace.")

col_chat, col_trace = st.columns([1, 1])

with col_chat:
    st.subheader("Clinical Note")
    note = st.text_area(
        "Paste clinical note here",
        height=200,
        placeholder="Patient presents with acute inferior STEMI. History of Type 2 DM uncontrolled and hypertension...",
    )
    run_btn = st.button("Generate Codes", type="primary", use_container_width=True)

with col_trace:
    st.subheader("Agent Trace")

if run_btn and note.strip():
    with col_chat:
        with st.spinner("Running coding pipeline..."):
            try:
                response = httpx.post(
                    f"{API_URL}/code",
                    json={"note": note},
                    timeout=120.0,
                )
                response.raise_for_status()
                data = response.json()
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                st.error(f"API error: {e}")
                st.stop()

    with col_chat:
        st.divider()
        st.subheader(f"Results  |  Request ID: `{data['request_id']}`")

        accepted = [c for c in data["codes"] if c.get("status") == "accepted"]
        rejected = [c for c in data["codes"] if c.get("status") == "rejected"]

        if accepted:
            st.success(f"{len(accepted)} code(s) accepted")
            for c in accepted:
                with st.expander(f"`{c['code']}` — {c.get('description', '')}"):
                    st.write(f"**System:** {c.get('system', 'ICD-10-CM')}")
                    st.write(f"**Reasoning:** {c.get('reasoning', '')}")

        if rejected:
            st.error(f"{len(rejected)} code(s) rejected")
            for c in rejected:
                with st.expander(f"`{c['code']}` — {c.get('description', '')} — REJECTED"):
                    st.write(f"**Reason:** {c.get('reason', '')}")

        query_required = [c for c in data["codes"] if c.get("code") == "QUERY_REQUIRED"]
        if query_required:
            st.warning(f"⚠️ {len(query_required)} term(s) need provider clarification")
            for c in query_required:
                with st.expander(f"QUERY REQUIRED — {c.get('description', 'Unclear term')}"):
                    st.write(f"**What to ask the provider:** {c.get('reasoning', '')}")

        summary = data.get("validation_summary", {})
        st.caption(
            f"Proposed: {summary.get('total_proposed', 0)} | "
            f"Accepted: {summary.get('accepted', 0)} | "
            f"Rejected: {summary.get('rejected', 0)}"
        )

    AGENT_COLORS = {
        "coordinator": "🟢",
        "icd_cm_worker": "🟣",
        "icd_pcs_worker": "🟣",
        "hcpcs_worker": "🟣",
        "validator": "🔴",
    }

    with col_trace:
        steps = data.get("trace_steps", [])
        if steps:
            for step in steps:
                agent = step.get("agent", "unknown")
                tool = step.get("tool", "")
                duration = step.get("duration_ms", 0)
                icon = AGENT_COLORS.get(agent, "⚪")
                with st.expander(f"{icon} [{agent}] `{tool}` — {duration}ms", expanded=False):
                    st.write("**Input:**")
                    st.json(step.get("input", {}))
                    st.write("**Output:**")
                    output = step.get("output", "")
                    try:
                        st.json(output if isinstance(output, (dict, list)) else json.loads(str(output)))
                    except Exception:
                        st.code(str(output))
        else:
            st.info("Trace will appear here after running a note.")

elif run_btn:
    st.warning("Please enter a clinical note.")
