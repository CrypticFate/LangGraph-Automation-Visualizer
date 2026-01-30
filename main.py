import os
import operator
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

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

def generate_topic(state: EssayState):
    """Generates a UPSC standard essay topic."""
    print("Node: Generating Topic...")
    prompt = "Generate a single, complex UPSC essay topic on social or economic issues. Output ONLY the topic text."
    response = llm.invoke(prompt)
    return {"topic": response.content.strip(), "revision_count": 0}

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
    response = llm.invoke(prompt)
    try:
        score = int(''.join(filter(str.isdigit, response.content)))
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
    response = llm.invoke(prompt)
    try:
        score = int(''.join(filter(str.isdigit, response.content)))
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
    response = llm.invoke(prompt)
    try:
        score = int(''.join(filter(str.isdigit, response.content)))
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
    response = llm.invoke(prompt)
    return {"feedback": response.content}

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

checkpointer = MemorySaver()
# interrupt_before=['collect_essay'] pauses the graph right before entering that node
app = workflow.compile(checkpointer=checkpointer, interrupt_before=["collect_essay"])

if __name__ == "__main__":
    # Configuration for the session
    config = {"configurable": {"thread_id": "session_1"}}

    print("--- STARTING UPSC ESSAY EVALUATION WORKFLOW ---")

    # 1. Run until the first human input is needed (Topic Generation)
    for event in app.stream({}, config=config):
        pass

    current_state = app.get_state(config).values
    topic = current_state.get('topic', 'No topic generated')
    print(f"\nASSIGNED TOPIC: {topic}")

    while True:
        try:
            user_essay = input("\n> Write your essay (or type 'quit' to exit): ")
            if user_essay.lower() in ['quit', 'exit']:
                print("Exiting...")
                break

            if not user_essay.strip():
                print("Essay cannot be empty.")
                continue

            # Update state with the user's essay
            # We are currently paused BEFORE 'collect_essay'.
            # We update the state to include the essay content.
            # Then we resume execution. The 'collect_essay' node will run (pass), then the evaluators.
            app.update_state(config, {"essay_content": user_essay})

            print("\nEvaluating (Running parallel nodes)...")
            
            # Resume the graph (pass None to indicate resumption from interrupt)
            for event in app.stream(None, config=config):
                if "aggregate_score" in event:
                    scores = event['aggregate_score']
                    print(f"\nTotal Score: {scores['total_score']}/15")
                if "generate_feedback" in event:
                    print(f"\nFEEDBACK REVISION:\n{event['generate_feedback']['feedback']}")
                    print("\n--- SENDING BACK FOR REWRITE ---")

            # Check if we are done (Graph finished)
            final_state = app.get_state(config)
            
            # If the conditional edge went to END, final_state.next will be empty tuple
            if not final_state.next:
                print("\nCONGRATULATIONS! Your essay passed the evaluation logic.")
                print(f"Final Score: {final_state.values.get('total_score')}")
                break
            else:
                # If we are looping back, the graph is paused again at 'collect_essay'
                # (because we have an edge generate_feedback -> collect_essay, and interrupt_before=['collect_essay'])
                pass

        except Exception as e:
            print(f"An error occurred: {e}")
            break
