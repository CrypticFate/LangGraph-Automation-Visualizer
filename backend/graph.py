import os
import operator
import time
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# Define the Shared State
class EssayState(TypedDict):
    topic: str
    essay_content: str
    clarity_score: int
    depth_score: int
    vocab_score: int
    total_score: int
    feedback: str
    revision_count: int

# Initialize Gemini Model
if not os.getenv("GOOGLE_API_KEY"):
    print("Warning: GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.5)

def generate_topic(state: EssayState):
    """Generates a UPSC standard essay topic."""
    print("Node: Generating Topic...")
    prompt = "Generate a single, complex UPSC essay topic on social or economic issues. Output ONLY the topic text."
    time.sleep(4)
    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        extracted_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                extracted_parts.append(part["text"])
            elif isinstance(part, str):
                extracted_parts.append(part)
            else:
                extracted_parts.append(str(part))
        content = " ".join(extracted_parts)
    return {"topic": content.strip(), "revision_count": 0}

def collect_essay(state: EssayState):
    """
    Placeholder for human input. 
    State is updated externally before this node resumes.
    """
    pass 

def eval_clarity(state: EssayState):
    """Evaluates flow, coherence, and structure."""
    print("Node: Evaluating Clarity...")
    prompt = f"""
    Evaluate the following essay on the topic '{state['topic']}' for CLARITY OF THOUGHT.
    Score it out of 5. Return ONLY the integer score.
    
    Essay: {state['essay_content']}
    """
    time.sleep(2)
    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        extracted_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                extracted_parts.append(part["text"])
            elif isinstance(part, str):
                extracted_parts.append(part)
            else:
                extracted_parts.append(str(part))
        content = " ".join(extracted_parts)
    try:
        score = int(''.join(filter(str.isdigit, content)))
    except:
        score = 0
    return {"clarity_score": score}

def eval_depth(state: EssayState):
    """Evaluates multidimensional analysis and evidence."""
    print("Node: Evaluating Depth...")
    prompt = f"""
    Evaluate the following essay on the topic '{state['topic']}' for DEPTH OF ANALYSIS.
    Did they cover social, political, economic dimensions?
    Score it out of 5. Return ONLY the integer score.
    
    Essay: {state['essay_content']}
    """
    time.sleep(2)
    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        extracted_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                extracted_parts.append(part["text"])
            elif isinstance(part, str):
                extracted_parts.append(part)
            else:
                extracted_parts.append(str(part))
        content = " ".join(extracted_parts)
    try:
        score = int(''.join(filter(str.isdigit, content)))
    except:
        score = 0
    return {"depth_score": score}

def eval_vocab(state: EssayState):
    """Evaluates language precision and vocabulary."""
    print("Node: Evaluating Vocabulary...")
    prompt = f"""
    Evaluate the following essay on the topic '{state['topic']}' for LANGUAGE & VOCABULARY.
    Score it out of 5. Return ONLY the integer score.
    
    Essay: {state['essay_content']}
    """
    time.sleep(2)
    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        extracted_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                extracted_parts.append(part["text"])
            elif isinstance(part, str):
                extracted_parts.append(part)
            else:
                extracted_parts.append(str(part))
        content = " ".join(extracted_parts)
    try:
        score = int(''.join(filter(str.isdigit, content)))
    except:
        score = 0
    return {"vocab_score": score}

def aggregate_score(state: EssayState):
    """Sync node: Waits for parallel evaluations and sums them."""
    print("Node: Aggregating Scores...")
    total = state.get('clarity_score', 0) + state.get('depth_score', 0) + state.get('vocab_score', 0)
    return {"total_score": total}

def generate_feedback(state: EssayState):
    """Generates feedback if the score is low."""
    print("Node: Generating Feedback...")
    prompt = f"""
    The student scored {state['total_score']}/15.
    Clarity: {state['clarity_score']}, Depth: {state['depth_score']}, Language: {state['vocab_score']}.
    Provide 3 bullet points on how to improve this specific essay for the next draft.
    """
    time.sleep(2)
    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        extracted_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                extracted_parts.append(part["text"])
            elif isinstance(part, str):
                extracted_parts.append(part)
            else:
                extracted_parts.append(str(part))
        content = " ".join(extracted_parts)
    return {"feedback": content}

def check_pass_fail(state: EssayState):
    if state['total_score'] >= 10:
        return "pass"
    return "fail"

# Initialize Graph
workflow = StateGraph(EssayState)

# Add Nodes
workflow.add_node("generate_topic", generate_topic)
workflow.add_node("collect_essay", collect_essay)
workflow.add_node("eval_clarity", eval_clarity)
workflow.add_node("eval_depth", eval_depth)
workflow.add_node("eval_vocab", eval_vocab)
workflow.add_node("aggregate_score", aggregate_score)
workflow.add_node("generate_feedback", generate_feedback)

# Add Edges
workflow.set_entry_point("generate_topic")
workflow.add_edge("generate_topic", "collect_essay")

workflow.add_edge("collect_essay", "eval_clarity")
workflow.add_edge("collect_essay", "eval_depth")
workflow.add_edge("collect_essay", "eval_vocab")

workflow.add_edge("eval_clarity", "aggregate_score")
workflow.add_edge("eval_depth", "aggregate_score")
workflow.add_edge("eval_vocab", "aggregate_score")

workflow.add_conditional_edges(
    "aggregate_score",
    check_pass_fail,
    {
        "pass": END,
        "fail": "generate_feedback"
    }
)

workflow.add_edge("generate_feedback", "collect_essay")

# We do NOT compile here with a specific checkpointer if we want to pass it dynamically, 
# but usually for the app we want a shared one or one per request. 
# The implementation plan uses a global in-memory checkpointer for simplicity as per the user request.
