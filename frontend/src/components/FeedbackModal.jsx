import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function FeedbackModal({ isOpen, feedback, onRetry }) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm transition-opacity duration-300">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg p-0 overflow-hidden transform transition-all scale-100 border border-orange-100">
                <div className="bg-orange-50 px-6 py-4 border-b border-orange-100 flex items-center gap-3">
                    <div className="p-2 bg-orange-100 rounded-full">
                        <AlertTriangle className="w-6 h-6 text-orange-600" />
                    </div>
                    <h2 className="text-xl font-bold text-gray-800"> improvement Needed</h2>
                </div>

                <div className="p-6">
                    <p className="text-gray-600 mb-4 text-sm font-medium">Your essay needs some work. Here is the AI feedback:</p>

                    <div className="bg-gray-50 p-4 rounded-lg border border-gray-100 text-gray-700 text-sm leading-relaxed whitespace-pre-wrap font-serif">
                        {typeof feedback === 'object' ? JSON.stringify(feedback, null, 2) : feedback}
                    </div>

                </div>

                <div className="px-6 py-4 bg-gray-50 flex justify-end">
                    <button
                        onClick={onRetry}
                        className="px-5 py-2.5 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition flex items-center gap-2 shadow-sm"
                    >
                        <RefreshCw className="w-4 h-4" /> Try Again
                    </button>
                </div>
            </div>
        </div>
    );
}
