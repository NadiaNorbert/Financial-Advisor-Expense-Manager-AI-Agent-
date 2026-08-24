"""
FinMate AI - Upload Expense Page
==================================
Handles screenshot OCR upload AND manual/CSV expense entry (via tabs).
"""

from __future__ import annotations

import datetime
import streamlit as st
import pandas as pd

from frontend.styles import COLORS
from backend.adapter import (
    extract_expense_from_image,
    categorize_expense,
    add_expense,
    import_csv_expenses,
    CATEGORIES,
    PAYMENT_METHODS,
)


def render() -> None:
    # ── Back button ───────────────────────────────────────────────
    if st.button("← Dashboard", key="back_to_dashboard"):
        st.session_state.selected_page = "Dashboard"
        st.rerun()

    st.markdown("<h1>📸 Add Expense</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; margin-top:-0.5rem;'>"
        "Upload a payment screenshot, fill in manually, or import a CSV file.</p>",
        unsafe_allow_html=True,
    )

    tab_ocr, tab_manual, tab_csv = st.tabs([
        "📸  Screenshot / OCR",
        "✍️  Manual Entry",
        "📄  CSV Import",
    ])

    with tab_ocr:
        _ocr_tab()

    with tab_manual:
        _manual_tab()

    with tab_csv:
        _csv_tab()


# ---------------------------------------------------------------------------
# Tab 1 — OCR Screenshot
# ---------------------------------------------------------------------------

def _ocr_tab() -> None:
    st.markdown("#### Upload Payment Screenshot")
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; font-size:0.85rem;'>"
        "Supports JPG, JPEG, PNG. The AI will extract merchant, amount, "
        "date, and payment method automatically.</p>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Drop your screenshot here",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if not uploaded:
        _upload_placeholder()
        return

    # Read bytes once — st.image() moves the stream cursor,
    # so we must read before displaying.
    image_bytes = uploaded.read()

    # ── Display uploaded image ──────────────────────────────────
    col_img, col_form = st.columns([1, 1.4])

    with col_img:
        st.image(image_bytes, caption="Uploaded Screenshot", use_container_width=True)

    with col_form:
        st.markdown("##### Extracting information…")

        # Call OCR backend
        with st.spinner("Running OCR analysis…"):
            try:
                result = extract_expense_from_image(image_bytes)
            except Exception as e:
                st.error(f"OCR failed: {e}")
                return

        is_mock = result.get("_mock", False)
        if is_mock:
            st.warning(
                "⚡ OCR backend not connected — showing demo extraction. "
                "Please verify and edit the fields below.",
                icon="⚠️",
            )
        else:
            confidence = result.get("confidence", 0)
            if confidence < 0.7:
                st.warning(
                    f"OCR confidence is low ({confidence:.0%}). "
                    "Please verify the extracted data carefully.",
                    icon="⚠️",
                )
            else:
                st.success(f"Extracted successfully ({confidence:.0%} confidence)")

        # ── Safely normalise OCR result fields (any may be None) ──
        ocr_merchant  = str(result.get("merchant") or "")
        ocr_amount    = float(result.get("amount") or 0)
        ocr_date      = str(result.get("date") or str(datetime.date.today()))
        ocr_payment   = str(result.get("payment_method") or "UPI")

        # Show error message if OCR failed
        ocr_error = result.get("error")
        if ocr_error:
            st.error(f"❌ OCR Error: {ocr_error}", icon="🚫")

        # ── Editable form ──────────────────────────────────────
        with st.form("ocr_form", clear_on_submit=True):
            merchant = st.text_input(
                "Merchant / Vendor",
                value=ocr_merchant,
                placeholder="e.g. Swiggy",
            )
            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                value=ocr_amount,
                step=0.5,
                format="%.2f",
            )
            date_val = _parse_date(ocr_date)
            date = st.date_input("Date", value=date_val)

            # Auto-suggest category from OCR result
            suggested_cat = categorize_expense(ocr_merchant, ocr_amount)
            cat_index = CATEGORIES.index(suggested_cat) if suggested_cat in CATEGORIES else 0
            category = st.selectbox("Category", CATEGORIES, index=cat_index)

            pay_index = (
                PAYMENT_METHODS.index(ocr_payment)
                if ocr_payment in PAYMENT_METHODS else 0
            )
            payment = st.selectbox("Payment Method", PAYMENT_METHODS, index=pay_index)
            notes = st.text_area("Notes (optional)", height=68, placeholder="Any extra details…")

            submitted = st.form_submit_button("💾  Save Expense", use_container_width=True)

        if submitted:
            _save_expense(merchant, amount, date, category, payment, notes, source="screenshot")


# ---------------------------------------------------------------------------
# Tab 2 — Manual Entry
# ---------------------------------------------------------------------------

