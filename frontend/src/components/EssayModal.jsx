import React, { useState } from 'react';

export default function EssayModal({ isOpen, onClose, topic, onSubmit, isSubmitting }) {
    const [essay, setEssay] = useState('');

    if (!isOpen) return null;

    const handleSubmit = () => {
        if (essay.trim()) {
            onSubmit(essay);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl p-6 transform transition-all scale-100">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Write Your Essay</h2>
                <div className="mb-4 p-3 bg-indigo-50 border border-indigo-100 rounded-lg">
                    <span className="text-xs font-bold text-indigo-500 uppercase tracking-wider block mb-1">Topic</span>
                    <p className="text-gray-800 font-serif text-lg leading-snug">{topic}</p>
                </div>

                <textarea
                    className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none font-serif text-gray-800 text-lg leading-relaxed mb-4"
                    placeholder="Start typing your analysis here..."
                    value={essay}
                    onChange={(e) => setEssay(e.target.value)}
                    disabled={isSubmitting}
                    autoFocus
                />

                <div className="flex justify-end gap-3">
                    {/* Optional Cancel button if needed, but per flow we might enforce writing 
          <button onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancel</button>
          */}
                    <button
                        onClick={handleSubmit}
                        disabled={!essay.trim() || isSubmitting}
                        className="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {isSubmitting ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                Submitting...
                            </>
                        ) : (
                            'Submit Essay'
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
