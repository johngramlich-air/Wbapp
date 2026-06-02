import streamlit as pd
import pandas as pd
import streamlit as st

# 1. Page Configuration & Styling (Kept the browser tab icon, removed from main header)
st.set_page_config(page_title="BotX Diagnostic Tool", page_icon="🤖", layout="centered")

# UPDATED: Removed the emoji logo from the title
st.title("BotX Diagnostic Tool")

# UPDATED: Changed the subtitle text
st.caption("BotX error code database")

# 2. Load the Local Database (Cached so it loads instantly)
@st.cache_data
def load_database():
    return pd.read_excel("workbook.xlsx", sheet_name=None, dtype=str)

try:
    workbook = load_database()
except Exception as e:
    st.error(f"Failed to load diagnostic database: {e}")
    st.stop()

# 3. Fuzzy Matching Helper Function
def is_smart_match(search_term, cell_value):
    if pd.isna(cell_value):
        return False
    s_clean = "".join(c for c in str(search_term) if c.isalnum()).lower()
    c_clean = "".join(c for c in str(cell_value) if c.isalnum()).lower()
    
    if not s_clean:
        return False
    if s_clean in c_clean:
        return True
    if c_clean.isdigit() and s_clean.startswith("e"):
        s_numeric = s_clean[1:]
        if s_numeric in c_clean or s_numeric in c_clean.zfill(3) or c_clean in s_numeric:
            return True
    return False

# 4. Search UI Component Input Bar
search_term = st.text_input("Search Error Code:", placeholder="e.g., E-000, E010, Plasma...")

# Professional Label Translations
PROFESSIONAL_LABELS = {
    "error code": "Error Code",
    "code explanation": "Condition / Description",
    "first try": "Check 1",
    "then try": "Check 2",
    "lastly it might be": "Check 3",
    "one more pleaseeeee": "Check 4",
    "note": "Technical Note"
}

# 5. Execution Search Scanning Core
if search_term:
    matched_entries = []
    
    for sheet_name, df in workbook.items():
        lname = sheet_name.lower()
        if "script" in lname or "properties" in lname or sheet_name.startswith("NV"):
            continue
            
        for _, row in df.iterrows():
            row_dict = row.dropna().to_dict()
            match_found = any(is_smart_match(search_term, val) for val in row_dict.values())
            
            if match_found:
                matched_entries.append({"sheet": sheet_name, "data": row_dict})
                
    if not matched_entries:
        st.error("No matching records located in the diagnostic registries.")
    else:
        st.success(f"Scan complete. Found {len(matched_entries)} matching entry(ies).")
        
        for item in matched_entries:
            with st.container():
                # UPDATED: Removed "Column Values" completely, leaving just the sheet name
                st.markdown(f"### `[{item['sheet']}]`")
                
                for orig_header, value in item["data"].items():
                    clean_val = str(value).strip()
                    if clean_val and clean_val.lower() != "none":
                        display_label = PROFESSIONAL_LABELS.get(orig_header.lower(), orig_header.title())
                        
                        if display_label in ["Error Code", "Fault Code"]:
                            st.markdown(f"**{display_label}:** :blue[{clean_val}]")
                        else:
                            st.markdown(f"**{display_label}:** {clean_val}")
                st.markdown("---")
