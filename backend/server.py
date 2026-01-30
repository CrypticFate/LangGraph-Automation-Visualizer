import sys
import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to sys.path to allow importing main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app as essay_app

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Unique thread_id for this connection could be generated or passed by client
    # For simplicity, we use a single fixed session for now, or generate one 
    import uuid
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"Client connected: {thread_id}")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            
            if action == "generate_topic":
                print("Generating topic...")
                # Run the graph until the first interruption (collect_essay)
                async for event in essay_app.astream({}, config=config):
                    for node, state_update in event.items():
                        await websocket.send_json({
                            "type": "update",
                            "node": node,
                            "state": state_update
                        })
                
                # Get current state to send the topic
                current_state = await essay_app.aget_state(config)
                topic = current_state.values.get("topic")
                await websocket.send_json({
                    "type": "topic_generated",
                    "topic": topic
                })

            elif action == "submit_essay":
                essay_text = message.get("essay")
                print(f"Received essay: {essay_text[:50]}...")
                
                # Update state with the user's essay
                await essay_app.aupdate_state(config, {"essay_content": essay_text})
                
                # Resume execution
                async for event in essay_app.astream(None, config=config):
                    for node, state_update in event.items():
                        await websocket.send_json({
                            "type": "update",
                            "node": node,
                            "state": state_update
                        })
                
                # Check final state
                final_state = await essay_app.aget_state(config)
                
                if not final_state.next:
                    # Workflow finished (Conditional edge went to END)
                    await websocket.send_json({
                        "type": "complete",
                        "score": final_state.values.get("total_score"),
                        "feedback": final_state.values.get("feedback", "No feedback")
                    })
                else:
                    # Workflow paused again (Conditional edge went to generate_feedback -> collect_essay)
                    # The feedback should be in the state from the 'generate_feedback' node
                    feedback = final_state.values.get("feedback")
                    await websocket.send_json({
                        "type": "feedback",
                        "feedback": feedback
                    })

    except WebSocketDisconnect:
        print(f"Client disconnected: {thread_id}")
    except Exception as e:
        print(f"Error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
