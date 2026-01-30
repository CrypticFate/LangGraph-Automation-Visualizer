from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver
from graph import workflow, EssayState  
import uuid
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database for graph state
checkpointer = MemorySaver()
graph_app = workflow.compile(checkpointer=checkpointer, interrupt_before=["collect_essay"])

class EssayInput(BaseModel):
    thread_id: str
    essay_content: str

@app.post("/start")
async def start_workflow():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Run ONLY until the first interruption (collect_essay)
    # We use stream to capture the output of "generate_topic"
    topic = ""
    async for event in graph_app.astream({}, config=config):
        if "generate_topic" in event:
            topic = event["generate_topic"]["topic"]
            
    return {"thread_id": thread_id, "topic": topic}

@app.post("/submit-essay")
async def submit_essay(input: EssayInput):
    config = {"configurable": {"thread_id": input.thread_id}}
    
    # Update state with user essay
    # Resume graph execution
    # We use a generator to STREAM updates to the frontend
    async def event_generator():
        # Resume by updating state
        # We need to make sure we are updating the correct key. 
        # The 'collect_essay' node in the graph is a pass-through, so we update the state 
        # which will be used by subsequent nodes. 
        # Using as_node="collect_essay" ensures we update as if we are at that node.
        await graph_app.aupdate_state(config, {"essay_content": input.essay_content}, as_node="collect_essay")
        
        # Stream subsequent nodes
        # passing None triggers resumption from the interrupted state
        async for event in graph_app.astream(None, config=config):
            for node_name, data in event.items():
                # Yield JSON string for SSE
                # We format it as a data: json_string\n\n for standard SSE or just lines if using StreamingResponse with media_type="application/x-ndjson"
                # The user requested specific json format logs
                # Format: {"event": "start/finish", ...} - though the example showed {"node": ...}
                yield f'{json.dumps({"node": node_name, "data": data})}\n'
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