def _manual_tab() -> None:
    st.markdown("#### Manual Expense Entry")
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; font-size:0.85rem;'>"
        "Fill in the form below to record an expense manually.</p>",
        unsafe_allow_html=True,
    )

    with st.form("manual_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            merchant = st.text_input("Merchant / Vendor *", placeholder="e.g. Amazon")
        with col2:
            amount = st.number_input("Amount (₹) *", min_value=0.01, step=0.5, format="%.2f")

        col3, col4 = st.columns(2)
        with col3:
            date = st.date_input("Date *", value=datetime.date.today())
        with col4:
            category = st.selectbox("Category *", CATEGORIES)

        col5, col6 = st.columns(2)
        with col5:
            payment = st.selectbox("Payment Method *", PAYMENT_METHODS)
        with col6:
            notes = st.text_input("Notes", placeholder="Optional details")

        submitted = st.form_submit_button("✅  Add Expense", use_container_width=True)

    if submitted:
        if not merchant.strip():
            st.error("Merchant name is required.")
        elif amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            _save_expense(merchant, amount, date, category, payment, notes, source="manual")


# ---------------------------------------------------------------------------
# Tab 3 — CSV Import
# ---------------------------------------------------------------------------

def _csv_tab() -> None:
    st.markdown("#### Import CSV Transactions")
    st.markdown(
        f"<p style='color:{COLORS['text_muted']}; font-size:0.85rem;'>"
        "Upload a CSV file exported from your bank or payment app. "
        "Expected columns: <code>merchant, amount, date, category, payment, notes</code> "
        "(extra columns are ignored).</p>",
        unsafe_allow_html=True,
    )

    # Sample download
    sample_csv = (
        "merchant,amount,date,category,payment,notes\n"
        "Swiggy,450,2026-08-01,Food & Dining,UPI,\n"
        "Uber,320,2026-08-02,Transport,UPI,\n"
        "Amazon,1200,2026-08-03,Shopping,Credit Card,\n"
    )
    st.download_button(
        "⬇️  Download Sample CSV",
        data=sample_csv.encode(),
        file_name="finmate_sample.csv",
        mime="text/csv",
    )

    uploaded_csv = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        label_visibility="collapsed",
    )

    if not uploaded_csv:
        return

    try:
        df = pd.read_csv(uploaded_csv)
    except Exception as e:
        st.error(f"Could not read CSV file: {e}")
        return

    if df.empty:
        st.warning("The CSV file is empty.")
        return

    # ── Preview ─────────────────────────────────────────────────
    st.markdown("##### File Preview")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Rows detected",     len(df))
    col_b.metric("Columns detected",  len(df.columns))

    # Try to sum amount column
    amount_col = next(
        (c for c in df.columns if c.lower() in ["amount", "debit", "credit"]), None
    )
    if amount_col:
        try:
            total = pd.to_numeric(df[amount_col], errors="coerce").sum()
            col_c.metric("Total Amount (approx.)", f"₹{total:,.2f}")
        except Exception:
            col_c.metric("Total Amount", "N/A")
    else:
        col_c.metric("Amount Column", "Not found")

    st.markdown(
        f"**Detected columns:** `{'`, `'.join(df.columns.tolist())}`"
    )
    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True,
    )

    if len(df) > 10:
        st.caption(f"Showing first 10 of {len(df)} rows.")

    # ── Import button ────────────────────────────────────────────
    if st.button("📥  Import Transactions", use_container_width=True, type="primary"):
        with st.spinner("Importing transactions…"):
            try:
                result = import_csv_expenses(df)
                if result["success"]:
                    st.success(
                        f"✅ Imported **{result['imported']}** transactions "
                        f"({result['skipped']} skipped). "
                        f"{result['message']}"
                    )
                    st.balloons()
                else:
                    st.error(f"Import failed: {result['message']}")
            except Exception as e:
                st.error(f"Unexpected error during import: {e}")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _save_expense(
    merchant: str,
    amount: float,
    date,
    category: str,
    payment: str,
    notes: str,
    source: str = "manual",
) -> None:
    """Validate, call backend, and show result."""
    if not merchant.strip():
        st.error("Merchant name cannot be empty.")
        return
    if amount <= 0:
        st.error("Amount must be greater than zero.")
        return

    expense = {
        "merchant": merchant.strip(),
        "amount":   round(float(amount), 2),
        "date":     str(date),
        "category": category,
        "payment":  payment,
        "notes":    notes.strip(),
        "source":   source,
    }

    try:
        result = add_expense(expense)
        if result.get("success"):
            st.success(
                f"✅ **{merchant}** — ₹{amount:,.2f} saved successfully! "
                f"(ID #{result.get('id', '?')})"
            )
            st.balloons()
        else:
            st.error(f"Could not save expense: {result.get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


def _upload_placeholder() -> None:
    st.markdown(
        f"""
        <div style="
            border: 2px dashed {COLORS['border']};
            border-radius: 12px;
            padding: 2.5rem;
            text-align: center;
            color: {COLORS['text_muted']};
            margin-top: 1rem;
        ">
            <div style="font-size:3rem; margin-bottom:0.5rem;">📸</div>
            <div style="font-size:1rem; font-weight:600; margin-bottom:4px;">
                Drop your payment screenshot here
            </div>
            <div style="font-size:0.82rem;">
                Supported formats: JPG, JPEG, PNG
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _parse_date(date_str: str) -> datetime.date:
    """Try common date formats and fall back to today."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d/%m/%y"):
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return datetime.date.today()
