import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Trash2, Edit, Calendar } from 'lucide-react';
import { useApp } from '~/renderer/contexts/AppContext';
import { GlassCard } from '~/renderer/components/GlassCard';
import { Button } from '~/renderer/components/ui/button';
import { Badge } from '~/renderer/components/ui/badge';
import { DIMENSIONS, MOODS, type MoodType } from '~/renderer/lib/constants';
import { formatDateTimeCN } from '~/renderer/lib/dateUtils';
import MDEditor from '@uiw/react-md-editor';

export function JournalDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { state, updateState } = useApp();

  const entry = state.journals.find((j) => j.id === id);

  if (!entry) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-apple-textTer dark:text-white/20">
        <p>日记不存在</p>
        <Link to="/journal">
          <Button variant="outline" className="mt-4">
            返回列表
          </Button>
        </Link>
      </div>
    );
  }

  const moodObj = MOODS.find((m) => m.type === entry.mood);
  const linkedDims = entry.linkedDimensions
    ? DIMENSIONS.filter((d) => entry.linkedDimensions?.includes(d.type))
    : [];

  const handleDelete = () => {
    if (confirm('确定要删除这篇日记吗？')) {
      updateState({
        journals: state.journals.filter((j) => j.id !== id),
      });
      navigate('/journal');
    }
  };

  const handleEdit = () => {
    navigate(`/journal/${id}/edit`);
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 max-w-4xl mx-auto">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/journal">
            <Button variant="ghost" size="icon">
              <ArrowLeft size={20} />
            </Button>
          </Link>
          <div>
            {entry.title && (
              <h1 className="text-2xl font-bold text-apple-textMain dark:text-white">
                {entry.title}
              </h1>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={handleEdit} title="编辑">
            <Edit size={18} />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={handleDelete}
            className="hover:bg-destructive/10 hover:text-destructive"
            title="删除"
          >
            <Trash2 size={18} />
          </Button>
        </div>
      </header>

      <GlassCard>
        <div className="space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-apple-border dark:border-white/5">
            <div className="flex items-center gap-4">
              <span className="text-4xl">{moodObj?.emoji()}</span>
              <div>
                <div className="text-sm font-medium text-apple-textTer dark:text-white/30 uppercase tracking-widest">
                  {moodObj?.label}
                </div>
                <div className="flex items-center gap-2 text-sm text-apple-textSec dark:text-white/40 mt-1">
                  <Calendar size={14} />
                  {formatDateTimeCN(entry.timestamp)}
                </div>
              </div>
            </div>
          </div>

          <div data-color-mode="auto">
            <MDEditor.Markdown
              source={entry.content}
              style={{ backgroundColor: 'transparent' }}
            />
          </div>

          {entry.tags && entry.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-4 border-t border-apple-border dark:border-white/5">
              {entry.tags.map((tag) => (
                <Badge key={tag} variant="secondary">
                  {tag}
                </Badge>
              ))}
            </div>
          )}

          {linkedDims.length > 0 && (
            <div className="pt-4 border-t border-apple-border dark:border-white/5">
              <div className="text-xs text-apple-textTer dark:text-white/20 uppercase font-bold mb-3 tracking-widest">
                关联维度
              </div>
              <div className="flex flex-wrap gap-2">
                {linkedDims.map((dim) => (
                  <Badge
                    key={dim.type}
                    className="text-white"
                    style={{ backgroundColor: dim.color }}
                  >
                    {dim.label}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
