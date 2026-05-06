'use client';

import { useState } from 'react';
import { Trash2, Check, Clock, AlertCircle } from 'lucide-react';

interface Reminder {
  id: string;
  title: string;
  description?: string;
  dueDate: Date;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
}

interface ReminderCardProps {
  reminder: Reminder;
  onComplete: (id: string) => void;
  onDelete: (id: string) => void;
}

export function ReminderCard({ reminder, onComplete, onDelete }: ReminderCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  const dueDate = reminder.dueDate instanceof Date ? reminder.dueDate : new Date(reminder.dueDate);
  const isOverdue = dueDate < new Date() && !reminder.completed;
  const isToday = dueDate.toDateString() === new Date().toDateString();
  
  const priorityStyles = {
    low: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
    medium: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
    high: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
  };
  
  const priorityBadgeColor = {
    low: 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200',
    medium: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-200',
    high: 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200',
  };
  
  const priorityLabel = {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
  };

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`relative group bg-surface border border-border rounded-lg p-4 transition-all duration-300 hover:shadow-lg hover:border-primary/30 ${priorityStyles[reminder.priority]} ${
        reminder.completed ? 'opacity-60' : ''
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          onClick={() => onComplete(reminder.id)}
          className={`mt-1 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
            reminder.completed
              ? 'bg-primary border-primary'
              : 'border-border hover:border-primary'
          }`}
        >
          {reminder.completed && <Check className="w-4 h-4 text-white" />}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`font-semibold text-foreground transition-all duration-200 ${
              reminder.completed ? 'line-through text-text-secondary' : ''
            }`}
          >
            {reminder.title}
          </h3>
          {reminder.description && (
            <p className="text-sm text-text-secondary mt-1 line-clamp-2">
              {reminder.description}
            </p>
          )}
          
          {/* Meta Information */}
          <div className="flex items-center gap-3 mt-3 flex-wrap">
            <span
              className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${priorityBadgeColor[reminder.priority]}`}
            >
              {reminder.priority.charAt(0).toUpperCase() + reminder.priority.slice(1)}
            </span>
            
            <div className="flex items-center gap-1 text-xs text-text-secondary">
              {isOverdue ? (
                <>
                  <AlertCircle className="w-3.5 h-3.5 text-error" />
                  <span className="text-error font-medium">Overdue</span>
                </>
              ) : isToday ? (
                <>
                  <Clock className="w-3.5 h-3.5 text-primary" />
                  <span className="text-primary font-medium">Today</span>
                </>
              ) : (
                <>
                  <Clock className="w-3.5 h-3.5" />
                  <span>{dueDate.toLocaleDateString()}</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Delete Button */}
        <button
          onClick={() => onDelete(reminder.id)}
          className={`flex-shrink-0 text-text-secondary hover:text-error transition-all duration-200 opacity-0 group-hover:opacity-100 ${
            isHovered ? 'opacity-100' : ''
          }`}
          aria-label="Delete reminder"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
