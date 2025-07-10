# app.py – Finance Simulation (realistic strategic logic)

import streamlit as st
import pandas as pd

# ----- CONFIG ------------------------------------------------------
YEARS     = 4
BUDGET    = 1_000_000
SHARES    = 1_000_000
TAX_RATE  = 0.30
PE        = 12

# Improved k() logic with strategy-aware return modifiers
def k(spend, base, lever, year):
    """
    Return reduced returns over time for different levers.
    - Innovation/R&D are most useful early (Year 1–2)
    - Efficiency is mid-game (Year 2–3)
    - Marketing works best late (Year 3–4)
    """
    if lever == "I":
        modifier = 1.2 if year == 1 else 0.8
    elif lever == "R":
        modifier = 1.0 if year <= 2 else 0.7
    elif lever == "E":
        modifier = 1.0 if year >= 2 else 0.5
    elif lever == "M":
        modifier = 0.6 if year <= 2 else 1.2
    else:
        modifier = 1.0

    return (base * modifier) / (1 + spend / 400_000)

COEFF = dict(M=2.5, I=0.00004, R=0.8, E=0.00002, E_OPEX=0.20)

# ----- SESSION STATE ----------------------------------------------
if "year" not in st.session_state:
    st.session_state.update(
        year      = 1,
        rev       = 5_000_000.0,
        cogs_pct  = 0.60,
        opex      = 1_000_000.0,
        prev_R    = 0.0,
        history   = []
    )

y   = st.session_state.year
key = lambda base: f"{base}_{y}"        # unique widget keys per year

# ----- HEADER ------------------------------------------------------
st.title("💰 Finance Strategy Simulation")
st.caption("Allocate **exactly $1 000 000** each year.  "
           "The **Run Year** button unlocks when *Remaining* = 0.")

# ----- RESULTS FIRST (so they appear above the form) --------------
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.subheader("📊 Results so far")
    st.dataframe(
        df.style.format({
            "Revenue": "{:,.2f}",
            "GM$": "{:,.2f}",
            "GM%": "{:.2%}",
            "OPEX": "{:,.2f}",
            "EBIT": "{:,.2f}",
            "Tax": "{:,.2f}",
            "Net Profit": "{:,.2f}",
            "EPS": "{:.2f}",
            "Market Value": "{:,.2f}"
        }),
        use_container_width=True
    )
    st.line_chart(df.set_index("Year")["EPS"])
    st.divider()

# ----- INPUT WIDGETS ----------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown("### Marketing")
    posters   = st.number_input("Posters",     0, BUDGET, 0, 10_000, key=key("posters"))
    billboard = st.number_input("Billboard",   0, BUDGET, 0, 10_000, key=key("bill"))
    samples   = st.number_input("Samples",     0, BUDGET, 0, 10_000, key=key("samples"))
    tv        = st.number_input("TV Ads",      0, BUDGET, 0, 10_000, key=key("tv"))
    M = posters + billboard + samples + tv

    st.markdown("### Innovation")
    brand  = st.number_input("Brand Building", 0, BUDGET, 0, 10_000, key=key("brand"))
    design = st.number_input("Product Design", 0, BUDGET, 0, 10_000, key=key("design"))
    I = brand + design

with c2:
    st.markdown("### R & D")
    prodRD = st.number_input("Product R&D", 0, BUDGET, 0, 10_000, key=key("prodRD"))
    procRD = st.number_input("Process R&D", 0, BUDGET, 0, 10_000, key=key("procRD"))
    R = prodRD + procRD

    st.markdown("### Efficiency")
    train   = st.number_input("Training",        0, BUDGET, 0, 10_000, key=key("train"))
    custsvc = st.number_input("Customer Service",0, BUDGET, 0, 10_000, key=key("cust"))
    E = train + custsvc

# ----- BALANCE + RUN BUTTON ---------------------------------------
total   = M + I + R + E
balance = BUDGET - total

if balance == 0:
    st.success("Remaining: $0  ✅")
else:
    st.error(f"Remaining: ${balance:,}  ❌")

submitted = st.button(f"Run Year {y}", disabled=(balance != 0))

# ----- CALCULATE & LOG --------------------------------------------
if submitted:
    s = st.session_state

    rev  = s.rev + k(M, COEFF["M"], "M", y) * M + k(R, COEFF["R"], "R", y) * s.prev_R
    cogs = rev * max(0, s.cogs_pct - k(E, COEFF["E"], "E", y))
    gm   = rev - cogs
    opex = max(0, s.opex - COEFF["E_OPEX"] * E)
    ebit = gm - opex
    tax  = max(0, ebit * TAX_RATE)
    np   = ebit - tax
    eps  = np / SHARES
    mv   = eps * SHARES * PE

    s.history.append({
        "Year": y,
        "Revenue": rev,
        "GM$": gm,
        "GM%": gm / rev,
        "OPEX": opex,
        "EBIT": ebit,
        "Tax": tax,
        "Net Profit": np,
        "EPS": eps,
        "Market Value": mv
    })

    s.update(
        year     = y + 1,
        rev      = rev,
        cogs_pct = max(0, s.cogs_pct - k(E, COEFF["E"], "E", y)),
        opex     = opex,
        prev_R   = R
    )

    st.rerun()

# ----- GAME END ----------------------------------------------------
if st.session_state.year > YEARS:
    st.success("🏆 Simulation complete – highest EPS wins.")
    if st.button("Show detailed analysis"):
        st.bar_chart(pd.DataFrame(st.session_state.history)
                     .set_index("Year")[["Revenue","Net Profit"]])
