# app.py  – Finance Simulation (10 sub-options, improved UX)

import streamlit as st
import pandas as pd

# ---------- CONFIG -------------------------------------------------
YEARS    = 4
BUDGET   = 1_000_000
SHARES   = 1_000_000
TAX_RATE = 0.30
PE       = 12

def k(spend, base):
    """diminishing return coefficient"""
    return base / (1 + spend/400_000)

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

st.markdown(
    """
Allocate **exactly $1 000 000** each year across the ten options below.
*Remaining* turns green when you hit the target.
""")

# generate unique keys per year so old inputs disappear
y = st.session_state.year
key = lambda base: f"{base}_{y}"

with st.form(key=f"alloc_form_{y}"):
    st.subheader(f"Year {y} Allocation")

    col1, col2 = st.columns(2)

    # --- Marketing & Innovation ---
    with col1:
        st.markdown("### Marketing")
        posters   = st.number_input("Posters",     0, BUDGET, 0, 10000, key=key("posters"))
        billboard = st.number_input("Billboard",   0, BUDGET, 0, 10000, key=key("bill"))
        samples   = st.number_input("Samples",     0, BUDGET, 0, 10000, key=key("samples"))
        tv        = st.number_input("TV Ads",      0, BUDGET, 0, 10000, key=key("tv"))
        M = posters + billboard + samples + tv

        st.markdown("### Innovation")
        brand  = st.number_input("Brand Building", 0, BUDGET, 0, 10000, key=key("brand"))
        design = st.number_input("Product Design", 0, BUDGET, 0, 10000, key=key("design"))
        I = brand + design

    # --- R&D & Efficiency ---
    with col2:
        st.markdown("### R & D")
        prodRD  = st.number_input("Product R&D",  0, BUDGET, 0, 10000, key=key("prodRD"))
        procRD  = st.number_input("Process R&D",  0, BUDGET, 0, 10000, key=key("procRD"))
        R = prodRD + procRD

        st.markdown("### Efficiency")
        train   = st.number_input("Training",        0, BUDGET, 0, 10000, key=key("train"))
        custsvc = st.number_input("Customer Service",0, BUDGET, 0, 10000, key=key("cust"))
        E = train + custsvc

    total   = M + I + R + E
    balance = BUDGET - total

    # colour feedback
    col_bal = "✅ **Remaining: $0**" if balance == 0 else f"❌ **Remaining: ${balance:,.0f}**"
    st.markdown(col_bal)

    can_run = balance == 0
    submitted = st.form_submit_button(
        f"Run Year {y}", disabled=not can_run
    )

# ---------- CALC & RESULTS ----------------------------------------
if submitted:
    s = st.session_state

    rev   = s.rev + k(M, COEFF["M"])*M + k(R, COEFF["R"])*s.prev_R
    cogs  = rev * max(0, s.cogs_pct - k(E, COEFF["E"]))
    gm    = rev - cogs
    opex  = max(0, s.opex - COEFF["E_OPEX"]*E)
    ebit  = gm - opex
    tax   = max(0, ebit*TAX_RATE)
    np    = ebit - tax
    eps   = np / SHARES
    mv    = eps * SHARES * PE

    s.history.append({
        "Year": y, "Revenue": rev, "GM$": gm, "GM%": gm / rev,
        "OPEX": opex, "EBIT": ebit, "Tax": tax,
        "Net Profit": np, "EPS": eps, "Market Value": mv
    })

    # update carry-forwards
    s.update(year=y+1, rev=rev,
             cogs_pct=max(0, s.cogs_pct - k(E, COEFF["E"])),
             opex=opex, prev_R=R)

    st.success(f"Year {y} executed! Scroll down for results.")

# ---------- DASHBOARD ---------------------------------------------
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.subheader("Results so far")
    st.dataframe(df.style.format({
        "Revenue":"{:,.0f}", "GM$":"{:,.0f}", "GM%":"{:.1%}",
        "OPEX":"{:,.0f}", "EBIT":"{:,.0f}", "Tax":"{:,.0f}",
        "Net Profit":"{:,.0f}", "EPS":"{:.2f}", "Market Value":"{:,.0f}"
    }))

    st.line_chart(df.set_index("Year")["EPS"])

    # detailed analysis button
    if st.button("Show detailed analysis"):
        st.subheader("Detailed insights")
        st.write("Highest EPS driver:",
                 df.iloc[-1][["Revenue","GM$","OPEX"]].idxmax())
        st.bar_chart(df.set_index("Year")[["Revenue","Net Profit"]])

    # end-of-game message
    if st.session_state.year > YEARS:
        st.success("🏆 Simulation complete! Highest EPS wins.")
