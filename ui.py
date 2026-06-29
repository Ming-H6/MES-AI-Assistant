import streamlit as st
from vectorstore import get_collection
from rag import ask
from storage import (save_chats,load_chats)

st.title("MES AI ASSISTANT")
with st.sidebar:

    Debug = st.checkbox("Debug Retrieval")

if "conversations" not in st.session_state:
    st.session_state.conversations = (
        load_chats()
    )

if "current_messages" not in st.session_state:
    st.session_state.current_messages = []

if"active_chat" not in st.session_state:
    st.session_state.active_chat = None

if"rename_chat" not in st.session_state:
    st.session_state.rename_chat = None

if "conversation_summary" not in st.session_state:
    st.session_state.conversation_summary =""

def update_summary(messages):
    user_questions = []

    for msg in messages:
        if msg["role"] == "user":
            user_questions.append(msg["content"])

    summary_questions = user_questions[-10:]

    return "\n".join(summary_questions)


for message in st.session_state.current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if (message["role"] == "assistant" and "sources" in message):
            
            with st.expander("Sources"):
                
                for source in message["sources"]:
                    st.write(f"{source['Customer']} | "
                             f"{source['Section']} | "
                             f"{source['Subject']}")
        

        if (Debug and message["role"] == "assistant" and "debug" in message):

            with st.expander("Debug Retrieval"):
                distances = message["debug"]["distances"]

                scores = message["scores"]

                metas = message["debug"]["metadatas"]

                for i in range(len(distances)):

                    st.write(f"Rank{i+1}")

                    st.write(f"Distance:{distances[i]:.4f}")

                    st.write(f"Keyword Score:{scores[i]:.4f}")

                    source = metas[i]
                    
                    st.write(f"{source['Customer']} | "
                             f"{source['Section']} | "
                             f"{source['Subject']}")
                    
                    st.divider()




question = st.chat_input("Input MES question...")

collection = get_collection()

if question:
    

    st.session_state.current_messages.append(
        {"role":"user",
         "content": question}
    )

    st.session_state.conversation_summary = (
        update_summary(st.session_state.current_messages)
    )

    with st.chat_message("user"):
        st.markdown(question)
    
    with st.spinner("MES AI is searching knowledge base..."):
        print("BFROE ASK")

        print(type(ask))

        answer = ask(collection, question,st.session_state.current_messages)

        print("AFTER ASK")

    full_response = ""
    with st.chat_message("assistant"):
        
        answer_placeholder = st.empty()
        source_placeholder = st.empty()
        debug_placeholder = st.empty()

        for chunk in answer["stream"]:
            content = chunk["message"]["content"]
            full_response += content
            answer_placeholder.markdown(full_response+"▌")

        answer_placeholder.markdown(full_response)
        with source_placeholder.container():
            
            with st.expander("Sources"):
                
                for source in answer["sources"]:

                    st.write(f"{source['Customer']} | "
                             f"{source['Section']} | "
                             f"{source['Subject']}")
    
    debug_placeholder = st.empty()
    with debug_placeholder.container():

        if (Debug and "debug" in answer):

                with st.expander("Debug Retrieval"):
                    distances = answer["debug"]["distances"]

                    scores = answer["scores"]

                    metas = answer["debug"]["metadatas"]

                    for i in range(len(distances)):

                        st.write(f"Rank{i+1}")

                        st.write(f"Distance:{distances[i]:.4f}")

                        st.write(f"Keyword Score:{scores[i]:.4f}")

                        source = metas[i]
                    
                        st.write(f"{source['Customer']} | "
                                f"{source['Section']} | "
                                f"{source['Subject']}")
                    
                        st.divider()

        


    st.session_state.current_messages.append(
        {
            "role":"assistant",
            "content": full_response,
            "sources":answer.get("sources",[]),
            "debug":answer.get("debug",{}),
            "scores":answer.get("scores",[])
         }
    )

    st.session_state.conversaiton_summary = (
        update_summary(st.session_state.current_messages)
    )

    if st.session_state.active_chat is not None:
        st.session_state.conversations[st.session_state.active_chat]["messages"] = st.session_state.current_messages.copy()
        save_chats(st.session_state.conversations)

with st.sidebar:
    st.title("\u2726 MES AI Assitant")

    st.divider()

    if st.button("\U0001F5EF\uFE0F New Chat"):
        
        if len(st.session_state.current_messages) > 0:
            
            first_question=""

            if st.session_state.active_chat is None:
        
                for msg in st.session_state.current_messages:
            
                    if msg["role"] == "user":

                        first_question = msg["content"]

                        break
        
                st.session_state.conversations.append(
                    {
                        "title":first_question,
                        "messages": st.session_state.current_messages.copy()
                    }
                )

                save_chats(st.session_state.conversations)

        st.session_state.current_messages =[]

        st.session_state.active_chat = None

        st.rerun()

    with st.expander(
        "🔍Search Chat",
        expanded = False
    ):
        search_text = st.text_input(
            "",
            placeholder = "Search chat...",
            label_visibility="collapsed"
        )

    conversations= st.session_state.conversations

    if search_text:

        filtered_conversations = []

        for index,chat in enumerate(conversations):

            if search_text.lower() in chat["title"].lower():

                filtered_conversations.append((index,chat))
    else:
        
        filtered_conversations = list(enumerate(conversations))

    st.divider()

    st.subheader("Recents")

    conversations = st.session_state.conversations

    for real_index,chat in reversed(filtered_conversations):

        col1, col2 = st.columns([8,2])
        
        with col1:

            if st.button(
                chat["title"][:30],
                key = f"chat_{real_index}"
            ):
                st.session_state.current_messages = (
                chat["messages"].copy()
                )

                st.session_state.active_chat = real_index

                st.rerun()
        
        with col2:
            with st.popover("⋮"):

                if st.button(
                    "\U0001F5D1\uFE0F Delete",
                    key = f"delete_{real_index}"
                ):
                
                    if st.session_state.active_chat == real_index:

                        st.session_state.current_messages= []
                        st.session_state.active_chat = None
            
                    del st.session_state.conversations[real_index]

                    save_chats(st.session_state.conversations)

                    st.rerun()

                if st.button(
                    "\U0001F58C\uFE0F Edit",
                    key = f"edit_{real_index}"
                ):
                    st.session_state.rename_chat = (real_index)

                    st.rerun()
            
        if (st.session_state.rename_chat == real_index):

            new_title = st.text_input(
                "",
                value=chat["title"],
                key = f"rename_{real_index}"
            )
                   
            if st.button(
                "💾",
                key = f"save_{real_index}"
            ):
                st.session_state.conversations[real_index]["title"]= new_title

                save_chats(st.session_state.conversations)

                st.session_state.rename_chat = None

                st.rerun()


