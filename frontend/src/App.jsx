import React, { useState, useEffect, useRef } from 'react';
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';
import CustomNode from './components/CustomNode';
import EssayModal from './components/EssayModal';
import FeedbackModal from './components/FeedbackModal';
import { BookOpen, CheckCircle, Play, Sparkles } from 'lucide-react';

// Initial Nodes Configuration
const initialNodesConfig = [
  { id: 'generate_topic', type: 'custom', data: { label: 'Generate Topic' }, position: { x: 250, y: 0 } },
  { id: 'collect_essay', type: 'custom', data: { label: 'Collect Essay' }, position: { x: 250, y: 120 } },
  { id: 'eval_clarity', type: 'custom', data: { label: 'Clarity Check' }, position: { x: 0, y: 300 } },
  { id: 'eval_depth', type: 'custom', data: { label: 'Depth Check' }, position: { x: 250, y: 300 } },
  { id: 'eval_vocab', type: 'custom', data: { label: 'Vocab Check' }, position: { x: 500, y: 300 } },
  { id: 'aggregate_score', type: 'custom', data: { label: 'Aggregate Score' }, position: { x: 250, y: 450 } },
  { id: 'generate_feedback', type: 'custom', data: { label: 'Generate Feedback' }, position: { x: 600, y: 120 } },
];

const edgeStyle = { stroke: '#94a3b8', strokeWidth: 1.5 }; // Slate-400

const initialEdges = [
  { id: 'e1-2', source: 'generate_topic', target: 'collect_essay', animated: true, style: edgeStyle, markerEnd: { type: MarkerType.ArrowClosed, color: '#94a3b8' } },
  { id: 'e2-3', source: 'collect_essay', target: 'eval_clarity', animated: true, type: 'smoothstep', style: edgeStyle },
  { id: 'e2-4', source: 'collect_essay', target: 'eval_depth', animated: true, type: 'smoothstep', style: edgeStyle },
  { id: 'e2-5', source: 'collect_essay', target: 'eval_vocab', animated: true, type: 'smoothstep', style: edgeStyle },
  { id: 'e3-6', source: 'eval_clarity', target: 'aggregate_score', animated: true, type: 'smoothstep', style: edgeStyle },
  { id: 'e4-6', source: 'eval_depth', target: 'aggregate_score', animated: true, type: 'smoothstep', style: edgeStyle },
  { id: 'e5-6', source: 'eval_vocab', target: 'aggregate_score', animated: true, type: 'smoothstep', style: edgeStyle },
  // Fail Edge
  { id: 'e6-7', source: 'aggregate_score', target: 'generate_feedback', animated: true, type: 'smoothstep', style: { stroke: '#ef4444', strokeWidth: 2, strokeDasharray: 5 }, label: 'Needs Improvement', labelStyle: { fill: '#ef4444', fontWeight: 700 } },
  // Retry Edge
  { id: 'e7-2', source: 'generate_feedback', target: 'collect_essay', animated: true, type: 'smoothstep', style: { stroke: '#f59e0b', strokeWidth: 1.5 }, label: 'Retry' },
];

