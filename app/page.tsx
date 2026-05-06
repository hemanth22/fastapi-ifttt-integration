'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/header';
import { AddReminderModal } from '@/components/add-reminder-modal';
import { ReminderCard } from '@/components/reminder-card';
import { StatsWidget } from '@/components/stats-widget';
import { FilterTabs } from '@/components/filter-tabs';
import { CheckCircle2 } from 'lucide-react';

interface Reminder {
  id: string;
  title: string;
  description?: string;
  dueDate: Date;
  priority: 'low' | 'medium' | 'high';
  completed: boolean;
}

type FilterType = 'all' | 'active' | 'completed' | 'overdue';

export default function Home() {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [filter, setFilter] = useState<FilterType>('all');
  const [mounted, setMounted] = useState(false);

  // Load reminders from localStorage on mount
  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem('reminders');
    if (saved) {
      const parsed = JSON.parse(saved);
      setReminders(parsed.map((r: any) => ({
        ...r,
        dueDate: new Date(r.dueDate),
      })));
    } else {
      // Add sample reminders for demo
      setReminders([
        {
          id: '1',
          title: 'Team standup meeting',
          description: 'Daily team sync at 10 AM',
          dueDate: new Date(new Date().setHours(10, 0, 0, 0)),
          priority: 'high',
          completed: false,
        },
        {
          id: '2',
          title: 'Review pull requests',
          description: 'Check and review pending PRs',
          dueDate: new Date(new Date().setHours(14, 0, 0, 0)),
          priority: 'medium',
          completed: false,
        },
        {
          id: '3',
          title: 'Buy groceries',
          description: 'Milk, eggs, bread, vegetables',
          dueDate: new Date(new Date().getTime() + 2 * 24 * 60 * 60 * 1000),
          priority: 'low',
          completed: false,
        },
      ]);
    }
  }, []);

  // Save reminders to localStorage whenever they change
  useEffect(() => {
    if (mounted) {
      localStorage.setItem('reminders', JSON.stringify(reminders));
    }
  }, [reminders, mounted]);

  const handleAddReminder = (newReminder: Omit<Reminder, 'id' | 'completed'>) => {
    const reminder: Reminder = {
      ...newReminder,
      id: Date.now().toString(),
      completed: false,
    };
    setReminders([reminder, ...reminders]);
  };

  const handleCompleteReminder = (id: string) => {
    setReminders(reminders.map(r =>
      r.id === id ? { ...r, completed: !r.completed } : r
    ));
  };

  const handleDeleteReminder = (id: string) => {
    setReminders(reminders.filter(r => r.id !== id));
  };

  // Calculate stats
  const now = new Date();
  const stats = {
    all: reminders.length,
    active: reminders.filter(r => !r.completed).length,
    completed: reminders.filter(r => r.completed).length,
    overdue: reminders.filter(r => r.dueDate < now && !r.completed).length,
  };

  // Filter reminders
  const filteredReminders = reminders.filter(r => {
    switch (filter) {
      case 'active':
        return !r.completed;
      case 'completed':
        return r.completed;
      case 'overdue':
        return r.dueDate < now && !r.completed;
      default:
        return true;
    }
  });

  // Sort reminders by due date
  const sortedReminders = [...filteredReminders].sort((a, b) =>
    a.dueDate.getTime() - b.dueDate.getTime()
  );

  if (!mounted) return null;

  const completionPercentage = stats.all > 0 
    ? Math.round((stats.completed / stats.all) * 100)
    : 0;

  return (
    <div className="min-h-screen bg-background">
      <Header onAddClick={() => setIsModalOpen(true)} />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {/* Stats */}
        <div className="mb-8">
          <StatsWidget
            total={stats.all}
            completed={stats.completed}
            overdue={stats.overdue}
            upcoming={stats.active}
          />
        </div>

        {/* Progress Bar */}
        {stats.all > 0 && (
          <div className="mb-8 bg-surface border border-border rounded-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-foreground">Overall Progress</h3>
              <span className="text-lg font-bold text-primary">{completionPercentage}%</span>
            </div>
            <div className="w-full bg-background rounded-full h-3">
              <div
                className="bg-gradient-to-r from-primary to-accent h-3 rounded-full transition-all duration-500"
                style={{ width: `${completionPercentage}%` }}
              />
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="mb-6">
          <FilterTabs activeFilter={filter} onFilterChange={setFilter} counts={stats} />
        </div>

        {/* Reminders List */}
        {sortedReminders.length > 0 ? (
          <div className="space-y-3">
            {sortedReminders.map(reminder => (
              <ReminderCard
                key={reminder.id}
                reminder={reminder}
                onComplete={handleCompleteReminder}
                onDelete={handleDeleteReminder}
              />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 px-4">
            <div className="bg-gradient-to-br from-primary/10 to-accent/10 rounded-full p-8 mb-4">
              <CheckCircle2 className="w-12 h-12 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-foreground mb-2">
              {filter === 'completed' ? 'No completed reminders' : 'No reminders yet'}
            </h3>
            <p className="text-text-secondary max-w-sm text-center">
              {filter === 'completed'
                ? 'You haven\'t completed any reminders yet'
                : 'Create your first reminder to get started and stay organized!'}
            </p>
            {filter !== 'all' && (
              <button
                onClick={() => setFilter('all')}
                className="mt-4 text-primary font-medium hover:underline"
              >
                View all reminders
              </button>
            )}
          </div>
        )}
      </main>

      {/* Add Reminder Modal */}
      <AddReminderModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAdd={handleAddReminder}
      />
    </div>
  );
}
