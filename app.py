Add initial Streamlit app
# app.py  – Finance Simulation (10 sub-options)

import streamlit as st
import pandas as pd

# ---------- CONFIG -------------------------------------------------
YEARS    = 4
BUDGET   = 1_000_000
SHARES   = 1_000_000
TAX_RATE = 0.30
PE       = 12

# coeffs (with built-in diminishing returns)
def k(spend, base): return base / (1 + spend/400_000)

COEFF = dict(M=2.5, I=0.00004, R=0.8, E=0.00002, E_OPEX=0.20)

# ---------- STATE --------------------------------------------------
if "year" not in st.session_state:
    st.session_state.update(
        year      = 1,
        rev       = 5_000_000.0,
        cogs_pct  = 0.60,
        opex      = 1_000_000.0,
        prev_R    = 0.0,
        history   = []
    )

# ---------- UI -----------------------------------------------------
st.title("💰 Finance Strategy Simulation")

st.markdown(f"Allocate exactly **${BUDGET:,.0f}** each year across the options below.")

with st.form(key=f"alloc_y{st.session_state.year}"):
    st.subheader(f"Year {st.session_state.year} Allocation")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Marketing")
        posters   = st.number_input("Posters",     0, BUDGET, 0, 10000, key="posters")
        billboard = st.number_input("Billboard",   0, BUDGET, 0, 10000, key="bill")
        samples   = st.number_input("Samples",     0, BUDGET, 0, 10000, key="samples")
        tv        = st.number_input("TV Ads",      0, BUDGET, 0, 10000, key="tv")
        M = posters + billboard + samples + tv

        st.markdown("#### Innovation")
        brand  = st.number_input("Brand Building", 0, BUDGET, 0, 10000, key="brand")
        design = st.number_input("Product Design", 0, BUDGET, 0, 10000, key="design")
        I = brand + design

    with col2:
        st.markdown("#### R & D")
        prodRD  = st.number_input("Product R&D",  0, BUDGET, 0, 10000, key="prodRD")
        procRD  = st.number_input("Process R&D",  0, BUDGET, 0, 10000, key="procRD")
        R = prodRD + procRD

        st.markdown("#### Efficiency")
        train   = st.number_input("Training",        0, BUDGET, 0, 10000, key="train")
        custsvc = st.number_input("Customer Service",0, BUDGET, 0, 10000, key="cust")
        E = train + custsvc

    total = M + I + R + E
    st.markdown(f"**Total spend:** ${total:,.0f} / ${BUDGET:,.0f}")

    valid = st.form_submit_button("Run Year")  # -----------------

# ---------- CALC & RESULTS ----------------------------------------
if valid:
    if total != BUDGET:
        st.error(f"Please spend exactly ${BUDGET:,.0f}. You are off by ${BUDGET-total:,.0f}.")
        st.stop()

    s = st.session_state     # shorthand

    # diminishing-return coefficients
    k1 = k(M, COEFF["M"]);        k2 = k(I, COEFF["I"])
    k3 = k(R, COEFF["R"]);        k4 = k(E, COEFF["E"])

    rev   = s.rev + k1*M + k3*s.prev_R
    cogs  = rev * max(0, s.cogs_pct - k4)     # Efficiency ↓ COGS%
    gm    = rev - cogs
    opex  = max(0, s.opex - COEFF["E_OPEX"]*E)
    ebit  = gm - opex
    tax   = max(0, ebit*TAX_RATE)
    np    = ebit - tax
    eps   = np / SHARES
    mv    = eps * SHARES * PE

    s.history.append(
        dict(Year=s.year, Revenue=rev, GM$=gm, GM%=gm/rev,
             OPEX=opex, EBIT=ebit, Tax=tax, NetProfit=np,
             EPS=eps, MarketValue=mv))

    # update carry-forwards
    s.update(year=s.year+1, rev=rev, cogs_pct=max(0, s.cogs_pct - k4),
             opex=opex, prev_R=R)

# ---------- DASHBOARD ---------------------------------------------
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.subheader("Year-by-Year Results")
    st.dataframe(df.style.format({"Revenue":"{:,.0f}",
                                  "GM$":"{:,.0f}",
                                  "GM%":"{:.1%}",
                                  "OPEX":"{:,.0f}",
                                  "EBIT":"{:,.0f}",
                                  "Tax":"{:,.0f}",
                                  "NetProfit":"{:,.0f}",
                                  "EPS":"{:.2f}",
                                  "MarketValue":"{:,.0f}"}))

    if st.session_state.year > YEARS:
        st.success("🏆 Simulation complete! Highest EPS wins.")
        st.bar_chart(df.set_index("Year")["EPS"])
