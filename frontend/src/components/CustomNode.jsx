import React from 'react';
import { Handle, Position } from 'reactflow';
import { CheckCircle2, CircleDashed, Loader2 } from 'lucide-react';

export default function CustomNode({ data }) {
    // Base Styles
    const baseClasses = "px-4 py-3 rounded-lg border min-w-[160px] text-center transition-all duration-500 flex flex-col items-center justify-center relative";

    let statusClasses = "bg-white border-gray-200 shadow-sm";
    let icon = <CircleDashed className="w-4 h-4 text-gray-400 mb-2" />;
    let labelColor = "text-gray-600";

    if (data.status === 'active') {
        statusClasses = "bg-blue-50 border-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.3)] scale-105 ring-2 ring-blue-100";
        icon = <Loader2 className="w-4 h-4 text-blue-500 mb-2 animate-spin" />;
        labelColor = "text-blue-800 font-semibold";
    } else if (data.status === 'completed') {
        statusClasses = "bg-green-50 border-green-400 shadow-md";
        icon = <CheckCircle2 className="w-4 h-4 text-green-500 mb-2" />;
        labelColor = "text-green-800 font-medium";
    } else if (data.status === 'error') {
        statusClasses = "bg-red-50 border-red-400";
        labelColor = "text-red-800";
    }


    let labelContent = data.label;
    if (typeof labelContent === 'object' && labelContent !== null) {
        labelContent = JSON.stringify(labelContent);
    }

    return (
        <div className={`${baseClasses} ${statusClasses}`}>
            <Handle type="target" position={Position.Top} className="!w-1.5 !h-1.5 !bg-gray-400 !border-0" />

            {icon}

            <div className={`text-sm ${labelColor} leading-tight`}>{labelContent}</div>

            {/* Show score if available with a nice badge look */}
            {data.score !== undefined && (
                <div className="mt-2 text-xs font-bold px-2 py-0.5 bg-white/60 rounded-full border border-gray-200/50 text-gray-700">
                    Score: {typeof data.score === 'object' ? JSON.stringify(data.score) : data.score}
                </div>
            )}


            <Handle type="source" position={Position.Bottom} className="!w-1.5 !h-1.5 !bg-gray-400 !border-0" />
        </div>
    );
}
