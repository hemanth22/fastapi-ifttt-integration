'use client';

import { Plus, CheckSquare } from 'lucide-react';

interface HeaderProps {
  onAddClick: () => void;
}

export function Header({ onAddClick }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 bg-surface/80 backdrop-blur-lg border-b border-border shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-primary via-primary-light to-accent w-10 h-10 rounded-lg flex items-center justify-center shadow-lg">
            <CheckSquare className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">Reminders</h1>
            <p className="text-xs text-text-secondary">Stay organized, never forget</p>
          </div>
        </div>

        {/* Add Button */}
        <button
          onClick={onAddClick}
          className="flex items-center gap-2 bg-gradient-to-r from-primary to-primary-dark text-white px-5 py-2.5 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 hover:scale-105 active:scale-95"
        >
          <Plus className="w-5 h-5" />
          <span className="hidden sm:inline">New Reminder</span>
          <span className="sm:hidden">Add</span>
        </button>
      </div>
    </header>
  );
}
