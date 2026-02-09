import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, X } from 'lucide-react';
import MDEditor from '@uiw/react-md-editor';
import { useApp } from '~/renderer/contexts/AppContext';
import { GlassCard } from '~/renderer/components/GlassCard';
import { Button } from '~/renderer/components/ui/button';
import { Input } from '~/renderer/components/ui/input';
import { Textarea } from '~/renderer/components/ui/textarea';
import { Badge } from '~/renderer/components/ui/badge';
import { DIMENSIONS } from '~/renderer/lib/constants';

type MoodType = 'great' | 'good' | 'neutral' | 'bad' | 'terrible';

const MOODS: { type: MoodType; icon: any; color: string; label: string }[] = [
  { type: 'great', icon: () => '💖', color: 'text-pink-500', label: '很棒' },
  { type: 'good', icon: () => '😊', color: 'text-green-500', label: '不错' },
  { type: 'neutral', icon: () => '😐', color: 'text-yellow-500', label: '一般' },
  { type: 'bad', icon: () => '😞', color: 'text-orange-500', label: '不好' },
  { type: 'terrible', icon: () => '😢', color: 'text-red-500', label: '很糟' },
];

export function JournalEditorPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { state, updateState } = useApp();
  const isEditing = Boolean(id);

  const existingEntry = isEditing
    ? state.journals.find((j) => j.id === id)
    : null;

  const [title, setTitle] = useState(existingEntry?.title || '');
  const [content, setContent] = useState(existingEntry?.content || '');
  const [mood, setMood] = useState<MoodType>(existingEntry?.mood || 'good');
  const [tags, setTags] = useState<string[]>(existingEntry?.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [linkedDimensions, setLinkedDimensions] = useState<string[]>(
    existingEntry?.linkedDimensions || [],
  );

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove));
  };

  const handleToggleDimension = (dimType: string) => {
    setLinkedDimensions((prev) =>
      prev.includes(dimType)
        ? prev.filter((d) => d !== dimType)
        : [...prev, dimType],
    );
  };

  const handleSave = () => {
    if (!content.trim()) return;

    const entry = {
      id: isEditing ? id! : Math.random().toString(36).substr(2, 9),
      timestamp: existingEntry?.timestamp || Date.now(),
      title: title.trim(),
      content,
      mood,
      tags,
      attachments: [] as string[],
      linkedDimensions,
    };

    if (isEditing) {
      updateState({
        journals: state.journals.map((j) => (j.id === id ? entry : j)),
      });
    } else {
      updateState({ journals: [entry, ...state.journals] });
    }

    navigate('/journal');
  };

  const handleCancel = () => {
    navigate('/journal');
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 max-w-5xl mx-auto">
      <header className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={handleCancel}>
          <ArrowLeft size={20} />
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-apple-textMain dark:text-white">
            {isEditing ? '编辑日记' : '新建日记'}
          </h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleCancel}>
            取消
          </Button>
          <Button onClick={handleSave} disabled={!content.trim()} className="bg-purple-500 hover:bg-purple-600">
            <Save size={18} className="mr-2" />
            保存
          </Button>
        </div>
      </header>

      <div className="space-y-6">
        <GlassCard>
          <div className="space-y-6">
            <Input
              type="text"
              placeholder="标题（可选）"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="text-lg font-semibold bg-black/5 dark:bg-white/5 border-apple-border dark:border-white/10"
            />

            <div>
              <label className="text-sm font-medium text-apple-textSec dark:text-white/60 mb-3 block">
                选择情绪
              </label>
              <div className="flex gap-4">
                {MOODS.map((m) => (
                  <button
                    key={m.type}
                    onClick={() => setMood(m.type)}
                    className={`flex-1 p-4 rounded-xl transition-all flex flex-col items-center gap-2 ${
                      mood === m.type
                        ? 'bg-apple-bg2 dark:bg-white/10 scale-105 shadow-md'
                        : 'opacity-50 hover:opacity-80 hover:scale-105'
                    }`}
                  >
                    <span className="text-3xl">{m.icon()}</span>
                    <span className="text-xs font-medium text-apple-textSec dark:text-white/60">
                      {m.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <div data-color-mode="auto">
                <MDEditor
                  value={content}
                  onChange={(val) => setContent(val || '')}
                  height={400}
                  preview="edit"
                  hideToolbar={false}
                  visibleDragBar={false}
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-apple-textSec dark:text-white/60 mb-3 block">
                标签
              </label>
              <div className="flex gap-2 flex-wrap">
                {tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-sm px-3 py-1">
                    {tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-2 hover:text-destructive"
                    >
                      <X size={14} />
                    </button>
                  </Badge>
                ))}
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder="添加标签"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
                    className="w-32 h-8 bg-black/5 dark:bg-white/5"
                  />
                  <Button size="sm" variant="outline" onClick={handleAddTag}>
                    添加
                  </Button>
                </div>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-apple-textSec dark:text-white/60 mb-3 block">
                关联维度（可选）
              </label>
              <div className="flex flex-wrap gap-2">
                {DIMENSIONS.map((dim) => (
                  <button
                    key={dim.type}
                    onClick={() => handleToggleDimension(dim.type)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      linkedDimensions.includes(dim.type)
                        ? 'bg-opacity-20 shadow-sm'
                        : 'opacity-50 hover:opacity-80'
                    }`}
                    style={{
                      backgroundColor: linkedDimensions.includes(dim.type)
                        ? `${dim.color}20`
                        : undefined,
                      color: linkedDimensions.includes(dim.type)
                        ? dim.color
                        : undefined,
                    }}
                  >
                    {dim.label.split(' ')[0]}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
