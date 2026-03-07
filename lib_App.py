"""
app.py
------
Streamlit-based UI for the Library Management System.
Run with: streamlit run app.py

Navigation is sidebar-driven:
  📚 Books | 👥 Members | 🔄 Issue/Return | 📊 Reports
"""

import logging
import pandas as pd
import streamlit as st

# ── Bootstrap DB on first run ──────────────────────────────────────
from db.schema import initialize_db
initialize_db()

# ── Service imports ────────────────────────────────────────────────
from services import book_service, member_service, issue_service, reporting_service

# ── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .metric-card h2 { font-size: 2.2rem; margin: 0; }
    .metric-card p  { font-size: 0.9rem; margin: 0; opacity: 0.85; }
    .metric-card.warn {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .section-header {
        border-left: 4px solid #667eea;
        padding-left: 10px;
        margin-bottom: 1rem;
    }
    .stDataFrame { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def success(msg: str):
    st.success(msg)

def error(msg: str):
    st.error(msg)

def show_df(df: pd.DataFrame, caption: str = ""):
    """Render a DataFrame or a friendly 'no records' message."""
    if df is None or df.empty:
        st.info("No records found.")
    else:
        if caption:
            st.caption(caption)
        st.dataframe(df, use_container_width=True)


def csv_download(df: pd.DataFrame, filename: str):
    """Render a CSV download button for a DataFrame."""
    if df is not None and not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Export CSV",
            data=csv,
            file_name=filename,
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════
PAGES = {
    "🏠 Dashboard": "dashboard",
    "📚 Books": "books",
    "👥 Members": "members",
    "🔄 Issue / Return": "issue",
    "📊 Reports": "reports",
}

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/library.png", width=80)
    st.title("Library System")
    st.markdown("---")
    page_label = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
    page = PAGES[page_label]
    st.markdown("---")
    st.caption("📘 Library Management System\nPowered by Python · SQLite · Streamlit")

# ══════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════

def render_dashboard():
    st.markdown("<div class='section-header'><h2>🏠 Dashboard</h2></div>",
                unsafe_allow_html=True)
    stats = reporting_service.dashboard_stats()

    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, stats["total_books"],       "📚 Total Books",       False),
        (c2, stats["total_members"],     "👥 Members",           False),
        (c3, stats["active_issues"],     "🔄 Active Issues",     False),
        (c4, stats["total_transactions"],"📋 Transactions",      False),
        (c5, stats["overdue_count"],     "⚠️ Overdue",           True),
    ]
    for col, val, label, warn in metrics:
        cls = "metric-card warn" if warn and val > 0 else "metric-card"
        col.markdown(
            f"<div class='{cls}'><h2>{val}</h2><p>{label}</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("📈 Top Borrowed Books")
        df_top = reporting_service.report_most_borrowed_books(5)
        show_df(df_top)

    with col_r:
        st.subheader("⚠️ Recently Overdue")
        df_od = reporting_service.report_overdue_books(14)
        show_df(df_od)


# ══════════════════════════════════════════════════════════════════
# BOOKS
# ══════════════════════════════════════════════════════════════════

def render_books():
    st.markdown("<div class='section-header'><h2>📚 Book Management</h2></div>",
                unsafe_allow_html=True)
    tab_view, tab_add, tab_update, tab_delete = st.tabs(
        ["📋 View / Search", "➕ Add Book", "✏️ Update Book", "🗑️ Delete Book"]
    )

    # ── View / Search ──────────────────────────────────────────
    with tab_view:
        query = st.text_input("🔍 Search by title, author, or category", "")
        books = book_service.search_books(query)
        df = pd.DataFrame(books) if books else pd.DataFrame()
        show_df(df, f"{len(books)} book(s) found")
        csv_download(df, "books.csv")

    # ── Add ────────────────────────────────────────────────────
    with tab_add:
        with st.form("form_add_book"):
            st.subheader("Add New Book")
            c1, c2 = st.columns(2)
            title  = c1.text_input("Title *")
            author = c2.text_input("Author *")
            category = st.selectbox("Category *", book_service.VALID_CATEGORIES)
            c3, c4, c5 = st.columns(3)
            total  = c3.number_input("Total Copies *", min_value=1, value=1)
            isbn   = c4.text_input("ISBN")
            year   = c5.number_input("Published Year", min_value=0, max_value=2100,
                                     value=0, step=1)
            submitted = st.form_submit_button("➕ Add Book", use_container_width=True)
        if submitted:
            ok, msg = book_service.add_book(
                title, author, category, int(total),
                isbn or None, int(year) if year else None
            )
            success(msg) if ok else error(msg)

    # ── Update ─────────────────────────────────────────────────
    with tab_update:
        books_all = book_service.get_all_books()
        if not books_all:
            st.info("No books in the system yet.")
        else:
            options = {f"[{b['book_id']}] {b['title']}": b["book_id"] for b in books_all}
            sel = st.selectbox("Select book to update", list(options.keys()))
            book = book_service.get_book_by_id(options[sel])
            if book:
                with st.form("form_update_book"):
                    c1, c2 = st.columns(2)
                    u_title  = c1.text_input("Title", book["title"])
                    u_author = c2.text_input("Author", book["author"])
                    cat_idx  = (book_service.VALID_CATEGORIES.index(book["category"])
                                if book["category"] in book_service.VALID_CATEGORIES else 0)
                    u_cat    = st.selectbox("Category", book_service.VALID_CATEGORIES,
                                           index=cat_idx)
                    c3, c4, c5, c6 = st.columns(4)
                    u_total  = c3.number_input("Total Copies", min_value=0,
                                              value=int(book["total_copies"]))
                    u_avail  = c4.number_input("Available Copies", min_value=0,
                                              value=int(book["available_copies"]))
                    u_isbn   = c5.text_input("ISBN", book["isbn"] or "")
                    u_year   = c6.number_input("Year", min_value=0, max_value=2100,
                                              value=int(book["published_year"] or 0))
                    submitted = st.form_submit_button("✏️ Update", use_container_width=True)
                if submitted:
                    ok, msg = book_service.update_book(
                        book["book_id"], u_title, u_author, u_cat,
                        int(u_total), int(u_avail), u_isbn or None,
                        int(u_year) if u_year else None
                    )
                    success(msg) if ok else error(msg)

    # ── Delete ─────────────────────────────────────────────────
    with tab_delete:
        books_all = book_service.get_all_books()
        if not books_all:
            st.info("No books to delete.")
        else:
            options = {f"[{b['book_id']}] {b['title']}": b["book_id"] for b in books_all}
            sel = st.selectbox("Select book to delete", list(options.keys()),
                               key="del_book_sel")
            st.warning("⚠️ This action is irreversible. Books with active issues cannot be deleted.")
            if st.button("🗑️ Delete Book", use_container_width=True):
                ok, msg = book_service.delete_book(options[sel])
                success(msg) if ok else error(msg)


# ══════════════════════════════════════════════════════════════════
# MEMBERS
# ══════════════════════════════════════════════════════════════════

def render_members():
    st.markdown("<div class='section-header'><h2>👥 Member Management</h2></div>",
                unsafe_allow_html=True)
    tab_view, tab_add, tab_update, tab_delete = st.tabs(
        ["📋 View / Search", "➕ Add Member", "✏️ Update Member", "🗑️ Delete Member"]
    )

    with tab_view:
        query = st.text_input("🔍 Search by name or email", "")
        members = member_service.search_members(query)
        df = pd.DataFrame(members) if members else pd.DataFrame()
        show_df(df, f"{len(members)} member(s) found")
        csv_download(df, "members.csv")

    with tab_add:
        with st.form("form_add_member"):
            st.subheader("Register New Member")
            c1, c2 = st.columns(2)
            name   = c1.text_input("Full Name *")
            gender = c2.selectbox("Gender *", member_service.VALID_GENDERS)
            c3, c4, c5 = st.columns(3)
            age    = c3.number_input("Age *", min_value=1, max_value=120, value=18)
            mobile = c4.text_input("Mobile Number")
            email  = c5.text_input("Email *")
            submitted = st.form_submit_button("➕ Register", use_container_width=True)
        if submitted:
            ok, msg = member_service.add_member(name, gender, int(age), mobile, email)
            success(msg) if ok else error(msg)

    with tab_update:
        members_all = member_service.get_all_members()
        if not members_all:
            st.info("No members registered yet.")
        else:
            options = {f"[{m['member_id']}] {m['name']}": m["member_id"]
                       for m in members_all}
            sel = st.selectbox("Select member to update", list(options.keys()))
            member = member_service.get_member_by_id(options[sel])
            if member:
                with st.form("form_update_member"):
                    c1, c2 = st.columns(2)
                    u_name   = c1.text_input("Full Name", member["name"])
                    g_idx    = list(member_service.VALID_GENDERS).index(member["gender"])
                    u_gender = c2.selectbox("Gender", member_service.VALID_GENDERS,
                                           index=g_idx)
                    c3, c4, c5 = st.columns(3)
                    u_age    = c3.number_input("Age", min_value=1, max_value=120,
                                              value=int(member["age"]))
                    u_mobile = c4.text_input("Mobile", member["mobile_number"] or "")
                    u_email  = c5.text_input("Email", member["email"])
                    submitted = st.form_submit_button("✏️ Update", use_container_width=True)
                if submitted:
                    ok, msg = member_service.update_member(
                        member["member_id"], u_name, u_gender,
                        int(u_age), u_mobile, u_email
                    )
                    success(msg) if ok else error(msg)

    with tab_delete:
        members_all = member_service.get_all_members()
        if not members_all:
            st.info("No members to delete.")
        else:
            options = {f"[{m['member_id']}] {m['name']}": m["member_id"]
                       for m in members_all}
            sel = st.selectbox("Select member to delete", list(options.keys()),
                               key="del_mem_sel")
            st.warning("⚠️ Members with active book issues cannot be deleted.")
            if st.button("🗑️ Delete Member", use_container_width=True):
                ok, msg = member_service.delete_member(options[sel])
                success(msg) if ok else error(msg)


# ══════════════════════════════════════════════════════════════════
# ISSUE / RETURN
# ══════════════════════════════════════════════════════════════════

def render_issue_return():
    st.markdown("<div class='section-header'><h2>🔄 Issue / Return Books</h2></div>",
                unsafe_allow_html=True)
    tab_issue, tab_return, tab_active = st.tabs(
        ["📤 Issue Book", "📥 Return Book", "📋 Active Issues"]
    )

    with tab_issue:
        books   = book_service.get_all_books()
        members = member_service.get_all_members()
        avail_books = [b for b in books if b["available_copies"] > 0]

        if not avail_books:
            st.warning("No books with available copies right now.")
        elif not members:
            st.warning("No members registered yet.")
        else:
            with st.form("form_issue"):
                st.subheader("Issue a Book")
                book_opts = {
                    f"[{b['book_id']}] {b['title']} (avail: {b['available_copies']})": b["book_id"]
                    for b in avail_books
                }
                member_opts = {
                    f"[{m['member_id']}] {m['name']}": m["member_id"]
                    for m in members
                }
                sel_book   = st.selectbox("Select Book *", list(book_opts.keys()))
                sel_member = st.selectbox("Select Member *", list(member_opts.keys()))
                submitted  = st.form_submit_button("📤 Issue Book", use_container_width=True)
            if submitted:
                ok, msg = issue_service.issue_book(
                    book_opts[sel_book], member_opts[sel_member]
                )
                success(msg) if ok else error(msg)

    with tab_return:
        active = issue_service.get_active_issues()
        if not active:
            st.info("No active issues to return.")
        else:
            txn_opts = {
                f"[TXN#{t['transaction_id']}] {t['book_title']} → {t['member_name']} "
                f"(issued: {t['issue_date']})": t["transaction_id"]
                for t in active
            }
            with st.form("form_return"):
                st.subheader("Return a Book")
                sel_txn   = st.selectbox("Select Transaction *", list(txn_opts.keys()))
                submitted = st.form_submit_button("📥 Return Book", use_container_width=True)
            if submitted:
                ok, msg = issue_service.return_book(txn_opts[sel_txn])
                success(msg) if ok else error(msg)

    with tab_active:
        active_all = issue_service.get_active_issues()
        df = pd.DataFrame(active_all) if active_all else pd.DataFrame()
        show_df(df, f"{len(active_all)} active issue(s)")
        csv_download(df, "active_issues.csv")


# ══════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════

def render_reports():
    st.markdown("<div class='section-header'><h2>📊 Reports & Analytics</h2></div>",
                unsafe_allow_html=True)

    tabs = st.tabs([
        "📤 All Issued",
        "⚠️ Overdue",
        "🏆 Most Borrowed",
        "👤 Member History",
        "📦 Inventory",
    ])

    # All Issued
    with tabs[0]:
        st.subheader("All Issued Books")
        df = reporting_service.report_all_issued_books()
        show_df(df)
        csv_download(df, "issued_books.csv")

    # Overdue
    with tabs[1]:
        st.subheader("Overdue Books")
        overdue_days = st.slider("Overdue threshold (days)", 7, 60, 14)
        df = reporting_service.report_overdue_books(overdue_days)
        show_df(df, f"Books overdue by more than {overdue_days} days")
        csv_download(df, "overdue_books.csv")

    # Most Borrowed
    with tabs[2]:
        st.subheader("Most Borrowed Books")
        top_n = st.slider("Show top N books", 5, 20, 10)
        df = reporting_service.report_most_borrowed_books(top_n)
        if df is not None and not df.empty:
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                chart_df = df.set_index("book_title")["borrow_count"]
                st.bar_chart(chart_df)
            with col_table:
                show_df(df)
            csv_download(df, "most_borrowed.csv")
        else:
            st.info("No borrowing data yet.")

    # Member Borrowing History
    with tabs[3]:
        st.subheader("Member Borrowing History")
        members = member_service.get_all_members()
        if not members:
            st.info("No members yet.")
        else:
            options = {"All Members": None}
            options.update({f"[{m['member_id']}] {m['name']}": m["member_id"]
                            for m in members})
            sel = st.selectbox("Filter by member", list(options.keys()))
            df  = reporting_service.report_member_borrowing_history(options[sel])
            show_df(df)
            csv_download(df, "member_history.csv")

    # Inventory
    with tabs[4]:
        st.subheader("Inventory Report")
        df = reporting_service.report_inventory()
        show_df(df, "Sorted by utilisation %")
        if df is not None and not df.empty:
            st.bar_chart(df.set_index("title")["utilisation_pct"])
        csv_download(df, "inventory.csv")


# ══════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════
if page == "dashboard":
    render_dashboard()
elif page == "books":
    render_books()
elif page == "members":
    render_members()
elif page == "issue":
    render_issue_return()
elif page == "reports":
    render_reports()
