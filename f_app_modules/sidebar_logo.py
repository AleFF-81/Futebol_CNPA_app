import streamlit as st

def sidebar_logo():
    with st.sidebar:
        cola, colb, colc = st.sidebar.columns([1, 4, 1])
        with colb:
            st.image('imgs/logo3.png')
        
        st.markdown('<h style="font-size: 16pt; color:#F9BC33; font-weigth:bold;">Sistema de Gestão Esportiva</h>', unsafe_allow_html=True)
