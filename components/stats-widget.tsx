'use client';

import { CheckCircle2, AlertCircle, Clock } from 'lucide-react';

interface StatsWidgetProps {
  total: number;
  completed: number;
  overdue: number;
  upcoming: number;
}

export function StatsWidget({ total, completed, overdue, upcoming }: StatsWidgetProps) {
  const stats = [
    {
      label: 'Total',
      value: total,
      icon: Clock,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      textColor: 'text-blue-700 dark:text-blue-200',
    },
    {
      label: 'Completed',
      value: completed,
      icon: CheckCircle2,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      textColor: 'text-green-700 dark:text-green-200',
    },
    {
      label: 'Overdue',
      value: overdue,
      icon: AlertCircle,
      color: 'from-red-500 to-red-600',
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      textColor: 'text-red-700 dark:text-red-200',
    },
    {
      label: 'Upcoming',
      value: upcoming,
      icon: Clock,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      textColor: 'text-purple-700 dark:text-purple-200',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div
            key={index}
            className={`${stat.bgColor} border border-transparent rounded-lg p-4 transition-all duration-300 hover:shadow-md hover:border-foreground/10`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-text-secondary font-medium">{stat.label}</p>
                <p className={`text-3xl font-bold mt-1 ${stat.textColor}`}>{stat.value}</p>
              </div>
              <div className={`bg-gradient-to-br ${stat.color} p-3 rounded-lg`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
