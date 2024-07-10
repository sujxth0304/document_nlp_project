import streamlit as st

def main():
    st.title('Document App')
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("###### Autocorrection")
        autocorrect_image = st.image('src/autocorrect_icon.png', width=100)
        autocorrect_button = st.button("Go to Autocorrection")
        if autocorrect_button:
            js_code = f"window.open('https://autocorrectpy-fzgsa27bt5tqd2dnf3tddj.streamlit.app/', '_blank')"
            st.components.v1.html(f'<script>{js_code}</script>')

    with col2:
        st.write("###### Named Entity Recognition")
        ner_image = st.image('src/ner_icon.png', width=100)
        ner_button = st.button("Go to NER")
        if ner_button:
            js_code = f"window.open('https://j72xxgcgnnnjxeappfxr5xj.streamlit.app/', '_blank')"
            st.components.v1.html(f'<script>{js_code}</script>')

    with col3:
        st.write("###### Document QnA")
        qna_image = st.image('src/pdf_icon.png', width=100)
        qna_button = st.button("Go to QnA")
        if qna_button:
            js_code = f"window.open('https://ibwnkoqu6quz3jzbsp4tab.streamlit.app/', '_blank')"
            st.components.v1.html(f'<script>{js_code}</script>')

if __name__ == '__main__':
    main()
