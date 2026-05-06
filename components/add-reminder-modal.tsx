'use client';

import { useState } from 'react';
import { X, Plus } from 'lucide-react';

interface AddReminderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (reminder: { title: string; description: string; dueDate: Date; priority: 'low' | 'medium' | 'high' }) => void;
}

export function AddReminderModal({ isOpen, onClose, onAdd }: AddReminderModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    onAdd({
      title,
      description,
      dueDate: new Date(dueDate || new Date()),
      priority,
    });

    // Reset form
    setTitle('');
    setDescription('');
    setDueDate('');
    setPriority('medium');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-surface border border-border rounded-xl shadow-xl max-w-md w-full animate-in">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="bg-gradient-to-br from-primary to-accent w-8 h-8 rounded-lg flex items-center justify-center">
              <Plus className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-lg font-semibold text-foreground">New Reminder</h2>
          </div>
          <button
            onClick={onClose}
            className="text-text-secondary hover:text-foreground transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Title *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What do you need to remember?"
              className="w-full px-4 py-2 bg-background border border-border rounded-lg text-foreground placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary"
              autoFocus
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add more details..."
              className="w-full px-4 py-2 bg-background border border-border rounded-lg text-foreground placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary resize-none h-24"
            />
          </div>

          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Due Date
            </label>
            <input
              type="datetime-local"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full px-4 py-2 bg-background border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Priority
            </label>
            <div className="flex gap-2">
              {(['low', 'medium', 'high'] as const).map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setPriority(p)}
                  className={`flex-1 px-3 py-2 rounded-lg font-medium transition-all duration-200 ${
                    priority === p
                      ? 'bg-primary text-white ring-2 ring-primary/50'
                      : 'bg-background border border-border text-text-secondary hover:border-primary'
                  }`}
                >
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-foreground bg-background border border-border rounded-lg font-medium hover:bg-surface-hover transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!title.trim()}
              className="flex-1 px-4 py-2 text-white bg-primary rounded-lg font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add Reminder
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
