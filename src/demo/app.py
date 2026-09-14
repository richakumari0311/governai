import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Enterprise Copilot", layout="centered")
st.title("Enterprise Copilot")
st.caption("Governed multi-agent enterprise assistant — HR, Finance, Support")

question = st.text_area("Ask a question", placeholder="How many leave days does a Manager get?")

with st.expander("Attach a policy check (optional)"):
    rule_id = st.text_input("Rule ID", placeholder="e.g. finance_travel_limit")
    level = st.text_input("Employee level", placeholder="e.g. Manager")
    value = st.number_input("Value to check", value=0.0)
    use_policy_check = st.checkbox("Include this policy check")

if st.button("Ask", type="primary"):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        payload = {"question": question}
        if use_policy_check:
            payload["policy_check"] = {
                "rule_id": rule_id or None,
                "level": level or None,
                "value": value if value else None,
            }

        with st.spinner("Routing and generating..."):
            response = requests.post(f"{API_URL}/ask", json=payload)

        if response.status_code != 200:
            st.error(f"Request failed: {response.status_code} — {response.text}")
        else:
            result = response.json()

            st.subheader("Answer")
            st.write(result["answer"])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Routed domain(s)", ", ".join(result["domains"]))
            with col2:
                action = result["decision"]["action"]
                color = {"auto_approve": "green", "auto_reject": "red", "human_approval": "orange"}.get(action, "gray")
                st.markdown(f"**Decision:** :{color}[{action}]")

            st.caption(f"Sources: {', '.join(result['sources'])}")

            with st.expander("Full decision detail"):
                st.json(result["decision"])