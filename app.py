import sqlite3
import streamlit as st
from pydantic import BaseModel, Field
from enum import Enum
import streamlit_pydantic as sp

class ProgressValue(str, Enum):
    UNF = "unfamiliar"
    REC = "recognized"
    UND = "understood"
    MAS = "mastered"

class WordBank(BaseModel):
    word: str
    POS: str
    definition: str
    progress: ProgressValue = Field(
        ...
    )

con = sqlite3.connect("wordbank.sqlite", isolation_level=None)
cur = con.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS word_list (
        id INTEGER PRIMARY KEY,
        word TEXT,
        POS TEXT,
        definition TEXT,
        progress TEXT
    )
    """
)

# Update progress only
def update_progress(progress, id):
    cur.execute(
        """
        UPDATE word_list SET progress = ? WHERE id = ?
        """,
        (progress, id),
    )

# Update entire entry
def update_entry(data, existing_word_id):
    cur.execute(
        """
        UPDATE word_list SET POS = ?, definition = ?, progress = ? WHERE id = ?
        """,
        (data.POS, data.definition, data.progress, existing_word_id),
    )

# Delete an entry
def delete_entry(id):
    cur.execute(
        """
        DELETE FROM word_list WHERE id = ?;
        """,
        (id,),
    )

def insert_word(data):
    existing_word = cur.execute(
        """
        SELECT id FROM word_list WHERE word = ?
        """,
        (data.word,),
    ).fetchone()

    if existing_word:
        # Word already exists, update the entire entry
        update_entry(data, existing_word[0])
        st.info(f"Word **{data.word}** updated!", icon="✨")

    else:
        # Word doesn't exist, insert a new record
        cur.execute(
            """
            INSERT INTO word_list (word, POS, definition, progress) VALUES (?, ?, ?, ?)
            """,
            (data.word, data.POS, data.definition, data.progress),
        )
        st.success(f"New entry for **{data.word}** added!", icon="✨")

        # Display only the entry that has just been entered
        data = cur.execute(
            """
            SELECT * FROM word_list WHERE id = LAST_INSERT_ROWID()
            """
        ).fetchall()

        cols = st.columns(5)
        cols[0].write("")
        cols[1].write("Progress")
        cols[2].write("Word")
        cols[3].write("POS")
        cols[4].write("Definition")

        def get_progress_color(progress):
            if progress == "unfamiliar":
                return "#F76F65"
            elif progress == "recognized":
                return "#F3A738"
            elif progress == "understood":
                return "#FDF984"
            elif progress == "mastered":
                return "#94C747"
            else:
                return "black"

        for row in data:
            progress_color = get_progress_color(row[4])
            cols = st.columns(5)

            delete_button_id = f"delete_button_{row[0]}.1"
            if cols[0].button("Delete", key=delete_button_id):
                # Button clicked, delete the entry
                delete_entry(row[0])
                st.rerun()

            cols[1].write(f'<div style="display: inline-block; padding: 6px 10px; background-color:{progress_color}; border-radius: 10px;">{row[4]}</div>', unsafe_allow_html=True)
            cols[2].write(row[1])
            cols[3].write(row[2])
            cols[4].write(row[3])

def main():
    st.title("Word Bank 🔡")

    # Tabs for form and list
    tabs = st.tabs(["Form", "List"])

    with tabs[0]:
        # Form tab to insert new entries
        st.write("To update an entry, simply fill the form again")
        data = sp.pydantic_form(key="word_form", model=WordBank)
        
        if data:
            insert_word(data)

    with tabs[1]:
        search_col, filter_col = st.columns(2)

        # Search bar
        search_term = search_col.text_input("🔎 Search for a word:", key="search_term")

        # Filter by progress
        selected_progress = filter_col.selectbox("Filter by Progress:", ["All"] + [progress.value for progress in ProgressValue], key="selected_progress")

        # Fetch data based on search and filter
        data = cur.execute(
            """
            SELECT * FROM word_list
            WHERE (word LIKE ? OR definition LIKE ?) AND (? = 'All' OR progress = ?)
            """,
            (f"%{search_term}%", f"%{search_term}%", selected_progress, selected_progress),
        ).fetchall()

        cols = st.columns(5)
        cols[0].write("")
        cols[1].write("Progress")
        cols[2].write("Word")
        cols[3].write("POS")
        cols[4].write("Definition")

        def get_progress_color(progress):
            if progress == "unfamiliar":
                return "#F76F65"
            elif progress == "recognized":
                return "#F3A738"
            elif progress == "understood":
                return "#FDF984"
            elif progress == "mastered":
                return "#94C747"
            else:
                return "black"
        
        for row in data:
            progress_color = get_progress_color(row[4])
            cols = st.columns(5)

            delete_button_id = f"delete_button_{row[0]}"
            if cols[0].button("Delete", key=delete_button_id):
                # Button clicked, delete the entry
                delete_entry(row[0])
                st.rerun()

            cols[1].write(f'<div style="display: inline-block; padding: 6px 10px; background-color:{progress_color}; border-radius: 10px;">{row[4]}</div>', unsafe_allow_html=True)
            cols[2].write(row[1])
            cols[3].write(row[2])
            cols[4].write(row[3])

main()