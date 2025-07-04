# app.py  – Finance Simulation  (improved UX v2)

import streamlit as st
import pandas as pd

# ---------- CONFIG -------------------------------------------------
YEARS    = 4
BUDGET   = 1_000_000
SHARES   = 1_000_000
TAX_RATE = 0.30
PE       = 12

def k(spend, base):              # diminishing return helper
    return base / (1 + spend/400_000)

COEFF = dict(M=2.5, I=0.00004, R=0.8, E=0.00002, E_OPEX=0.20)

# ---------- SESSION STATE ------------------------------------------
if "year" not in st.session_state:
    st.session_state.update(
        year      = 1,
        rev       = 5_000_000.0,
        cogs_pct  = 0.60,
        opex      = 1_000_000.0,
        prev_R    = 0.0,
        history   = []
    )

y   = st.session_state.year               # current year (1‒4)
key = lambda base: f"{base}_{y}"          # unique widget keys per year

# ---------- PAGE HEADER --------------------------------------------
st.title("💰 Finance Strategy Simulation")
st.caption("Allocate **exactly $1 000 000** each year. "
           "The *Run Year* button unlocks when Remaining = 0.")

# ---------- INPUT FORM ---------------------------------------------
with st.form(key=f"form_{y}"):
    st.subheader(f"Year {y} Allocation")

    c1, c2 = st.columns(2)

    # -------- left column (Marketing + Innovation) --------
    with c1:
        st.markdown("#### Marketing")
        posters   = st.number_input("Posters",     0, BUDGET, 0, 10_000, format="%d", key=key("posters"))
        billboard = st.number_input("Billboard",   0, BUDGET, 0, 10_000, format="%d", key=key("bill"))
        samples   = st.number_input("Samples",     0, BUDGET, 0, 10_000, format="%d", key=key("samples"))
        tv        = st.number_input("TV Ads",      0, BUDGET, 0, 10_000, format="%d", key=key("tv"))
        M = posters + billboard + samples + tv

        st.markdown("#### Innovation")
        brand  = st.number_input("Brand Building", 0, BUDGET, 0, 10_000, format="%d", key=key("brand"))
        design = st.number_input("Product Design", 0, BUDGET, 0, 10_000, format="%d", key=key("design"))
        I = brand + design

    # -------- right column (R&D + Efficiency) --------
    with c2:
        st.markdown("#### R & D")
        prodRD  = st.number_input("Product R&D",  0, BUDGET, 0, 10_000, format="%d", key=key("prodRD"))
        procRD  = st.number_input("Process R&D",  0, BUDGET, 0, 10_000, format="%d", key=key("procRD"))
        R = prodRD + procRD

        st.markdown("#### Efficiency")
        train   = st.number_input("Training",         0, BUDGET, 0, 10_000, format="%d", key=key("train"))
        custsvc = st.number_input("Customer Service", 0, BUDGET, 0, 10_000, format="%d", key=key("cust"))
        E = train + custsvc

    # -------- total & balance feedback --------
    total   = M + I + R + E
    balance = BUDGET - total
    if balance == 0:
        st.success("Remaining: $0  ✅  (You’re good to run)")
    else:
        colour = "under-allocate" if balance > 0 else "over-allocate"
        st.error(f"Remaining: ${balance:,.0f}  ❌  (You {colour})")

    # -------- run button --------
    submitted = st.form_submit_button(
        f"Run Year {y}",
        disabled = balance != 0
    )

# ---------- CALCULATE & LOG RESULTS -------------------------------
if submitted:
    s = st.session_state

    rev  = s.rev + k(M, COEFF["M"])*M + k(R, COEFF["R"])*s.prev_R
    cogs = rev * max(0, s.cogs_pct - k(E, COEFF["E"]))
    gm   = rev - cogs
    opex = max(0, s.opex - COEFF["E_OPEX"]*E)
    ebit = gm - opex
    tax  = max(0, ebit * TAX_RATE)
    np   = ebit - tax
    eps  = np / SHARES
    mv   = eps * SHARES * PE

    s.history.append({
        "Year": y, "Revenue": rev, "GM$": gm, "GM%": gm / rev,
        "OPEX": opex, "EBIT": ebit, "Tax": tax,
        "Net Pr
