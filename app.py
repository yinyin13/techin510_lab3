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
        ..., description="Allows multiple items from a set."
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

def update_progress(progress, id):
    cur.execute(
        """
        UPDATE word_list SET progress = ? WHERE id = ?
        """,
        (progress, id),
    )

def insert_word(data):
    existing_word = cur.execute(
        """
        SELECT id, progress FROM word_list WHERE word = ?
        """,
        (data.word,),
    ).fetchone()

    if existing_word:
        # Word already exists, update progress
        update_progress(data.progress, existing_word[0])
        st.info(f"Progress for **{data.word}** updated! New progress: **{data.progress.value}**", icon = "✨")
    else:
        # Word doesn't exist, insert a new record
        cur.execute(
            """
            INSERT INTO word_list (word, POS, definition, progress) VALUES (?, ?, ?, ?)
            """,
            (data.word, data.POS, data.definition, data.progress),
        )

def main():
    st.title("Word Bank 🔡")
    data = sp.pydantic_form(key="word_form", model=WordBank)
    if data:
        insert_word(data)

    data = cur.execute(
        """
        SELECT * FROM word_list
        """
    ).fetchall()

    # HINT: how to implement a Edit button?
    # if st.query_params.get('id') == "123":
    #     st.write("Hello 123")
    #     st.markdown(
    #         f'<a target="_self" href="/" style="display: inline-block; padding: 6px 10px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; font-size: 12px; border-radius: 4px;">Back</a>',
    #         unsafe_allow_html=True,
    #     )
    #     return

    cols = st.columns(4)
    cols[0].write("Progress")
    cols[1].write("Word")
    cols[2].write("POS")
    cols[3].write("Definition")

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
        cols = st.columns(4)

        cols[0].write(f'<div style="display: inline-block; padding: 6px 10px; background-color:{progress_color}; border-radius: 10px;">{row[4]}</div>', unsafe_allow_html=True)
        cols[1].write(row[1])
        cols[2].write(row[2])
        cols[3].write(row[3])
        
        # cols[2].markdown(
        #     f'<a target="_self" href="/?id=123" style="display: inline-block; padding: 6px 10px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; font-size: 12px; border-radius: 4px;">Action Text on Button</a>',
        #     unsafe_allow_html=True,
        # )

main()