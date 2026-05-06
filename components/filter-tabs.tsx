'use client';

import { Filter } from 'lucide-react';

type FilterType = 'all' | 'active' | 'completed' | 'overdue';

interface FilterTabsProps {
  activeFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
  counts: {
    all: number;
    active: number;
    completed: number;
    overdue: number;
  };
}

export function FilterTabs({ activeFilter, onFilterChange, counts }: FilterTabsProps) {
  const filters: { id: FilterType; label: string; icon?: string }[] = [
    { id: 'all', label: 'All' },
    { id: 'active', label: 'Active' },
    { id: 'completed', label: 'Completed' },
    { id: 'overdue', label: 'Overdue' },
  ];

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2">
      <div className="flex items-center gap-1 text-text-secondary mr-2">
        <Filter className="w-4 h-4" />
        <span className="text-sm font-medium">Filter:</span>
      </div>
      
      <div className="flex gap-2">
        {filters.map((filter) => (
          <button
            key={filter.id}
            onClick={() => onFilterChange(filter.id)}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 whitespace-nowrap flex items-center gap-2 ${
              activeFilter === filter.id
                ? 'bg-primary text-white shadow-lg'
                : 'bg-background border border-border text-foreground hover:border-primary hover:text-primary'
            }`}
          >
            {filter.label}
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              activeFilter === filter.id
                ? 'bg-white/20'
                : 'bg-foreground/5'
            }`}>
              {counts[filter.id]}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
