import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Search, Smile, Frown, Meh, Heart, Calendar, Plus } from 'lucide-react';
import { useApp } from '~/renderer/contexts/AppContext';
import { GlassCard } from '~/renderer/components/GlassCard';
import { Input } from '~/components/ui/input';
import { Button } from '~/components/ui/button';
import { Badge } from '~/components/ui/badge';

type MoodType = 'great' | 'good' | 'neutral' | 'bad' | 'terrible';

const MOODS: { type: MoodType; icon: any; color: string; label: string }[] = [
  { type: 'great', icon: Heart, color: 'text-pink-500', label: '很棒' },
  { type: 'good', icon: Smile, color: 'text-green-500', label: '不错' },
  { type: 'neutral', icon: Meh, color: 'text-yellow-500', label: '一般' },
  { type: 'bad', icon: Frown, color: 'text-orange-500', label: '不好' },
  { type: 'terrible', icon: Frown, color: 'text-red-500', label: '很糟' },
];

export function JournalPage() {
  const { state, updateState } = useApp();
  const [content, setContent] = useState('');
  const [mood, setMood] = useState<MoodType>('good');
  const [search, setSearch] = useState('');

  const addEntry = () => {
    if (!content.trim()) return;
    const entry = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: Date.now(),
      content,
      mood,
      tags: [] as string[],
      attachments: [] as string[],
      linkedDimensions: [] as string[],
    };
    updateState({ journals: [entry, ...state.journals] });
    setContent('');
    setMood('good');
  };

  const filteredJournals = state.journals.filter((j) =>
    j.content.toLowerCase().includes(search.toLowerCase()),
  );

  // 按日期分组
  const groupedJournals = filteredJournals.reduce((acc, journal) => {
    const date = new Date(journal.timestamp).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(journal);
    return acc;
  }, {} as Record<string, typeof filteredJournals>);

  // 计算情绪分布
  const moodDistribution = state.journals.reduce(
    (acc, j) => {
      acc[j.mood] = (acc[j.mood] || 0) + 1;
      return acc;
    },
    {} as Record<MoodType, number>,
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-apple-textMain dark:text-white flex items-center gap-3">
            <Sparkles className="text-purple-500" />
            生活日记
          </h1>
          <p className="text-apple-textSec dark:text-white/40 mt-1">
            记录您的旅程，捕捉您的情绪，在反思中不断成长。
          </p>
        </div>
        <Link to="/journal/new">
          <Button className="bg-purple-500 hover:bg-purple-600">
            <Plus size={20} className="mr-2" />
            新建日记
          </Button>
        </Link>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <GlassCard title="快速记录">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex gap-3">
                  {MOODS.map((m) => (
                    <button
                      key={m.type}
                      onClick={() => setMood(m.type)}
                      className={`p-2 rounded-xl transition-all ${
                        mood === m.type
                          ? 'bg-apple-bg2 dark:bg-white/10 scale-110 shadow-sm'
                          : 'opacity-40 hover:opacity-100'
                      }`}
                      title={m.label}
                    >
                      <m.icon className={m.color} size={28} />
                    </button>
                  ))}
                </div>
                <div className="text-xs text-apple-textTer dark:text-white/30 font-medium">
                  {new Date().toLocaleDateString('zh-CN', {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric',
                  })}
                </div>
              </div>

              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="现在在想什么？今天过得怎么样？"
                className="w-full h-40 bg-black/5 dark:bg-white/5 border border-apple-border dark:border-white/10 rounded-2xl p-5 text-apple-textMain dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 resize-none text-base leading-relaxed shadow-inner"
              />

              <div className="flex justify-end">
                <Button
                  onClick={addEntry}
                  disabled={!content.trim()}
                  className="bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 disabled:opacity-50"
                >
                  保存日记
                </Button>
              </div>
            </div>
          </GlassCard>

          <div className="space-y-6">
            {Object.entries(groupedJournals).map(([date, journals]) => (
              <div key={date}>
                <h3 className="text-sm font-bold text-apple-textTer dark:text-white/30 uppercase tracking-widest mb-3 flex items-center gap-2">
                  <Calendar size={16} />
                  {date}
                </h3>
                <div className="space-y-3">
                  {journals.map((j) => {
                    const moodObj = MOODS.find((m) => m.type === j.mood);
                    const MoodIcon = moodObj?.icon;

                    return (
                      <GlassCard
                        key={j.id}
                        className="group border-apple-border dark:border-white/5 hover:border-purple-500/20 cursor-pointer"
                      >
                        <Link to={`/journal/${j.id}`} className="block">
                          <div className="flex gap-5">
                            <div className="flex flex-col items-center gap-2 pt-1">
                              {MoodIcon && <MoodIcon className={moodObj?.color} size={24} />}
                            </div>
                            <div className="flex-1 space-y-2">
                              <div className="flex justify-between items-start">
                                <div className="text-xs font-bold text-apple-textTer dark:text-white/20 uppercase tracking-widest">
                                  {new Date(j.timestamp).toLocaleTimeString('zh-CN', {
                                    hour: '2-digit',
                                    minute: '2-digit',
                                  })}
                                </div>
                                {j.tags && j.tags.length > 0 && (
                                  <div className="flex gap-1">
                                    {j.tags.slice(0, 2).map((tag) => (
                                      <Badge key={tag} variant="secondary" className="text-xs">
                                        {tag}
                                      </Badge>
                                    ))}
                                  </div>
                                )}
                              </div>
                              <p className="text-apple-textSec dark:text-white/80 leading-relaxed line-clamp-3">
                                {j.content}
                              </p>
                            </div>
                          </div>
                        </Link>
                      </GlassCard>
                    );
                  })}
                </div>
              </div>
            ))}

            {filteredJournals.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16 text-apple-textTer dark:text-white/20">
                <Sparkles size={48} className="mb-3 opacity-50" />
                <p className="text-lg">开始记录您的第一篇日记吧</p>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <GlassCard title="搜索">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-apple-textSec dark:text-white/30" size={18} />
              <Input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="搜索回忆..."
                className="pl-10 bg-black/5 dark:bg-white/5 border-apple-border dark:border-white/10"
              />
            </div>
          </GlassCard>

          <GlassCard title="数据统计">
            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="text-apple-textSec dark:text-white/40">日记总数</span>
                <span className="text-apple-textMain dark:text-white font-bold">
                  {state.journals.length}
                </span>
              </div>

              <div className="pt-4 border-t border-apple-border dark:border-white/5">
                <div className="text-xs text-apple-textTer dark:text-white/20 uppercase font-bold mb-3 tracking-widest">
                  情绪分布
                </div>
                <div className="space-y-2">
                  {MOODS.map((m) => {
                    const count = moodDistribution[m.type] || 0;
                    const percentage = state.journals.length
                      ? Math.round((count / state.journals.length) * 100)
                      : 0;
                    return (
                      <div key={m.type} className="flex items-center gap-2 text-xs">
                        <m.icon className={m.color} size={16} />
                        <div className="flex-1 h-2 bg-apple-bg2 dark:bg-white/5 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${m.color.replace('text-', 'bg-')} shadow-[0_0_8px_currentColor]`}
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="text-apple-textTer dark:text-white/30 w-8 text-right">
                          {count}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