function App() {
  const nodeTypes = React.useMemo(() => ({
    custom: CustomNode,
  }), []);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodesConfig);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const [threadId, setThreadId] = useState(null);
  const [topic, setTopic] = useState('');

  // Modals
  const [isEssayModalOpen, setIsEssayModalOpen] = useState(false);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);

  const [status, setStatus] = useState('idle');
  const [finalScore, setFinalScore] = useState(null);
  const [feedbackContent, setFeedbackContent] = useState('');

  // Queue for processing events with delay
  const eventQueue = useRef([]);
  const isProcessingQueue = useRef(false);

  // Helper: Update specific node status
  const updateNodeStatus = (nodeId, status, score = undefined) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          const newData = { ...node.data, status };
          if (score !== undefined) newData.score = score;
          return { ...node, data: newData };
        }
        return node;
      })
    );
  };

  // Process Event Queue
  const processQueue = async () => {
    if (isProcessingQueue.current || eventQueue.current.length === 0) return;

    isProcessingQueue.current = true;
    const event = eventQueue.current.shift(); // Dequeue
    const { node, data } = event;

    console.log("Processing Event:", node, "Data:", data);

    // 1. Activate Node
    updateNodeStatus(node, 'active');

    // 2. Wait (Visual Delay)
    // 800ms to let user see the "active" spin
    await new Promise(resolve => setTimeout(resolve, 800));

    // 3. Complete Node (with score if present)
    let docScore = undefined;

    // Helper to safely extract number
    const getScore = (val) => {
      if (typeof val === 'number') return val;
      if (typeof val === 'string' && !isNaN(parseFloat(val))) return parseFloat(val);
      // If it's an object with extras (like the error suggests), try to find a score field or return undefined
      if (typeof val === 'object' && val !== null) {
        console.warn("Received object for score:", val);
        return undefined;
      }
      return undefined;
    };

    if (node === 'eval_clarity') docScore = getScore(data.clarity_score);
    if (node === 'eval_depth') docScore = getScore(data.depth_score);
    if (node === 'eval_vocab') docScore = getScore(data.vocab_score);
    if (node === 'aggregate_score') docScore = getScore(data.total_score);

    updateNodeStatus(node, 'completed', docScore);

    // 4. Handle Logic
    const totalScore = getScore(data.total_score);
    if (node === 'aggregate_score' && totalScore !== undefined && totalScore >= 10) {
      setStatus('finished');
      setFinalScore(totalScore);
    }

    if (node === 'generate_feedback') {
      const fb = data.feedback;
      setFeedbackContent(fb);
      // Show Feedback Modal
      // We do WAIT a tiny bit so the node turns 'green' first
      setTimeout(() => setIsFeedbackModalOpen(true), 500);
    }

    isProcessingQueue.current = false;
    processQueue(); // Recursive call to process next
  };

  const enqueueEvent = (event) => {
    eventQueue.current.push(event);
    processQueue();
  };


  const handleStart = async () => {
    setStatus('generating_topic');
    updateNodeStatus('generate_topic', 'active');
    // Reset Everything
    setFinalScore(null);
    setFeedbackContent('');
    // Clear node statuses
    setNodes((nds) => nds.map(n => ({ ...n, data: { ...n.data, status: 'idle', score: undefined } })));
    updateNodeStatus('generate_topic', 'active');

    try {
      const response = await fetch('http://localhost:8000/start', { method: 'POST' });
      const data = await response.json();

      // Delay for effect
      await new Promise(resolve => setTimeout(resolve, 800));

      setThreadId(data.thread_id);
      setTopic(data.topic);

      updateNodeStatus('generate_topic', 'completed');

      await new Promise(resolve => setTimeout(resolve, 300));
      updateNodeStatus('collect_essay', 'active'); // Ready

      setStatus('waiting_essay');
      setIsEssayModalOpen(true);

    } catch (error) {
      console.error("Error starting:", error);
      updateNodeStatus('generate_topic', 'error');
    }
  };

  const handleSubmitEssay = async (essayContent) => {
    setIsEssayModalOpen(false);
    setStatus('evaluating');
    updateNodeStatus('collect_essay', 'completed');

    // Reset Evaluators for a fresh run
    setNodes((nds) => nds.map(n => {
      if (['eval_clarity', 'eval_depth', 'eval_vocab', 'aggregate_score', 'generate_feedback'].includes(n.id)) {
        return { ...n, data: { ...n.data, status: 'idle', score: undefined } };
      }
      return n;
    }));

    try {
      const response = await fetch('http://localhost:8000/submit-essay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: threadId, essay_content: essayContent }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);
            enqueueEvent(event); // Add to queue
          } catch (e) {
            console.error("Error parsing SSE:", e);
          }
        }
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleRetry = () => {
    setIsFeedbackModalOpen(false);
    // Loop back
    updateNodeStatus('generate_feedback', 'idle'); // Reset generic
    updateNodeStatus('collect_essay', 'active');
    setStatus('waiting_essay');
    setIsEssayModalOpen(true);
  };

  return (
    <div className="flex h-screen w-full flex-col bg-gray-50/50 font-sans text-gray-800">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 px-8 py-4 flex items-center justify-between shadow-sm z-10 sticky top-0">
        <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2 tracking-tight">
          <BookOpen className="w-6 h-6 text-indigo-600" />
          LangGraph <span className="text-gray-400 font-light">Evaluator</span>
        </h1>

        <div className="flex items-center gap-6">
          {threadId && (
            <div className="flex items-center gap-2 text-xs font-mono text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              ID: {threadId.slice(0, 8)}...
            </div>
          )}

          {status === 'idle' || status === 'finished' ? (
            <button
              onClick={handleStart}
              className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 transition shadow-lg shadow-indigo-200 font-medium"
            >
              <Play className="w-4 h-4 fill-current" />
              {status === 'finished' ? 'Start New Session' : 'Start Workflow'}
            </button>
          ) : (
            <div className="px-4 py-2 bg-gray-100/50 text-gray-500 rounded-lg text-sm font-medium animate-pulse">
              Workflow Running...
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 relative overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-right"
          minZoom={0.5}
          maxZoom={1.5}
        >
          <Background color="#cbd5e1" gap={24} size={1} />
          <Controls className="!bg-white !border-gray-200 !shadow-sm !rounded-lg" />
          <MiniMap
            nodeColor={(n) => {
              if (n.data.status === 'completed') return '#10b981';
              if (n.data.status === 'active') return '#3b82f6';
              return '#e2e8f0';
            }}
            className="!bg-white !border-gray-200 !shadow-md !rounded-lg"
          />
        </ReactFlow>

        {/* Modals */}
        <EssayModal
          isOpen={isEssayModalOpen}
          topic={topic}
          onSubmit={handleSubmitEssay}
          isSubmitting={status === 'evaluating'}
        />

        <FeedbackModal
          isOpen={isFeedbackModalOpen}
          feedback={feedbackContent}
          onRetry={handleRetry}
        />

        {/* Success Overlay */}
        {status === 'finished' && (
          <div className="absolute inset-0 z-40 bg-white/40 backdrop-blur-sm flex flex-col items-center justify-center animate-in fade-in duration-500">
            <div className="bg-white p-8 rounded-2xl shadow-2xl border border-green-100 text-center max-w-sm transform transition-all hover:scale-105">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Evaluation Passed!</h2>
              <div className="text-4xl font-black text-green-600 mb-4">{finalScore}/15</div>
              <p className="text-gray-500 mb-6">Great job! Your essay demonstrates strong analytical depth and clarity.</p>
              <button onClick={handleStart} className="w-full py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition font-semibold">
                Start New Topic
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
